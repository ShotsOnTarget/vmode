import os
import time

from board_config.board_config import board_config
from housekeep.housekeep import housekeep
from prove_once.prove_once import prove_once
from pull_once.pull_once import pull_once
from record_graph.record_graph import record_graph
from release_supervisor.release_supervisor import release_supervisor


def _default_once(role, config_path, invoke):
    if role == "supervisor":
        housekeep(".")
        return prove_once(config_path)
    return pull_once(role, config_path, invoke)


def puller(role: str, config_path: str, invoke, options: dict) -> int:
    """Loop calling once() for a role until a stop file appears.

    options: stop_file (required), once (override for tests), worktree (the
    checkout this process runs from). The Supervisor also keeps house each
    pass, and when its worktree is behind HEAD and the board is quiet it
    moves the worktree forward and returns -1 so the runner restarts it.
    """
    config = board_config(config_path)
    intervals = [
        r["poll_seconds"]
        for r in config["columns"].values()
        if r["role"] == role and r["poll_seconds"] > 0
    ]
    if not intervals:
        raise ValueError(f"no polled column for role: {role}")
    interval = min(intervals)
    stop_file = options["stop_file"]
    once = options.get("once") or _default_once
    passes = 0
    while not os.path.exists(stop_file):
        once(role, config_path, invoke)
        passes += 1
        if role == "supervisor" and release_supervisor(
            os.getcwd(), options.get("worktree", ""), record_graph()
        ):
            return -1
        time.sleep(interval)
        if os.path.exists(stop_file):
            break
    return passes
