import os
import time

from board_config.board_config import board_config
from housekeep.housekeep import housekeep
from prove_once.prove_once import prove_once
from pull_once.pull_once import pull_once
from puller_pass.puller_pass import puller_pass


def _default_once(role, config_path, invoke):
    if role != "supervisor":
        return pull_once(role, config_path, invoke)
    housekeep(".")
    return prove_once(config_path)


def puller(role: str, config_path: str, invoke, options: dict) -> int:
    """Loop calling once() for a role until the stop file appears.

    options: stop_file (required), once (override for tests), worktree (the
    checkout this process runs from). Returns the pass count, or -1 when the
    Supervisor moved its worktree to HEAD (see puller_pass) and the runner
    must restart it on the new code.
    """
    config = board_config(config_path)
    rows = [r for r in config["columns"].values() if r["role"] == role]
    intervals = [r["poll_seconds"] for r in rows if r["poll_seconds"] > 0]
    if not intervals:
        raise ValueError(f"no polled column for role: {role}")
    once, worktree = options.get("once") or _default_once, options.get("worktree", "")
    passes = 0
    while not os.path.exists(options["stop_file"]):
        if puller_pass(role, lambda: once(role, config_path, invoke), worktree):
            return -1
        passes += 1
        time.sleep(min(intervals))
        if os.path.exists(options["stop_file"]):
            break
    return passes
