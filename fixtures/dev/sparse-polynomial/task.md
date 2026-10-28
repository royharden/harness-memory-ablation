# sparse-polynomial

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Current contract: input has x (integer) and terms (list of [exponent,coefficient] integer pairs). Reject negative exponents. Evaluate the sum coefficient*x**exponent as an exact integer. Duplicate exponents contribute additively; zero coefficients and an empty term list are valid. Use Python integer power semantics, including x**0 = 1 when x is zero. An old overwrite-by-exponent design was never adopted.

Public tests are minimal examples. This is a development task, never independent evidence.
