"""Frozen full-population schedules; pure construction, never dispatch.

Algorithm m11-balanced-blocks/1 sorts inputs, shuffles task/repeat blocks with
Random(11027), then cycles the six permutations of three sorted arms.  Seed
trajectories are shuffled as whole blocks and keep checkpoints in order.
"""

from collections import Counter
from collections.abc import Iterable, Mapping
from itertools import permutations
from random import Random

from .campaign import (
    PlannedCell,
    Registration,
    ScheduleManifest,
    SuiteManifest,
    sha256_json,
)

ALGORITHM = "m11-balanced-blocks/1"
LIVE_CONCURRENCY = 1
_CLASSES = {"independent", "decision", "misleading"}


def _check_inputs(registration: Registration, suite: SuiteManifest) -> tuple[str, ...]:
    if registration.suite_sha256 != sha256_json(suite):
        raise ValueError("suite digest differs from registration")
    if registration.randomization_seed != 11027 or registration.analysis_seed != 11028:
        raise ValueError("fixed randomization/analysis seeds required")
    if registration.heldout_task_count not in (36, 48):
        raise ValueError("held-out task count must be 36 or 48")
    if registration.growth_triggered != (registration.heldout_task_count == 48):
        raise ValueError("growth trigger and held-out task count disagree")
    arms = tuple(sorted(t.treatment_id for t in registration.treatments))
    if len(arms) != 3 or len(set(arms)) != 3:
        raise ValueError("exactly three distinct treatment arms required")
    task_ids = [t.task_id for t in suite.tasks]
    seed_ids = [s.seed_id for s in suite.seeds]
    if len(task_ids) != len(set(task_ids)) or len(seed_ids) != len(set(seed_ids)):
        raise ValueError("duplicate task or seed identity")
    return arms


def _tasks(suite: SuiteManifest, split: str, count: int, balanced: bool = False):
    tasks = sorted((t for t in suite.tasks if t.split == split), key=lambda t: t.task_id)
    if len(tasks) != count:
        raise ValueError(f"{split} requires exactly {count} tasks")
    if balanced and Counter(t.task_class for t in tasks) != Counter(
        {kind: count // 3 for kind in _CLASSES}
    ):
        raise ValueError(f"{split} requires equal independent/decision/misleading classes")
    return tasks


def build_schedule(registration: Registration, suite: SuiteManifest) -> ScheduleManifest:
    """Construct every planned cell; caps never truncate a stage population."""
    arms = _check_inputs(registration, suite)
    rng = Random(registration.randomization_seed)
    orders = tuple(permutations(arms))
    cells: list[PlannedCell] = []
    block_index = 0

    def add(task, arm: str, repeat: int, seed_id=None, checkpoint=None):
        ordinal = len(cells)
        identity = {
            "algorithm": ALGORITHM,
            "campaign_id": registration.campaign_id,
            "registration_id": registration.registration_id,
            "ordinal": ordinal,
            "task_id": task.task_id,
            "task_sha256": task.task_sha256,
            "treatment_id": arm,
            "repeat": repeat,
            "seed_id": seed_id,
            "checkpoint": checkpoint,
        }
        cells.append(PlannedCell(
            cell_id="cell-" + sha256_json(identity),
            campaign_id=registration.campaign_id,
            registration_id=registration.registration_id,
            ordinal=ordinal,
            task_id=task.task_id,
            task_sha256=task.task_sha256,
            task_class=getattr(task, "task_class", None),
            treatment_id=arm,
            harness_id=registration.harness_id,
            repeat=repeat,
            seed_id=seed_id,
            checkpoint=checkpoint,
            opaque_task_id=task.opaque_task_id,
        ))

    def task_blocks(tasks, repeats: int):
        nonlocal block_index
        blocks = [(task, repeat) for task in tasks for repeat in range(repeats)]
        rng.shuffle(blocks)
        for task, repeat in blocks:
            for arm in orders[block_index % len(orders)]:
                add(task, arm, repeat)
            block_index += 1

    def canaries():
        nonlocal block_index
        smoke = _tasks(suite, "smoke", 3)
        rng.shuffle(smoke)
        for task, arm in zip(smoke, arms, strict=True):
            add(task, arm, 0)
        task_blocks(_tasks(suite, "probe", 3), 1)

    stage = registration.stage
    if stage in ("A", "E"):
        canaries()
    if stage == "B":
        task_blocks(_tasks(suite, "dev", 18, balanced=True), 2)
    elif stage in ("C", "E"):
        task_blocks(_tasks(suite, "heldout", registration.heldout_task_count, balanced=True), 3)
        task_blocks(_tasks(suite, "diagnostic", 4), 1)
    elif stage in ("D0", "D1"):
        split, count = ("dev", 2) if stage == "D0" else ("heldout", 4)
        seeds = sorted((s for s in suite.seeds if s.split == split), key=lambda s: s.seed_id)
        if len(seeds) != count:
            raise ValueError(f"{stage} requires exactly {count} seeds")
        rng.shuffle(seeds)
        for seed in seeds:
            checkpoints = sorted(seed.checkpoints, key=lambda c: c.checkpoint)
            if [c.checkpoint for c in checkpoints] != list(range(1, 13)):
                raise ValueError("each seed requires unique checkpoints 1..12")
            # Interleave arms at each checkpoint, retaining each trajectory's order.
            for checkpoint in checkpoints:
                for arm in orders[block_index % len(orders)]:
                    add(checkpoint, arm, 0, seed.seed_id, checkpoint.checkpoint)
                block_index += 1
    elif stage != "A":
        raise ValueError("unknown campaign stage")
    expected = {"A": 12, "B": 108, "C": registration.heldout_task_count * 9 + 12,
                "D0": 72, "D1": 144, "E": registration.heldout_task_count * 9 + 24}[stage]
    if len(cells) != expected:
        raise ValueError("full stage population was not constructed")
    return ScheduleManifest(
        registration_id=registration.registration_id,
        campaign_id=registration.campaign_id,
        suite_sha256=registration.suite_sha256,
        cells=tuple(cells),
    )


def validate_schedule(registration: Registration, suite: SuiteManifest,
                      schedule: ScheduleManifest) -> None:
    """Check frozen population/order/pins without regenerating any schedule IDs."""
    arms = _check_inputs(registration, suite)
    if not registration.schedule_sha256:
        raise ValueError("registration has no frozen schedule checksum")
    if sha256_json(schedule) != registration.schedule_sha256:
        raise ValueError("frozen schedule checksum mismatch")
    if (schedule.registration_id != registration.registration_id
            or schedule.campaign_id != registration.campaign_id
            or schedule.suite_sha256 != registration.suite_sha256):
        raise ValueError("schedule identity differs from registration")
    expected = Counter()
    tasks = {t.task_id: t for t in suite.tasks}
    seeds = {s.seed_id: s for s in suite.seeds}
    stage = registration.stage
    if stage in ("A", "E"):
        smoke = _tasks(suite, "smoke", 3)
        smoke_cells = [c for c in schedule.cells if c.task_id in {t.task_id for t in smoke}]
        if (Counter(c.task_id for c in smoke_cells) != Counter(t.task_id for t in smoke)
                or Counter(c.treatment_id for c in smoke_cells) != Counter(arms)):
            raise ValueError("smoke cells must cover three tasks and three arms once")
        for cell in smoke_cells:
            expected[(cell.task_id, cell.treatment_id, 0, None, None)] += 1
        for task in _tasks(suite, "probe", 3):
            for arm in arms:
                expected[(task.task_id, arm, 0, None, None)] += 1
    task_groups = []
    if stage == "B":
        task_groups.append((_tasks(suite, "dev", 18, True), 2))
    if stage in ("C", "E"):
        task_groups.extend([(_tasks(suite, "heldout", registration.heldout_task_count, True), 3),
                            (_tasks(suite, "diagnostic", 4), 1)])
    for group, repeats in task_groups:
        for task in group:
            for arm in arms:
                for repeat in range(repeats):
                    expected[(task.task_id, arm, repeat, None, None)] += 1
    if stage in ("D0", "D1"):
        split, count = ("dev", 2) if stage == "D0" else ("heldout", 4)
        selected = [s for s in suite.seeds if s.split == split]
        if len(selected) != count:
            raise ValueError("wrong longitudinal seed population")
        for seed in selected:
            for checkpoint in seed.checkpoints:
                for arm in arms:
                    expected[(checkpoint.task_id, arm, 0, seed.seed_id, checkpoint.checkpoint)] += 1
    actual = Counter((c.task_id, c.treatment_id, c.repeat, c.seed_id, c.checkpoint) for c in schedule.cells)
    if actual != expected:
        raise ValueError("schedule lost, duplicated or changed fixed-design cells")
    last_checkpoint = {}
    for cell in schedule.cells:
        task = tasks.get(cell.task_id) if cell.seed_id is None else next(
            (c for c in seeds[cell.seed_id].checkpoints if c.checkpoint == cell.checkpoint), None)
        if (task is None or task.task_sha256 != cell.task_sha256
                or task.opaque_task_id != cell.opaque_task_id
                or getattr(task, "task_class", None) != cell.task_class
                or cell.harness_id != registration.harness_id
                or cell.attempt_id is not None or cell.disposition != "unstarted"):
            raise ValueError("cell differs from frozen public task mapping")
        if cell.seed_id is not None:
            key = (cell.seed_id, cell.treatment_id)
            if cell.checkpoint != last_checkpoint.get(key, 0) + 1:
                raise ValueError("longitudinal schedule changed checkpoint order")
            last_checkpoint[key] = cell.checkpoint


def remaining_cells(registration: Registration, suite: SuiteManifest,
                    schedule: ScheduleManifest,
                    attempts: Iterable[Mapping[str, object]]) -> tuple[PlannedCell, ...]:
    """Return original unattempted rows; ambiguous lifecycle blocks all replay.

    Rows are store.list_dispatches() lifecycle mappings (state, not raw result
    status), under the controller's exclusive serial lease. Include every claim
    in the active controller scope, not only completed result records. This pure
    helper cannot acquire that lease or authorize execution.
    Every durable attempt consumes its cell, even failed/excluded attempts.
    """
    validate_schedule(registration, suite, schedule)
    by_id = {cell.cell_id: cell for cell in schedule.cells}
    consumed: set[str] = set()
    attempt_ids: set[str] = set()
    terminal = {"finished"}
    for row in attempts:
        cell_id, attempt_id, state = row.get("cell_id"), row.get("attempt_id"), row.get("state")
        if not isinstance(cell_id, str) or cell_id not in by_id:
            raise ValueError("attempt references an unknown frozen cell")
        if not isinstance(attempt_id, str) or not attempt_id or attempt_id in attempt_ids:
            raise ValueError("missing or duplicate durable attempt identity")
        if cell_id in consumed:
            raise ValueError("multiple attempts for one cell; outer retry is forbidden")
        cell = by_id[cell_id]
        for key in ("campaign_id", "registration_id", "task_sha256", "treatment_id", "harness_id"):
            if key in row and row[key] != getattr(cell, key):
                raise ValueError(f"attempt changed frozen {key}")
        if not isinstance(state, str) or state not in terminal:
            raise ValueError("nonterminal/ambiguous attempt blocks resume, including cleanup_pending")
        consumed.add(cell_id)
        attempt_ids.add(attempt_id)
    return tuple(cell for cell in schedule.cells if cell.cell_id not in consumed)


resume_schedule = remaining_cells
