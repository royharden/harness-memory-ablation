"""Public result analysis. Construction checkpoint: runtime and P0 unverified."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, InvalidOperation
from typing import Any

from .statistics import task_cluster_comparison
from .comparisons import descriptive_comparisons
from .design import calculate_task_statistics
from .trajectories import summarize_trajectory, summarize_public_checkpoints
from .outcomes import resolve_cell_outcome


class ExportValidationError(ValueError):
    """An export cannot be safely interpreted."""


def _parse_export(payload: Any) -> dict:
    # The separate campaign producer owns closed DTOs and hash/reference checks.
    # Never fall back to a permissive local model when that contract is missing.
    try:
        from m11.campaign import PublicExport, parse_export
    except ImportError as exc:
        raise ExportValidationError("campaign_public_export_contract_unavailable") from exc
    try:
        # A canonical DTO from the CLI is explicitly supported, but revalidated
        # from serialized bytes/fields rather than trusting model_construct.
        material = payload.model_dump(mode="json") if isinstance(payload, PublicExport) else payload
        return parse_export(material).model_dump(mode="json")
    except (ValueError, TypeError) as exc:
        raise ExportValidationError("invalid_public_export") from exc


def _unique(records: list[dict], key: str) -> dict:
    result = {}
    for record in records:
        identifier = record.get(key)
        if not isinstance(identifier, str) or not identifier or identifier in result:
            raise ExportValidationError(f"invalid_or_duplicate_{key}")
        result[identifier] = record
    return result


def _money(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ExportValidationError("invalid_estimated_cost")
    try:
        amount = Decimal(str(value))
    except InvalidOperation as exc:
        raise ExportValidationError("invalid_estimated_cost") from exc
    if not amount.is_finite() or amount < 0:
        raise ExportValidationError("invalid_estimated_cost")
    return amount


def analyze_export(payload: Any) -> dict:
    """Analyze the canonical m11-export/1 DTO without grading or native activity.

    PublicExport is a provisional DL3 seam. Until producer eligibility metadata is
    reconciled, inferential output refuses unavailable admission/embargo evidence.
    Raw planned slots/attempts and explicit descriptive bounds remain visible.
    """
    export = _parse_export(payload)
    if export.get("schema_version") != "m11-export/1":
        raise ExportValidationError("unsupported_export_version")
    required = ("planned_cells", "attempts", "grades", "usage_observations", "model_evidence", "limitations", "cost_observations", "trajectory_checkpoints")
    if any(not isinstance(export.get(key), list) for key in required):
        raise ExportValidationError("missing_export_collection")
    mode = export["mode"]
    if mode not in ("SIMULATED", "MEASURED"):
        raise ExportValidationError("invalid_mode")
    cells = _unique(export["planned_cells"], "cell_id")
    attempts = _unique(export["attempts"], "attempt_id")
    grades = _unique(export["grades"], "attempt_id")
    _unique(export["cost_observations"], "cost_id")
    estimates = [cost for cost in export["cost_observations"] if cost["kind"] == "list_price_estimate"]
    tranche_receipts = [cost for cost in export["cost_observations"] if cost["kind"] == "tranche_receipt"]
    # Multiple competing per-attempt estimates require explicit source resolution,
    # never additive scope guessing. Tranche actual receipts are never allocated.
    costs = _unique(estimates, "attempt_id")
    usage = _unique(export["usage_observations"], "observation_id")
    models = _unique(export["model_evidence"], "model_evidence_id")
    by_cell: dict[str, list[dict]] = defaultdict(list)
    for attempt in attempts.values():
        if attempt.get("mode") != mode or attempt.get("cell_id") not in cells:
            raise ExportValidationError("mixed_mode_or_unresolved_cell")
        by_cell[attempt["cell_id"]].append(attempt)
        for key in ("parent_attempt_id", "retry_of"):
            reference = attempt.get(key)
            if reference is not None and reference not in attempts:
                raise ExportValidationError("unresolved_attempt_lineage")
        if any(ref not in usage for ref in attempt["usage_observation_ids"]) or any(ref not in models for ref in attempt["model_evidence_ids"]):
            raise ExportValidationError("unresolved_observation")
        if any(usage[ref]["attempt_id"] != attempt["attempt_id"] for ref in attempt["usage_observation_ids"]) or any(models[ref]["attempt_id"] != attempt["attempt_id"] for ref in attempt["model_evidence_ids"]):
            raise ExportValidationError("cross_attempt_evidence")
    for record in [*grades.values(), *costs.values(), *usage.values(), *models.values(), *export["limitations"]]:
        if record.get("attempt_id") not in attempts:
            raise ExportValidationError("unresolved_attempt_reference")
    for identifier, grade in grades.items():
        artifact = attempts[identifier].get("artifact_sha256")
        if artifact is None or artifact != grade["artifact_sha256"]:
            raise ExportValidationError("grade_artifact_mismatch")

    limitation_by_attempt: dict[str, set[str]] = defaultdict(set)
    for limitation in export["limitations"]:
        limitation_by_attempt[limitation["attempt_id"]].add(limitation["code"])

    outcomes = []
    for cell_id, cell in cells.items():
        identifier = cell.get("attempt_id")
        if identifier is not None and (identifier not in attempts or attempts[identifier]["cell_id"] != cell_id):
            raise ExportValidationError("invalid_planned_attempt_link")
        attempt = attempts.get(identifier)
        disposition = resolve_cell_outcome(cell, attempt, grades.get(identifier), limitation_by_attempt[identifier])
        outcomes.append({**cell, "declared_disposition": cell["disposition"], "disposition": disposition})

    group_rows: dict[tuple, list[dict]] = defaultdict(list)
    for row in outcomes:
        group_rows[(row["harness_id"], row["treatment_id"], row.get("task_class"))].append(row)
        if row.get("task_class") is not None:
            group_rows[(row["harness_id"], row["treatment_id"], None)].append(row)
    groups = []
    for (harness, arm, task_class), rows in sorted(group_rows.items(), key=lambda item: str(item[0])):
        members = [attempt for row in rows for attempt in by_cell[row["cell_id"]]]
        known = Decimal(0)
        unpriced_reported = Decimal(0)
        failure_cost = Decimal(0)
        unknown_costs = 0
        for attempt in members:
            cost = costs.get(attempt["attempt_id"])
            value = _money(cost.get("estimated_usd")) if cost else None
            if value is None or cost.get("coverage") != "complete" or not cost.get("pricetable_sha256") or attempt.get("usage_coverage") != "complete":
                unknown_costs += 1
            if value is not None and cost.get("pricetable_sha256"):
                known += value
                if any(row["cell_id"] == attempt["cell_id"] and row["disposition"] == "fail" for row in rows):
                    failure_cost += value
            elif value is not None:
                unpriced_reported += value
        counts = {name: sum(row["disposition"] == name for row in rows) for name in ("pass", "fail", "evaluator_error", "infra_excluded", "unknown", "unstarted")}
        missing = counts["evaluator_error"] + counts["infra_excluded"] + counts["unknown"] + counts["unstarted"]
        solved_tasks = {row["task_id"] for row in rows if row["disposition"] == "pass"}
        economic_reason = "unknown_cost" if unknown_costs else "incomplete_population" if missing else "undefined_zero_pass" if not counts["pass"] else None
        groups.append({
            "harness_id": harness, "treatment_id": arm, "task_class": task_class,
            "planned": len(rows), "started": sum(a.get("started_at") is not None for a in members),
            "started_slots": sum(any(a.get("started_at") is not None for a in by_cell[row["cell_id"]]) for row in rows),
            "processes_completed": sum(a.get("ended_at") is not None and a.get("process_state") == "exited" for a in members),
            "attempts": len(members), "counts": counts, "judged_coverage": (counts["pass"] + counts["fail"]) / len(rows),
            "distinct_tasks_solved": len(solved_tasks), "solved_task_ids": sorted(solved_tasks),
            "success_over_planned": counts["pass"] / len(rows),
            "missingness_bounds": [counts["pass"] / len(rows), (counts["pass"] + missing) / len(rows)],
            "known_estimated_subtotal_usd": str(known), "unknown_cost_attempts": unknown_costs,
            "unpriced_reported_subtotal_usd": str(unpriced_reported),
            "known_failure_estimated_subtotal_usd": str(failure_cost),
            "usage_cost_coverage": (len(members) - unknown_costs) / len(members) if members else None,
            "cost_per_pass_usd": None if economic_reason else str(known / counts["pass"]),
            "cost_per_distinct_task_usd": None if economic_reason else str(known / len(solved_tasks)),
            "cost_per_pass_reason": economic_reason, "price_label": "estimated at dated list prices",
        })
    missing = sum(row["disposition"] not in ("pass", "fail") for row in outcomes)
    # Comparison-arm uncertainty suppresses both economic arms, including class
    # companions; never leave a complete-case cost headline on the other side.
    for group in groups:
        peers = [other for other in groups if other["harness_id"] == group["harness_id"] and other["task_class"] == group["task_class"]]
        if any(other["unknown_cost_attempts"] for other in peers):
            group["cost_per_pass_usd"] = None
            group["cost_per_distinct_task_usd"] = None
            group["cost_per_pass_reason"] = "comparison_arm_unknown_cost"
    eligibility = export["eligibility"]
    # Canonical r1 intentionally has no verified released-MEASURED state. Never
    # invent eligibility from caller booleans, receipt hashes or the source ruling.
    if eligibility["inferential_eligible"] is not False or eligibility["public_release_eligible"] is not False:
        raise ExportValidationError("unavailable_independent_release_verification")
    reasons = ["simulated_no_inference"] if mode == "SIMULATED" else [eligibility["unavailable_reason"]]
    return {
        "schema_version": "m11-analysis/1", "campaign_id": export["campaign_id"], "mode": mode,
        "experiment_kind": export["experiment_kind"], "construction_status": "runtime-unverified",
        "status": "INCOMPLETE" if missing else "DESCRIPTIVE_ONLY",
        "unavailable_reasons": reasons, "planned_cells": outcomes, "attempts": export["attempts"],
        "groups": groups, "comparisons": descriptive_comparisons(outcomes),
        "trajectories": summarize_public_checkpoints(export["trajectory_checkpoints"]),
        "eligibility": eligibility, "billing_reconciliation": tranche_receipts,
        "limitations": export["limitations"], "provenance": export,
        "inferential_claim": None, "independent_worksheets": "PENDING",
    }


__all__ = ["analyze_export", "ExportValidationError", "task_cluster_comparison", "calculate_task_statistics", "summarize_trajectory"]
