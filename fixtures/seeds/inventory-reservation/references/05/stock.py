"""Original integer stock primitives; no I/O or persistent global state."""


def units(value):
    if type(value) is not int or value < 0:
        raise ValueError("nonnegative integer units required")
    return value


def sku(value):
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError("nonblank canonical SKU required")
    return value


def normalize(stock):
    return {sku(key): units(value) for key, value in stock.items()}


def available(stock, reserved, key):
    sku(key)
    supply = units(stock.get(key, 0))
    held = units(reserved.get(key, 0))
    if held > supply:
        raise ValueError("over-reserved stock")
    return supply - held


def merge_units(left, right):
    result = normalize(left)
    for key, value in normalize(right).items():
        result[key] = result.get(key, 0) + value
    return result
