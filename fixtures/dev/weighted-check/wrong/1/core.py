"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    total = 0
    for index, value in enumerate(sequence(data)):
        value = integer(value)
        if not 0 <= value <= 255:
            raise ValueError("byte outside range")
        total += value
    return total % 251
