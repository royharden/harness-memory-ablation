"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    rows = [sequence(row) for row in sequence(data)]
    if not rows:
        return []
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("ragged matrix")
    result = []
    for column in reversed(range(width)):
        result.append([row[column] for row in reversed(rows)])
    return result
