"""Trusted grader boundary. Plans and binds observations, never imports candidates."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .admission import GateContext, assess_gate
from .formats import Refusal, closed, digest, parse_json, read_bound, sha256, text
from .wire import identifier, wire_text


@dataclass(frozen=True)
class GradeRequest:
    attempt_id: str
    artifact_sha256: str
    opaque_task_id: str
    grader_sha256: str
    suite_sha256: str
    split: str
    registration_binding_sha256: str


@dataclass(frozen=True)
class GradingAuthority:
    """Externally verified isolation/authorization, not fields from candidate input."""
    runtime_authorized: bool = False
    approved_image_sha256: str | None = None
    isolation_evidence_sha256: str | None = None
    frozen_mapping: tuple[tuple[str, str, str], ...] = ()
    # mapping row: opaque grading ID, suite hash, trusted grader hash


def prepare_grade(request: GradeRequest, *, authority: GradingAuthority,
                  p0_raw: bytes | None, p0_root: Path | None,
                  p0_context: GateContext | None,
                  full_raw: bytes | None = None, full_root: Path | None = None,
                  full_context: GateContext | None = None) -> dict[str, Any]:
    """Return data for a future approved offline grader, never execute/import it."""
    for field in ("attempt_id", "opaque_task_id"):
        identifier(getattr(request, field), field)
    for field in ("artifact_sha256", "grader_sha256", "suite_sha256", "registration_binding_sha256"):
        digest(getattr(request, field), field)
    if request.split not in {"dev", "heldout", "diagnostic"}:
        raise Refusal("grading split not admitted")
    p0 = assess_gate(p0_raw, root=p0_root, context=p0_context)
    if p0.decision != "PASS" or p0.gate_kind != "P0":
        raise Refusal("independent P0 unavailable")
    if request.split in {"heldout", "diagnostic"}:
        full = assess_gate(full_raw, root=full_root, context=full_context)
        if full.decision != "PASS" or full.gate_kind != "full_pack":
            raise Refusal("independent full-pack admission unavailable")
    if authority.runtime_authorized is not True:
        raise Refusal("runtime remains unauthorized")
    image = digest(authority.approved_image_sha256, "offline image")
    isolation = digest(authority.isolation_evidence_sha256, "isolation evidence")
    mapping = (request.opaque_task_id, request.suite_sha256, request.grader_sha256)
    if authority.frozen_mapping.count(mapping) != 1:
        raise Refusal("opaque grading ID/suite/grader mapping unresolved")
    if len({row[0] for row in authority.frozen_mapping}) != len(authority.frozen_mapping):
        raise Refusal("ambiguous frozen grading mapping")
    return {
        "schema_version": "m11-grade-plan/2",
        "registration_binding_sha256": request.registration_binding_sha256,
        "attempt_id": request.attempt_id, "artifact_sha256": request.artifact_sha256,
        "opaque_task_id": request.opaque_task_id, "grader_sha256": request.grader_sha256,
        "suite_sha256": request.suite_sha256, "offline_image_sha256": image,
        "isolation_evidence_sha256": isolation,
        "network": "disabled", "candidate_mount": "immutable_read_only",
        "hidden_grader_mount": "grader_only", "disposition": "PLAN_ONLY_NOT_EXECUTED",
    }


def grade_plan_sha256(plan: dict[str, Any]) -> str:
    """m11-grade-plan/2 digest over UTF-8 canonical JSON, without a self-hash field."""
    return sha256(json.dumps(plan, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8"))

def bind_external_grade(plan: dict[str, Any], observation: dict[str, Any], *,
                        receipt_root: Path | None = None,
                        receipt_path: str | None = None,
                        verify_receipt: Callable[[bytes], bool] | None = None) -> dict[str, Any]:
    """Bind only verified external offline execution evidence; never infer a grade.

    A trusted operator supplies the verifier for the approved external runner's
    signing/attestation mechanism. No default verifier or local success flag exists.
    """
    closed(plan, {"schema_version", "attempt_id", "artifact_sha256", "opaque_task_id",
                  "grader_sha256", "suite_sha256", "offline_image_sha256",
                  "isolation_evidence_sha256", "network", "candidate_mount",
                  "hidden_grader_mount", "disposition", "registration_binding_sha256"}, "grade plan")
    if plan["schema_version"] != "m11-grade-plan/2":
        raise Refusal("unknown grade plan")
    for field in ("attempt_id", "opaque_task_id"):
        identifier(plan[field], field)
    for field in ("artifact_sha256", "grader_sha256", "suite_sha256",
                  "offline_image_sha256", "isolation_evidence_sha256", "registration_binding_sha256"):
        digest(plan[field], field)
    fixed = {"network": "disabled", "candidate_mount": "immutable_read_only",
             "hidden_grader_mount": "grader_only", "disposition": "PLAN_ONLY_NOT_EXECUTED"}
    if any(plan[field] != value for field, value in fixed.items()):
        raise Refusal("offline grade plan isolation/disposition differs")
    fields = {"attempt_id", "artifact_sha256", "opaque_task_id", "grader_sha256",
              "verdict", "receipt_ref", "receipt_sha256"}
    closed(observation, fields, "external grade")
    if not callable(verify_receipt) or receipt_root is None or receipt_path is None:
        raise Refusal("external grading receipt verifier unavailable")
    for field in ("attempt_id", "artifact_sha256", "opaque_task_id", "grader_sha256"):
        if observation[field] != plan[field]:
            raise Refusal("external grading observation binding differs")
    if observation["verdict"] not in {"pass", "fail", "evaluator_error"}:
        raise Refusal("unknown grader verdict")
    wire_text(observation["receipt_ref"], "grading receipt")
    raw = read_bound(receipt_root, receipt_path,
                     digest(observation["receipt_sha256"], "grading receipt hash"))
    if verify_receipt(raw) is not True:
        raise Refusal("external execution attestation not verified")
    receipt = closed(parse_json(raw), {
        "schema_version", "attempt_id", "artifact_sha256", "opaque_task_id",
        "grader_sha256", "verdict", "offline_image_sha256",
        "isolation_evidence_sha256", "execution_id", "suite_sha256", "grade_plan_sha256",
    }, "external execution receipt")
    if receipt["schema_version"] != "m11-grader-execution/1":
        raise Refusal("unknown execution evidence")
    text(receipt["execution_id"], "execution ID")
    if receipt["grade_plan_sha256"] != grade_plan_sha256(plan):
        raise Refusal("external receipt grade-plan digest differs")
    if receipt["suite_sha256"] != plan["suite_sha256"]:
        raise Refusal("external receipt suite differs")
    for field in ("attempt_id", "artifact_sha256", "opaque_task_id",
                  "grader_sha256", "verdict"):
        if receipt[field] != observation[field]:
            raise Refusal("receipt and observation differ")
    for field in ("offline_image_sha256", "isolation_evidence_sha256"):
        if receipt[field] != plan[field]:
            raise Refusal("execution isolation/image differs")
    return {"schema_version": "harnessrun/1", "record_type": "GradeResult", **observation}