"""Narrow accepted registration/suite/cell/attempt to private grade-plan bridge.

Only hash-bound caller-verified canonical JSON is accepted. No m11/harnessrun
imports, candidate execution, eligibility grant or public result release.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .admission import GateContext
from .formats import Refusal, closed, digest, parse_json, sha256
from .grade import (GradeRequest, GradingAuthority, bind_external_grade,
                    grade_plan_sha256, prepare_grade)
from .wire import identifier


@dataclass(frozen=True)
class FrozenJoinAuthority:
    """Actual caller's frozen pins and canonical-model verifier; no default pass."""
    suite_sha256: str
    registration_sha256: str
    verify_graph: Callable[[bytes, bytes, bytes, bytes], bool] | None = None


def _canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _record(raw: bytes, version: str) -> dict[str, Any]:
    value = parse_json(raw)
    if not isinstance(value, dict) or value.get("schema_version") != version:
        raise Refusal("unsupported canonical join record version")
    if _canonical(value) != raw:
        raise Refusal("join input must be exact accepted canonical model bytes")
    return value


def _sequence(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise Refusal(f"{label}: expected serialized model array")
    return value


def _one(items: list[dict[str, Any]], field: str, value: Any) -> dict[str, Any]:
    selected = [item for item in items if item.get(field) == value]
    if len(selected) != 1:
        raise Refusal("execution item missing or ambiguous")
    return selected[0]


def prepare_registered_grade(*, suite_raw: bytes, registration_raw: bytes,
                             cell_raw: bytes, attempt_raw: bytes,
                             frozen: FrozenJoinAuthority, grader_sha256: str,
                             authority: GradingAuthority,
                             p0_raw: bytes | None = None, p0_root: Path | None = None,
                             p0_context: GateContext | None = None,
                             full_raw: bytes | None = None, full_root: Path | None = None,
                             full_context: GateContext | None = None) -> dict[str, Any]:
    """Join exact accepted source fields, then invoke the existing gated planner.

    The caller verifier must validate the complete canonical records AND frozen
    schedule/attempt relationships using accepted producer types. This function
    only checks the narrow grading join; it never duplicates the whole producer.
    """
    if frozen.verify_graph is None:
        raise Refusal("trusted frozen canonical-model/schedule verifier unavailable")
    if frozen.verify_graph(suite_raw, registration_raw, cell_raw, attempt_raw) is not True:
        raise Refusal("canonical record graph not verified by caller")
    suite = _record(suite_raw, "m11-suite/1")
    registration = _record(registration_raw, "m11-registration/1")
    cell = _record(cell_raw, "m11-cell/1")
    attempt = _record(attempt_raw, "harnessrun/1")
    if attempt.get("record_type") != "AttemptRecord":
        raise Refusal("join requires actual AttemptRecord")
    suite_hash = digest(frozen.suite_sha256, "frozen suite hash")
    registration_hash = digest(frozen.registration_sha256, "frozen registration hash")
    if sha256(suite_raw) != suite_hash or sha256(registration_raw) != registration_hash:
        raise Refusal("join input differs from frozen registration/suite bytes")
    if registration.get("suite_sha256") != suite_hash:
        raise Refusal("registration suite binding differs")
    campaign_id = identifier(registration.get("campaign_id"), "campaign ID")
    registration_id = identifier(registration.get("registration_id"), "registration ID")
    cell_id = identifier(cell.get("cell_id"), "cell ID")
    task_id = identifier(cell.get("task_id"), "execution task ID")
    attempt_id = identifier(attempt.get("attempt_id"), "attempt ID")
    if (cell.get("campaign_id"), cell.get("registration_id")) != (campaign_id, registration_id):
        raise Refusal("cell campaign/registration differs")
    if (attempt.get("campaign_id"), attempt.get("cell_id"), cell.get("attempt_id")) != (campaign_id, cell_id, attempt_id):
        raise Refusal("attempt does not resolve exact planned cell")
    if attempt.get("mode") != registration.get("mode"):
        raise Refusal("attempt registration mode differs")
    if attempt.get("status") not in {"finished", "timeout", "spend_cap", "output_cap", "crash"} or attempt.get("process_state") != "exited":
        raise Refusal("no retained exited candidate ready for trusted grading")
    artifact_hash = digest(attempt.get("artifact_sha256"), "retained candidate hash")
    seed_id = cell.get("seed_id")
    checkpoint = cell.get("checkpoint")
    if seed_id is None:
        if checkpoint is not None:
            raise Refusal("checkpoint without seed")
        item = _one(_sequence(suite.get("tasks"), "suite tasks"), "task_id", task_id)
        if cell.get("task_class") != item.get("task_class"):
            raise Refusal("task class mapping differs")
        split = item.get("split")
    else:
        identifier(seed_id, "seed ID")
        if type(checkpoint) is not int or not 1 <= checkpoint <= 12:
            raise Refusal("invalid seed checkpoint")
        seed = _one(_sequence(suite.get("seeds"), "suite seeds"), "seed_id", seed_id)
        item = _one(_sequence(seed.get("checkpoints"), "seed checkpoints"), "checkpoint", checkpoint)
        if item.get("task_id") != task_id or cell.get("task_class") is not None:
            raise Refusal("seed checkpoint execution item differs")
        split = seed.get("split")
    if split not in {"dev", "heldout", "diagnostic"}:
        raise Refusal("unsupported grading split; no implicit probe/smoke compatibility")
    opaque_id = identifier(item.get("opaque_task_id"), "admitted opaque grading ID")
    task_hash = digest(item.get("task_sha256"), "execution task hash")
    if (cell.get("opaque_task_id"), cell.get("task_sha256")) != (opaque_id, task_hash):
        raise Refusal("planned cell suite item/hash/opaque mapping differs")
    binding = {
        "schema_version": "m11-registered-grade-binding/1",
        "campaign_id": campaign_id, "registration_id": registration_id,
        "registration_sha256": registration_hash, "suite_id": identifier(suite.get("suite_id"), "suite ID"),
        "suite_sha256": suite_hash, "cell_id": cell_id, "cell_sha256": sha256(cell_raw),
        "task_id": task_id, "task_sha256": task_hash, "seed_id": seed_id,
        "checkpoint": checkpoint, "attempt_id": attempt_id,
        "attempt_sha256": sha256(attempt_raw), "artifact_sha256": artifact_hash,
        "opaque_task_id": opaque_id, "grader_sha256": digest(grader_sha256, "grader hash"),
        "mode": registration["mode"], "split": split,
    }
    binding_hash = sha256(_canonical(binding))
    request = GradeRequest(
        attempt_id=attempt_id, artifact_sha256=artifact_hash, opaque_task_id=opaque_id,
        grader_sha256=grader_sha256, suite_sha256=suite_hash, split=split,
        registration_binding_sha256=binding_hash,
    )
    plan = prepare_grade(request, authority=authority, p0_raw=p0_raw, p0_root=p0_root,
                         p0_context=p0_context, full_raw=full_raw, full_root=full_root,
                         full_context=full_context)
    return {
        "schema_version": "m11-registered-grade-plan/1", "binding": binding,
        "binding_sha256": binding_hash, "grade_plan": plan,
        "grade_plan_sha256": grade_plan_sha256(plan),
    }


def _binding(value: Any) -> dict[str, Any]:
    result = closed(value, {
        "schema_version", "campaign_id", "registration_id", "registration_sha256",
        "suite_id", "suite_sha256", "cell_id", "cell_sha256", "task_id", "task_sha256",
        "seed_id", "checkpoint", "attempt_id", "attempt_sha256", "artifact_sha256",
        "opaque_task_id", "grader_sha256", "mode", "split",
    }, "registered grading binding")
    if result["schema_version"] != "m11-registered-grade-binding/1":
        raise Refusal("unsupported registered grading binding")
    for field in ("campaign_id", "registration_id", "suite_id", "cell_id",
                  "task_id", "attempt_id", "opaque_task_id"):
        identifier(result[field], field)
    for field in ("registration_sha256", "suite_sha256", "cell_sha256", "task_sha256",
                  "attempt_sha256", "artifact_sha256", "grader_sha256"):
        digest(result[field], field)
    if result["mode"] not in {"SIMULATED", "MEASURED"} or result["split"] not in {"dev", "heldout", "diagnostic"}:
        raise Refusal("registered grading provenance/split differs")
    if result["seed_id"] is None:
        if result["checkpoint"] is not None:
            raise Refusal("checkpoint without seed")
    else:
        identifier(result["seed_id"], "seed ID")
        if type(result["checkpoint"]) is not int or not 1 <= result["checkpoint"] <= 12:
            raise Refusal("invalid seed checkpoint")
    return result

def bind_registered_grade(joined: dict[str, Any], observation: dict[str, Any], *,
                          receipt_root: Path | None = None,
                          receipt_path: str | None = None,
                          verify_receipt: Callable[[bytes], bool] | None = None) -> dict[str, Any]:
    """Return GradeResult only; no PublicExport/eligibility/claim observation emitted."""
    closed(joined, {"schema_version", "binding", "binding_sha256", "grade_plan",
                    "grade_plan_sha256"}, "registered grade plan")
    if joined["schema_version"] != "m11-registered-grade-plan/1":
        raise Refusal("unsupported registered grade plan")
    binding = _binding(joined["binding"])
    binding_hash = digest(joined["binding_sha256"], "registered binding hash")
    plan = joined["grade_plan"]
    if sha256(_canonical(binding)) != binding_hash or not isinstance(plan, dict):
        raise Refusal("registered grading binding bytes differ")
    if plan.get("registration_binding_sha256") != binding_hash:
        raise Refusal("grade plan belongs to another registration join")
    for field in ("attempt_id", "artifact_sha256", "opaque_task_id", "grader_sha256", "suite_sha256"):
        if binding.get(field) != plan.get(field):
            raise Refusal("registered binding and grade plan differ")
    if grade_plan_sha256(plan) != digest(joined["grade_plan_sha256"], "grade plan hash"):
        raise Refusal("registered grade plan digest differs")
    return bind_external_grade(plan, observation, receipt_root=receipt_root,
                               receipt_path=receipt_path, verify_receipt=verify_receipt)
