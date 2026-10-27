"""Presentation-ready trajectory metrics from explicitly normalized observations."""

from m11.rot import tripwire_area


def summarize_trajectory(seed_id: str, treatment_id: str, checkpoints: list[dict]) -> dict:
    """No wire-shape guessing: the producer adapter supplies rot's documented input.

    A chart point is unavailable if any of its four tripwire observations is
    unknown. Missing sessions remain twelve planned checkpoints, not shorter plots.
    """
    if not isinstance(seed_id, str) or not seed_id or treatment_id not in {"L0", "L1", "L2"}:
        raise ValueError("explicit seed ID and longitudinal treatment required")
    metrics = tripwire_area(checkpoints)
    return {
        "seed_id": seed_id, "treatment_id": treatment_id,
        "metrics": metrics,
        "points": [
            {"checkpoint": row["checkpoint"],
             "value": row["failed"] / 4 if row["unknown"] == 0 else None,
             "numerator": row["failed"], "denominator": 4,
             "unknown_cells": row["unknown"],
             "reason": "unknown_tripwire_cells" if row["unknown"] else None}
            for row in metrics["checkpoints"]
        ],
        "point_definition": "observed_checkpoint_tripwire_failure_fraction",
        "trajectory_definition": "fixed48_tripwire_area",
        "interpretation": "descriptive_only; feature completion remains separate",
    }
