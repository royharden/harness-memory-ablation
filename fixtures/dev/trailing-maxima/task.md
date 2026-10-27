# trailing-maxima

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Input has values (integer list) and width (positive integer). For each position return the maximum of that value and up to width-1 immediately preceding values. Initial windows may be shorter; width above length is allowed. Empty values returns [].

Public tests are minimal examples. This is a development task, never independent evidence.
