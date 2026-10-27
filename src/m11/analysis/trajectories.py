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


def summarize_public_checkpoints(checkpoints: list[dict]) -> list[dict]:
    """Adapt DL3 PublicCheckpoint only, after canonical PublicExport validation."""
    grouped = {}
    for row in checkpoints:
        key = (row["campaign_id"], row["trajectory_id"], row["seed_id"], row["treatment_id"], row["harness_id"])
        grouped.setdefault(key, []).append(row)
    results = []
    for (campaign, trajectory, seed, arm, harness), rows in sorted(grouped.items()):
        ordered = sorted(rows, key=lambda row: row["checkpoint"])
        normalized = []
        for row in ordered:
            identifiers, values = row["tripwire_ids"], row["tripwire_outcomes"]
            if len(identifiers) != 4 or len(values) != 4 or len(set(identifiers)) != 4:
                raise ValueError("four unique ordered tripwire IDs and outcomes required")
            if any(value is not None and type(value) is not bool for value in values):
                raise ValueError("tripwire outcomes must be boolean or null")
            normalized.append({"checkpoint": row["checkpoint"], "tripwires": {
                identifier: "unknown" if value is None else "pass" if value else "fail"
                for identifier, value in zip(identifiers, values, strict=True)
            }})
        summary = summarize_trajectory(seed, arm, normalized)
        summary.update({
            "campaign_id": campaign, "trajectory_id": trajectory, "harness_id": harness,
            "checkpoint_evidence": ordered,
            "new_feature_observations": [{"checkpoint": row["checkpoint"], "completed": row["feature_completed"], "missing_reason": row["feature_missing_reason"]} for row in ordered],
            "feature_inventory_reason": "public_checkpoint_has_completion_not_accrued_test_inventory",
            "reference_evidence": [{"checkpoint": row["checkpoint"], "reference_sha256": row["reference_sha256"], "missing_reason": row["reference_missing_reason"]} for row in ordered],
        })
        results.append(summary)
    return results
