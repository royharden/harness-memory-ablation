"""Closed harnessrun/1 records. Construction source; conformance remains unrun."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator

Text = Annotated[str, StringConstraints(min_length=1, max_length=4096, pattern=r"^[^\x00-\x1f\x7f]+$")]
Identifier = Annotated[str, StringConstraints(min_length=1, max_length=256, pattern=r"^[^\x00-\x1f\x7f]+$")]
SHA256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
Count = Annotated[int, Field(strict=True, ge=0)]
Positive = Annotated[int, Field(strict=True, gt=0)]
Seconds = Annotated[float, Field(ge=0, allow_inf_nan=False)]
USD = Annotated[str, StringConstraints(pattern=r"^(0|[1-9][0-9]*)(\.[0-9]+)?$")]
EnvName = Annotated[str, StringConstraints(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")]
Mode = Literal["SIMULATED", "MEASURED"]
ExperimentKind = Literal["task", "diagnostic", "probe", "longitudinal", "smoke"]
Coverage = Literal["complete", "partial", "unknown"]
EvidenceStrength = Literal["verified", "hypothesis", "unsupported"]
TerminalStatus = Literal["finished", "timeout", "spend_cap", "output_cap", "crash", "refused", "cleanup_pending"]
LimitationCode = Literal[
    "unknown_usage", "unobservable_retry", "budget_bound_unproven", "undefined_cost_ratio",
    "model_substitution", "model_unverified", "parser_schema_drift", "global_context_leak",
    "treatment_not_loaded", "stale_memory_followed", "decoy_followed", "memory_write_invalid",
    "grader_flake", "evaluator_error", "oracle_circularity", "heldout_exposure", "timeout",
    "spend_cap_stop", "agent_error", "infra_excluded", "cleanup_pending", "workspace_lost",
    "trajectory_divergence", "claim_deleted", "metric_unavailable", "ceiling", "floor",
]


class ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True, allow_inf_nan=False)


class Record(ClosedModel):
    schema_version: Literal["harnessrun/1"] = "harnessrun/1"


class TreatmentFile(ClosedModel):
    path: Text
    sha256: SHA256
    access: Literal["read_only", "read_write"]


class Mount(ClosedModel):
    source_ref: Text
    target_path: Text
    access: Literal["read_only", "read_write"]


class ProviderConfig(Record):
    record_type: Literal["ProviderConfig"] = "ProviderConfig"
    vendor: Identifier
    endpoint_profile_id: Identifier
    requested_model_id: Identifier
    auth_reference_name: EnvName | None
    billing_mode: Literal["api", "none", "subscription"]


class AttemptSpec(Record):
    record_type: Literal["AttemptSpec"] = "AttemptSpec"
    campaign_id: Identifier
    attempt_id: Identifier
    cell_id: Identifier
    parent_attempt_id: Identifier | None
    retry_of: Identifier | None
    experiment_kind: ExperimentKind
    mode: Mode
    suite_id: Identifier
    suite_sha256: SHA256
    task_id: Identifier
    task_sha256: SHA256
    treatment_id: Identifier
    treatment_manifest_sha256: SHA256
    harness_id: Identifier
    provider_config_sha256: SHA256
    model_settings_sha256: SHA256
    repeat: Count
    checkpoint: Annotated[int, Field(strict=True, ge=1, le=12)] | None
    workspace_ref: Text
    workspace_manifest_sha256: SHA256
    treatment_files: tuple[TreatmentFile, ...]
    timeout_seconds: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    max_turns: Positive
    output_cap_bytes: Positive
    ledger_reservation_id: Identifier | None
    spend_bound_sha256: SHA256 | None
    environment_names: tuple[EnvName, ...]

    @model_validator(mode="after")
    def check_design(self) -> AttemptSpec:
        if (self.experiment_kind == "longitudinal") != (self.checkpoint is not None):
            raise ValueError("checkpoint required only for longitudinal attempts")
        arms = {"task": {"M0", "M1", "M2"}, "longitudinal": {"L0", "L1", "L2"}}
        if self.experiment_kind in arms and self.treatment_id not in arms[self.experiment_kind]:
            raise ValueError("treatment arm does not match experiment")
        if self.treatment_id in {"M0", "L0"} and self.treatment_files:
            raise ValueError("baseline has no treatment file")
        if self.experiment_kind == "task" and any(f.access != "read_only" for f in self.treatment_files):
            raise ValueError("task treatment files must be immutable")
        if self.treatment_id != "L2" and any(f.access == "read_write" for f in self.treatment_files):
            raise ValueError("only L2 permits typed memory updates")
        if self.attempt_id in {self.parent_attempt_id, self.retry_of}:
            raise ValueError("attempt cannot reference itself")
        _unique(self.environment_names, "environment_names")
        _unique(tuple(f.path for f in self.treatment_files), "treatment paths")
        return self


class LaunchSpec(Record):
    record_type: Literal["LaunchSpec"] = "LaunchSpec"
    launch_id: Identifier
    attempt_id: Identifier
    attempt_spec_sha256: SHA256
    argv: tuple[Text, ...]
    cwd: Text
    binary_sha256: SHA256
    image_sha256: SHA256 | None
    allowed_mounts: tuple[Mount, ...]
    environment_names: tuple[EnvName, ...]
    deadline_utc: Text
    output_cap_bytes: Positive

    @field_validator("deadline_utc")
    @classmethod
    def deadline_is_utc(cls, value: str) -> str:
        _utc(value)
        return value

    @model_validator(mode="after")
    def check_launch(self) -> LaunchSpec:
        if not self.argv:
            raise ValueError("argv must name an executable")
        _unique(self.environment_names, "environment_names")
        _unique(tuple(m.target_path for m in self.allowed_mounts), "mount targets")
        return self


class CapabilityEvidence(ClosedModel):
    status: EvidenceStrength
    evidence_ref: Text | None
    evidence_sha256: SHA256 | None
    reason: Text

    @model_validator(mode="after")
    def verified_requires_evidence(self) -> CapabilityEvidence:
        if (self.evidence_ref is None) != (self.evidence_sha256 is None):
            raise ValueError("evidence reference/hash must be paired")
        if self.status == "verified" and self.evidence_ref is None:
            raise ValueError("verified capability requires evidence")
        return self


class CapabilityRecord(Record):
    record_type: Literal["CapabilityRecord"] = "CapabilityRecord"
    harness_id: Identifier
    cli_version: Identifier
    binary_sha256: SHA256
    image_sha256: SHA256 | None
    provider_config_sha256: SHA256
    settings_sha256: SHA256
    model_evidence: CapabilityEvidence
    native_memory: CapabilityEvidence
    usage_buckets: CapabilityEvidence
    spend_bound: CapabilityEvidence


class ObservedRecord(Record):
    evidence_ref: Text
    evidence_sha256: SHA256
    source_locator: Text


class ModelEvidence(ObservedRecord):
    record_type: Literal["ModelEvidence"] = "ModelEvidence"
    model_evidence_id: Identifier
    attempt_id: Identifier
    response_id: Identifier | None
    requested_model_id: Identifier
    advertised_model_id: Identifier | None
    provider_returned_model_id: Identifier | None
    evidence_kind: Literal["configuration_echo", "harness_advertised", "provider_response", "unavailable"]
    strength: EvidenceStrength
    unknown_reason: Text | None

    @model_validator(mode="after")
    def identity_is_not_echo(self) -> ModelEvidence:
        if self.strength == "verified" and (
            self.evidence_kind != "provider_response" or self.provider_returned_model_id is None
            or self.response_id is None
        ):
            raise ValueError("model verification requires provider response evidence")
        if self.provider_returned_model_id is None and self.unknown_reason is None:
            raise ValueError("unknown provider model needs an explicit reason")
        return self


class StartedPayload(ClosedModel):
    launch_id: Identifier


class ResponsePayload(ClosedModel):
    response_id: Identifier


class MemorySourcePayload(ClosedModel):
    source_ref: Text
    source_sha256: SHA256 | None
    observation: Literal["listed", "read", "unexpected"]


class StopPayload(ClosedModel):
    reason: TerminalStatus


class ParserErrorPayload(ClosedModel):
    code: Literal["parser_schema_drift"]
    detail_ref: Text


class HarnessEvent(ObservedRecord):
    record_type: Literal["HarnessEvent"] = "HarnessEvent"
    event_id: Identifier
    attempt_id: Identifier
    sequence: Count
    kind: Literal["started", "response", "memory_source", "stop", "parser_error"]
    payload: StartedPayload | ResponsePayload | MemorySourcePayload | StopPayload | ParserErrorPayload

    @model_validator(mode="after")
    def payload_matches_tag(self) -> HarnessEvent:
        expected = {"started": StartedPayload, "response": ResponsePayload,
                    "memory_source": MemorySourcePayload, "stop": StopPayload,
                    "parser_error": ParserErrorPayload}
        if not isinstance(self.payload, expected[self.kind]):
            raise ValueError("payload does not match event kind")
        return self


class UsageBuckets(ClosedModel):
    ordinary_input: Count | None
    cached_input: Count | None
    cache_write_5m: Count | None
    cache_write_1h: Count | None
    output: Count | None


class UsageObservation(ObservedRecord):
    record_type: Literal["UsageObservation"] = "UsageObservation"
    observation_id: Identifier
    attempt_id: Identifier
    scope_id: Identifier
    counter_basis: Literal["incremental", "cumulative", "final"]
    usage_source: Literal["harness_reported"] = "harness_reported"
    coverage: Coverage
    unknown_reason: Text | None
    buckets: UsageBuckets
    input_total: Count | None
    cached_input_subset: Count | None
    reasoning_output_subset: Count | None
    harness_estimate_usd: USD | None
    pricetable_sha256: SHA256 | None

    @model_validator(mode="after")
    def check_coverage(self) -> UsageObservation:
        import re

        match = re.fullmatch(r"bytes:([0-9]+):([0-9]+)", self.source_locator)
        if match is None or int(match[1]) >= int(match[2]):
            raise ValueError("usage source_locator must identify nonempty raw capture byte range")
        if self.coverage == "complete" and any(v is None for v in self.buckets.model_dump().values()):
            raise ValueError("complete usage cannot contain unknown billing buckets")
        if self.coverage != "complete" and self.unknown_reason is None:
            raise ValueError("incomplete usage requires an explicit reason")
        if self.input_total is not None and self.cached_input_subset is not None:
            if self.cached_input_subset > self.input_total:
                raise ValueError("cached subset exceeds input total")
        if self.reasoning_output_subset is not None and self.buckets.output is not None:
            if self.reasoning_output_subset > self.buckets.output:
                raise ValueError("reasoning subset exceeds total output")
        return self


class AttemptRecord(Record):
    record_type: Literal["AttemptRecord"] = "AttemptRecord"
    campaign_id: Identifier
    attempt_id: Identifier
    cell_id: Identifier
    launch_id: Identifier | None
    parent_attempt_id: Identifier | None
    retry_of: Identifier | None
    mode: Mode
    attempt_spec_sha256: SHA256
    launch_spec_sha256: SHA256 | None
    created_at: Text
    started_at: Text | None
    ended_at: Text | None
    status: Literal["pending", "running", "finished", "timeout", "spend_cap", "output_cap", "crash", "refused", "cleanup_pending"]
    exit_code: Annotated[int, Field(strict=True)] | None
    process_state: Literal["not_started", "running", "exited", "cleanup_pending"]
    artifact_sha256: SHA256 | None
    transcript_ref: Text | None
    transcript_sha256: SHA256 | None
    usage_observation_ids: tuple[Identifier, ...]
    usage_coverage: Coverage
    model_evidence_ids: tuple[Identifier, ...]
    model_coverage: Coverage
    billing_provenance_hashes: tuple[SHA256, ...]
    ledger_run_id: Identifier | None
    ledger_reservation_id: Identifier | None
    wall_seconds: Seconds | None
    harness_estimate_usd: USD | None
    limitation_codes: tuple[LimitationCode, ...]

    @model_validator(mode="after")
    def check_lifecycle(self) -> AttemptRecord:
        created = _utc(self.created_at)
        start = _utc(self.started_at) if self.started_at else None
        end = _utc(self.ended_at) if self.ended_at else None
        if start is not None and start < created or end is not None and end < (start or created):
            raise ValueError("attempt timestamps are out of order")
        if self.status not in {"pending", "running"} and end is None:
            raise ValueError("terminal state requires ended_at")
        if self.status == "refused" and any(x is not None for x in (
            self.launch_id, self.launch_spec_sha256, self.started_at, self.exit_code, self.artifact_sha256
        )):
            raise ValueError("pre-launch refusal cannot invent launched work")
        if self.status == "refused" and not self.limitation_codes:
            raise ValueError("refusal requires a limitation reason")
        if (self.transcript_ref is None) != (self.transcript_sha256 is None):
            raise ValueError("transcript reference/hash must be paired")
        if self.process_state == "cleanup_pending" and self.status != "cleanup_pending":
            raise ValueError("cleanup_pending process must block result lifecycle")
        for name in ("usage_observation_ids", "model_evidence_ids", "billing_provenance_hashes", "limitation_codes"):
            _unique(getattr(self, name), name)
        return self


class GradeResult(Record):
    record_type: Literal["GradeResult"] = "GradeResult"
    attempt_id: Identifier
    artifact_sha256: SHA256
    opaque_task_id: Identifier
    verdict: Literal["pass", "fail", "evaluator_error"]
    grader_sha256: SHA256
    receipt_ref: Text
    receipt_sha256: SHA256


class Limitation(Record):
    record_type: Literal["Limitation"] = "Limitation"
    attempt_id: Identifier
    code: LimitationCode
    raw_code: Text
    evidence_ref: Text
    evidence_sha256: SHA256
    disposition: Literal["stop", "retain_descriptive", "missing", "secondary"]

    @model_validator(mode="after")
    def alias_is_explicit(self) -> Limitation:
        aliases = {"unverified_model": "model_unverified", "treatment_not_read": "treatment_not_loaded",
                   "metric_parse_failure": "metric_unavailable"}
        if aliases.get(self.raw_code, self.raw_code) != self.code:
            raise ValueError("raw limitation code does not map to normalized code")
        return self


WireRecord = Annotated[Union[ProviderConfig, AttemptSpec, LaunchSpec, CapabilityRecord,
    ModelEvidence, HarnessEvent, UsageObservation, AttemptRecord, GradeResult, Limitation],
    Field(discriminator="record_type")]


def _unique(values: tuple[object, ...], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {label}")


def _utc(value: str) -> datetime:
    if not value.endswith(("Z", "+00:00")) or "T" not in value:
        raise ValueError("timestamp must be RFC3339 UTC")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp must be UTC")
    return parsed
