"""Pure reservation transforms: inputs remain untouched."""
from stock import available, merge_units, normalize, sku, units


def reserve(stock, reserved, key, quantity):
    units(quantity)
    if available(stock, reserved, key) < quantity:
        raise ValueError("insufficient stock")
    result = normalize(reserved)
    result[sku(key)] = result.get(key, 0) + quantity
    return result


def release(reserved, key, quantity):
    units(quantity)
    result = normalize(reserved)
    if result.get(key, 0) < quantity:
        raise ValueError("release exceeds reservation")
    result[sku(key)] = result.get(key, 0) - quantity
    return result


def stock_report(stock, reserved):
    stock, reserved = normalize(stock), normalize(reserved)
    return tuple((key, stock.get(key, 0), reserved.get(key, 0), available(stock, reserved, key))
                 for key in sorted(stock.keys() | reserved.keys()))


def validate_state(stock, reserved):
    stock_report(stock, reserved)
    return True


def total_available(stock, reserved):
    return sum(row[3] for row in stock_report(stock, reserved))


def empty_reservations():
    return {}


def reserve_batch(stock, reserved, requests):
    result = normalize(reserved)
    for key, quantity in requests:
        result = reserve(stock, result, key, quantity)
    return result


def release_batch(reserved, requests):
    result = normalize(reserved)
    for key, quantity in requests:
        result = release(result, key, quantity)
    return result


def fulfill(stock, reserved, key, quantity):
    validate_state(stock, reserved)
    result_reserved = release(reserved, key, quantity)
    result_stock = normalize(stock)
    result_stock[key] = result_stock.get(key, 0) - quantity
    return result_stock, result_reserved


def restock(stock, deliveries):
    return merge_units(stock, deliveries)


def encode_state(stock, reserved):
    import json
    validate_state(stock, reserved)
    return json.dumps({'version': 1, 'stock': normalize(stock), 'reserved': normalize(reserved)}, sort_keys=True, separators=(',', ':'))


def decode_state(text):
    import json
    data = json.loads(text)
    if type(data) is not dict or set(data) != {'version', 'stock', 'reserved'} or type(data['version']) is not int or data['version'] != 1:
        raise ValueError("unsupported stock format")
    validate_state(data['stock'], data['reserved'])
    return normalize(data['stock']), normalize(data['reserved'])


def transfer(source, destination, source_reserved, key, quantity):
    units(quantity)
    if available(source, source_reserved, key) < quantity:
        raise ValueError("reserved supply cannot move")
    left, right = normalize(source), normalize(destination)
    left[sku(key)] = left.get(key, 0) - quantity
    right[key] = right.get(key, 0) + quantity
    return left, right


def allocate_orders(stock, reserved, orders):
    result = normalize(reserved)
    accepted = []
    for requests in orders:
        try:
            candidate = reserve_batch(stock, result, requests)
        except ValueError:
            accepted.append(False)
        else:
            result = candidate
            accepted.append(True)
    return result, tuple(accepted)


def expire_holds(holds, now):
    units(now)
    active, released, seen = [], {}, set()
    for identifier, key, quantity, expiry in holds:
        sku(identifier)
        sku(key)
        units(quantity)
        units(expiry)
        if identifier in seen:
            raise ValueError("duplicate hold")
        seen.add(identifier)
        if expiry <= now:
            released[key] = released.get(key, 0) + quantity
        else:
            active.append((identifier, key, quantity, expiry))
    return tuple(active), released


def shortage(stock, reserved, requests):
    totals = {}
    for key, quantity in requests:
        sku(key)
        totals[key] = totals.get(key, 0) + units(quantity)
    return tuple((key, deficit) for key in sorted(totals)
                 if (deficit := max(0, totals[key] - available(stock, reserved, key))))


def rebalance(stock, reserved, targets):
    validate_state(stock, reserved)
    return tuple((key, units(targets[key]) - available(stock, reserved, key)) for key in sorted(targets))


def audit_transition(before_stock, before_reserved, after_stock, after_reserved):
    before = {row[0]: row[1:] for row in stock_report(before_stock, before_reserved)}
    after = {row[0]: row[1:] for row in stock_report(after_stock, after_reserved)}
    return tuple((key,) + tuple(a - b for a, b in zip(after.get(key, (0, 0, 0)), before.get(key, (0, 0, 0))))
                 for key in sorted(before.keys() | after.keys()))


def apply_operations(stock, reserved, operations):
    supply, held = normalize(stock), normalize(reserved)
    validate_state(supply, held)
    for operation in operations:
        kind = operation['kind']
        if kind == 'reserve':
            held = reserve(supply, held, operation['sku'], operation['quantity'])
        elif kind == 'release':
            held = release(held, operation['sku'], operation['quantity'])
        elif kind == 'fulfill':
            supply, held = fulfill(supply, held, operation['sku'], operation['quantity'])
        elif kind == 'restock':
            supply = restock(supply, operation['deliveries'])
        else:
            raise ValueError("unknown operation")
    return supply, held
