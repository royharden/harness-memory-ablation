"""Original in-memory invoice library. Amounts returned in integer cents."""
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


def tax_cents(subtotal, basis_points):
    integer(subtotal)
    integer(basis_points)
    return cents(Decimal(subtotal) * basis_points / Decimal(1000000))


def discounted(subtotal, discount):
    integer(subtotal)
    integer(discount)
    if discount > subtotal:
        raise ValueError("discount exceeds subtotal")
    return subtotal - discount


def split_charge(total, weights):
    return allocate(total, weights)


def quote(lines, discount=0, tax_basis_points=0):
    subtotal = invoice_total(lines)
    net = discounted(subtotal, discount)
    tax = tax_cents(net, tax_basis_points)
    return {'subtotal': subtotal, 'discount': discount, 'tax': tax, 'total': net + tax}


def encode_lines(lines):
    import json
    return json.dumps({'version': 1, 'lines': [[str(decimal(p)), q] for p, q in validate_lines(lines)]}, sort_keys=True, separators=(',', ':'))


def decode_lines(text):
    import json
    data = json.loads(text)
    if type(data) is not dict or set(data) != {'version', 'lines'} or type(data['version']) is not int or data['version'] != 1:
        raise ValueError("unsupported invoice format")
    return validate_lines(data['lines'])


def quote_batch(requests):
    return tuple(quote(**request) for request in requests)


def credit_balance(total, credits):
    integer(total)
    supplied = sum(integer(value) for value in credits)
    return {'due': max(0, total - supplied), 'unused': max(0, supplied - total)}


def group_totals(rows):
    totals = {}
    for code, lines in rows:
        code = currency_code(code)
        totals[code] = totals.get(code, 0) + invoice_total(lines)
    return tuple(sorted(totals.items()))


def installment_plan(total, count):
    integer(count, 1)
    return split_charge(total, [1] * count)
