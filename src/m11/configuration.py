"""Non-operational activation metadata and explicit placeholder refusals.

No environment lookup, credential value, account lookup or authority is supplied.
Even a fully filled template cannot replace authentic admission/runtime evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

from harnessrun import ContractError, canonical_json, strict_json
from harnessrun.models import Identifier

_MARKER = re.compile(r"PLACEHOLDER_[A-Z0-9]+(?:_[A-Z0-9]+)*", re.IGNORECASE)
EnvironmentName = Annotated[str, StringConstraints(
    min_length=1, max_length=128, pattern=r"^[A-Za-z_][A-Za-z0-9_]*$"
)]


class ConfigurationRefusal(ContractError):
    """Unresolved configuration; no input values are echoed in this error."""


@dataclass(frozen=True)
class PlaceholderUse:
    name: str
    location: str


def placeholder_uses(value: object, location: str = "$") -> tuple[PlaceholderUse, ...]:
    """Detect named markers even when embedded, case changed or brackets removed.

    Byte payloads/captures are not activation metadata and are not decoded here.
    Traversal is limited to supplied model/JSON-like data; it performs no I/O.
    """
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="python")
    if isinstance(value, str):
        return tuple(PlaceholderUse(f"<{m.group().upper()}>", location)
                     for m in _MARKER.finditer(value))
    if isinstance(value, dict):
        return tuple(use for key, item in value.items()
                     for use in placeholder_uses(item, f"{location}.{key}"))
    if isinstance(value, (tuple, list)):
        return tuple(use for index, item in enumerate(value)
                     for use in placeholder_uses(item, f"{location}[{index}]"))
    return ()


def require_no_placeholders(value: object) -> None:
    if placeholder_uses(value):
        # Never leak actual field contents or environment values into errors.
        raise ConfigurationRefusal("named placeholder is non-operational; authentic configuration unavailable")


class ActivationTemplate(BaseModel):
    """Only non-secret metadata; no secret-value or verified/approved field."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    schema_version: Literal["m11-activation-template/1"]
    operational: Literal[False]
    harness_id: Literal["claude", "codex"]
    model_pin: Identifier
    account_id: Identifier
    endpoint_profile_id: Identifier
    credential_environment_name: EnvironmentName

    @field_validator("operational", mode="before")
    @classmethod
    def never_operational(cls, value: object) -> bool:
        if type(value) is not bool or value is not False:
            raise ValueError("activation template is strictly non-operational")
        return False

    @field_validator("model_pin", "account_id", "endpoint_profile_id")
    @classmethod
    def explicit_slot(cls, value: str) -> str:
        if not value.strip() or value != value.strip():
            raise ValueError("activation metadata must be nonblank with no surrounding whitespace")
        return value


class TemplateInspection(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    status: Literal["refused"] = "refused"
    operational: Literal[False] = False
    placeholder_names: tuple[str, ...]
    unresolved_fields: tuple[str, ...]
    reasons: tuple[str, ...]


def parse_activation_template(payload: bytes | dict) -> ActivationTemplate:
    try:
        raw = canonical_json(payload) if isinstance(payload, dict) else payload
        decoded = strict_json(raw, max_bytes=64 * 1024)
        if not isinstance(decoded, dict):
            raise ValueError("object required")
        return ActivationTemplate.model_validate_json(canonical_json(decoded), strict=True)
    except (ValueError, TypeError):
        raise ConfigurationRefusal("invalid activation template; only closed non-secret metadata is permitted") from None


def inspect_activation_template(payload: bytes | dict) -> TemplateInspection:
    template = parse_activation_template(payload)
    markers = placeholder_uses(template)
    reasons = ("named_placeholders_non_operational",) if markers else ()
    return TemplateInspection(
        placeholder_names=tuple(sorted({use.name for use in markers})),
        unresolved_fields=tuple(sorted({use.location for use in markers})),
        reasons=reasons + ("template_not_execution_authority", "authentic_runtime_admission_unavailable"),
    )
