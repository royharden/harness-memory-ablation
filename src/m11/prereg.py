"""Immutable prospective registration files, with a single exclusive write.

These records freeze source metadata only. They grant no P0 admission, authority,
model activation, monetary approval, or permission to execute the instrument.
"""

import json
import os
from collections.abc import Iterable
from pathlib import Path

from .campaign import (
    Pin,
    Registration,
    ScheduleManifest,
    SuiteManifest,
    canonical_json,
    sha256_json,
)
from .schedule import build_schedule, validate_schedule

_VERSION = "m11-preregistration/1"


def _pin_map(pins: Iterable[Pin]) -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    for pin in pins:
        identity = (pin.role, pin.name)
        if identity in result:
            raise ValueError("duplicate frozen pin identity")
        result[identity] = pin.sha256
    if not result:
        raise ValueError("registration requires explicit frozen pins")
    return result


def _prepare(registration: Registration, suite: SuiteManifest):
    _pin_map(registration.pins)
    if bool(registration.parent_registration_sha256) != bool(registration.amendment_reason):
        raise ValueError("parent digest and amendment reason must appear together")
    if registration.amendment_reason is not None and not registration.amendment_reason.strip():
        raise ValueError("amendment reason must be nonempty")
    schedule = build_schedule(registration, suite)
    digest = sha256_json(schedule)
    if registration.schedule_sha256 not in (None, digest):
        raise ValueError("supplied schedule checksum does not match full fixed design")
    frozen = registration.model_copy(update={"schedule_sha256": digest})
    validate_schedule(frozen, suite, schedule)
    return frozen, schedule


def _write_exclusive(path: str | Path, registration: Registration,
                     schedule: ScheduleManifest) -> None:
    envelope = {
        "schema_version": _VERSION,
        "registration_sha256": sha256_json(registration),
        "registration": registration.model_dump(mode="json"),
        "schedule": schedule.model_dump(mode="json"),
    }
    # 'x' refuses every pre-existing path. A failed/partial write is preserved,
    # never deleted or overwritten; later verification fails closed on its bytes.
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(canonical_json(envelope) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def freeze_registration(path: str | Path, registration: Registration,
                        suite: SuiteManifest) -> Registration:
    """Freeze an initial full design; amendments must use amend_registration."""
    if registration.parent_registration_sha256 is not None or registration.amendment_reason is not None:
        raise ValueError("initial freeze cannot bypass amendment lineage checks")
    frozen, schedule = _prepare(registration, suite)
    _write_exclusive(path, frozen, schedule)
    return frozen


def _read(path: str | Path, suite: SuiteManifest):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON object key in registration")
            result[key] = value
        return result

    raw = Path(path).read_text(encoding="utf-8")
    payload = json.loads(raw, object_pairs_hook=unique_object)
    keys = {"schema_version", "registration_sha256", "registration", "schedule"}
    if not isinstance(payload, dict) or set(payload) != keys or payload["schema_version"] != _VERSION:
        raise ValueError("invalid closed preregistration envelope")
    # Validate through JSON for strict Pydantic tuple fields as well as strings.
    registration = Registration.model_validate_json(canonical_json(payload["registration"]))
    schedule = ScheduleManifest.model_validate_json(canonical_json(payload["schedule"]))
    if payload["registration_sha256"] != sha256_json(registration):
        raise ValueError("registration checksum mismatch")
    _pin_map(registration.pins)
    if bool(registration.parent_registration_sha256) != bool(registration.amendment_reason):
        raise ValueError("invalid amendment lineage")
    if registration.amendment_reason is not None and not registration.amendment_reason.strip():
        raise ValueError("empty amendment reason")
    validate_schedule(registration, suite, schedule)
    return registration, schedule


def verify_registration(path: str | Path, suite: SuiteManifest, *,
                        current_pins: Iterable[Pin] | None = None) -> Registration:
    """Verify frozen bytes, full schedule, suite and optionally current pin equality.

    Callers checking execution eligibility must supply current_pins; omitted pins
    only verify artifact integrity and never constitute dispatch authorization.
    """
    registration, _ = _read(path, suite)
    if current_pins is not None and _pin_map(current_pins) != _pin_map(registration.pins):
        raise ValueError("current pins differ from frozen registration")
    return registration


def amend_registration(path: str | Path, parent: Registration, suite: SuiteManifest,
                       amendment: Registration, *,
                       consumed_cell_ids: Iterable[str] = ()) -> Registration:
    """Freeze a distinct prospective campaign without replacing consumed slots.

    The caller supplies a previously verified frozen parent and durable consumed
    identities under the controller lease. This conservative implementation
    forbids any same-campaign redesign after consumption; use a separately
    disclosed campaign rather than relabel or replace prior outcomes.
    """
    if not parent.schedule_sha256:
        raise ValueError("parent must be a frozen, verified registration")
    if tuple(consumed_cell_ids):
        raise ValueError("cannot amend consumed campaign retrospectively")
    if amendment.registration_id == parent.registration_id:
        raise ValueError("amendment requires a distinct registration identity")
    if amendment.campaign_id != parent.campaign_id or amendment.mode != parent.mode:
        raise ValueError("amendment must preserve campaign identity and mode")
    if amendment.parent_registration_sha256 != sha256_json(parent):
        raise ValueError("amendment does not bind exact frozen parent")
    if not amendment.amendment_reason or not amendment.amendment_reason.strip():
        raise ValueError("prospective amendment requires an explicit reason")
    frozen, schedule = _prepare(amendment, suite)
    _write_exclusive(path, frozen, schedule)
    return frozen
