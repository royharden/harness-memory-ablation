"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    obj = mapping(data)
    result = dict(mapping(obj["base"]))
    for edit in sequence(obj["edits"]):
        pair = sequence(edit)
        if len(pair) != 2:
            raise ValueError("edit needs key and value")
        key = text(pair[0])
        value = pair[1]
        if not value:
            result.pop(key, None)
        else:
            result[key] = value
    return result
