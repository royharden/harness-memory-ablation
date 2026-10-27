# literal-redactor

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Current contract: input has text (string) and secrets (list of nonempty strings). Scan left to right. At each position choose the longest literal matching secret, mask it with the same number of asterisks, then advance its length. Otherwise copy one character. Match case sensitively and preserve length. Reject empty secrets. Archived deletion advice is obsolete.

Public tests are minimal examples. This is a development task, never independent evidence.
