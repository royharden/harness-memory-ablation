"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    obj = mapping(data)
    rows = integer(obj["rows"])
    cols = integer(obj["cols"])
    row = integer(obj["row"])
    col = integer(obj["col"])
    if not (0 <= row < rows and 0 <= col < cols):
        raise ValueError("position outside grid")
    offsets = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    result = []
    for dr, dc in offsets:
        nr, nc = row + dr, col + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            result.append([nr, nc])
    return result
