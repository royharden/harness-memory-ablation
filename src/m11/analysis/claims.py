"""Explicit export/2 observation conversion; no expected assertions are authored."""

from collections import defaultdict

from m11.rot import claim_drift


def summarize_public_claims(observations: list[dict], checkpoints: list[dict], seeds: list[dict]) -> list[dict]:
    """Consume only canonical parsed PublicClaim records and frozen seed mapping.

    The canonical producer owns candidate/grader/receipt/embargo validation. Keep
    every observation and unknown reason alongside the arithmetic presentation.
    """
    seed_by_id = {seed["seed_id"]: seed for seed in seeds}
    points = {point["cell_id"]: point for point in checkpoints}
    by_cell = defaultdict(list)
    seen = set()
    for observation in observations:
        key = (observation["cell_id"], observation["claim_id"])
        if observation["schema_version"] != "m11-public-claim/1" or key in seen:
            raise ValueError("invalid or duplicate public claim observation")
        seen.add(key)
        point = points.get(observation["cell_id"])
        if point is None or any(observation[key] != point[key] for key in ("campaign_id", "trajectory_id", "seed_id", "checkpoint", "attempt_id")) or observation["candidate_sha256"] != point["source_after_sha256"]:
            raise ValueError("public claim checkpoint/candidate binding mismatch")
        by_cell[observation["cell_id"]].append(observation)
    results = []
    for point in checkpoints:
        rows = by_cell[point["cell_id"]]
        registered = [row for row in rows if row["registered"]]
        additions = [row for row in rows if not row["registered"]]
        expected_ids = seed_by_id[point["seed_id"]]["claim_ids"]
        if [row["claim_id"] for row in registered] != expected_ids:
            raise ValueError("four ordered frozen registered claim observations required")
        normalized = []
        for row in registered:
            if any(value is not None and type(value) is not bool for value in (row["present"], row["anchor_present"], row["test_passed"])):
                raise ValueError("observed claim values must be boolean or null")
            normalized.append({
                "claim_id": row["claim_id"], "present": row["present"],
                "anchor_present": row["anchor_present"],
                "outcome": "unknown" if row["test_passed"] is None else "pass" if row["test_passed"] else "fail",
            })
        drift = claim_drift({"registered": normalized, "unregistered": [row["claim_id"] for row in additions]})
        results.append({
            "campaign_id": point["campaign_id"], "trajectory_id": point["trajectory_id"],
            "seed_id": point["seed_id"], "checkpoint": point["checkpoint"], "cell_id": point["cell_id"],
            "attempt_id": point["attempt_id"], "candidate_sha256": point["source_after_sha256"],
            "drift": drift, "claim_observations": rows,
            "interpretation": "observed_state_only; no independent evidence authenticated by analysis",
        })
    return results
