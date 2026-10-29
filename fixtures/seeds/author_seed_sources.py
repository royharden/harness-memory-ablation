"""Builder source writer only. Does not import or execute authored seed code."""
import ast
import json
import os
from pathlib import Path

ROOT = Path(__file__).parent
SESSION = os.environ['CODEX_THREAD_ID']
CALLSIGN = '0986_Codex_gpt-61-sol_Sub_M11DevSeeds'

MONEY = '''"""Exact invoice primitives; decimal inputs must be strings or integers."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def decimal(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise ValueError("use exact decimal input")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("invalid decimal input") from exc
    if not result.is_finite():
        raise ValueError("finite amounts required")
    return result


def cents(value):
    """Round ties away from zero, once, at the currency boundary."""
    return int((decimal(value) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("invalid integer")
    return value


def allocate(total, weights):
    """Largest remainder allocation, stable ties by input position."""
    integer(total)
    weights = tuple(integer(w) for w in weights)
    if not weights or sum(weights) == 0:
        raise ValueError("positive weight sum required")
    denominator = sum(weights)
    result = [total * w // denominator for w in weights]
    order = sorted(range(len(weights)), key=lambda i: (-(total * weights[i] % denominator), i))
    for i in order[:total - sum(result)]:
        result[i] += 1
    return tuple(result)
'''
INVOICE = '''"""Original in-memory invoice library. Amounts returned in integer cents."""
from decimal import Decimal
from money import allocate, cents, decimal, integer


def line_total(price, quantity):
    integer(quantity)
    amount = decimal(price)
    if amount < 0:
        raise ValueError("negative price")
    return cents(amount * quantity)


def invoice_total(lines):
    return sum(line_total(price, quantity) for price, quantity in lines)


def format_cents(amount):
    if type(amount) is not int:
        raise ValueError("integer cents required")
    sign = '-' if amount < 0 else ''
    whole, fraction = divmod(abs(amount), 100)
    return f'{sign}{whole}.{fraction:02d}'


def validate_lines(lines):
    rows = tuple(lines)
    for price, quantity in rows:
        line_total(price, quantity)
    return rows


def subtotal_report(lines):
    rows = validate_lines(lines)
    totals = tuple(line_total(*row) for row in rows)
    return {'lines': totals, 'total': sum(totals)}


def currency_code(code):
    if not isinstance(code, str) or len(code) != 3 or not code.isascii() or not code.isupper() or not code.isalpha():
        raise ValueError("three uppercase ASCII letters required")
    return code
'''
STOCK = '''"""Original integer stock primitives; no I/O or persistent global state."""


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
'''
RESERVATIONS = '''"""Pure reservation transforms: inputs remain untouched."""
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
'''
# Each tuple contains request, complete accrued source addition, and its public unit source.
INV = [
('Add tax_cents(subtotal, basis_points); round the tax half-up and reject negative inputs.', '''def tax_cents(subtotal, basis_points):
    integer(subtotal)
    integer(basis_points)
    return cents(Decimal(subtotal) * basis_points / Decimal(1000000))
''', "assert tax_cents(101, 5000) == 51\nassert tax_cents(0, 500) == 0"),
('Add discounted(subtotal, discount); discounts are integer cents and cannot exceed subtotal.', '''def discounted(subtotal, discount):
    integer(subtotal)
    integer(discount)
    if discount > subtotal:
        raise ValueError("discount exceeds subtotal")
    return subtotal - discount
''', 'assert discounted(101, 1) == 100\nassert discounted(10, 10) == 0'),
('Expose split_charge(total, weights) using stable largest remainders; conserve all cents.', '''def split_charge(total, weights):
    return allocate(total, weights)
''', 'assert split_charge(5, [1, 1, 1]) == (2, 2, 1)\nassert split_charge(1, [0, 2]) == (0, 1)'),
('Add quote(lines, discount=0, tax_basis_points=0), applying discount before tax.', '''def quote(lines, discount=0, tax_basis_points=0):
    subtotal = invoice_total(lines)
    net = discounted(subtotal, discount)
    tax = tax_cents(net, tax_basis_points)
    return {'subtotal': subtotal, 'discount': discount, 'tax': tax, 'total': net + tax}
''', "assert quote([('1.00', 2)], 50, 1000) == {'subtotal': 200, 'discount': 50, 'tax': 15, 'total': 165}"),
('Add encode_lines/decode_lines pure JSON format version1; preserve exact decimal text and order; reject unsupported versions.', '''def encode_lines(lines):
    import json
    return json.dumps({'version': 1, 'lines': [[str(p), q] for p, q in validate_lines(lines)]}, sort_keys=True, separators=(',', ':'))


def decode_lines(text):
    import json
    data = json.loads(text)
    if type(data) is not dict or set(data) != {'version', 'lines'} or type(data['version']) is not int or data['version'] != 1:
        raise ValueError("unsupported invoice format")
    return validate_lines(data['lines'])
''', "assert decode_lines(encode_lines([('1.005', 2)])) == (['1.005', 2],); assert decode_lines(encode_lines([('001.00', 2), ('1e2', 1)])) == (['001.00', 2], ['1e2', 1])"),
('Add quote_batch(requests) accepting dictionaries with lines and optional quote options; preserve input order.', '''def quote_batch(requests):
    return tuple(quote(**request) for request in requests)
''', "assert [r['total'] for r in quote_batch([{'lines': [('1', 1)]}, {'lines': []}])] == [100, 0]"),
('Add credit_balance(total, credits); apply ordered nonnegative credits with zero floor; return unused credit.', '''def credit_balance(total, credits):
    integer(total)
    supplied = sum(integer(value) for value in credits)
    return {'due': max(0, total - supplied), 'unused': max(0, supplied - total)}
''', "assert credit_balance(100, [30, 90]) == {'due': 0, 'unused': 20}"),
('Add group_totals(rows) where rows are (currency,lines); do not mix currencies; output currency-sorted pairs.', '''def group_totals(rows):
    totals = {}
    for code, lines in rows:
        code = currency_code(code)
        totals[code] = totals.get(code, 0) + invoice_total(lines)
    return tuple(sorted(totals.items()))
''', "assert group_totals([('USD', [('1', 1)]), ('EUR', [('2', 1)]), ('USD', [])]) == (('EUR', 200), ('USD', 100))"),
('Add installment_plan(total,count); positive count, earliest installments receive remainder cents.', '''def installment_plan(total, count):
    integer(count, 1)
    return split_charge(total, [1] * count)
''', 'assert installment_plan(10, 3) == (4, 3, 3)\nassert installment_plan(0, 2) == (0, 0)'),
('Add progressive_total(quantity, tiers) where sorted (exclusive upper bound, price) tiers cover quantity; charge marginal quantities, round each tier once.', '''def progressive_total(quantity, tiers):
    integer(quantity)
    previous = 0
    total = 0
    for upper, price in tiers:
        integer(upper, previous + 1)
        line_total(price, 0)
        used = max(0, min(quantity, upper) - previous)
        total += line_total(price, used)
        previous = upper
    if quantity > previous:
        raise ValueError("tiers do not cover quantity")
    return total
''', "assert progressive_total(5, [(3, '1.00'), (10, '0.50')]) == 400"),
('Add reconcile(total,payments); signed integer payments permit refunds, return signed outstanding and settlement flag.', '''def reconcile(total, payments):
    integer(total)
    paid = 0
    for value in payments:
        if type(value) is not int:
            raise ValueError("integer payment required")
        paid += value
    return {'outstanding': total - paid, 'settled': paid == total}
''', "assert reconcile(100, [120, -20]) == {'outstanding': 0, 'settled': True}"),
('Refactor quote aggregation through summarize_quotes(quotes); expose batch_summary(requests) counting invoices and summing subtotal/discount/tax/total.', '''def summarize_quotes(quotes):
    result = {'count': 0, 'subtotal': 0, 'discount': 0, 'tax': 0, 'total': 0}
    for row in quotes:
        result['count'] += 1
        for field in ('subtotal', 'discount', 'tax', 'total'):
            result[field] += integer(row[field])
    return result


def batch_summary(requests):
    return summarize_quotes(quote_batch(requests))
''', "assert batch_summary([{'lines': [('1', 2)], 'discount': 50, 'tax_basis_points': 1000}]) == {'count': 1, 'subtotal': 200, 'discount': 50, 'tax': 15, 'total': 165}")]
INVENT = [
('Add reserve_batch(stock,reserved,requests); apply ordered (SKU,quantity) atomically without mutating inputs.', '''def reserve_batch(stock, reserved, requests):
    result = normalize(reserved)
    for key, quantity in requests:
        result = reserve(stock, result, key, quantity)
    return result
''', "assert reserve_batch({'A': 5}, {}, [('A', 2), ('A', 1)]) == {'A': 3}"),
('Add release_batch(reserved,requests); ordered releases use the same validation and leave input untouched.', '''def release_batch(reserved, requests):
    result = normalize(reserved)
    for key, quantity in requests:
        result = release(result, key, quantity)
    return result
''', "assert release_batch({'A': 5}, [('A', 1), ('A', 2)]) == {'A': 2}"),
('Add fulfill(stock,reserved,SKU,quantity); reduce both supply and reservation after bounds checks.', '''def fulfill(stock, reserved, key, quantity):
    validate_state(stock, reserved)
    result_reserved = release(reserved, key, quantity)
    result_stock = normalize(stock)
    result_stock[key] = result_stock.get(key, 0) - quantity
    return result_stock, result_reserved
''', "assert fulfill({'A': 5}, {'A': 3}, 'A', 2) == ({'A': 3}, {'A': 1})"),
('Add restock(stock,deliveries); merge nonnegative per-SKU quantities purely.', '''def restock(stock, deliveries):
    return merge_units(stock, deliveries)
''', "assert restock({'A': 2}, {'A': 3, 'B': 1}) == {'A': 5, 'B': 1}"),
('Add encode_state/decode_state pure version1 sorted JSON; validate state before encoding and after decoding.', '''def encode_state(stock, reserved):
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
''', "assert decode_state(encode_state({'A': 5}, {'A': 2})) == ({'A': 5}, {'A': 2})"),
('Add transfer(source,destination,source_reserved,SKU,quantity); only unreserved source supply can move.', '''def transfer(source, destination, source_reserved, key, quantity):
    units(quantity)
    if available(source, source_reserved, key) < quantity:
        raise ValueError("reserved supply cannot move")
    left, right = normalize(source), normalize(destination)
    left[sku(key)] = left.get(key, 0) - quantity
    right[key] = right.get(key, 0) + quantity
    return left, right
''', "assert transfer({'A': 5}, {'A': 1}, {'A': 2}, 'A', 3) == ({'A': 2}, {'A': 4})"),
('Add allocate_orders(stock,reserved,orders); first-fit whole orders, return final reservations and ordered accepted booleans.', '''def allocate_orders(stock, reserved, orders):
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
''', "assert allocate_orders({'A': 3}, {}, [[('A', 2)], [('A', 2)], [('A', 1)]]) == ({'A': 3}, (True, False, True))"),
('Add expire_holds(holds,now); holds are (id,SKU,quantity,expiry), expiry<=now releases; return active rows and released quantities.', '''def expire_holds(holds, now):
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
''', "assert expire_holds([('h1', 'A', 2, 5), ('h2', 'A', 1, 6)], 5) == ((('h2', 'A', 1, 6),), {'A': 2})"),
('Add shortage(stock,reserved,requests); aggregate repeated SKU requests then return only positive deficits sorted by SKU.', '''def shortage(stock, reserved, requests):
    totals = {}
    for key, quantity in requests:
        sku(key)
        totals[key] = totals.get(key, 0) + units(quantity)
    return tuple((key, deficit) for key in sorted(totals)
                 if (deficit := max(0, totals[key] - available(stock, reserved, key))))
''', "assert shortage({'A': 4}, {'A': 1}, [('A', 2), ('A', 3)]) == (('A', 2),)"),
('Add rebalance(stock,reserved,targets); targets are desired available units; return sorted signed adjustment quantities without applying them.', '''def rebalance(stock, reserved, targets):
    validate_state(stock, reserved)
    return tuple((key, units(targets[key]) - available(stock, reserved, key)) for key in sorted(targets))
''', "assert rebalance({'A': 5}, {'A': 2}, {'A': 1, 'B': 2}) == (('A', -2), ('B', 2))"),
('Add audit_transition(before_stock,before_reserved,after_stock,after_reserved); report per-SKU supply/reservation/available deltas including removed keys.', '''def audit_transition(before_stock, before_reserved, after_stock, after_reserved):
    before = {row[0]: row[1:] for row in stock_report(before_stock, before_reserved)}
    after = {row[0]: row[1:] for row in stock_report(after_stock, after_reserved)}
    return tuple((key,) + tuple(a - b for a, b in zip(after.get(key, (0, 0, 0)), before.get(key, (0, 0, 0))))
                 for key in sorted(before.keys() | after.keys()))
''', "assert audit_transition({'A': 5}, {'A': 2}, {'A': 4}, {'A': 1}) == (('A', -1, -1, 0),)"),
('Refactor operation dispatch through apply_operations(stock,reserved,operations); support reserve/release/fulfill/restock op dictionaries atomically, reject unknown operations.', '''def apply_operations(stock, reserved, operations):
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
''', "assert apply_operations({'A': 2}, {}, [{'kind': 'reserve', 'sku': 'A', 'quantity': 2}, {'kind': 'fulfill', 'sku': 'A', 'quantity': 1}]) == ({'A': 1}, {'A': 1})")]


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + '\n', encoding='utf-8')


def unit(module, name, body):
    return f'from {module} import *\n\n\ndef test_{name}():\n' + ''.join('    ' + line + '\n' for line in body.splitlines())


def build(identifier, modules, main, features, invariants):
    folder = ROOT / identifier
    tripwire_ids = [f'{identifier}-B{i}' for i in range(1, 5)]
    claim_ids = [f'{identifier}-C{i}' for i in range(1, 5)]
    readme = f'# {identifier}\n\nOriginal builder-owned DEVELOPMENT seed only. Rights: private_only_pending_review.\nExecution: NOT_RUN. Independent/P0/held-out status: absent.\n\n'
    claims = []
    for index, (text, check) in enumerate(invariants, 1):
        anchor = f'claim-{identifier}-C{index}'
        readme += f'<a id="{anchor}"></a>\n- [{identifier}-C{index}] {text}\n'
        check_path = f'claims/check_C{index}.py'
        write(folder / check_path, unit(main, f'claim_C{index}', check))
        claims.append({'id': claim_ids[index-1], 'assertion': text, 'source_anchor': {'path': 'README.md', 'anchor': anchor}, 'check_path': check_path, 'check_callable': f'test_claim_C{index}'})
        write(folder / f'tripwires/test_B{index}.py', unit(main, f'baseline_B{index}', check))
    readme += '\nReference sources and checkers share builder lineage. They are private construction artifacts, not independent oracles. Future trusted custody must keep references and future features/tests out of candidate workspaces. No source execution has occurred.\n'
    for name, source in modules.items():
        write(folder / 'baseline' / name, source)
    write(folder / 'baseline/README.md', readme)
    write(folder / 'README.md', readme + '\nEach checkpoint exposes baseline README/tripwires/claim checks, its feature request, and only tests with ordinal <= current. Earlier requests may be archived; future requests and all references are withheld by future custody tooling. Tests are source only and have not been evaluated.\n')
    write(folder / 'claims/registry.json', json.dumps({'schema_version': 'm11-dev-claims/1', 'execution_status': 'NOT_RUN', 'claims': claims}, indent=2))
    checkpoints = []
    accrued = dict(modules)
    for ordinal, (request, addition, assertions) in enumerate(features, 1):
        feature_path = f'features/{ordinal:02d}.md'
        test_path = f'visible_tests/test_{ordinal:02d}.py'
        write(folder / feature_path, f'# Feature {ordinal}: {identifier}\n\n{request}\n\nPreserve all baseline and previously requested behavior. All operations are in-memory, deterministic and pure; invalid inputs raise ValueError. No external I/O. Inputs satisfying the request shape are required.\n')
        write(folder / test_path, unit(main, f'feature_{ordinal:02d}', assertions))
        accrued[main + '.py'] += '\n\n' + addition
        paths = []
        for name, source in accrued.items():
            path = f'references/{ordinal:02d}/{name}'
            write(folder / path, source)
            paths.append(path)
        write(folder / f'references/{ordinal:02d}/README.md', readme)
        paths.append(f'references/{ordinal:02d}/README.md')
        checkpoints.append({'ordinal': ordinal, 'feature_path': feature_path, 'reference_paths': paths, 'visible_test_paths': [f'visible_tests/test_{i:02d}.py' for i in range(1, ordinal + 1)], 'claim_expectations': {claim: True for claim in claim_ids}, 'source_anchor': {claim['id']: claim['source_anchor'] for claim in claims}, 'execution_status': 'NOT_RUN'})
    return {'id': identifier, 'path': identifier, 'baseline_paths': ['baseline/' + name for name in modules] + ['baseline/README.md'], 'tripwire_ids': tripwire_ids, 'tripwire_paths': [f'tripwires/test_B{i}.py' for i in range(1, 5)], 'claim_ids': claim_ids, 'claim_registry_path': 'claims/registry.json', 'checkpoints': checkpoints}


manifest = {'schema_version': 'm11-dev-seeds/1', 'split': 'dev', 'author_session': SESSION, 'author_callsign': CALLSIGN, 'independence': 'builder_lineage', 'rights': 'private_only_pending_review', 'execution_status': 'NOT_RUN', 'split_seed': 11027, 'seeds': []}
manifest['seeds'].append(build('invoice-rounding', {'money.py': MONEY, 'invoice.py': INVOICE}, 'invoice', INV, [
    ('Unit prices multiply by quantity before half-up cent rounding.', "assert line_total('0.005', 2) == 1\nassert line_total('0.005', 1) == 1"),
    ('An empty invoice totals zero.', 'assert invoice_total([]) == 0'),
    ('Negative prices are rejected.', "try:\n    line_total('-0.01', 1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('negative price accepted')"),
    ('Signed integer cent formatting always emits two decimal digits.', "assert format_cents(-1) == '-0.01'\nassert format_cents(120) == '1.20'")]))
manifest['seeds'].append(build('inventory-reservation', {'stock.py': STOCK, 'reservations.py': RESERVATIONS}, 'reservations', INVENT, [
    ('Reserving supply never mutates the caller reservation mapping.', "original = {'A': 1}\nassert reserve({'A': 5}, original, 'A', 2) == {'A': 3}\nassert original == {'A': 1}"),
    ('Requests above available supply raise ValueError.', "try:\n    reserve({'A': 2}, {'A': 1}, 'A', 2)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('oversell accepted')"),
    ('Missing SKUs have zero available supply.', "assert available({}, {}, 'missing') == 0"),
    ('A zero reservation preserves the existing quantity.', "assert reserve({'A': 2}, {'A': 1}, 'A', 0) == {'A': 1}")]))
write(ROOT / 'manifest.json', json.dumps(manifest, indent=2))
write(ROOT / 'README.md', '# Builder development seed chains\n\nTwo original standard-library seed chains, twelve ordered feature requests each. All baseline modules, 24 full reference snapshots, accrued visible test sources, tripwire and claim check sources are builder-authored, private_only_pending_review and NOT_RUN. No independent P0/held-out material or execution receipt is present. manifest.json declares relative source paths and explicit claim expectations. Per-checkpoint visible_test_paths includes only accrued tests; references and future test/request source must not be mounted into candidate workspaces.\n\nReference R=0 is a future verification requirement, not an observed result. No oracle pass, baseline pass, feature completion, deterministic stability, custody seal or admission is claimed. References/checkers need future authorized execution and independent review. Claims are invariant baseline contracts expected true at every checkpoint; false or missing assertions/anchors must still be scored by the future checker.\n\nThe source writer is builder tooling only and does not evaluate authored modules.\n')
# Syntax parsing is the only authored-Python check; never import/compile/execute it.
paths = list(ROOT.rglob('*.py'))
for path in paths:
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
print(json.dumps({'author_session': SESSION, 'seeds': len(manifest['seeds']), 'full_reference_snapshots': sum(len(s['checkpoints']) for s in manifest['seeds']), 'syntax_parsed_python_files': len(paths), 'execution_status': 'NOT_RUN'}))
