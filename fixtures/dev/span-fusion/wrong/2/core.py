"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    prepared = []
    for span in sequence(data):
        pair = sequence(span)
        if len(pair) != 2:
            raise ValueError("two endpoints required")
        start, end = (integer(v) for v in pair)
        if start > end:
            raise ValueError("reversed span")
        if start != end:
            prepared.append([start, end])
    result = []
    for start, end in sorted(prepared):
        if result and start <= result[-1][1]:
            result[-1][1] = end
        else:
            result.append([start, end])
    return result
