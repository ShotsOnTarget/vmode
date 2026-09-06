def summary_lines(job_id: str, outcome: dict, recipient: str) -> list[str]:
    """Return the eight escalation summary lines for a failed gate.

    Inputs:
        job_id: the job's id.
        outcome: a dict with `action` (`bounce` or `escalate`),
            `retries` (int) and `rules` (list of str).
        recipient: the role the summary is for, as `summary_for`
            returns it.

    Outputs:
        Exactly eight lines in order, in the shape of
        roles/shared/summary-format.md.

    Side effects:
        None. Pure. Raises ValueError when `action` is not
        `bounce` or `escalate`.
    """
    action = outcome["action"]
    if action not in ("bounce", "escalate"):
        raise ValueError("action must be bounce or escalate")
    retries = outcome["retries"]
    rules = outcome["rules"]
    return [
        f"- **Work item id**: {job_id}",
        "- **From**: Supervisor",
        f"- **For**: {recipient}",
        "- **What failed**: gate checks did not pass.",
        f"- **How many times**: {retries}",
        f"- **Which rule or gate**: {', '.join(rules)}",
        f"- **What was already tried**: {action}d {retries} time(s).",
        f"- **Decision needed**: {recipient}: split the pair or "
        "rewrite the sheet; if the Story checklist must change, "
        "raise it to the architect.",
    ]
