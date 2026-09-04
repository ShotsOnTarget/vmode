from log_events.log_events import log_events
from step.step import step


def replay_log(path: str, item_id: str) -> str:
    state = "waiting"
    retries = 0
    for from_state, event in log_events(path, item_id):
        _action, state, retries = step(from_state, event, retries)
    return state
