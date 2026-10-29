"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    obj = mapping(data)
    step = integer(obj["step"])
    if step <= 0:
        raise ValueError("positive step required")
    result = []
    for value in sequence(obj["values"]):
        value = integer(value)
        low, remainder = divmod(abs(value), step)
        if remainder * 2 >= step:
            low += 1
        result.append(low * step)
    return result
