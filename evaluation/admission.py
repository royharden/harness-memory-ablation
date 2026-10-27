"""Independent gate intake. No signer, custodian or expected answer is invented."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .formats import Refusal, closed, digest, parse_json, read_bound, sha256, strings, text

PLAN_SHA256 = "0126184f9d0ddd2de1f0fe4c9e7fb5c170d5676004c0a023bf8fe63d53c8e99c"
CLASSES = {"memory-independent", "decision-dependent", "misleading-memory"}
FIELDS = {
    "schema_version", "gate_kind", "gate_id", "pack_id", "pack_sha256",
    "plan_sha256", "author_session", "author_lineage", "custodian_ref",
    "human_reviewer_ref", "reviewed_at", "rights_verdict", "semantic_verdict",
    "expected_answers_ref", "attestation_ref", "adversarial_session",
    "adversarial_lineage", "items", "checks", "source_hashes", "seal_ref",
    "exposure_state", "custodian_signature_ref", "human_signature_ref",
    "execution", "adversarial_coverage", "run_ids",
}
COMMON_CHECKS = {"rights_semantic", "family_disjoint", "isolation",
                 "stability"}
REQUIRED_CHECKS = {
    "task": COMMON_CHECKS | {"oracle", "untouched", "wrong_1", "wrong_2",
                              "wrong_3", "null_zero", "leakage"},
    "diagnostic": COMMON_CHECKS | {"oracle", "untouched", "null_zero", "leakage"},
    "seed": COMMON_CHECKS | {"baseline", "tripwire_1", "tripwire_2", "tripwire_3",
                              "tripwire_4", "claim_1", "claim_2", "claim_3", "claim_4"},
    "reference": COMMON_CHECKS | {"accrued_features", "tripwire_1", "tripwire_2",
                                   "tripwire_3", "tripwire_4", "claims"},
}


@dataclass(frozen=True)
class GateContext:
    """Trusted operator configuration, never copied from the incoming receipt.

    Signature verifier must verify role, finalized receipt hash and reference using
    actual externally appointed signing authority. There is no permissive default.
    """
    custodian_session: str
    custodian_ref: str
    human_reviewer_ref: str
    builder_sessions: frozenset[str]
    expected_pack_sha256: str
    heldout_task_count: int = 36
    growth_authorization_ref: str | None = None
    verify_signature: Callable[[str, str, str], bool] | None = None
    operator_session: str | None = None
    kit_sha256: str | None = None
    config_sha256: str | None = None
    image_sha256: str | None = None
    python_version: str | None = None


@dataclass(frozen=True)
class GateAssessment:
    gate_kind: str
    gate_id: str | None
    decision: str
    reasons: tuple[str, ...]
    receipt_sha256: str | None
    pack_sha256: str | None
    checked_items: int = 0


def _items(receipt: dict[str, Any], task_count: int) -> dict[str, dict[str, Any]]:
    if not isinstance(receipt["items"], list):
        raise Refusal("items must be a list")
    items: dict[str, dict[str, Any]] = {}
    class_counts: Counter[str] = Counter()
    kinds: Counter[str] = Counter()
    families: set[str] = set()
    diagnostics: Counter[str] = Counter()
    checkpoints: set[tuple[str, int]] = set()
    for item in receipt["items"]:
        closed(item, {"id", "kind", "task_class", "parent_seed_id", "checkpoint",
                      "family_id", "diagnostic_kind", "human_detailed", "wrong_patch_ids",
                      "grader_sha256"}, "item")
        item_id = text(item["id"], "item ID")
        kind = item["kind"]
        if item_id in items or kind not in REQUIRED_CHECKS:
            raise Refusal("duplicate item or unknown kind")
        if kind == "task":
            if item["task_class"] not in CLASSES:
                raise Refusal("task class missing")
            class_counts[item["task_class"]] += 1
        elif item["task_class"] is not None:
            raise Refusal("non-study item has a primary class")
        if kind != "reference" and item["parent_seed_id"] is not None:
            raise Refusal("only reference items have parent seed")
        wrong_ids = strings(item["wrong_patch_ids"], "wrong patch IDs", empty=True)
        if kind == "task" and set(wrong_ids) != {"wrong_1", "wrong_2", "wrong_3"}:
            raise Refusal("study task requires three declared wrong patches")
        if kind not in {"task", "diagnostic"} and wrong_ids:
            raise Refusal("unexpected wrong patch inventory")
        if any(not name.startswith("wrong_") for name in wrong_ids):
            raise Refusal("wrong patch control name differs")
        digest(item["grader_sha256"], "item grader hash")
        family = text(item["family_id"], "family ID")
        if type(item["human_detailed"]) is not bool:
            raise Refusal("human detailed-review flag must be boolean")
        if kind != "reference":
            if family in families:
                raise Refusal("family duplicated within pack")
            families.add(family)
            if item["checkpoint"] is not None:
                raise Refusal("only references have checkpoint ordinals")
        else:
            ordinal = item["checkpoint"]
            if type(ordinal) is not int or not 1 <= ordinal <= (2 if receipt["gate_kind"] == "P0" else 12):
                raise Refusal("invalid reference checkpoint")
            key = (text(item["parent_seed_id"], "reference parent"), ordinal)
            if key in checkpoints:
                raise Refusal("duplicate seed checkpoint")
            checkpoints.add(key)
        if kind == "diagnostic":
            if item["diagnostic_kind"] not in {"ceiling", "floor"}:
                raise Refusal("diagnostic kind missing")
            diagnostics[item["diagnostic_kind"]] += 1
        elif item["diagnostic_kind"] is not None:
            raise Refusal("unexpected diagnostic kind")
        items[item_id] = item
        kinds[kind] += 1
    sample = receipt["gate_kind"] == "P0"
    required = {"task": 3 if sample else task_count, "diagnostic": 0 if sample else 4,
                "seed": 1 if sample else 4, "reference": 2 if sample else 48}
    if any(kinds[kind] != count for kind, count in required.items()):
        raise Refusal("gate inventory counts differ")
    if set(class_counts) != CLASSES or len(set(class_counts.values())) != 1:
        raise Refusal("unbalanced primary classes")
    if not sample and (diagnostics["ceiling"] != 2 or diagnostics["floor"] != 2):
        raise Refusal("diagnostic population differs")
    if sample and not all(item["human_detailed"] for item in items.values()):
        raise Refusal("every P0 item needs detailed human review")
    if not sample:
        audited = sum(item["kind"] == "task" and item["human_detailed"] for item in items.values())
        if audited < 6 or any(item["kind"] == "seed" and not item["human_detailed"] for item in items.values()):
            raise Refusal("full-pack human audit coverage insufficient")
    references: Counter[str] = Counter()
    for item in items.values():
        if item["kind"] == "reference":
            parent = text(item["parent_seed_id"], "reference parent")
            if parent not in items or items[parent]["kind"] != "seed":
                raise Refusal("reference parent not an admitted seed")
            if item["family_id"] != items[parent]["family_id"]:
                raise Refusal("reference family differs from seed")
            references[parent] += 1
    for item_id, item in items.items():
        if item["kind"] == "seed" and references[item_id] != (2 if sample else 12):
            raise Refusal("seed reference inventory differs")
    return items


def _verify_checks(receipt: dict[str, Any], items: dict[str, dict[str, Any]],
                   root: Path) -> None:
    if not isinstance(receipt["checks"], list):
        raise Refusal("checks must be a list")
    run_ids = strings(receipt["run_ids"], "operator rerun IDs")
    if len(run_ids) != 3:
        raise Refusal("exactly three distinct keyless reruns required")
    expected = {(item_id, check, run_id) for item_id, item in items.items()
                for check in (REQUIRED_CHECKS[item["kind"]] | set(item["wrong_patch_ids"]))
                for run_id in run_ids}
    seen: set[tuple[str, str, str]] = set()
    for check in receipt["checks"]:
        closed(check, {"item_id", "check", "outcome", "run_id",
                       "evidence_path", "evidence_sha256"}, "check")
        key = (text(check["item_id"], "check item"),
               text(check["check"], "check name"), text(check["run_id"], "check run"))
        if key not in expected or key in seen:
            raise Refusal("unexpected or duplicate item/control/rerun")
        if check["outcome"] != "pass":
            raise Refusal("required control did not pass")
        read_bound(root, text(check["evidence_path"], "check evidence"),
                   digest(check["evidence_sha256"], "check evidence hash"))
        seen.add(key)
    if seen != expected:
        raise Refusal("required per-item per-rerun control evidence missing")

def _verify_execution(receipt: dict[str, Any], context: GateContext, root: Path,
                      items: dict[str, dict[str, Any]]) -> None:
    execution = closed(receipt["execution"], {
        "operator_session", "kit_sha256", "config_sha256", "image_sha256",
        "python_version", "evidence_path", "evidence_sha256",
    }, "operator execution")
    if execution["operator_session"] != text(context.operator_session, "appointed operator"):
        raise Refusal("operator session differs")
    for name in ("kit_sha256", "config_sha256", "image_sha256"):
        if digest(execution[name], name) != digest(getattr(context, name), "pinned " + name):
            raise Refusal("operator execution pins differ")
    version = text(execution["python_version"], "Python version")
    if version != text(context.python_version, "pinned Python patch version"):
        raise Refusal("operator Python patch version differs")
    pieces = version.split(".")
    if len(pieces) != 3 or pieces[:2] != ["3", "12"] or not pieces[2].isdigit():
        raise Refusal("approved Python3.12 patch version required")
    read_bound(root, text(execution["evidence_path"], "operator evidence"),
               digest(execution["evidence_sha256"], "operator evidence hash"))
    coverage = receipt["adversarial_coverage"]
    if not isinstance(coverage, list):
        raise Refusal("adversarial grader coverage absent")
    required = {item["grader_sha256"] for item in items.values()}
    seen: set[str] = set()
    for record in coverage:
        closed(record, {"grader_sha256", "evidence_path", "evidence_sha256"},
               "adversarial grader record")
        grader = digest(record["grader_sha256"], "adversarial grader hash")
        if grader in seen or grader not in required:
            raise Refusal("unexpected or duplicate adversarial grader")
        read_bound(root, text(record["evidence_path"], "adversarial evidence"),
                   digest(record["evidence_sha256"], "adversarial evidence hash"))
        seen.add(grader)
    if seen != required:
        raise Refusal("not every trusted grader has adversarial evidence")

def assess_gate(raw: bytes | None, *, root: Path | None = None,
                context: GateContext | None = None) -> GateAssessment:
    """Inspect finalized external evidence; absence of context always refuses PASS.

    None means the gate has not been attempted. Supplied invalid/incomplete bytes
    mean an attempted admission NO-GO. No artifact content is returned publicly.
    """
    if raw is None:
        return GateAssessment("unknown", None, "PENDING", ("gate_not_attempted",), None, None)
    receipt_hash = sha256(raw)
    gate_kind = "unknown"
    gate_id = None
    pack_hash = None
    try:
        receipt = closed(parse_json(raw), FIELDS, "admission receipt")
        if receipt["schema_version"] != "m11-admission/1":
            raise Refusal("unsupported admission schema")
        gate_kind = receipt["gate_kind"]
        if gate_kind not in {"P0", "full_pack"}:
            raise Refusal("unknown gate kind")
        gate_id = text(receipt["gate_id"], "gate ID")
        text(receipt["pack_id"], "pack ID")
        pack_hash = digest(receipt["pack_sha256"], "pack hash")
        if receipt["plan_sha256"] != PLAN_SHA256:
            raise Refusal("controlling plan differs")
        if context is None or root is None:
            raise Refusal("independent appointment/signature context unavailable")
        if context.verify_signature is None or not context.builder_sessions:
            raise Refusal("trusted verifier or builder lineage registry unavailable")
        if context.heldout_task_count not in {36, 48}:
            raise Refusal("invalid held-out design count")
        if context.heldout_task_count == 48 and not context.growth_authorization_ref:
            raise Refusal("prospective growth authorization absent")
        if pack_hash != digest(context.expected_pack_sha256, "expected pack hash"):
            raise Refusal("pack differs from operator-pinned scope")
        author = text(receipt["author_session"], "author session")
        author_lineage = set(strings(receipt["author_lineage"], "author lineage"))
        adversarial = text(receipt["adversarial_session"], "adversarial session")
        adversarial_lineage = set(strings(receipt["adversarial_lineage"], "adversarial lineage"))
        if author != context.custodian_session or author not in author_lineage:
            raise Refusal("custodian session/lineage differs")
        if adversarial not in adversarial_lineage or author_lineage & adversarial_lineage:
            raise Refusal("separate adversarial session required")
        if (author_lineage | adversarial_lineage) & context.builder_sessions:
            raise Refusal("builder lineage cannot establish independent admission")
        if receipt["custodian_ref"] != text(context.custodian_ref, "appointed custodian"):
            raise Refusal("custodian appointment differs")
        if receipt["human_reviewer_ref"] != text(context.human_reviewer_ref, "appointed human"):
            raise Refusal("human reviewer appointment differs")
        for field in ("reviewed_at", "expected_answers_ref", "attestation_ref", "seal_ref"):
            text(receipt[field], field)
        if receipt["rights_verdict"] != "pass" or receipt["semantic_verdict"] != "pass":
            raise Refusal("rights/semantic verdict absent or refused")
        if receipt["exposure_state"] != "unexposed":
            raise Refusal("exposure invalidates confirmation")
        for role, field in (("custodian", "custodian_signature_ref"),
                            ("human", "human_signature_ref")):
            if context.verify_signature(role, receipt_hash, text(receipt[field], field)) is not True:
                raise Refusal("signature/appointment evidence not verified")
        if not isinstance(receipt["source_hashes"], dict) or not receipt["source_hashes"]:
            raise Refusal("source hashes absent")
        for path, expected_hash in receipt["source_hashes"].items():
            read_bound(root, text(path, "source path"), digest(expected_hash, "source hash"))
        items = _items(receipt, context.heldout_task_count)
        _verify_checks(receipt, items, root)
        _verify_execution(receipt, context, root, items)
        return GateAssessment(gate_kind, gate_id, "PASS", (), receipt_hash, pack_hash, len(items))
    except (Refusal, OSError, TypeError, ValueError, KeyError) as exc:
        return GateAssessment(gate_kind, gate_id, "NO-GO", (str(exc),), receipt_hash, pack_hash)
