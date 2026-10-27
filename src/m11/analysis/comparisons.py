"""Descriptive paired task summaries; no inferential or eligibility claims."""

from collections import defaultdict
from statistics import mean


def descriptive_comparisons(cells: list[dict]) -> list[dict]:
    by_harness = defaultdict(list)
    for cell in cells:
        if cell.get("task_class") is not None and cell["treatment_id"] in {"M0", "M1", "M2"}:
            by_harness[cell["harness_id"]].append(cell)
    results = []
    for harness, rows in sorted(by_harness.items()):
        for left, right in (("M2", "M0"), ("M2", "M1"), ("M1", "M0")):
            tasks = defaultdict(lambda: defaultdict(dict))
            classes = {}
            for row in rows:
                task, arm, repeat = row["task_id"], row["treatment_id"], row["repeat"]
                if task in classes and classes[task] != row["task_class"]:
                    raise ValueError("task has conflicting class membership")
                classes[task] = row["task_class"]
                if repeat in tasks[task][arm]:
                    raise ValueError("duplicate semantic task/arm/repeat slot")
                tasks[task][arm][repeat] = row["disposition"]
            paired = []
            available = []
            for task, arms in sorted(tasks.items()):
                if left not in arms or right not in arms:
                    continue
                rates = {}
                for arm in (left, right):
                    observed = [state == "pass" for state in arms[arm].values() if state in {"pass", "fail"}]
                    rates[arm] = {"passes": sum(observed), "observed_repeats": len(observed), "planned_repeats": len(arms[arm]), "value": mean(observed) if observed else None}
                available.append({"task_id": task, "task_class": classes[task], "arms": rates})
                if all(set(arms[arm]) == {0, 1, 2} and all(state in {"pass", "fail"} for state in arms[arm].values()) for arm in ("M0", "M1", "M2")):
                    paired.append({"task_id": task, "task_class": classes[task], "difference": rates[left]["value"] - rates[right]["value"]})
            class_rows = defaultdict(list)
            for row in paired:
                class_rows[row["task_class"]].append(row["difference"])
            results.append({
                "harness_id": harness, "left": left, "right": right,
                "population": "exploratory_complete_all_arm_task_blocks",
                "independent_tasks": len(paired),
                "descriptive_difference": mean(row["difference"] for row in paired) if len(paired) >= 2 else None,
                "reason": None if len(paired) >= 2 else "fewer_than_two_independent_tasks",
                "by_class": {name: {"independent_tasks": len(values), "descriptive_difference": mean(values) if len(values) >= 2 else None} for name, values in sorted(class_rows.items())},
                "paired_tasks": paired, "available_repeat_tasks": available,
                "inferential_claim": None,
            })
    return results
