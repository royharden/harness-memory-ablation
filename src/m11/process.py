"""Future isolated Linux supervision source; unavailable authorities refuse by default.

This source has not executed. No isolation, activation or durable journal backend
is supplied here. Trusted integrations must prove those properties before spawn.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
import selectors
import signal
import subprocess
import sys
import time
from collections.abc import Callable, Mapping
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from harnessrun import AttemptSpec, ContractError, LaunchSpec, canonical_json, sha256_bytes

from .workspace import (RuntimeAttestation, RuntimePermit, RuntimeVerifier,
    TaskDelivery, UnavailableRuntimeVerifier, WorkspacePolicy,
    confirm_execution_permission, validate_workspace)


class ControllerRefusal(ContractError):
    """Dispatch refused; inspect phase/message before inferring claim state.

    Preflight refusals do not claim a launch. A durable-claim binding failure
    remains consumed/ambiguous; this exception never authorizes refund or retry.
    """


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


StopReason = Literal["finished", "timeout", "output_cap", "crash", "cancelled"]


@dataclass(frozen=True)
class LaunchClaim:
    """Durable single-use claim; construction of this value grants nothing."""

    claim_id: str
    attempt_id: str
    launch_id: str
    attempt_spec_sha256: str
    launch_spec_sha256: str
    permit_sha256: str
    ledger_run_id: str


@dataclass(frozen=True)
class ControllerOutcome:
    lifecycle: Lifecycle
    output: bytes
    output_truncated: bool
    stdin_bytes_written: int
    exit_code: int | None
    wall_seconds: float
    liability: Literal["retained"] = "retained"
    journal_confirmed: bool = False


class DurableLaunchJournal(Protocol):
    """Missing durable/M9 integration, NOT a memory-only retry cache.

    claim must atomically persist and fsync uniqueness of BOTH attempt and launch,
    exact hashes and actual M9 begin binding before returning. Every claimed ID
    remains consumed after crash, exception or failed spawn; never retry it.
    Uncertain writes must fail closed with durable pending liability.
    record_spawn_intent must durably mark begin ambiguous before Popen; only a
    confirmed PID receipt may advance to begun. record_* must be idempotent
    exact-binding durable updates; none settles/releases money. Calls must have
    bounded latency; implementations with unbounded IO are inadmissible.

    group_state is a trusted *live* ownership authority, not just a PID lookup.
    It must pin an exclusive Linux PID namespace/ownership lease, prevent PGID
    reuse/escape through the following signal, account for all descendants, and
    return empty only after reaping/confirming all owned processes absent. A
    killpg(0) probe or leader exit alone is insufficient. Unknown loses authority
    to signal and retains cleanup_pending. No implementation is supplied.
    """

    def claim(self, attempt: AttemptSpec, launch: LaunchSpec, permit: RuntimePermit,
              attestation: RuntimeAttestation) -> LaunchClaim: ...
    def record_started(self, claim: LaunchClaim, pid: int, pgid: int) -> None: ...
    def record_spawn_intent(self, claim: LaunchClaim) -> None: ...
    def record_cleanup_pending(self, claim: LaunchClaim, reason: StopReason) -> None: ...
    def group_state(self, claim: LaunchClaim, pid: int, pgid: int) -> Literal["owned", "empty", "unknown"]: ...
    def record_finished(self, claim: LaunchClaim, outcome: ControllerOutcome) -> None: ...


class UnavailableLaunchJournal:
    def claim(self, attempt: AttemptSpec, launch: LaunchSpec, permit: RuntimePermit,
              attestation: RuntimeAttestation) -> LaunchClaim:
        raise ControllerRefusal("durable single-use launch/M9 journal and live group ownership integration unavailable")

    def record_started(self, claim: LaunchClaim, pid: int, pgid: int) -> None:
        raise ControllerRefusal("durable launch journal unavailable")

    def record_spawn_intent(self, claim: LaunchClaim) -> None:
        raise ControllerRefusal("durable spawn intent unavailable")

    def record_cleanup_pending(self, claim: LaunchClaim, reason: StopReason) -> None:
        raise ControllerRefusal("durable launch journal unavailable; retain liability")

    def group_state(self, claim: LaunchClaim, pid: int, pgid: int) -> Literal["owned", "empty", "unknown"]:
        return "unknown"

    def record_finished(self, claim: LaunchClaim, outcome: ControllerOutcome) -> None:
        raise ControllerRefusal("durable launch journal unavailable; retain liability")


class ProcessController:
    """Only trusted constructor integrations can reach future Linux OS effects.

    This is not a host fallback. The verifier and journal must independently
    attest the current isolated execution context and descendant ownership.
    No request flag, permit artifact alone, or in-memory claim enables execution.
    """

    def __init__(self, *, verifier: RuntimeVerifier | None = None,
                 journal: DurableLaunchJournal | None = None) -> None:
        self._verifier = verifier if verifier is not None else UnavailableRuntimeVerifier()
        self._journal = journal if journal is not None else UnavailableLaunchJournal()

    def prepare(self, attempt: AttemptSpec, launch: LaunchSpec, policy: WorkspacePolicy) -> DispatchRefusal:
        validate_workspace(attempt, launch, policy)
        return DispatchRefusal(attempt_id=attempt.attempt_id)

    def execute(self, attempt: AttemptSpec, launch: LaunchSpec, policy: WorkspacePolicy, *,
                delivery: TaskDelivery | None = None, permit: RuntimePermit | None = None,
                environment: Mapping[str, str] | None = None,
                cancel_requested: Callable[[], bool] | None = None) -> ControllerOutcome:
        validate_workspace(attempt, launch, policy)
        if delivery is None or permit is None:
            raise ControllerRefusal("task delivery and externally verified runtime permit required; no launch claimed")
        if isinstance(self._journal, UnavailableLaunchJournal) or isinstance(self._verifier, UnavailableRuntimeVerifier):
            raise ControllerRefusal("runtime verification and durable launch journal unavailable; no launch claimed")
        if sys.platform != "linux":
            raise ControllerRefusal("isolated Linux execution context required; host fallback forbidden")
        # Never inherit os.environ, PATH, secrets, startup hooks or user config.
        env = dict(environment) if environment is not None else {}
        if set(env) != set(policy.environment_names) or any(
            not isinstance(key, str) or not isinstance(value, str) or "\x00" in value
            for key, value in env.items()
        ):
            raise ControllerRefusal("explicit environment must match exact admitted names")
        if env.get("HOME") != policy.fresh_home:
            raise ControllerRefusal("explicit HOME must equal admitted fresh home")
        if not launch.argv[0].startswith("/"):
            raise ControllerRefusal("absolute pinned executable required; no PATH search")
        if cancel_requested is not None and cancel_requested():
            raise ControllerRefusal("cancelled before claim; no dispatch")
        attestation = confirm_execution_permission(attempt, launch, policy, delivery, permit, self._verifier)
        deadline = datetime.fromisoformat(launch.deadline_utc.replace("Z", "+00:00"))
        permit_end = datetime.fromisoformat(permit.expires_at.replace("Z", "+00:00"))
        remaining = (min(deadline, permit_end) - datetime.now(timezone.utc)).total_seconds()
        if remaining <= 0:
            raise ControllerRefusal("absolute launch deadline elapsed before claim")
        try:
            claim = self._journal.claim(attempt, launch, permit, attestation)
        except Exception:
            raise ControllerRefusal(
                "durable claim acknowledgement unavailable; attempt/launch remain consumed or ambiguous; retain liability"
            ) from None
        expected = (attempt.attempt_id, launch.launch_id, sha256_bytes(canonical_json(attempt)),
                    sha256_bytes(canonical_json(launch)), sha256_bytes(canonical_json(permit)), permit.ledger_run_id)
        actual = (claim.attempt_id, claim.launch_id, claim.attempt_spec_sha256,
                  claim.launch_spec_sha256, claim.permit_sha256, claim.ledger_run_id)
        if not claim.claim_id or actual != expected:
            # The authority may have durably consumed a claim: no ambiguous retry.
            raise ControllerRefusal("durable claim binding uncertain; claim remains consumed and liability retained")
        return self._run_claimed(attempt, launch, policy, delivery, permit, env, cancel_requested, claim)

    def _run_claimed(self, attempt: AttemptSpec, launch: LaunchSpec, policy: WorkspacePolicy,
                     delivery: TaskDelivery, permit: RuntimePermit, environment: dict[str, str],
                     cancel_requested: Callable[[], bool] | None, claim: LaunchClaim) -> ControllerOutcome:
        started = time.monotonic()
        plan = supervision_plan(attempt, launch)
        deadline = min(datetime.fromisoformat(launch.deadline_utc.replace("Z", "+00:00")),
            datetime.fromisoformat(permit.expires_at.replace("Z", "+00:00")))
        remaining = (deadline - datetime.now(timezone.utc)).total_seconds()
        end = started + min(attempt.timeout_seconds, max(0.0, remaining))
        proc: subprocess.Popen[bytes] | None = None
        selector = selectors.DefaultSelector()
        output = bytearray()
        sent = 0
        truncated = False
        reason: StopReason = "crash"
        journal_ok = True
        started_acknowledged = False
        empty = False
        try:
            # Recheck after durable claim latency. Any refusal consumes the claim.
            confirm_execution_permission(attempt, launch, policy, delivery, permit, self._verifier)
            if time.monotonic() >= end:
                reason = "timeout"
            elif cancel_requested is not None and cancel_requested():
                reason = "cancelled"
            else:
                # Persist an ambiguous launch intent BEFORE the OS call. Any
                # crash/lost Popen acknowledgement must block redispatch.
                try:
                    self._journal.record_spawn_intent(claim)
                except Exception:
                    journal_ok = False
                    raise
                if time.monotonic() >= end or datetime.now(timezone.utc) >= deadline:
                    raise ControllerRefusal("launch deadline expired during durable spawn intent")
                proc = subprocess.Popen(launch.argv, cwd=launch.cwd, env=environment,
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    shell=False, start_new_session=True, close_fds=True, bufsize=0)
                # start_new_session makes the successfully spawned child pid its
                # SID and PGID. Persist before IO; all failures enter cleanup.
                try:
                    self._journal.record_started(claim, proc.pid, proc.pid)
                    started_acknowledged = True
                except Exception:
                    journal_ok = False
                    raise
                assert proc.stdin is not None and proc.stdout is not None
                os.set_blocking(proc.stdin.fileno(), False)
                os.set_blocking(proc.stdout.fileno(), False)
                selector.register(proc.stdin, selectors.EVENT_WRITE, "input")
                selector.register(proc.stdout, selectors.EVENT_READ, "output")
                while True:
                    if cancel_requested is not None and cancel_requested():
                        reason = "cancelled"
                        break
                    if time.monotonic() >= end or datetime.now(timezone.utc) >= deadline:
                        reason = "timeout"
                        break
                    if proc.poll() is not None and not any(key.data == "output" for key in selector.get_map().values()):
                        reason = "finished" if proc.returncode == 0 and sent == len(delivery.payload) else "crash"
                        break
                    for key, _ in selector.select(min(0.05, max(0.0, end - time.monotonic()))):
                        if key.data == "input":
                            try:
                                sent += os.write(key.fd, delivery.payload[sent:sent + 65536])
                            except BlockingIOError:
                                continue
                            except BrokenPipeError:
                                selector.unregister(key.fileobj)
                                proc.stdin.close()
                                continue
                            if sent == len(delivery.payload):
                                selector.unregister(key.fileobj)
                                proc.stdin.close()
                        else:
                            try:
                                chunk = os.read(key.fd, min(65536, attempt.output_cap_bytes - len(output) + 1))
                            except BlockingIOError:
                                continue
                            if not chunk:
                                selector.unregister(key.fileobj)
                                continue
                            room = attempt.output_cap_bytes - len(output)
                            output.extend(chunk[:room])
                            if len(chunk) > room:
                                truncated = True
                                reason = "output_cap"
                                break
                    if truncated:
                        break
        except Exception:
            # Do not expose environment/task/output through exception text. A
            # failed Popen/receipt may be ambiguous; never permit redispatch.
            reason = "crash"
        finally:
            try:
                self._journal.record_cleanup_pending(claim, reason)
            except Exception:
                journal_ok = False
            if proc is not None:
                empty = self._cleanup_group(proc, claim, plan)
            # No child object does not prove that an ambiguous spawn failed.
            try:
                selector.close()
            except Exception:
                journal_ok = False
            if proc is not None:
                for stream in (proc.stdin, proc.stdout):
                    if stream is not None:
                        try:
                            stream.close()
                        except Exception:
                            journal_ok = False
        confirmed = empty and journal_ok and started_acknowledged
        state = Lifecycle(attempt_id=attempt.attempt_id, launch_id=launch.launch_id,
            process_state="exited" if confirmed else "cleanup_pending",
            begin_state="begun" if started_acknowledged else "ambiguous", terminal_reason=reason,
            cleanup_state="confirmed" if confirmed else "unconfirmed")
        result = ControllerOutcome(state, bytes(output), truncated, sent,
            proc.returncode if proc is not None else None, time.monotonic() - started)
        try:
            self._journal.record_finished(claim, result)
        except Exception:
            return ControllerOutcome(Lifecycle(attempt_id=attempt.attempt_id, launch_id=launch.launch_id,
                process_state="cleanup_pending", begin_state=state.begin_state,
                terminal_reason=reason, cleanup_state="unconfirmed"), result.output,
                truncated, sent, result.exit_code, result.wall_seconds)
        return ControllerOutcome(result.lifecycle, result.output, truncated, sent,
            result.exit_code, result.wall_seconds, journal_confirmed=journal_ok)

    def _cleanup_group(self, proc: subprocess.Popen[bytes], claim: LaunchClaim,
                       plan: ProcessGroupPlan) -> bool:
        """Bounded TERM/KILL for owned descendants, including exited leaders.

        Trusted live ownership must hold across each signal to prevent PGID reuse.
        Escaped/unverifiable descendants mean pending; leader wait is not proof.
        """
        try:
            if proc.pid <= 1 or proc.pid in (os.getpid(), os.getpgrp()):
                return False  # Never signal this supervisor or its own group.
            for sig, grace in ((signal.SIGTERM, plan.term_grace_seconds),
                               (signal.SIGKILL, plan.kill_grace_seconds)):
                ownership = self._journal.group_state(claim, proc.pid, proc.pid)
                if ownership == "empty":
                    proc.poll()
                    return proc.returncode is not None
                if ownership != "owned":
                    return False
                try:
                    os.killpg(proc.pid, sig)
                except ProcessLookupError:
                    pass  # Still requires trusted whole-group verification.
                until = time.monotonic() + grace
                while time.monotonic() < until:
                    proc.poll()  # Nonblocking leader reap, including a zombie.
                    ownership = self._journal.group_state(claim, proc.pid, proc.pid)
                    if ownership == "empty":
                        return proc.returncode is not None
                    if ownership != "owned":
                        return False
                    time.sleep(min(0.02, max(0.0, until - time.monotonic())))
            proc.poll()
            return (self._journal.group_state(claim, proc.pid, proc.pid) == "empty"
                    and proc.returncode is not None)
        except Exception:
            return False

    def dispatch(self, attempt: AttemptSpec, launch: LaunchSpec, policy: WorkspacePolicy, **kwargs: object) -> ControllerOutcome:
        # Legacy entrypoint deliberately accepts no enabling flag or kwargs.
        if kwargs:
            raise ControllerRefusal("use typed execute delivery/permit arguments; dispatch options unavailable")
        return self.execute(attempt, launch, policy)
