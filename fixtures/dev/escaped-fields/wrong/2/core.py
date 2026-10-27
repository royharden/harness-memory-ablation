"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    fields = []
    current = []
    escaped = False
    for char in text(data):
        if escaped:
            current.extend(["\\", char])
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            fields.append("".join(current))
            current = []
        else:
            current.append(char)
    if escaped:
        raise ValueError("unfinished escape")
    fields.append("".join(current))
    return fields
