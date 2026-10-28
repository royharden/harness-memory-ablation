"""Tripwire area and registered README assertion drift from explicit observations."""

from collections.abc import Mapping, Sequence


_STATES = {"pass": "pass", "fail": "fail", "unknown": "unknown",
           "generated_code_error": "fail", "infrastructure_loss": "unknown"}


def _states(value, label):
    if not isinstance(value, Mapping):
        raise TypeError(f"{label} must be a mapping")
    result = {}
    for key, state in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{label} IDs must be nonempty strings")
        if not isinstance(state, str) or state not in _STATES:
            raise ValueError(f"{label} contains an invalid observation")
        result[key] = _STATES[state]
    return result


def _area(failures, unknown, denominator):
    return {"numerator": failures, "denominator": denominator,
            "unknown_cells": unknown,
            "value": failures / denominator if denominator and not unknown else None,
            "lower_bound": failures / denominator if denominator else None,
            "upper_bound": (failures + unknown) / denominator if denominator else None,
            "unavailable_reason": "zero_denominator" if not denominator else
                "unknown_cells" if unknown else None}


def tripwire_area(checkpoints) -> dict:
    """Consume up to twelve checkpoint mappings; omitted checkpoints are unknown.

    Each supplied checkpoint requires four stable baseline IDs. Feature tests
    are independent observations, never inferred from baseline tripwire passes.
    """
    if not isinstance(checkpoints, Sequence) or isinstance(checkpoints, (str, bytes)):
        raise TypeError("checkpoints must be a sequence")
    rows = {}
    baseline_ids = None
    feature_ids = set()
    for row in checkpoints:
        if not isinstance(row, Mapping) or set(row) - {"checkpoint", "tripwires", "feature_tests"}:
            raise ValueError("invalid checkpoint mapping")
        if not {"checkpoint", "tripwires"} <= row.keys():
            raise ValueError("checkpoint and tripwires are required")
        checkpoint = row["checkpoint"]
        if type(checkpoint) is not int or not 1 <= checkpoint <= 12 or checkpoint in rows:
            raise ValueError("checkpoint must be unique integer 1..12")
        baseline = _states(row["tripwires"], "tripwires")
        if len(baseline) != 4:
            raise ValueError("exactly four baseline tripwires are required")
        if baseline_ids is None:
            baseline_ids = set(baseline)
        elif set(baseline) != baseline_ids:
            raise ValueError("baseline IDs must remain fixed across checkpoints")
        features = _states(row.get("feature_tests", {}), "feature_tests")
        feature_ids.update(features)
        rows[checkpoint] = (baseline, features)
    failures = unknown = 0
    first_failure = None
    series = []
    for checkpoint in range(1, 13):
        baseline, _ = rows.get(checkpoint, ({}, {}))
        failed = sum(state == "fail" for state in baseline.values())
        missing = 4 - len(baseline) + sum(state == "unknown" for state in baseline.values())
        failures += failed
        unknown += missing
        if failed and first_failure is None:
            first_failure = checkpoint
        series.append({"checkpoint": checkpoint, "failed": failed, "unknown": missing})
    result = _area(failures, unknown, 48)
    result.update({"definition": "tripwire-area/1", "reference_value": 0,
                   "reference_excess": result["value"], "checkpoints": series,
                   "first_observed_failure": first_failure,
                   "first_failure_exact": first_failure is not None and not any(
                       row["unknown"] for row in series[:first_failure - 1]),
                   "final_tripwire_failures": series[-1]["failed"],
                   "final_tripwire_unknown": series[-1]["unknown"]})
    activations = {}
    established_failures = established_unknown = established_denominator = 0
    for feature_id in sorted(feature_ids):
        activation = next((checkpoint for checkpoint in range(1, 13)
                           if rows.get(checkpoint, ({}, {}))[1].get(feature_id) == "pass"), None)
        activations[feature_id] = activation
        if activation is not None:
            for checkpoint in range(activation + 1, 13):
                state = rows.get(checkpoint, ({}, {}))[1].get(feature_id, "unknown")
                established_denominator += 1
                established_failures += state == "fail"
                established_unknown += state == "unknown"
    final_features = rows.get(12, ({}, {}))[1]
    result["feature_completion"] = {
        "definition": "feature-completion/1", "observed_feature_count": len(feature_ids),
        "final_passed": sum(state == "pass" for state in final_features.values()),
        "final_failed": sum(state == "fail" for state in final_features.values()),
        "final_unknown": sum(final_features.get(key, "unknown") == "unknown" for key in feature_ids),
        "ever_passed": sum(value is not None for value in activations.values()),
        "coverage_reason": "feature_inventory_not_supplied" if not feature_ids else "observed_inventory_only",
    }
    result["established_regression_area"] = {
        "definition": "established-regression-area/1",
        **_area(established_failures, established_unknown, established_denominator),
        "activation_checkpoints": activations,
    }
    return result


def claim_drift(claims) -> dict:
    """Score exactly four frozen registered assertions; additions stay unscored."""
    if not isinstance(claims, Mapping) or set(claims) != {"registered", "unregistered"}:
        raise ValueError("claims requires registered and unregistered lists")
    registered, unregistered = claims["registered"], claims["unregistered"]
    if not isinstance(registered, list) or len(registered) != 4:
        raise ValueError("exactly four registered claims are required")
    if not isinstance(unregistered, list) or any(not isinstance(item, str) or not item for item in unregistered):
        raise ValueError("unregistered must list nonempty addition IDs")
    if len(set(unregistered)) != len(unregistered):
        raise ValueError("duplicate unregistered claim IDs")
    seen = set()
    observations = []
    failures = unknown = 0
    for claim in registered:
        if not isinstance(claim, Mapping) or set(claim) != {"claim_id", "anchor_present", "present", "outcome"}:
            raise ValueError("invalid registered claim fields")
        claim_id = claim["claim_id"]
        if not isinstance(claim_id, str) or not claim_id or claim_id in seen or claim_id in unregistered:
            raise ValueError("claim IDs must be unique nonempty strings")
        seen.add(claim_id)
        anchor, present, outcome = claim["anchor_present"], claim["present"], claim["outcome"]
        if any(value is not None and type(value) is not bool for value in (anchor, present)) or outcome not in ("pass", "fail", "unknown"):
            raise ValueError("present/anchor_present must be boolean or null; outcome must be pass/fail/unknown")
        if present is False:
            state, reason = "fail", "deleted"
        elif anchor is False:
            state, reason = "fail", "missing_anchor"
        elif outcome == "fail":
            state, reason = "fail", "false_assertion"
        elif present is None or anchor is None or outcome == "unknown":
            state, reason = "unknown", "observation_unavailable"
        else:
            state, reason = "pass", "pass"
        failures += state == "fail"
        unknown += state == "unknown"
        observations.append({"claim_id": claim_id, "anchor_present": anchor, "present": present,
                             "state": state, "reason": reason})
    return {"definition": "claim-drift/1", **_area(failures, unknown, 4),
            "registered": observations, "unregistered_unscored": list(unregistered)}
