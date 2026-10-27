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
