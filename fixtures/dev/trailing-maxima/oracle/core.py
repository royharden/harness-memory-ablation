"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    obj = mapping(data)
    values = [integer(v) for v in sequence(obj["values"])]
    width = integer(obj["width"])
    if width <= 0:
        raise ValueError("positive width required")
    result = []
    for index in range(len(values)):
        start = max(0, index - width + 1)
        result.append(max(values[start:index + 1]))
    return result
