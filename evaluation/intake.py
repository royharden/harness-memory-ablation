"""Sealed visible intake planning; no file copying, hidden export or code execution."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .admission import GateContext, assess_gate
from .formats import Refusal, closed, digest, parse_json, sha256, text
from .inventory import inspect_inventory, public_inventory

FORBIDDEN_VISIBLE_PARTS = {"hidden", "oracle", "wrong", "reference", "references"}


def prepare_visible_intake(manifest_raw: bytes, receipt_raw: bytes, *,
                           root: Path, context: GateContext) -> dict[str, Any]:
    expected = digest(context.expected_pack_sha256, "pinned pack")
    if sha256(manifest_raw) != expected:
        raise Refusal("sealed manifest differs from pinned pack")
    manifest = closed(parse_json(manifest_raw),
                      {"schema_version", "pack_id", "artifacts"}, "sealed manifest")
    if manifest["schema_version"] != "m11-sealed-pack/1":
        raise Refusal("unsupported sealed pack")
    assessment = assess_gate(receipt_raw, root=root, context=context)
    if assessment.decision != "PASS":
        raise Refusal("independent gate not passed: " + "; ".join(assessment.reasons))
    receipt = parse_json(receipt_raw)
    if manifest["pack_id"] != receipt["pack_id"]:
        raise Refusal("receipt and sealed pack ID differ")
    inspect_inventory(root, manifest["artifacts"])
    visible = public_inventory(manifest["artifacts"])
    if not visible:
        raise Refusal("no execution-visible artifacts")
    for entry in visible:
        if any(part.casefold() in FORBIDDEN_VISIBLE_PARTS
               for part in entry["path"].split("/")):
            raise Refusal("trusted artifact cannot enter visible intake")
    return {
        "schema_version": "m11-visible-intake-plan/1",
        "pack_id": text(manifest["pack_id"], "pack ID"),
        "pack_sha256": expected, "gate_kind": assessment.gate_kind,
        "gate_id": assessment.gate_id, "receipt_sha256": assessment.receipt_sha256,
        "visible_artifacts": visible, "disposition": "PLAN_ONLY_NOT_MATERIALIZED",
    }
