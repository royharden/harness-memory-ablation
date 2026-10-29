"""Pure, closed twelve-checkpoint carry transitions; no workspace/process calls.

Every next launch requires a fresh process/home and the exact produced tree.
Candidate failures continue; infrastructure tree loss ends with unknown future
checkpoints. A pause can only be resolved on the same artifact/attempt, never by
repair, replacement, oracle rollback or a fresh dispatch of that checkpoint.
Construction checkpoint: runtime unverified.
"""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .campaign import TrajectoryCheckpoint, TripwireObservation, canonical_json

Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Identifier = Annotated[str, Field(min_length=1)]


class ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class InvalidMemoryArchive(ClosedModel):
    checkpoint: Annotated[int, Field(ge=1, le=12)]
    attempt_id: Identifier
    artifact_sha256: Digest


class PauseResolution(ClosedModel):
    checkpoint: Annotated[int, Field(ge=1, le=12)]
    receipt_sha256: Digest


class TrajectoryState(ClosedModel):
    schema_version: Literal["m11-trajectory-state/1"] = "m11-trajectory-state/1"
    checkpoints: tuple[TrajectoryCheckpoint, ...]
    tripwire_ids: tuple[Identifier, ...]
    phase: Literal["active", "paused", "terminated", "completed"]
    next_checkpoint: Annotated[int, Field(ge=1, le=13)]
    carry_source_sha256: Digest | None
    carry_memory_sha256: Digest | None
    invalid_memory_archives: tuple[InvalidMemoryArchive, ...] = ()
    pause_resolutions: tuple[PauseResolution, ...] = ()

    @model_validator(mode="after")
    def complete_lineage(self) -> Self:
        if len(self.checkpoints) != 12 or tuple(c.checkpoint for c in self.checkpoints) != tuple(range(1, 13)):
            raise ValueError("retain exactly twelve prescribed checkpoints in order")
        if len(set(self.tripwire_ids)) != 4 or len(self.tripwire_ids) != 4:
            raise ValueError("exactly four frozen tripwire IDs required")
        first = self.checkpoints[0]
        identity = (first.campaign_id, first.trajectory_id, first.seed_id, first.seed_sha256, first.treatment_id, first.harness_id)
        if len({c.cell_id for c in self.checkpoints}) != 12:
            raise ValueError("checkpoint cell IDs must be unique")
        attempts = [c.attempt_id for c in self.checkpoints if c.attempt_id is not None]
        if len(set(attempts)) != len(attempts):
            raise ValueError("attempt cannot be reused across checkpoints")
        for c in self.checkpoints:
            if (c.campaign_id, c.trajectory_id, c.seed_id, c.seed_sha256, c.treatment_id, c.harness_id) != identity:
                raise ValueError("mixed trajectory lineage")
            if tuple(t.tripwire_id for t in c.tripwires) != self.tripwire_ids:
                raise ValueError("checkpoint must retain all four frozen tripwires")
        for previous, current in zip(self.checkpoints, self.checkpoints[1:]):
            if current.status in ("produced", "paused", "workspace_lost") and (current.source_before_sha256, current.memory_before_sha256) != (previous.source_after_sha256, previous.memory_after_sha256):
                raise ValueError("observed checkpoints must carry the exact previous tree")
        if first.treatment_id == "L0" and self.carry_memory_sha256 is not None:
            raise ValueError("L0 carries no memory")
        if self.phase == "completed":
            if self.next_checkpoint != 13 or any(c.status != "produced" for c in self.checkpoints):
                raise ValueError("completion requires all twelve produced checkpoints")
        elif self.phase == "terminated":
            if self.next_checkpoint > 12 or self.checkpoints[self.next_checkpoint - 1].status != "workspace_lost" or self.carry_source_sha256 is not None or self.carry_memory_sha256 is not None:
                raise ValueError("termination requires infrastructure tree loss")
            for c in self.checkpoints:
                expected = "produced" if c.checkpoint < self.next_checkpoint else "workspace_lost" if c.checkpoint == self.next_checkpoint else "unknown"
                if c.status != expected:
                    raise ValueError("loss must retain earlier output and all remaining unknown slots")
        else:
            if self.next_checkpoint > 12 or self.carry_source_sha256 is None:
                raise ValueError("active/paused trajectory requires a carry tree")
            for c in self.checkpoints:
                expected = "produced" if c.checkpoint < self.next_checkpoint else "planned"
                if self.phase == "paused" and c.checkpoint == self.next_checkpoint:
                    expected = "paused"
                if c.status != expected:
                    raise ValueError("checkpoint state differs from cursor")
        archived = {(a.checkpoint, a.attempt_id) for a in self.invalid_memory_archives}
        if len(archived) != len(self.invalid_memory_archives):
            raise ValueError("duplicate invalid-memory archive")
        if archived != {(c.checkpoint, c.attempt_id) for c in self.checkpoints if c.invalid_memory}:
            raise ValueError("every malformed/invalid memory observation needs its archive")
        if self.phase != "terminated":
            observed_index = self.next_checkpoint - 1 if self.phase == "paused" else self.next_checkpoint - 2
            if observed_index >= 0:
                last = self.checkpoints[observed_index]
                if (self.carry_source_sha256, self.carry_memory_sha256) != (last.source_after_sha256, last.memory_after_sha256):
                    raise ValueError("carry hashes must match the latest preserved artifact")
        resolved = [r.checkpoint for r in self.pause_resolutions]
        if len(set(resolved)) != len(resolved) or any(self.checkpoints[index - 1].status != "produced" for index in resolved):
            raise ValueError("pause receipts must uniquely bind resolved produced checkpoints")
        return self


class CarryRequest(ClosedModel):
    """Controller input requirements, never a process invocation or permission."""

    cell_id: Identifier
    checkpoint: Annotated[int, Field(ge=1, le=12)]
    source_sha256: Digest
    memory_sha256: Digest | None
    fresh_process_required: Literal[True] = True
    fresh_home_required: Literal[True] = True
    hidden_feedback_allowed: Literal[False] = False
    reference_repair_allowed: Literal[False] = False
    future_requests_allowed: Literal[False] = False


class CheckpointOutcome(ClosedModel):
    checkpoint: Annotated[int, Field(ge=1, le=12)]
    attempt_id: Identifier
    kind: Literal["produced", "candidate_error", "evaluator_error", "cleanup_pending", "stop_gate", "workspace_lost"]
    source_before_sha256: Digest
    source_after_sha256: Digest | None
    memory_before_sha256: Digest | None
    memory_after_sha256: Digest | None
    tripwires: tuple[TripwireObservation, ...]
    feature_verdict: Literal["pass", "fail", "unknown"]
    grade_receipt_sha256: Digest | None
    invalid_memory: bool = False
    invalid_memory_archive_sha256: Digest | None = None
    stop_reason: Identifier | None = None

    @model_validator(mode="after")
    def observed_not_invented(self) -> Self:
        if len(self.tripwires) != 4 or len({t.tripwire_id for t in self.tripwires}) != 4:
            raise ValueError("retain exactly four tripwire observations")
        if self.kind != "workspace_lost" and self.source_after_sha256 is None:
            raise ValueError("produced tree must be preserved even on candidate/grader failure")
        if self.kind in ("produced", "candidate_error"):
            if self.grade_receipt_sha256 is None or self.feature_verdict == "unknown" or any(t.verdict == "unknown" for t in self.tripwires):
                raise ValueError("produced grading requires a receipt and complete verdicts")
        if self.kind == "candidate_error" and (self.feature_verdict != "fail" or any(t.verdict != "fail" for t in self.tripwires)):
            raise ValueError("candidate error preventing execution fails feature/tripwires, never missing")
        if self.kind in ("evaluator_error", "workspace_lost") and (self.feature_verdict != "unknown" or any(t.verdict != "unknown" for t in self.tripwires)):
            raise ValueError("trusted evaluator fault/tree loss is unknown, never candidate failure")
        if self.invalid_memory != (self.invalid_memory_archive_sha256 is not None):
            raise ValueError("invalid memory needs an immutable archive digest")
        if self.kind == "stop_gate" and self.stop_reason is None:
            raise ValueError("stop gate needs its explicit reason")
        return self


def _checkpoint(value: TrajectoryCheckpoint, **changes: object) -> TrajectoryCheckpoint:
    payload = value.model_dump(mode="json")
    payload.update(changes)
    # JSON parsing preserves strict tuple/date model semantics and revalidates all fields.
    return TrajectoryCheckpoint.model_validate_json(canonical_json(payload))


def _state(value: TrajectoryState, **changes: object) -> TrajectoryState:
    payload = value.model_dump(mode="json")
    payload.update(changes)
    return TrajectoryState.model_validate_json(canonical_json(payload))


def start_trajectory(
    checkpoints: tuple[TrajectoryCheckpoint, ...],
    *,
    source_sha256: str,
    memory_sha256: str | None,
    tripwire_ids: tuple[str, ...],
) -> TrajectoryState:
    """Bind a frozen twelve-slot plan to original seed/treatment tree hashes."""
    if len(checkpoints) != 12 or any(c.status != "planned" or c.attempt_id is not None for c in checkpoints):
        raise ValueError("a fresh trajectory requires all twelve unstarted prescribed slots")
    if any(c.source_before_sha256 is not None or c.source_after_sha256 is not None or c.memory_before_sha256 is not None or c.memory_after_sha256 is not None or c.invalid_memory for c in checkpoints):
        raise ValueError("fresh planned slots cannot contain invented observations")
    if checkpoints[0].treatment_id != "L0" and memory_sha256 is None:
        raise ValueError("memory arms require the initial treatment artifact")
    unknown = [TripwireObservation(tripwire_id=t, verdict="unknown").model_dump(mode="json") for t in tripwire_ids]
    bound = tuple(_checkpoint(c, tripwires=unknown) for c in checkpoints)
    return TrajectoryState(checkpoints=bound, tripwire_ids=tripwire_ids, phase="active", next_checkpoint=1, carry_source_sha256=source_sha256, carry_memory_sha256=memory_sha256)


def next_carry(state: TrajectoryState) -> CarryRequest:
    """Return exact carry requirements; pause/loss/completion cannot dispatch."""
    if state.phase != "active" or state.carry_source_sha256 is None:
        raise ValueError("trajectory is not eligible for its next checkpoint")
    current = state.checkpoints[state.next_checkpoint - 1]
    return CarryRequest(cell_id=current.cell_id, checkpoint=current.checkpoint, source_sha256=state.carry_source_sha256, memory_sha256=state.carry_memory_sha256)


def apply_outcome(state: TrajectoryState, outcome: CheckpointOutcome) -> TrajectoryState:
    """Carry actual output, including failed candidates and archived bad memory."""
    if state.phase != "active" or outcome.checkpoint != state.next_checkpoint:
        raise ValueError("outcome must belong to the next active checkpoint")
    current = state.checkpoints[state.next_checkpoint - 1]
    if (outcome.source_before_sha256, outcome.memory_before_sha256) != (state.carry_source_sha256, state.carry_memory_sha256):
        raise ValueError("before hashes differ from exact preceding produced tree")
    if tuple(t.tripwire_id for t in outcome.tripwires) != state.tripwire_ids:
        raise ValueError("tripwire mapping differs from frozen plan")
    if current.treatment_id == "L0" and (outcome.memory_before_sha256 is not None or outcome.memory_after_sha256 is not None or outcome.invalid_memory):
        raise ValueError("source-only arm cannot acquire a memory treatment")
    if current.treatment_id == "L1" and outcome.kind != "workspace_lost" and outcome.memory_after_sha256 != outcome.memory_before_sha256 and not outcome.invalid_memory:
        raise ValueError("static-memory modification must remain archived nonadherence")
    if current.treatment_id != "L0" and outcome.memory_after_sha256 is None and outcome.kind != "workspace_lost" and not outcome.invalid_memory:
        raise ValueError("deleted memory must remain archived nonadherence")
    lost = outcome.kind == "workspace_lost"
    paused = outcome.kind in ("cleanup_pending", "evaluator_error", "stop_gate")
    status = "workspace_lost" if lost else "paused" if paused else "produced"
    reason = outcome.stop_reason or (outcome.kind if lost or paused else None)
    updated = _checkpoint(current, attempt_id=outcome.attempt_id, source_before_sha256=outcome.source_before_sha256, source_after_sha256=outcome.source_after_sha256, memory_before_sha256=outcome.memory_before_sha256, memory_after_sha256=outcome.memory_after_sha256, status=status, stop_reason=reason, invalid_memory=outcome.invalid_memory, tripwires=[t.model_dump(mode="json") for t in outcome.tripwires], feature_verdict=outcome.feature_verdict, grade_receipt_sha256=outcome.grade_receipt_sha256)
    checkpoints = list(state.checkpoints)
    checkpoints[state.next_checkpoint - 1] = updated
    archives = list(state.invalid_memory_archives)
    if outcome.invalid_memory:
        archives.append(InvalidMemoryArchive(checkpoint=outcome.checkpoint, attempt_id=outcome.attempt_id, artifact_sha256=outcome.invalid_memory_archive_sha256))
    if lost:
        for index in range(state.next_checkpoint, 12):
            checkpoints[index] = _checkpoint(checkpoints[index], status="unknown", stop_reason="workspace_lost")
    next_index = state.next_checkpoint if paused or lost else state.next_checkpoint + 1
    phase = "terminated" if lost else "paused" if paused else "completed" if next_index == 13 else "active"
    return _state(state, checkpoints=[c.model_dump(mode="json") for c in checkpoints], phase=phase, next_checkpoint=next_index, carry_source_sha256=None if lost else outcome.source_after_sha256, carry_memory_sha256=None if lost else outcome.memory_after_sha256, invalid_memory_archives=[a.model_dump(mode="json") for a in archives])


def resolve_pause(
    state: TrajectoryState,
    *,
    resolution_receipt_sha256: str,
    tripwires: tuple[TripwireObservation, ...],
    feature_verdict: Literal["pass", "fail"],
    grade_receipt_sha256: str,
) -> TrajectoryState:
    """Record externally proven gate resolution/regrading on the SAME artifact.

    Callers must establish cleanup/evaluator/safety clearance externally; this
    metadata transition grants no runtime authority. No tree/hash/attempt argument
    is accepted, so resolution cannot substitute repaired reference output.
    """
    if state.phase != "paused":
        raise ValueError("no paused checkpoint to resolve")
    if tuple(t.tripwire_id for t in tripwires) != state.tripwire_ids or any(t.verdict == "unknown" for t in tripwires):
        raise ValueError("resolution requires all four frozen tripwire verdicts")
    current = state.checkpoints[state.next_checkpoint - 1]
    if current.feature_verdict != "unknown" and current.feature_verdict != feature_verdict:
        raise ValueError("resolution cannot rewrite an observed feature verdict")
    for prior, resolved in zip(current.tripwires, tripwires, strict=True):
        if prior.verdict != "unknown" and prior.verdict != resolved.verdict:
            raise ValueError("resolution cannot rewrite an observed tripwire verdict")
    if current.grade_receipt_sha256 is not None and current.feature_verdict != "unknown":
        if (current.feature_verdict, current.tripwires, current.grade_receipt_sha256) != (feature_verdict, tripwires, grade_receipt_sha256):
            raise ValueError("cleanup/gate resolution cannot rewrite already observed grading")
    updated = _checkpoint(current, status="produced", tripwires=[t.model_dump(mode="json") for t in tripwires], feature_verdict=feature_verdict, grade_receipt_sha256=grade_receipt_sha256)
    checkpoints = list(state.checkpoints)
    checkpoints[state.next_checkpoint - 1] = updated
    receipt = PauseResolution(checkpoint=current.checkpoint, receipt_sha256=resolution_receipt_sha256)
    return _state(state, checkpoints=[c.model_dump(mode="json") for c in checkpoints], phase="completed" if state.next_checkpoint == 12 else "active", next_checkpoint=state.next_checkpoint + 1, pause_resolutions=[r.model_dump(mode="json") for r in (*state.pause_resolutions, receipt)])
