# threshold-buckets

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Input has cuts (strictly increasing integer list) and values (integer list). Return bucket indices in 0..len(cuts). Values not equal to cuts cross all strictly smaller cuts. Equality uses the retained project choice: cross that cut or stay in its lower bucket. This artificial intervention withholds exactly one synthetic project choice in treatment memory; visible examples do not select it.

Public tests are minimal examples. This is a development task, never independent evidence.
