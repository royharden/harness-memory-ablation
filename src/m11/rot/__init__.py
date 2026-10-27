"""Pure, stdlib-only M11 source and longitudinal metrics.

This package consumes explicit observations; it never executes candidate code.
See INPUTS.md for the public input contract and unavailable-state semantics.
"""

from .source import analyze_python
from .trajectory import claim_drift, tripwire_area

__all__ = ["analyze_python", "tripwire_area", "claim_drift"]
