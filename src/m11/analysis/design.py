"""Complete-design arithmetic, separate from export/admission eligibility.

Only a future canonical eligibility-aware consumer may present these calculations
as research. Source review is not an independent arithmetic worksheet.
"""

from collections import defaultdict
from decimal import Decimal

from .statistics import task_cluster_comparison


CLASSES = {"memory-independent", "decision-dependent", "misleading-memory"}


def calculate_task_statistics(
    cells: list[dict], cost_by_cell: dict[str, Decimal | None], *, mode: str
) -> list[dict]:
    """Calculate a complete fixed task design; costs include all attempts/slot.

    Input is normalized analysis-owned cells with observed disposition, not an
    alternate wire format. Caller filters diagnostics/probes/calibration explicitly
    and proves scope/admission/freeze/result-release eligibility separately.
    This helper cannot validate those proofs or authorize a 48-task growth decision.
    """
    if mode == "SIMULATED":
        return [{"inferential_claim": None, "reason": "simulated_no_inference"}]
    if mode != "MEASURED":
        raise ValueError("explicit provenance mode required")
    by_harness = defaultdict(list)
    seen_cells = set()
    for cell in cells:
        if cell["cell_id"] in seen_cells:
            raise ValueError("duplicate planned cell")
        seen_cells.add(cell["cell_id"])
        by_harness[cell["harness_id"]].append(cell)
    results = []
    for harness, rows in sorted(by_harness.items()):
        tasks = defaultdict(lambda: defaultdict(dict))
        classes = {}
        for row in rows:
            task, arm, repeat = row["task_id"], row["treatment_id"], row["repeat"]
            if row["task_class"] not in CLASSES or arm not in {"M0", "M1", "M2"} or type(repeat) is not int or repeat not in {0, 1, 2}:
                raise ValueError("caller must supply only prescheduled primary task cells")
            if task in classes and classes[task] != row["task_class"]:
                raise ValueError("conflicting task class")
            classes[task] = row["task_class"]
            if repeat in tasks[task][arm]:
                raise ValueError("duplicate semantic task slot")
            tasks[task][arm][repeat] = row
        strata_counts = {name: sum(value == name for value in classes.values()) for name in CLASSES}
        complete_design = set(strata_counts.values()) in ({12}, {16}) and all(
            set(arms) == {"M0", "M1", "M2"} and all(
                set(arms[arm]) == {0, 1, 2} and all(row["disposition"] in {"pass", "fail"} for row in arms[arm].values())
                for arm in ("M0", "M1", "M2")
            ) for arms in tasks.values()
        )
        if not complete_design:
            results.append({"harness_id": harness, "inferential_claim": None, "reason": "incomplete_prespecified_task_design", "tasks_by_class": strata_counts})
            continue
        for left, right, primary in (("M2", "M0", True), ("M2", "M1", False), ("M1", "M0", False)):
            strata = {name: [] for name in sorted(CLASSES)}
            for task, arms in sorted(tasks.items()):
                record = {"task_id": task}
                for side, arm in (("left", left), ("right", right)):
                    record[side] = [arms[arm][repeat]["disposition"] == "pass" for repeat in range(3)]
                    record[side + "_costs"] = [
                        float(cost_by_cell[arms[arm][repeat]["cell_id"]]) if cost_by_cell.get(arms[arm][repeat]["cell_id"]) is not None else None
                        for repeat in range(3)
                    ]
                strata[classes[task]].append(record)
            results.append({
                "harness_id": harness, "left": left, "right": right,
                "primary": primary, "secondary_unadjusted": not primary,
                "population": "complete_prescheduled_task_design",
                "conditional_calculation": True, "requires_external_eligibility": True,
                **task_cluster_comparison(strata),
            })
    return results
