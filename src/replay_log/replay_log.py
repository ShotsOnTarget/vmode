from log_events.log_events import log_events
from step.step import step


def replay_log(item_id: str) -> str:
    """The state an item's events imply, replayed through the step table.

    Starts at waiting with no retries and applies every transition
    log_events derives, so the Analyst can check the recorded state against
    the one the rules would have produced.
    """
    state = "waiting"
    retries = 0
    for from_state, event in log_events(item_id):
        _action, state, retries = step(from_state, event, retries)
    return state
