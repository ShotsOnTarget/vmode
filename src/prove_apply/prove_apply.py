import datetime

from commit_job.commit_job import commit_job
from log_append.log_append import log_append
from prove_move.prove_move import prove_move
from prove_rules.prove_rules import prove_rules
from step.step import step


def prove_apply(job_id: str, gathered: dict, log_path: str) -> str:
    def _log(base, gate):
        log_append(log_path, {**base, "gate": gate})

    rules = prove_rules(gathered)
    event = "gate_pass" if rules == [] else "gate_fail"
    action, state, retries = step("checking", event, gathered["retries"])
    outcome = {"action": action, "state": state, "retries": retries, "rules": rules}
    prove_move(job_id, outcome)
    if action == "log_done":
        commit_job(job_id, gathered["folder"], gathered.get("repo", "."))
    usage = gathered["usage"]
    base = {
        "ts": datetime.datetime.now(datetime.UTC).isoformat(),
        "item": job_id,
        "rule": ",".join(rules) if rules else "pass",
        "inputs": {"retries": retries, "action": action},
        "state": state,
        "tokens": int(usage.get("tokens", -1)),
        "seconds": float(usage.get("seconds", 0.0)),
    }
    _log(base, "Built")
    if gathered["kind"] == "test":
        _log(base, "Proven")
    return state
