# duration-terms

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Current contract: input string has zero or more nonnegative integer terms immediately followed by ms or s. Sum milliseconds (s=1000 ms). Whitespace is allowed before, between or after terms; adjacent terms need no separator. Repeated terms add. Empty/whitespace returns 0. Reject signs, decimals, unknown or missing suffixes and junk. Old integer-seconds-only advice is obsolete.

Public tests are minimal examples. This is a development task, never independent evidence.
