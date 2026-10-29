"""Stdlib scalar projection of accepted harnessrun/1 GradeResult text domains.

Source reference: src/harnessrun/models.py on joined baseline d77f78d.
No Pydantic/product import; this is not a replacement general wire parser.
"""
from __future__ import annotations

from typing import Any

from .formats import Refusal


def wire_text(value: Any, label: str, *, maximum: int = 4096) -> str:
    if (
        not isinstance(value, str) or not 1 <= len(value) <= maximum
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        raise Refusal(f"{label}: outside accepted harnessrun text domain")
    return value


def identifier(value: Any, label: str) -> str:
    return wire_text(value, label, maximum=256)
