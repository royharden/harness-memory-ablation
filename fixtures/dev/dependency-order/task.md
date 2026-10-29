# dependency-order

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Input maps string node names to lists of prerequisite names. All prerequisite names must be declared. Return a topological order, always choosing the lexicographically smallest currently ready node. Duplicate prerequisites have no extra effect. Reject cycles and unknown names.

Public tests are minimal examples. This is a development task, never independent evidence.
