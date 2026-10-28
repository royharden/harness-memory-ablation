# rooted-path

Builder-authored development task; private-only pending rights and semantic review.

Implement `solve(data)` in `fixture/core.py`. Python 3.12 standard library only. Candidate module root contains `core.py` and `helpers.py`. Inputs and outputs are JSON-compatible. Reject out-of-domain inputs with `ValueError` (missing required fields may raise `KeyError`). Do not mutate inputs.

Current contract: input is a slash-separated string starting with /. Normalize repeated slashes and dot components. Resolve .. by popping a prior ordinary component. Reject attempts above root; never clamp silently. Return a rooted string with no trailing slash except root. Preserve other spelling literally, including backslashes. Archived clamping advice is stale.

Public tests are minimal examples. This is a development task, never independent evidence.
