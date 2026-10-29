"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    obj = mapping(data)
    graph = mapping(obj["graph"])
    start = text(obj["start"])
    if start not in graph:
        raise ValueError("unknown start")
    for node, neighbors in graph.items():
        text(node)
        if not {text(v) for v in sequence(neighbors)} <= graph.keys():
            raise ValueError("unknown neighbor")
    queue = [start]
    seen = {start}
    result = []
    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in sorted(set(graph[node]), reverse=False):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return result
