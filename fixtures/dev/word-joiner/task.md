# word-joiner

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Input is a string. Split on runs of Unicode whitespace, lowercase every word with str.lower and join words using the retained separator choice (hyphen, underscore or period). Empty/whitespace-only input returns an empty string. Preserve nonwhitespace punctuation inside words. This artificial intervention withholds exactly one synthetic project choice in treatment memory; visible examples do not select it.

Public tests are minimal examples. This is a development task, never independent evidence.
