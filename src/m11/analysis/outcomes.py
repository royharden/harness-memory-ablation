"""Resolve canonical planned disposition separately from process and grade state."""


def resolve_cell_outcome(cell: dict, attempt: dict | None, grade: dict | None, codes: set[str]) -> str:
    declared = cell["disposition"]
    missing = {"evaluator_error", "infra_excluded", "unknown"}
    if attempt is None:
        return declared if declared in missing else "unstarted"
    if attempt["status"] in {"pending", "running", "cleanup_pending"}:
        return "unknown"
    if grade and grade["verdict"] == "evaluator_error":
        observed = "evaluator_error"
    elif attempt["status"] in {"timeout", "spend_cap", "output_cap", "crash"} and attempt["started_at"] is not None:
        observed = "fail"
    elif grade and grade["verdict"] in {"pass", "fail"}:
        observed = grade["verdict"]
    elif "infra_excluded" in codes:
        observed = "infra_excluded"
    elif declared in missing:
        observed = declared
    else:
        observed = "unstarted" if attempt["status"] == "refused" else "unknown"
    # Do not favor either side of contradictory recorded evidence. Unstarted/
    # unknown declarations may be stale, but an asserted terminal disposition
    # cannot conceal a conflicting grade or dispatched failure.
    if declared in {"pass", "fail", "evaluator_error", "infra_excluded"} and declared != observed:
        raise ValueError("conflicting planned disposition and outcome evidence")
    return observed
