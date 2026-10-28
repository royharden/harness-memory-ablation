"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    source = text(data)
    if not source.startswith("/"):
        raise ValueError("rooted path required")
    parts = []
    for part in source.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                raise ValueError("above root")
            parts.pop(0)
        else:
            parts.append(part)
    return "/" + "/".join(parts)
