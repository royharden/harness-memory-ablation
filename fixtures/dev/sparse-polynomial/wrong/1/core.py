"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    obj = mapping(data)
    x = integer(obj["x"])
    coefficients = {}
    for term in sequence(obj["terms"]):
        pair = sequence(term)
        if len(pair) != 2:
            raise ValueError("term needs exponent and coefficient")
        exponent, coefficient = (integer(v) for v in pair)
        if exponent < 0:
            raise ValueError("negative exponent")
        coefficients[exponent] = coefficient
    total = 0
    for exponent, coefficient in coefficients.items():
        total += coefficient * x ** exponent
    return total
