from commit_job.commit_job import commit_job
from log_append.log_append import log_append
from prove_move.prove_move import prove_move
from prove_rules.prove_rules import prove_rules
from step.step import step


def _log_gate(job_id, gate, base):
    log_append({"item": job_id, "gate": gate, "actor": "supervisor", **base})


def prove_apply(job_id: str, gathered: dict) -> str:
    """Compose gate rules, step the state machine, apply the move, and log one line per
    gate that ran.
    """
    rules = prove_rules(gathered)
    event = "gate_pass" if rules == [] else "gate_fail"
    action, state, retries = step("checking", event, gathered["retries"])
    outcome = {"action": action, "state": state, "retries": retries, "rules": rules}
    prove_move(job_id, outcome)
    if action == "log_done":
        commit_job(job_id, gathered["folder"], gathered.get("repo", "."))
    usage = gathered["usage"]
    base = {
        "rule": ",".join(rules) if rules else "pass",
        "inputs": {
            "retries": retries,
            "action": action,
            "harness": usage.get("harness"),
            "model": usage.get("model"),
        },
        "state": state,
        "tokens": int(usage.get("tokens", -1)),
        "seconds": float(usage.get("seconds", 0.0)),
        "usd": usage.get("cost_usd"),
        "turns": usage.get("turns"),
    }
    _log_gate(job_id, "Built", base)
    if gathered["kind"] == "test":
        _log_gate(job_id, "Proven", base)
    return state
