# record-overlay

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Input has base (object) and edits (list of [key,value]). Keys are strings. Apply edits in order to a copy. A null value deletes the key (missing deletes are harmless); all other JSON values overwrite or insert. Return resulting object.

Public tests are minimal examples. This is a development task, never independent evidence.
