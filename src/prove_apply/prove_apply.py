import datetime

from log_append.log_append import log_append
from prove_move.prove_move import prove_move
from prove_rules.prove_rules import prove_rules
from step.step import step


def prove_apply(job_id: str, gathered: dict, log_path: str) -> str:
    def _log(base, gate):
        log_append(log_path, {**base, "gate": gate})

    rules = prove_rules(gathered)
    event = "gate_pass" if not rules else "gate_fail"
    action, state, retries = step("checking", event, gathered["retries"])
    outcome = {"action": action, "state": state, "retries": retries, "rules": rules}
    prove_move(job_id, outcome)
    base = {
        "ts": datetime.datetime.now(datetime.UTC).isoformat(),
        "item": job_id,
        "rule": ",".join(rules) if rules else "pass",
        "inputs": {"retries": retries, "action": action},
        "state": state,
        **gathered["usage"],
    }
    _log(base, "Built")
    if gathered["kind"] == "test":
        _log(base, "Proven")
    return state
