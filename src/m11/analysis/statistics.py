"""Pure statistics; source construction only, no independent reference claim."""

from __future__ import annotations

import math
import random
from collections.abc import Mapping, Sequence
from statistics import mean


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> dict:
    if type(total) is not int or type(successes) is not int or not 0 <= successes <= total:
        raise ValueError("invalid binomial counts")
    if total == 0:
        return {"value": None, "interval": None, "reason": "no_observations"}
    p = successes / total
    scale = 1 + z * z / total
    center = (p + z * z / (2 * total)) / scale
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / scale
    return {"value": p, "interval": [max(0.0, center - radius), min(1.0, center + radius)], "reason": None}


def mcnemar_exact(left_only: int, right_only: int) -> float:
    if any(type(n) is not int or n < 0 for n in (left_only, right_only)):
        raise ValueError("discordant counts must be nonnegative integers")
    n = left_only + right_only
    if not n:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(left_only, right_only) + 1)) / 2**n)


def _quantile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    low = math.floor(position)
    high = math.ceil(position)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def task_cluster_comparison(
    strata: Mapping[str, Sequence[Mapping]], *, draws: int = 10000, seed: int = 11028
) -> dict:
    """Rows carry task_id,left/right pass vectors and nullable left/right costs.

    Caller supplies complete paired blocks after admission/freeze/embargo checks.
    Three classes retain equal weight. This helper confers no eligibility itself.
    """
    if set(strata) != {"memory-independent", "decision-dependent", "misleading-memory"}:
        raise ValueError("three preregistered classes required")
    if type(draws) is not int or draws <= 0:
        raise ValueError("positive bootstrap draw count required")
    sizes = {len(rows) for rows in strata.values()}
    if len(sizes) != 1 or not sizes.issubset({12, 16}):
        raise ValueError("complete 12/class or prospectively admitted 16/class required")
    seen = set()
    for rows in strata.values():
        for row in rows:
            if not isinstance(row["task_id"], str) or row["task_id"] in seen:
                raise ValueError("unique task IDs required")
            seen.add(row["task_id"])
            for key in ("left", "right"):
                values = row[key]
                if len(values) != 3 or any(type(v) is not bool for v in values):
                    raise ValueError("three observed boolean outcomes per arm required")
            for key in ("left_costs", "right_costs"):
                values = row[key]
                if len(values) != 3 or any(v is not None and (type(v) not in (int, float) or not math.isfinite(v) or v < 0) for v in values):
                    raise ValueError("three finite nonnegative costs or null required")

    def effect(rows: Sequence[Mapping]) -> float:
        return mean(mean(row["left"]) - mean(row["right"]) for row in rows)

    def economics(rows: Sequence[Mapping]) -> tuple[float | None, str | None]:
        if any(v is None for row in rows for key in ("left_costs", "right_costs") for v in row[key]):
            return None, "unknown_cost"
        left_pass = sum(sum(row["left"]) for row in rows)
        right_pass = sum(sum(row["right"]) for row in rows)
        if not left_pass or not right_pass:
            return None, "undefined_zero_pass"
        left_cost = sum(sum(row["left_costs"]) for row in rows)
        right_cost = sum(sum(row["right_costs"]) for row in rows)
        if right_cost == 0:
            return None, "undefined_zero_cost_denominator"
        return (left_cost / left_pass) / (right_cost / right_pass), None

    classes = sorted(strata)
    flattened = [row for name in classes for row in strata[name]]
    rng = random.Random(seed)
    effects, ratios = [], []
    for _ in range(draws):
        sample = [row for name in classes for row in rng.choices(list(strata[name]), k=len(strata[name]))]
        effects.append(effect(sample))
        ratio, _ = economics(sample)
        if ratio is not None:
            ratios.append(ratio)
    degenerate = min(effects) == max(effects)
    ratio, ratio_reason = economics(flattened)
    undefined = draws - len(ratios)
    ratio_degenerate = bool(ratios) and min(ratios) == max(ratios)
    repeat_zero = [row for row in flattened]
    left_only = sum(row["left"][0] and not row["right"][0] for row in repeat_zero)
    right_only = sum(row["right"][0] and not row["left"][0] for row in repeat_zero)
    return {
        "difference": effect(flattened),
        "by_class": {name: effect(strata[name]) for name in classes},
        "interval": None if degenerate else [_quantile(effects, .025), _quantile(effects, .975)],
        "interval_reason": "degenerate_bootstrap" if degenerate else None,
        "draws": draws, "seed": seed, "independent_tasks": len(flattened),
        "repeat0_left_wilson": wilson(sum(row["left"][0] for row in flattened), len(flattened)),
        "repeat0_right_wilson": wilson(sum(row["right"][0] for row in flattened), len(flattened)),
        "repeat0_mcnemar": mcnemar_exact(left_only, right_only),
        "estimated_cost_ratio": ratio, "cost_ratio_reason": ratio_reason,
        "undefined_ratio_draw_mass": undefined / draws,
        "cost_ratio_interval": None if undefined or ratio_degenerate else [_quantile(ratios, .025), _quantile(ratios, .975)],
        "cost_ratio_interval_reason": "undefined_draws" if undefined else "degenerate_bootstrap" if ratio_degenerate else None,
    }
