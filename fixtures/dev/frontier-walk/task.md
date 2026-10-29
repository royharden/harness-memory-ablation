# frontier-walk

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Input has graph (object of string names to lists of adjacent names) and start (declared string name). Return reachable names once in breadth-first order. Reject unknown references. Ignore duplicate edges. Within each node process unseen neighbors in the retained lexical priority, either ascending or descending. Start comes first. This artificial intervention withholds exactly one synthetic project choice in treatment memory; visible examples do not select it.

Public tests are minimal examples. This is a development task, never independent evidence.
