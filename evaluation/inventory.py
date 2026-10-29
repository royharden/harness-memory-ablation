"""Custody-safe inventory checks; inspection is not admission or originality proof."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .formats import Refusal, closed, digest, read_bound, text

ARTIFACT_FIELDS = {"path", "sha256", "visibility"}


def inspect_inventory(root: Path, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    """Hash only caller-enumerated artifacts; never recursively discover private data."""
    if not isinstance(artifacts, list) or not artifacts:
        raise Refusal("empty artifact inventory")
    seen: set[str] = set()
    totals = {"visible": 0, "trusted": 0}
    for entry in artifacts:
        closed(entry, ARTIFACT_FIELDS, "artifact")
        path = text(entry["path"], "artifact path")
        # Canonical names prevent slash aliases of the same file.
        if "\\" in path or path.casefold() in seen:
            raise Refusal("noncanonical or duplicate artifact path")
        seen.add(path.casefold())
        visibility = entry["visibility"]
        if visibility not in totals:
            raise Refusal("unknown artifact visibility")
        read_bound(root, path, digest(entry["sha256"], "artifact hash"))
        totals[visibility] += 1
    return {
        "schema_version": "m11-inventory-inspection/1",
        "files": len(seen), "visibility_counts": totals,
        "disposition": "HASH_INSPECTION_ONLY",
        "admission": "PENDING", "independence": "NOT_ESTABLISHED",
    }


def public_inventory(artifacts: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Export only explicit visible artifact identities, not trusted file locations."""
    result = []
    for entry in artifacts:
        closed(entry, ARTIFACT_FIELDS, "artifact")
        if entry["visibility"] not in {"visible", "trusted"}:
            raise Refusal("unknown artifact visibility")
        if entry["visibility"] == "visible":
            result.append({
                "path": text(entry["path"], "visible path"),
                "sha256": digest(entry["sha256"], "visible hash"),
            })
    return result
