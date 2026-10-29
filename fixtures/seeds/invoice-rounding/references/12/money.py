"""Exact invoice primitives; decimal inputs must be strings or integers."""
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
