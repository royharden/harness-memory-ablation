"""Strict stdlib input helpers. No candidate imports, execution or implicit paths."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

DIGEST = re.compile(r"[0-9a-f]{64}\Z")


class Refusal(ValueError):
    """Malformed, unavailable or unsafe evaluation input."""


def closed(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise Refusal(f"{label}: required fields differ")
    return value


def text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise Refusal(f"{label}: expected nonempty text")
    return value


def digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or DIGEST.fullmatch(value) is None:
        raise Refusal(f"{label}: expected lowercase SHA256")
    return value


def strings(value: Any, label: str, *, empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not empty):
        raise Refusal(f"{label}: expected list")
    result = [text(item, label) for item in value]
    if len(result) != len(set(result)):
        raise Refusal(f"{label}: duplicate entry")
    return result


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise Refusal(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(raw: bytes, *, max_bytes: int = 4_000_000) -> Any:
    if len(raw) > max_bytes:
        raise Refusal("JSON input exceeds limit")
    try:
        return json.loads(
            raw.decode("utf-8-sig"), object_pairs_hook=_pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(Refusal("nonfinite JSON")),
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Refusal("invalid JSON encoding or syntax") from exc


def safe_file(root: Path, relative: str) -> Path:
    """Reject absolute paths, traversal, links and escapes before reading bytes."""
    text(relative, "relative path")
    normalized = relative.replace("\\", "/")
    parts = normalized.split("/")
    if (
        normalized.startswith("/") or ":" in normalized
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise Refusal("unsafe relative path")
    base = root.resolve(strict=True)
    current = base
    for part in parts:
        current = current / part
        if current.is_symlink() or current.is_junction():
            raise Refusal("linked evaluation path refused")
    try:
        resolved = current.resolve(strict=True)
        resolved.relative_to(base)
    except (OSError, ValueError) as exc:
        raise Refusal("evaluation path absent or outside root") from exc
    if not resolved.is_file():
        raise Refusal("evaluation artifact is not a file")
    return resolved


def read_bound(root: Path, relative: str, expected_sha256: str) -> bytes:
    expected = digest(expected_sha256, "artifact hash")
    path = safe_file(root, relative)
    if path.stat().st_size > 16_000_000:
        raise Refusal("artifact exceeds input limit")
    raw = path.read_bytes()
    if sha256(raw) != expected:
        raise Refusal("artifact hash mismatch")
    return raw
