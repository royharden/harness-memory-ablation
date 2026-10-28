"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    winners = {}
    for record in sequence(data):
        record = mapping(record)
        key = text(record["key"])
        revision = integer(record["revision"])
        if key not in winners or revision > winners[key][0]:
            winners[key] = (revision, record["value"])
    return {key: entry[1] for key, entry in winners.items()}
