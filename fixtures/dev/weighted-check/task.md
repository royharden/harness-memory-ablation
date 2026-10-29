# weighted-check

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Current contract: input is a list of integers in 0..255. Return sum((index+1)*byte) modulo 251, where index starts at zero. Empty returns 0. Reject out-of-range bytes, booleans and nonintegers. Current positional weighting and modulus override the archived plain-sum checksum proposal.

Public tests are minimal examples. This is a development task, never independent evidence.
