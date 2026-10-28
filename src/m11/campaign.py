"""Closed campaign metadata and public exports; construction is runtime-unverified.

These models are separate from harnessrun/1. They contain public manifests and
opaque references, never independent answers, credentials or monetary authority.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, Self

from pydantic import Field, model_validator

from harnessrun import (
    AttemptRecord,
    GradeResult,
    Limitation,
    ModelEvidence,
    UsageObservation,
    ClosedModel,
    canonical_json as canonical_json_bytes,
    sha256_json,
    strict_json,
)

Identifier = Annotated[str, Field(min_length=1, max_length=256)]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Money = Annotated[str, Field(pattern=r"^(0|[1-9][0-9]*)(\.[0-9]+)?$")]
TaskClass = Literal["independent", "decision", "misleading"]
Mode = Literal["SIMULATED", "MEASURED"]


def canonical_json(value: Any) -> str:
    """Explicit text view of shared canonical bytes for SQLite/text files.

    Hashing uses harnessrun.sha256_json directly, not a second algorithm.
    Callers needing bytes use harnessrun.canonical_json.
    """
    return canonical_json_bytes(value).decode("utf-8")


def _unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {label}")


class Pin(ClosedModel):
    role: Literal["code", "image", "cli", "config", "provider", "model", "price", "analysis", "billing_bound", "authorization", "treatment"]
    name: Identifier
    sha256: Digest


class TreatmentBinding(ClosedModel):
    treatment_id: Literal["M0", "M1", "M2", "L0", "L1", "L2"]
    treatment_manifest_sha256: Digest


class AdmissionReference(ClosedModel):
    gate_kind: Literal["P0", "full_pack"]
    gate_id: Identifier
    pack_id: Identifier
    pack_sha256: Digest
    status: Literal["PENDING", "NO-GO", "PASS"]
    receipt_sha256: Digest | None
    evidence_ref: Identifier | None
    scope_item_ids: tuple[Identifier, ...]

    @model_validator(mode="after")
    def receipt_binding(self) -> Self:
        _unique(list(self.scope_item_ids), "admission scope item")
        if self.status == "PASS" and (not self.receipt_sha256 or not self.evidence_ref or not self.scope_item_ids):
            raise ValueError("PASS requires scoped receipt and evidence references; signatures still need external verification")
        return self


class SuiteTask(ClosedModel):
    task_id: Identifier
    task_sha256: Digest
    task_class: TaskClass | None
    split: Literal["dev", "heldout", "diagnostic", "smoke", "probe"]
    opaque_task_id: Identifier

    @model_validator(mode="after")
    def class_binding(self) -> Self:
        if (self.split in ("dev", "heldout")) != (self.task_class is not None):
            raise ValueError("study tasks require a class; diagnostics/smoke/probes have none")
        return self


class SeedCheckpoint(ClosedModel):
    checkpoint: Annotated[int, Field(ge=1, le=12)]
    feature_id: Identifier
    task_id: Identifier
    task_sha256: Digest
    opaque_task_id: Identifier
    reference_sha256: Digest | None
    reference_missing_reason: Identifier | None

    @model_validator(mode="after")
    def reference_binding(self) -> Self:
        if (self.reference_sha256 is None) != (self.reference_missing_reason is not None):
            raise ValueError("checkpoint reference must be hash-bound or explicitly unavailable")
        return self


class SuiteSeed(ClosedModel):
    seed_id: Identifier
    seed_sha256: Digest
    split: Literal["dev", "heldout"]
    tripwire_ids: Annotated[tuple[Identifier, ...], Field(min_length=4, max_length=4)]
    claim_ids: Annotated[tuple[Identifier, ...], Field(min_length=4, max_length=4)]
    checkpoints: tuple[SeedCheckpoint, ...]

    @model_validator(mode="after")
    def complete_chain(self) -> Self:
        if tuple(c.checkpoint for c in self.checkpoints) != tuple(range(1, 13)):
            raise ValueError("seed requires ordered checkpoints 1..12")
        _unique([c.task_id for c in self.checkpoints], "seed execution item")
        _unique([c.feature_id for c in self.checkpoints], "seed feature")
        _unique(list(self.tripwire_ids), "seed tripwire")
        _unique(list(self.claim_ids), "registered claim")
        return self


class SuiteManifest(ClosedModel):
    schema_version: Literal["m11-suite/1"] = "m11-suite/1"
    suite_id: Identifier
    tasks: tuple[SuiteTask, ...]
    seeds: tuple[SuiteSeed, ...]
    admission_refs: tuple[AdmissionReference, ...]

    @model_validator(mode="after")
    def inventory(self) -> Self:
        items = list(self.tasks) + [c for seed in self.seeds for c in seed.checkpoints]
        _unique([t.task_id for t in items], "execution task ID")
        _unique([t.opaque_task_id for t in items], "opaque grading ID")
        _unique([s.seed_id for s in self.seeds], "seed ID")
        _unique([a.gate_id for a in self.admission_refs], "gate ID")
        return self


class Registration(ClosedModel):
    schema_version: Literal["m11-registration/1"] = "m11-registration/1"
    registration_id: Identifier
    campaign_id: Identifier
    mode: Mode
    stage: Literal["A", "B", "C", "D0", "D1", "E"]
    harness_id: Identifier
    suite_sha256: Digest
    treatments: tuple[TreatmentBinding, ...]
    pins: tuple[Pin, ...]
    randomization_seed: Literal[11027] = 11027
    analysis_seed: Literal[11028] = 11028
    heldout_task_count: Literal[36, 48] = 36
    growth_triggered: bool = False
    growth_rule_adopted: Literal[True] = True
    requested_model_id: Identifier | None = None
    schedule_sha256: Digest | None = None
    parent_registration_sha256: Digest | None = None
    amendment_reason: Identifier | None = None
    timeout_seconds: Annotated[int, Field(ge=1)] = 900
    output_cap_bytes: Annotated[int, Field(ge=1)] = 10 * 1024 * 1024
    max_turns: Annotated[int, Field(ge=1)] = 1
    launch_bound_usd: Money | None = None
    ceiling_usd: Literal["40"] = "40"
    authorized_spend_usd: Literal["0"] = "0"
    live_concurrency: Literal[1] = 1
    discipline_label: Literal["M11 experimental structured-memory discipline"] = "M11 experimental structured-memory discipline"

    @model_validator(mode="after")
    def frozen_design(self) -> Self:
        _unique([t.treatment_id for t in self.treatments], "treatment")
        _unique([f"{p.role}:{p.name}" for p in self.pins], "pin")
        expected = {"L0", "L1", "L2"} if self.stage in ("D0", "D1") else {"M0", "M1", "M2"}
        if {t.treatment_id for t in self.treatments} != expected:
            raise ValueError("registration must retain all three experiment arms")
        if self.growth_triggered and self.heldout_task_count != 48:
            raise ValueError("triggered growth cannot silently revert to 36")
        if bool(self.parent_registration_sha256) != bool(self.amendment_reason):
            raise ValueError("prospective amendment needs both parent hash and reason")
        return self


class PlannedCell(ClosedModel):
    schema_version: Literal["m11-cell/1"] = "m11-cell/1"
    cell_id: Identifier
    campaign_id: Identifier
    registration_id: Identifier
    ordinal: Annotated[int, Field(ge=0)]
    task_id: Identifier
    task_sha256: Digest
    task_class: TaskClass | None
    treatment_id: Literal["M0", "M1", "M2", "L0", "L1", "L2"]
    harness_id: Identifier
    repeat: Annotated[int, Field(ge=0)]
    seed_id: Identifier | None = None
    checkpoint: Annotated[int, Field(ge=1, le=12)] | None = None
    opaque_task_id: Identifier
    attempt_id: Identifier | None = None
    disposition: Literal["unstarted", "pass", "fail", "evaluator_error", "infra_excluded", "unknown"] = "unstarted"

    @model_validator(mode="after")
    def checkpoint_pair(self) -> Self:
        if (self.seed_id is None) != (self.checkpoint is None):
            raise ValueError("seed and checkpoint must be bound together")
        if self.seed_id is not None and (self.repeat != 0 or self.task_class is not None):
            raise ValueError("longitudinal cells use repeat 0 and no task class")
        if self.attempt_id is None and self.disposition in ("pass", "fail"):
            raise ValueError("scored outcomes need an actual attempt")
        return self


class ScheduleManifest(ClosedModel):
    schema_version: Literal["m11-schedule/1"] = "m11-schedule/1"
    registration_id: Identifier
    campaign_id: Identifier
    suite_sha256: Digest
    cells: tuple[PlannedCell, ...]

    @model_validator(mode="after")
    def frozen_slots(self) -> Self:
        _unique([c.cell_id for c in self.cells], "cell ID")
        if tuple(c.ordinal for c in self.cells) != tuple(range(len(self.cells))):
            raise ValueError("schedule ordinals must be complete and ordered")
        if any(c.campaign_id != self.campaign_id or c.registration_id != self.registration_id for c in self.cells):
            raise ValueError("cell belongs to another campaign/registration")
        return self


class TripwireObservation(ClosedModel):
    tripwire_id: Identifier
    verdict: Literal["pass", "fail", "unknown"]


class TrajectoryCheckpoint(ClosedModel):
    schema_version: Literal["m11-checkpoint/1"] = "m11-checkpoint/1"
    campaign_id: Identifier
    trajectory_id: Identifier
    seed_id: Identifier
    seed_sha256: Digest
    treatment_id: Literal["L0", "L1", "L2"]
    harness_id: Identifier
    checkpoint: Annotated[int, Field(ge=1, le=12)]
    cell_id: Identifier
    attempt_id: Identifier | None
    source_before_sha256: Digest | None
    source_after_sha256: Digest | None
    memory_before_sha256: Digest | None
    memory_after_sha256: Digest | None
    status: Literal["planned", "produced", "paused", "workspace_lost", "unknown"]
    invalid_memory: bool = False
    stop_reason: Identifier | None = None
    tripwires: tuple[TripwireObservation, ...] = ()
    feature_verdict: Literal["pass", "fail", "unknown"] = "unknown"
    grade_receipt_sha256: Digest | None = None

    @model_validator(mode="after")
    def artifact_observation(self) -> Self:
        _unique([t.tripwire_id for t in self.tripwires], "tripwire ID")
        if self.tripwires and len(self.tripwires) != 4:
            raise ValueError("observed tripwires must retain fixed four-item denominator")
        if self.status == "produced" and (not self.attempt_id or not self.source_before_sha256 or not self.source_after_sha256):
            raise ValueError("produced checkpoint needs actual attempt and both source hashes")
        if self.treatment_id == "L0" and (self.memory_before_sha256 or self.memory_after_sha256):
            raise ValueError("source-only arm has no memory artifact")
        # A prior archived deletion may leave no before-memory. Recovery can
        # create valid memory without falsely labelling the new write invalid.
        if self.status == "produced" and self.treatment_id != "L0" and not self.memory_after_sha256 and not self.invalid_memory:
            raise ValueError("absent produced memory must remain explicit archived nonadherence")
        if self.status in ("workspace_lost", "unknown", "planned") and (self.feature_verdict != "unknown" or any(t.verdict != "unknown" for t in self.tripwires)):
            raise ValueError("unobserved checkpoint cannot fabricate grader outcomes")
        if (self.feature_verdict != "unknown" or any(t.verdict != "unknown" for t in self.tripwires)) and not self.grade_receipt_sha256:
            raise ValueError("observed grading needs its receipt digest")
        return self


class CostObservation(ClosedModel):
    schema_version: Literal["m11-cost/1"] = "m11-cost/1"
    cost_id: Identifier
    kind: Literal["list_price_estimate", "tranche_receipt"]
    scope_id: Identifier
    attempt_id: Identifier | None
    estimated_usd: Money | None
    actual_usd: Money | None
    coverage: Literal["complete", "partial", "unknown"]
    unknown_reason: Identifier | None
    pricetable_sha256: Digest | None
    billing_receipt_sha256: Digest | None
    usage_observation_ids: tuple[Identifier, ...]
    evidence_ref: Identifier
    evidence_sha256: Digest

    @model_validator(mode="after")
    def separated_money(self) -> Self:
        _unique(list(self.usage_observation_ids), "cost usage reference")
        amount = self.estimated_usd if self.kind == "list_price_estimate" else self.actual_usd
        if (amount is None or self.coverage != "complete") and self.unknown_reason is None:
            raise ValueError("unknown/partial cost requires explicit reason")
        if self.kind == "tranche_receipt":
            if self.attempt_id is not None or not self.billing_receipt_sha256 or self.pricetable_sha256 is not None or self.usage_observation_ids or self.estimated_usd is not None:
                raise ValueError("scope-level billing receipt cannot invent per-attempt allocation")
        elif not self.attempt_id or self.billing_receipt_sha256 is not None or self.actual_usd is not None:
            raise ValueError("launch estimate needs attempt; billing receipts remain separate")
        if self.kind == "list_price_estimate" and self.coverage == "complete" and (self.estimated_usd is None or not self.pricetable_sha256):
            raise ValueError("complete estimate needs dated price hash and amount")
        return self


class PublicCheckpoint(ClosedModel):
    """Public observation shape; no expected answer or reference code is embedded."""

    schema_version: Literal["m11-public-checkpoint/1"] = "m11-public-checkpoint/1"
    campaign_id: Identifier
    trajectory_id: Identifier
    seed_id: Identifier
    seed_sha256: Digest
    treatment_id: Literal["L0", "L1", "L2"]
    harness_id: Identifier
    checkpoint: Annotated[int, Field(ge=1, le=12)]
    cell_id: Identifier
    task_id: Identifier
    attempt_id: Identifier | None
    source_before_sha256: Digest | None
    source_after_sha256: Digest | None
    memory_before_sha256: Digest | None
    memory_after_sha256: Digest | None
    status: Literal["planned", "produced", "paused", "workspace_lost", "unknown"]
    tripwire_ids: Annotated[tuple[Identifier, ...], Field(min_length=4, max_length=4)]
    tripwire_outcomes: Annotated[tuple[bool | None, ...], Field(min_length=4, max_length=4)]
    tripwire_missing_reasons: Annotated[tuple[Identifier | None, ...], Field(min_length=4, max_length=4)]
    feature_completed: bool | None
    feature_missing_reason: Identifier | None
    reference_sha256: Digest | None
    reference_missing_reason: Identifier | None
    grade_receipt_sha256: Digest | None
    stop_reason: Identifier | None

    @model_validator(mode="after")
    def public_observation(self) -> Self:
        _unique(list(self.tripwire_ids), "registered tripwire")
        for value, reason in zip(self.tripwire_outcomes, self.tripwire_missing_reasons, strict=True):
            if (value is None) != (reason is not None):
                raise ValueError("tripwire null needs a missing reason; known outcome has none")
        if (self.feature_completed is None) != (self.feature_missing_reason is not None):
            raise ValueError("feature completion null needs missing reason")
        if (self.reference_sha256 is None) != (self.reference_missing_reason is not None):
            raise ValueError("reference binding must be known or explicitly unavailable")
        observed = self.feature_completed is not None or any(v is not None for v in self.tripwire_outcomes)
        if observed and (not self.attempt_id or not self.source_after_sha256 or not self.grade_receipt_sha256):
            raise ValueError("observed checkpoint needs exact attempt/artifact/grading receipt")
        if self.status in ("planned", "unknown", "workspace_lost") and observed:
            raise ValueError("missing checkpoint cannot carry fabricated outcomes")
        if self.treatment_id == "L0" and (self.memory_before_sha256 or self.memory_after_sha256):
            raise ValueError("source-only public checkpoint has no memory artifact")
        return self


class ResultEligibility(ClosedModel):
    """Current source cannot attest independent evidence or authorize release.

    A future appointed verifier and approved runtime phase must supply a new
    explicit decision boundary. Hash-resolved caller assertions are not proof.
    """

    schema_version: Literal["m11-eligibility/1"] = "m11-eligibility/1"
    registration_sha256: Digest
    suite_sha256: Digest
    admission_refs: tuple[AdmissionReference, ...]
    result_release_state: Literal["withheld", "embargoed", "simulated_descriptive"]
    frozen_final_analysis_sha256: Digest | None
    release_receipt_sha256: Digest | None
    release_scope_cell_ids: tuple[Identifier, ...]
    provenance_ref: Identifier | None
    inferential_eligible: Literal[False] = False
    public_release_eligible: Literal[False] = False
    unavailable_reason: Identifier


class PublicExport(ClosedModel):
    schema_version: Literal["m11-export/1"] = "m11-export/1"
    campaign_id: Identifier
    mode: Mode
    experiment_kind: Literal["task", "longitudinal", "calibration", "probe", "system_comparison"]
    registration_sha256: Digest
    suite_sha256: Digest
    registration: Registration
    suite: SuiteManifest
    eligibility: ResultEligibility
    planned_cells: tuple[PlannedCell, ...]
    attempts: tuple[AttemptRecord, ...]
    grades: tuple[GradeResult, ...]
    usage_observations: tuple[UsageObservation, ...]
    model_evidence: tuple[ModelEvidence, ...]
    limitations: tuple[Limitation, ...]
    cost_observations: tuple[CostObservation, ...]
    trajectory_checkpoints: tuple[PublicCheckpoint, ...]

    @model_validator(mode="after")
    def resolved_export(self) -> Self:
        if sha256_json(self.registration) != self.registration_sha256 or sha256_json(self.suite) != self.suite_sha256:
            raise ValueError("registration/suite digest mismatch")
        if self.registration.suite_sha256 != self.suite_sha256 or self.registration.campaign_id != self.campaign_id or self.registration.mode != self.mode:
            raise ValueError("campaign registration binding/mode mismatch")
        expected_kind = {"A": "probe", "B": "calibration", "C": "task", "D0": "longitudinal", "D1": "longitudinal", "E": "system_comparison"}[self.registration.stage]
        if self.experiment_kind != expected_kind:
            raise ValueError("experiment kind differs from frozen campaign stage")
        if (self.eligibility.registration_sha256, self.eligibility.suite_sha256, self.eligibility.admission_refs) != (self.registration_sha256, self.suite_sha256, self.suite.admission_refs):
            raise ValueError("eligibility scope differs from frozen registration/suite")
        if any(ref.status == "PASS" for ref in self.eligibility.admission_refs):
            raise ValueError("source parser cannot authenticate independent PASS; appointed verification is unavailable")
        if self.mode == "SIMULATED" and self.eligibility.result_release_state != "simulated_descriptive":
            raise ValueError("simulation eligibility must stay descriptive")
        if self.mode == "MEASURED" and (self.eligibility.result_release_state == "simulated_descriptive" or self.grades or any(c.feature_completed is not None or any(v is not None for v in c.tripwire_outcomes) for c in self.trajectory_checkpoints)):
            raise ValueError("measured hidden outcomes remain embargoed; release verification is unavailable")
        cells = {c.cell_id: c for c in self.planned_cells}
        _unique(list(self.eligibility.release_scope_cell_ids), "release scope cell")
        if any(ref not in cells for ref in self.eligibility.release_scope_cell_ids):
            raise ValueError("release scope references unknown planned cell")
        attempts = {a.attempt_id: a for a in self.attempts}
        usage = {u.observation_id: u for u in self.usage_observations}
        models = {m.model_evidence_id: m for m in self.model_evidence}
        for records, label in (([c.cell_id for c in self.planned_cells], "cell"), ([a.attempt_id for a in self.attempts], "attempt"), ([u.observation_id for u in self.usage_observations], "usage"), ([m.model_evidence_id for m in self.model_evidence], "model evidence"), ([c.cost_id for c in self.cost_observations], "cost")):
            _unique(records, label)
        schedule = ScheduleManifest(registration_id=self.registration.registration_id, campaign_id=self.campaign_id, suite_sha256=self.suite_sha256, cells=tuple(c.model_copy(update={"attempt_id": None, "disposition": "unstarted"}) for c in self.planned_cells))
        if self.registration.schedule_sha256 is None or sha256_json(schedule) != self.registration.schedule_sha256:
            raise ValueError("planned population/order differs from frozen schedule")
        # Late import keeps pure campaign types upstream of scheduling while
        # rejecting a self-consistently rehashed, truncated population at intake.
        from .schedule import validate_schedule

        validate_schedule(self.registration, self.suite, schedule)
        items = {t.task_id: t for t in self.suite.tasks}
        seed_items = {c.task_id: (s, c) for s in self.suite.seeds for c in s.checkpoints}
        for cell in self.planned_cells:
            item = items.get(cell.task_id)
            seed_item = seed_items.get(cell.task_id)
            if item is None and seed_item is None:
                raise ValueError("cell execution item is absent from suite")
            if seed_item:
                seed, item = seed_item
                if cell.seed_id != seed.seed_id or cell.checkpoint != item.checkpoint:
                    raise ValueError("seed/checkpoint mapping mismatch")
            elif cell.seed_id is not None or cell.task_class != item.task_class:
                raise ValueError("task class/seed mapping mismatch")
            if cell.task_sha256 != item.task_sha256 or cell.opaque_task_id != item.opaque_task_id:
                raise ValueError("cell item/hash/grading mapping mismatch")
            if cell.harness_id != self.registration.harness_id or cell.treatment_id not in {t.treatment_id for t in self.registration.treatments}:
                raise ValueError("cell treatment/system outside frozen registration")
            if cell.attempt_id is not None and (cell.attempt_id not in attempts or attempts[cell.attempt_id].cell_id != cell.cell_id):
                raise ValueError("unresolved cell attempt linkage")
        seen_cells: set[str] = set()
        for attempt in self.attempts:
            if attempt.cell_id not in cells or attempt.campaign_id != self.campaign_id or attempt.mode != self.mode:
                raise ValueError("attempt campaign/cell/mode mismatch")
            if attempt.cell_id in seen_cells:
                raise ValueError("outer replacement/retry of a scheduled cell is prohibited")
            seen_cells.add(attempt.cell_id)
            if cells[attempt.cell_id].attempt_id != attempt.attempt_id:
                raise ValueError("attempt is not linked by its planned cell")
            for ref in (attempt.parent_attempt_id, attempt.retry_of):
                if ref is not None and (ref not in attempts or ref == attempt.attempt_id):
                    raise ValueError("unresolved/self attempt lineage")
            for ref in attempt.usage_observation_ids:
                if ref not in usage or usage[ref].attempt_id != attempt.attempt_id:
                    raise ValueError("unresolved usage reference")
            for ref in attempt.model_evidence_ids:
                if ref not in models or models[ref].attempt_id != attempt.attempt_id:
                    raise ValueError("unresolved model evidence reference")
        grades: dict[str, GradeResult] = {}
        for grade in self.grades:
            if grade.attempt_id in grades or grade.attempt_id not in attempts:
                raise ValueError("duplicate/unresolved grading attempt")
            attempt = attempts[grade.attempt_id]
            if not attempt.artifact_sha256 or grade.artifact_sha256 != attempt.artifact_sha256 or grade.opaque_task_id != cells[attempt.cell_id].opaque_task_id:
                raise ValueError("grade does not bind exact candidate and admitted grading ID")
            grades[grade.attempt_id] = grade
        for cell in self.planned_cells:
            if cell.disposition in ("pass", "fail"):
                grade = grades.get(cell.attempt_id)
                attempt = attempts.get(cell.attempt_id)
                candidate_failure = attempt is not None and attempt.status in ("timeout", "spend_cap", "output_cap", "crash")
                if not (grade and grade.verdict == cell.disposition) and not (cell.disposition == "fail" and candidate_failure):
                    raise ValueError("scored cell lacks matching grading/failure evidence")
        for record in (*self.usage_observations, *self.model_evidence, *self.limitations):
            if record.attempt_id not in attempts:
                raise ValueError("observation/limitation references unknown attempt")
        for cost in self.cost_observations:
            if cost.attempt_id is not None and cost.attempt_id not in attempts:
                raise ValueError("unknown cost attempt")
            for ref in cost.usage_observation_ids:
                if ref not in usage or usage[ref].attempt_id != cost.attempt_id:
                    raise ValueError("cost usage reference mismatch")
            if cost.kind == "list_price_estimate" and cost.coverage == "complete":
                attempt = attempts[cost.attempt_id]
                if attempt.usage_coverage != "complete" or not cost.usage_observation_ids or any(usage[r].coverage != "complete" for r in cost.usage_observation_ids):
                    raise ValueError("complete priced estimate cannot conceal partial/missing usage")
        _unique([f"{c.trajectory_id}:{c.checkpoint}" for c in self.trajectory_checkpoints], "trajectory checkpoint")
        _unique([c.cell_id for c in self.trajectory_checkpoints], "checkpoint cell")
        if {c.cell_id for c in self.trajectory_checkpoints} != {c.cell_id for c in self.planned_cells if c.seed_id is not None}:
            raise ValueError("public checkpoints must retain every planned longitudinal cell, including unknowns")
        trajectory_groups: dict[str, list[PublicCheckpoint]] = {}
        seed_arm_ids: dict[tuple[str, str], str] = {}
        for point in self.trajectory_checkpoints:
            cell = cells.get(point.cell_id)
            if cell is None or point.campaign_id != self.campaign_id or (point.seed_id, point.checkpoint, point.treatment_id, point.harness_id, point.attempt_id, point.task_id) != (cell.seed_id, cell.checkpoint, cell.treatment_id, cell.harness_id, cell.attempt_id, cell.task_id):
                raise ValueError("trajectory checkpoint does not resolve scheduled cell")
            seed = next((s for s in self.suite.seeds if s.seed_id == point.seed_id), None)
            if seed is None or seed.seed_sha256 != point.seed_sha256:
                raise ValueError("trajectory seed digest mismatch")
            if point.attempt_id is not None:
                attempt = attempts[point.attempt_id]
                if point.source_after_sha256 is not None and point.source_after_sha256 != attempt.artifact_sha256:
                    raise ValueError("checkpoint source artifact differs from its exact attempt")
            observed = point.feature_completed is not None or any(v is not None for v in point.tripwire_outcomes)
            if observed or point.grade_receipt_sha256 is not None:
                grade = grades.get(point.attempt_id)
                if grade is None or grade.receipt_sha256 != point.grade_receipt_sha256 or grade.artifact_sha256 != point.source_after_sha256:
                    raise ValueError("checkpoint grading receipt/artifact reference is unresolved or mismatched")
            frozen = seed.checkpoints[point.checkpoint - 1]
            if point.tripwire_ids != seed.tripwire_ids or (point.reference_sha256, point.reference_missing_reason) != (frozen.reference_sha256, frozen.reference_missing_reason):
                raise ValueError("trajectory tripwire/reference mapping differs from frozen seed")
            key = (point.seed_id, point.treatment_id)
            if key in seed_arm_ids and seed_arm_ids[key] != point.trajectory_id:
                raise ValueError("one seed/arm cannot split into alternate trajectories")
            seed_arm_ids[key] = point.trajectory_id
            trajectory_groups.setdefault(point.trajectory_id, []).append(point)
        for points in trajectory_groups.values():
            if tuple(p.checkpoint for p in points) != tuple(range(1, 13)) or len({(p.seed_id, p.treatment_id) for p in points}) != 1:
                raise ValueError("public trajectory must preserve its full twelve-slot chain")
            for previous, current in zip(points, points[1:]):
                if current.status in ("produced", "paused", "workspace_lost") and (current.source_before_sha256, current.memory_before_sha256) != (previous.source_after_sha256, previous.memory_after_sha256):
                    raise ValueError("public trajectory source/memory carry diverges")
        return self


def parse_export(payload: str | bytes | dict[str, Any]) -> PublicExport:
    """Validate closed records and cross-references; no code, grader or I/O runs."""
    raw = canonical_json_bytes(payload) if isinstance(payload, dict) else payload.encode("utf-8") if isinstance(payload, str) else payload
    decoded = strict_json(raw)
    if not isinstance(decoded, dict):
        raise ValueError("public export must be an object")
    # Shared constructors have Python defaults for these literals. Embedded
    # wire records still must state them explicitly, as parse_record requires.
    record_types = {
        "attempts": "AttemptRecord", "grades": "GradeResult",
        "usage_observations": "UsageObservation", "model_evidence": "ModelEvidence",
        "limitations": "Limitation",
    }
    for collection, record_type in record_types.items():
        records = decoded.get(collection)
        if not isinstance(records, list):
            raise ValueError("required shared record array missing")
        for record in records:
            if not isinstance(record, dict) or record.get("schema_version") != "harnessrun/1" or record.get("record_type") != record_type:
                raise ValueError("embedded shared record requires explicit version/type")
    return PublicExport.model_validate_json(canonical_json_bytes(decoded))
