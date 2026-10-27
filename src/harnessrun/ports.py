"""Public structural interfaces. No implementation here authorizes execution."""

from dataclasses import dataclass
from typing import Protocol

from .models import AttemptSpec, CapabilityRecord, GradeResult, HarnessEvent, LaunchSpec, ModelEvidence, UsageObservation


class HarnessPort(Protocol):
    def capabilities(self) -> CapabilityRecord: ...
    def prepare(self, attempt: AttemptSpec) -> LaunchSpec: ...
    def parse(self, data: bytes) -> tuple[HarnessEvent | UsageObservation | ModelEvidence, ...]: ...


@dataclass(frozen=True)
class LedgerReference:
    """References to actual M9 records, never an alternative monetary balance."""

    run_id: str
    reservation_id: str
    receipt_ref: str
    receipt_sha256: str


class LedgerPort(Protocol):
    def reserve(self, attempt: AttemptSpec) -> LedgerReference: ...
    def begin(self, reference: LedgerReference) -> LedgerReference: ...
    def settle(self, reference: LedgerReference, *, usage_state: str) -> LedgerReference: ...
    def snapshot(self) -> LedgerReference: ...
    def export(self) -> LedgerReference: ...


class GraderPort(Protocol):
    def grade(self, immutable_artifact: str, opaque_task_id: str) -> GradeResult: ...
