import re
import time
from pathlib import Path

from board_config.board_config import board_config
from column_of.column_of import column_of
from count_written.count_written import count_written
from record_graph.record_graph import record_graph
from record_labels.record_labels import record_labels
from record_run.record_run import record_run
from story_status.story_status import story_status
from timeline.timeline import timeline

_ROOT = Path(__file__).resolve().parents[2]
_CONFIG = board_config(str(_ROOT / "roles" / "board.toml"))
_POLL = 0.1


def _passing(status: dict) -> bool:
    if status["state"] != "checking" or any(
        job["state"] != "done" for job in status["jobs"]
    ):
        return False
    seen = 0
    wanted = ("ready", "built", "proven")
    for run in status["runs"]:
        if run["gate"] == wanted[seen]:
            seen += 1
            if seen == 3:
                return True
    return False


def _version(story_id: str) -> int | None:
    criteria = record_run(["show", story_id])[0].get("acceptance_criteria", "")
    match = re.search(r"run count is (\d+)", criteria)
    return int(match.group(1)) if match else None


def _bounces(story_id: str, graph: dict) -> int:
    return sum(
        1
        for event in timeline(story_id, graph)
        if (event.get("inputs") or {}).get("action") == "bounce"
    )


def _stall(status: dict, graph: dict, labels: dict) -> dict:
    item = next(
        (graph[job["id"]] for job in status["jobs"] if job["state"] != "done"),
        graph[status["id"]],
    )
    column = column_of(item, labels.get(item["id"], []), _CONFIG)
    return {"column": column, "id": item["id"], "state": item["state"]}


def smoke_judge(story_id: str, timeout_seconds: float) -> dict:
    """Judge a smoke run from the record and the log.

    Inputs: story_id, the smoke Story to observe; timeout_seconds, the max
    wall-clock wait. Outputs: on pass, the run-count version and the bounce
    count; when the count written is not the one asked for, both; on
    timeout, the stall's column, item id and state. No gate reads the count
    itself, so a run writing any value with a test agreeing to it passes
    them all: it is read back here. Side effects: polls the record to the
    timeout; raises ValueError when story_id is not a Story.
    """
    deadline = time.monotonic() + timeout_seconds
    while True:
        graph = record_graph()
        status = story_status(story_id, graph, record_labels())
        if _passing(status):
            asked, wrote = _version(story_id), count_written()
            if asked != wrote:
                return {"result": "fail", "count": {"asked": asked, "wrote": wrote}}
            bounces = _bounces(story_id, graph)
            return {"result": "pass", "version": asked, "bounces": bounces}
        if time.monotonic() >= deadline:
            return {"result": "fail", "stall": _stall(status, graph, record_labels())}
        time.sleep(_POLL)
