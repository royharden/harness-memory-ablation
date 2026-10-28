"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    import re
    source = text(data)
    position = 0
    total = 0
    while position < len(source):
        if source[position].isspace():
            position += 1
            continue
        match = re.match(r"([0-9]+)(s|m)", source[position:])
        if match is None:
            raise ValueError("invalid duration term")
        amount = int(match.group(1))
        unit = match.group(2)
        total += amount * (1000 if unit == "s" else 1)
        position += match.end()
    return total
