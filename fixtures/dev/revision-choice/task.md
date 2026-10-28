# revision-choice

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Input is a list of records with key (string), revision (integer) and value (JSON). For each key keep the greatest revision and return key-to-value mapping. Equal greatest revisions follow the retained encounter rule (first or last). This artificial intervention withholds exactly one synthetic project choice in treatment memory; visible examples do not select it.

Public tests are minimal examples. This is a development task, never independent evidence.
