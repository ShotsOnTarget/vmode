import os
import time

from board_config.board_config import board_config
from prove_once.prove_once import prove_once
from pull_once.pull_once import pull_once


def _default_once(role, config_path, invoke):
    if role == "supervisor":
        return prove_once(config_path)
    return pull_once(role, config_path, invoke)


def puller(role: str, config_path: str, invoke, options: dict) -> int:
    """Loop calling once() for a role until a stop file appears."""
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
        time.sleep(interval)
        if os.path.exists(stop_file):
            break
    return passes
