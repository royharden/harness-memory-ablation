"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    obj = mapping(data)
    cuts = [integer(v) for v in sequence(obj["cuts"])]
    if any(a >= b for a, b in zip(cuts, cuts[1:])):
        raise ValueError("cuts must strictly increase")
    result = []
    for value in sequence(obj["values"]):
        value = integer(value)
        result.append(sum(value >= cut for cut in cuts))
    return result
