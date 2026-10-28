# span-fusion

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Input is a list of [start,end] integer half-open spans. Reject reversed endpoints. Omit empty spans. Sort by start then end and merge overlaps AND touching spans. Return sorted disjoint spans.

Public tests are minimal examples. This is a development task, never independent evidence.
