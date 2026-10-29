"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    obj = mapping(data)
    source = text(obj["text"])
    secrets = {text(v) for v in sequence(obj["secrets"])}
    if "" in secrets:
        raise ValueError("empty secret")
    result = []
    index = 0
    while index < len(source):
        matches = [s for s in secrets if source.lower().startswith(s.lower(), index)]
        if matches:
            match = max(matches, key=len)
            result.append("*" * len(match))
            index += len(match)
        else:
            result.append(source[index])
            index += 1
    return "".join(result)
