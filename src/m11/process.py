"""Source-only controller boundary and conservative lifecycle transitions.

No spawning, killing, ledger calls, host fallback or runtime activation exists in
this phase. Future Linux process-group ownership must cover child/grandchild
processes and prove cleanup; this module does not claim that proof.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from harnessrun import AttemptSpec, ContractError, LaunchSpec, canonical_json, sha256_bytes

from .workspace import WorkspacePolicy, validate_workspace


class ControllerRefusal(ContractError):
    """Dispatch is unavailable; no attempt was begun and no money reserved."""


class ProcessGroupPlan(BaseModel):
    """Inert Linux supervision plan; no OS calls or observed cleanup receipt.

    A future admitted backend must start the child in a fresh session and track
    its process group, including grandchildren. Killing only the leader is not
    cleanup. PID/PGID reuse and ownership must be checked by that backend.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    attempt_id: str
    launch_id: str
    start_new_session: Literal[True] = True
    target_scope: Literal["owned_linux_process_group"] = "owned_linux_process_group"
    timeout_seconds: float = Field(gt=0, allow_inf_nan=False)
    output_cap_bytes: int = Field(strict=True, gt=0)
    term_grace_seconds: float = Field(default=5.0, gt=0, allow_inf_nan=False)
    kill_grace_seconds: float = Field(default=5.0, gt=0, allow_inf_nan=False)
    cleanup_actions: tuple[Literal["mark_cleanup_pending", "signal_owned_group_TERM",
        "wait_bounded", "signal_remaining_owned_group_KILL", "verify_group_empty",
        "retain_ambiguous_liability"], ...] = (
            "mark_cleanup_pending", "signal_owned_group_TERM", "wait_bounded",
            "signal_remaining_owned_group_KILL", "wait_bounded", "verify_group_empty",
            "retain_ambiguous_liability")

    @model_validator(mode="after")
    def exact_cleanup_order(self) -> ProcessGroupPlan:
        if self.cleanup_actions != (
            "mark_cleanup_pending", "signal_owned_group_TERM", "wait_bounded",
            "signal_remaining_owned_group_KILL", "wait_bounded", "verify_group_empty",
            "retain_ambiguous_liability"
        ):
            raise ValueError("cleanup actions may not omit descendant verification or liability retention")
        return self


def supervision_plan(attempt: AttemptSpec, launch: LaunchSpec) -> ProcessGroupPlan:
    if launch.attempt_id != attempt.attempt_id or launch.attempt_spec_sha256 != sha256_bytes(canonical_json(attempt)):
        raise ContractError("supervision plan attempt/launch mismatch")
    return ProcessGroupPlan(attempt_id=attempt.attempt_id, launch_id=launch.launch_id,
        timeout_seconds=attempt.timeout_seconds, output_cap_bytes=attempt.output_cap_bytes)


class Lifecycle(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    attempt_id: str
    launch_id: str | None
    process_state: Literal["not_started", "running", "exited", "cleanup_pending"]
    begin_state: Literal["not_begun", "begun", "ambiguous"]
    terminal_reason: Literal["finished", "timeout", "spend_cap", "output_cap", "crash", "cancelled", "refused"] | None
    cleanup_state: Literal["not_needed", "unconfirmed", "confirmed"]

    @model_validator(mode="after")
    def consistency(self) -> Lifecycle:
        if not self.attempt_id:
            raise ValueError("empty attempt identity")
        if self.process_state == "not_started" and (self.begin_state != "not_begun" or self.cleanup_state != "not_needed"):
            raise ValueError("unstarted state cannot conceal ambiguous begin or cleanup")
        if self.process_state != "not_started" and (not self.launch_id or self.begin_state == "not_begun"):
            raise ValueError("started state needs launch identity and begin lineage")
        if self.begin_state == "ambiguous" and self.process_state != "cleanup_pending":
            raise ValueError("ambiguous begin must block scheduling")
        if self.process_state == "running" and (self.terminal_reason is not None or self.cleanup_state != "unconfirmed"):
            raise ValueError("running lifecycle cannot claim terminal/cleaned state")
        if self.process_state == "exited" and (self.cleanup_state != "confirmed" or self.terminal_reason is None):
            raise ValueError("exit requires entire owned process group confirmed gone")
        if self.process_state == "cleanup_pending" and self.cleanup_state != "unconfirmed":
            raise ValueError("cleanup_pending must retain unresolved cleanup")
        return self

    @property
    def blocks_dispatch(self) -> bool:
        return self.process_state in ("running", "cleanup_pending") or self.begin_state == "ambiguous"


def mark_cleanup_pending(state: Lifecycle, reason: Literal["finished", "timeout", "spend_cap", "output_cap", "crash", "cancelled"], *, ambiguous_begin: bool = False) -> Lifecycle:
    """Pure bookkeeping; this does not terminate a process or release liability."""
    if state.process_state not in ("running", "cleanup_pending"):
        raise ContractError("cannot clean an unowned/unstarted or already cleaned launch")
    return Lifecycle(attempt_id=state.attempt_id, launch_id=state.launch_id,
                     process_state="cleanup_pending", begin_state="ambiguous" if ambiguous_begin else state.begin_state,
                     terminal_reason=reason, cleanup_state="unconfirmed")


class DispatchRefusal(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    schema_version: Literal["m11-controller-refusal/1"] = "m11-controller-refusal/1"
    attempt_id: str
    status: Literal["refused"] = "refused"
    process_state: Literal["not_started"] = "not_started"
    reason_codes: tuple[Literal["source_only_phase", "P0_pending", "runtime_activation_unavailable"], ...] = (
        "source_only_phase", "P0_pending", "runtime_activation_unavailable")
    reserved: Literal[False] = False
    begun: Literal[False] = False


class ProcessController:
    """No caller-supplied flag can enable execution in source-construction mode."""

    def prepare(self, attempt: AttemptSpec, launch: LaunchSpec, policy: WorkspacePolicy) -> DispatchRefusal:
        validate_workspace(attempt, launch, policy)
        return DispatchRefusal(attempt_id=attempt.attempt_id)

    def execute(self, attempt: AttemptSpec, launch: LaunchSpec, policy: WorkspacePolicy) -> None:
        raise ControllerRefusal("source_only_phase: independent P0 pending; runtime activation unavailable; no dispatch/reserve/begin performed")

    def dispatch(self, attempt: AttemptSpec, launch: LaunchSpec, policy: WorkspacePolicy) -> None:
        self.execute(attempt, launch, policy)
