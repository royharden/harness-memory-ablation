"""Builder-authored dev source; NOT_RUN; private-only pending review."""
from helpers import integer, mapping, sequence, text

def solve(data):
    graph = mapping(data)
    pending = {}
    for node, dependencies in graph.items():
        text(node)
        pending[node] = {text(v) for v in sequence(dependencies)}
        if not pending[node] <= graph.keys():
            raise ValueError("unknown prerequisite")
    order = []
    while pending:
        ready = sorted(node for node, deps in pending.items() if not deps)
        if not ready:
            raise ValueError("cycle")
        node = ready[0]
        order.append(node)
        del pending[node]
        for deps in pending.values():
            deps.discard(node)
    return order
