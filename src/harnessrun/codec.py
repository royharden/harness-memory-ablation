"""Deterministic serialization and closed JSONL parsing, without application execution."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, TypeAdapter, ValidationError

from .models import WireRecord


class ContractError(ValueError):
    """A closed format or provenance requirement was not satisfied."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(value: BaseModel | dict | list | tuple) -> str:
    return sha256_bytes(canonical_json(value))


def canonical_json(value: BaseModel | dict | list | tuple) -> bytes:
    """UTF-8, sorted keys, no whitespace/NaN; hashes bind these exact bytes."""
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    _string_keys(value)
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise ContractError("value cannot be canonically serialized") from exc


def _string_keys(value: object) -> None:
    if isinstance(value, dict):
        if any(not isinstance(k, str) for k in value):
            raise ContractError("JSON object keys must be strings")
        for item in value.values():
            _string_keys(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _string_keys(item)


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("duplicate JSON key")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise ContractError("nonfinite JSON number")


def strict_json(data: bytes, *, max_bytes: int = 10 * 1024 * 1024) -> object:
    if len(data) > max_bytes:
        raise ContractError("JSON input exceeds byte cap")
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_object, parse_constant=_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ContractError("malformed UTF-8 JSON") from exc


def parse_record(data: bytes) -> WireRecord:
    payload = strict_json(data)
    if not isinstance(payload, dict) or payload.get("schema_version") != "harnessrun/1":
        raise ContractError("explicit harnessrun/1 schema_version required")
    if "record_type" not in payload:
        raise ContractError("explicit record_type required")
    try:
        return TypeAdapter(WireRecord).validate_json(canonical_json(payload), strict=True)
    except ValidationError as exc:
        # Never echo rejected payloads: they can contain accidental secrets/hidden text.
        raise ContractError("record violates closed harnessrun/1 schema") from exc


def parse_jsonl(data: bytes, *, max_bytes: int = 10 * 1024 * 1024) -> tuple[WireRecord, ...]:
    if len(data) > max_bytes:
        raise ContractError("JSONL input exceeds byte cap")
    if data and not data.endswith(b"\n"):
        raise ContractError("truncated JSONL final record")
    records = []
    for line in data.splitlines():
        if not line.strip():
            raise ContractError("blank JSONL record")
        records.append(parse_record(line))
    return tuple(records)


def dump_jsonl(records: tuple[WireRecord, ...]) -> bytes:
    return b"".join(canonical_json(record) + b"\n" for record in records)
