"""Preparation data and bounded, hash-bound parser framing. No process effects."""
from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict

from harnessrun import (
    AttemptSpec, CapabilityRecord, ContractError, HarnessEvent, LaunchSpec,
    ModelEvidence, Mount, ProviderConfig, UsageObservation, canonical_json, sha256_bytes,
)


class PreparationContext(BaseModel):
    """Resolved non-secret pins supplied by a controller, never discovered here."""
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    launch_id: str
    provider: ProviderConfig
    cli_version: str
    binary_sha256: str
    image_sha256: str | None
    cwd: str
    allowed_mounts: tuple[Mount, ...]
    deadline_utc: str
    executable: str


class NativePreparationRefused(ContractError):
    """The candidate launch is data only; current native dispatch is unavailable."""


def capability(harness_id: str, context: PreparationContext, settings_sha256: str,
               simulated: bool = False) -> CapabilityRecord:
    reason = ("SIMULATED builder-authored control; no native capability evidence"
              if simulated else "Live-unverified: no admitted pinned native execution evidence")
    status = "unsupported" if simulated else "hypothesis"
    entry = dict(status=status, evidence_ref=None, evidence_sha256=None, reason=reason)
    return CapabilityRecord(
        harness_id=harness_id, cli_version=context.cli_version,
        binary_sha256=context.binary_sha256, image_sha256=context.image_sha256,
        provider_config_sha256=sha256_bytes(canonical_json(context.provider)),
        settings_sha256=settings_sha256, model_evidence=entry, native_memory=entry,
        usage_buckets=entry,
        spend_bound=dict(status="unsupported", evidence_ref=None,
                         evidence_sha256=None, reason="No finite liability proof; native dispatch refused"),
    )


class AdapterBase:
    harness_id: str
    simulated: bool = False

    def __init__(self, context: PreparationContext, settings_sha256: str):
        self.context = context
        self.settings_sha256 = settings_sha256

    def capabilities(self) -> CapabilityRecord:
        return capability(self.harness_id, self.context, self.settings_sha256, self.simulated)

    def _validate(self, spec: AttemptSpec) -> None:
        if spec.harness_id != self.harness_id:
            raise ContractError("adapter harness_id mismatch")
        if spec.provider_config_sha256 != sha256_bytes(canonical_json(self.context.provider)):
            raise ContractError("provider configuration pin mismatch")
        if spec.model_settings_sha256 != self.settings_sha256:
            raise ContractError("model settings pin mismatch")
        if self.simulated:
            if (spec.mode != "SIMULATED" or self.context.provider.billing_mode != "none"
                    or self.context.provider.auth_reference_name is not None):
                raise ContractError("null/scripted require SIMULATED, billing none and no auth reference")
        elif spec.mode != "MEASURED":
            raise ContractError("native adapter cannot reinterpret SIMULATED as native")

    def _launch(self, spec: AttemptSpec, argv: tuple[str, ...]) -> LaunchSpec:
        self._validate(spec)
        return LaunchSpec(
            launch_id=self.context.launch_id, attempt_id=spec.attempt_id,
            attempt_spec_sha256=sha256_bytes(canonical_json(spec)), argv=argv,
            cwd=self.context.cwd, binary_sha256=self.context.binary_sha256,
            image_sha256=self.context.image_sha256,
            allowed_mounts=self.context.allowed_mounts,
            environment_names=spec.environment_names, deadline_utc=self.context.deadline_utc,
            output_cap_bytes=spec.output_cap_bytes,
        )


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("duplicate native JSON key")
        result[key] = value
    return result


class CaptureParser:
    """Incremental framing over an already frozen capture, not a live transport.

    Feed chunks of the supplied exact capture in order. Every record resolves a
    byte range in that capture. Mapping errors retain a parser-error record and
    unknown usage; no untrusted content is echoed into wire payloads.
    """
    def __init__(self, *, attempt_id: str, requested_model_id: str,
                 evidence_ref: str, capture: bytes, max_record_bytes: int = 1_048_576):
        if not attempt_id or not requested_model_id or not evidence_ref:
            raise ContractError("parser identity and capture reference are required")
        if type(max_record_bytes) is not int or max_record_bytes <= 0:
            raise ContractError("positive parser record bound required")
        self.attempt_id = attempt_id
        self.requested_model_id = requested_model_id
        self.evidence_ref = evidence_ref
        self.capture = capture
        self.capture_sha256 = sha256_bytes(capture)
        self.max_record_bytes = max_record_bytes
        self._received = 0
        self._consumed = 0
        self._buffer = b""
        self._sequence = 0
        self._closed = False

    def _provenance(self, start: int, end: int) -> dict[str, str]:
        return dict(evidence_ref=self.evidence_ref, evidence_sha256=self.capture_sha256,
                    source_locator=f"bytes:{start}:{end}")

    def _event(self, kind: str, payload: dict[str, object], start: int, end: int) -> HarnessEvent:
        sequence = self._sequence
        self._sequence += 1
        return HarnessEvent(event_id=self._id(start, kind),
                            attempt_id=self.attempt_id, sequence=sequence,
                            kind=kind, payload=payload, **self._provenance(start, end))

    def _model(self, response_id: str | None, advertised: str | None,
               returned: str | None, start: int, end: int) -> ModelEvidence:
        return ModelEvidence(
            model_evidence_id=self._id(start, "model"),
            attempt_id=self.attempt_id, response_id=response_id,
            requested_model_id=self.requested_model_id, advertised_model_id=advertised,
            provider_returned_model_id=returned,
            evidence_kind=("provider_response" if returned else
                           "harness_advertised" if advertised else "unavailable"),
            strength="hypothesis" if returned or advertised else "unsupported",
            unknown_reason="Native mapping unverified; response coverage and backend identity unproven",
            **self._provenance(start, end),
        )

    def _usage(self, start: int, end: int, buckets: dict[str, int | None], *,
               basis: Literal["incremental", "cumulative", "final"] = "incremental",
               input_total: int | None = None, cached: int | None = None,
               reasoning: int | None = None, estimate: str | None = None) -> UsageObservation:
        return UsageObservation(
            observation_id=self._id(start, "usage"),
            attempt_id=self.attempt_id, scope_id=self.attempt_id,
            counter_basis=basis, usage_source="harness_reported", coverage="partial",
            unknown_reason="Live-unverified mapping; nested calls/retries and bucket coverage unproven",
            buckets=buckets, input_total=input_total, cached_input_subset=cached,
            reasoning_output_subset=reasoning, harness_estimate_usd=estimate,
            pricetable_sha256=None, **self._provenance(start, end),
        )

    def _drift(self, start: int, end: int) -> tuple[HarnessEvent | UsageObservation, ...]:
        return (self._event("parser_error", dict(code="parser_schema_drift",
                          detail_ref=f"{self.evidence_ref}#bytes:{start}:{end}"), start, end),
                self._usage(start, end, empty_buckets()))

    def _id(self, start: int, kind: str) -> str:
        return kind + ":" + sha256_bytes(canonical_json(
            (self.attempt_id, self.capture_sha256, start, kind)))

    def parse(self, chunk: bytes) -> tuple[HarnessEvent | UsageObservation | ModelEvidence, ...]:
        if self._closed or type(chunk) is not bytes:
            raise ContractError("parser closed or non-byte input")
        end = self._received + len(chunk)
        if self.capture[self._received:end] != chunk or end > len(self.capture):
            raise ContractError("chunk differs from pinned raw capture")
        self._received = end
        self._buffer += chunk
        records: list[HarnessEvent | UsageObservation | ModelEvidence] = []
        while b"\n" in self._buffer:
            raw, self._buffer = self._buffer.split(b"\n", 1)
            start = self._consumed
            self._consumed += len(raw) + 1
            stop = self._consumed
            if not raw.strip() or len(raw) > self.max_record_bytes:
                records.extend(self._drift(start, stop))
                continue
            try:
                value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                                   parse_constant=lambda _: (_ for _ in ()).throw(ContractError("nonfinite JSON")))
                if not isinstance(value, dict):
                    raise ContractError("native record must be an object")
                records.extend(self._map(value, start, stop))
            except (ValueError, TypeError, KeyError, UnicodeError):
                records.extend(self._drift(start, stop))
        if len(self._buffer) > self.max_record_bytes:
            raise ContractError("incomplete native record exceeds parser bound")
        return tuple(records)

    def finalize(self) -> tuple[HarnessEvent | UsageObservation, ...]:
        if self._closed:
            raise ContractError("parser already finalized")
        self._closed = True
        if self._received != len(self.capture):
            raise ContractError("capture not fully supplied")
        return self._drift(self._consumed, self._received) if self._buffer else ()

    def _map(self, value: dict[str, object], start: int, end: int) -> tuple:
        raise NotImplementedError


def empty_buckets() -> dict[str, int | None]:
    return dict(ordinary_input=None, cached_input=None, cache_write_5m=None,
                cache_write_1h=None, output=None)


def counter(value: object) -> int | None:
    if value is None:
        return None
    if type(value) is not int or value < 0:
        raise ContractError("invalid native usage counter")
    return value


def closed(value: object, fields: set[str]) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) - fields:
        raise ContractError("unrecognized native object shape")
    return value
