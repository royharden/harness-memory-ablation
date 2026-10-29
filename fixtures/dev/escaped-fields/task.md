# escaped-fields

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Input is a string of fields delimited by vertical bars. Backslash escapes exactly the next character, whether bar, backslash, or any other character. Preserve empty and trailing fields. Return decoded fields. Reject a trailing unpaired backslash.

Public tests are minimal examples. This is a development task, never independent evidence.
