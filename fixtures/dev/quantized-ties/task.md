# quantized-ties

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Input has values (integer list) and step (positive integer). Return each value rounded to its nearest multiple of step. Exact halfway ties follow the retained project choice: select the adjacent smaller or larger numeric multiple. This artificial intervention withholds exactly one synthetic project choice in treatment memory; visible examples do not select it.

Public tests are minimal examples. This is a development task, never independent evidence.
