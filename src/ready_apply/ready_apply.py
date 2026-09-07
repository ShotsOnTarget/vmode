from log_append.log_append import log_append
from record_add_note.record_add_note import record_add_note
from record_run.record_run import record_run
from record_set_state.record_set_state import record_set_state


def ready_apply(story_id: str, rules: list[str], gathered: dict) -> str:
    """Apply the Ready gate outcome to the record.

    Args:
        story_id: The Story item id.
        rules: The list `gate_ready` returned; empty means pass.
        gathered: The dict `ready_gather` returned with graph, jobs, usage.

    Returns:
        The new Story state: 'ready' when rules is empty, 'reopened' otherwise.

    Side effects:
        Writes the record: on a pass, sets each job under the Story to
        'ready' only when its state in gathered['graph'] is 'waiting', and
        sets the Story to 'ready'. On failure sets the Story to 'reopened',
        removes the 'cut' label and adds a note, leaving job states as they
        are. Either way appends exactly one ready gate event.
    """
    usage = gathered["usage"]
    graph = gathered["graph"]
    jobs = gathered["jobs"]
    pairs = sum(1 for j in jobs if graph.get(j, {}).get("kind") == "code")
    if not rules:
        for job_id in jobs:
            if graph.get(job_id, {}).get("state") == "waiting":
                record_set_state(job_id, "ready")
        record_set_state(story_id, "ready")
        state = "ready"
        rule = "pass"
    else:
        record_set_state(story_id, "reopened")
        record_run(["label", "remove", story_id, "cut"])
        record_add_note(story_id, "ready: " + ",".join(rules))
        state = "reopened"
        rule = ",".join(rules)
    log_append(
        {
            "item": story_id,
            "gate": "ready",
            "rule": rule,
            "inputs": {
                "pairs": pairs,
                "harness": usage.get("harness"),
                "model": usage.get("model"),
                "effort": usage.get("effort"),
            },
            "state": state,
            "tokens": int(usage.get("tokens", -1)),
            "seconds": float(usage.get("seconds", 0.0)),
            "usd": usage.get("cost_usd"),
            "turns": usage.get("turns"),
            "actor": "supervisor",
        }
    )
    return state
