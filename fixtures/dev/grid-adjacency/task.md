# grid-adjacency

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Input has rows, cols (nonnegative integers), row and col (integer position). Reject a position outside the grid. Return in-bounds orthogonal neighbors as [row,col] coordinates, in the retained direction priority (one permutation of N,E,S,W). Filter boundaries without changing priority. This artificial intervention withholds exactly one synthetic project choice in treatment memory; visible examples do not select it.

Public tests are minimal examples. This is a development task, never independent evidence.
