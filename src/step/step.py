TABLE = {
    ("waiting", "needs_done"): ("none", "waiting"),
    ("waiting", "ready_gate_pass"): ("none", "ready"),
    ("ready", "claimed"): ("none", "in_progress"),
    ("in_progress", "claim_timeout"): ("release", "ready"),
    ("checking", "gate_pass"): ("log_done", "done"),
    ("blocked", "sheet_changed"): ("reset", "waiting"),
    ("done", "edited"): ("reopen_checkers", "reopened"),
    ("reopened", "ready_gate_pass"): ("none", "ready"),
}


def step(state: str, event: str, retries: int) -> tuple[str, str, int]:
    """Compute the next policy transition for a work item."""
    if state == "checking" and event == "gate_fail":
        if retries < 3:
            return ("bounce", "ready", retries + 1)
        return ("escalate", "blocked", retries)
    key = (state, event)
    if key not in TABLE:
        raise ValueError(f"no transition for state={state!r} event={event!r}")
    action, next_state = TABLE[key]
    return (action, next_state, 0 if key == ("blocked", "sheet_changed") else retries)
