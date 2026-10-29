# rectangular-turn

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Current contract: input is a rectangular list of equal-length row lists with arbitrary JSON cells. Return a new matrix rotated 90 degrees clockwise. [] or a zero-column rectangular matrix returns []. Reject ragged rows. Preserve cell values. A historical transpose-only suggestion was never adopted.

Public tests are minimal examples. This is a development task, never independent evidence.
