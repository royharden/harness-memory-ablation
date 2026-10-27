"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    source = text(data)
    words = source.split()
    normalized = []
    for word in words:
        normalized.append(word)
    return ".".join(normalized)
