import json
import re

from changed_paths.changed_paths import changed_paths
from record_graph.record_graph import record_graph
from record_run.record_run import RecordError, record_run
from record_show_item.record_show_item import record_show_item


def _usage(job_id: str) -> dict:
    try:
        comments = record_run(["comments", job_id])
    except RecordError:
        comments = record_run(["show", job_id])[0].get("comments", [])
    for comment in reversed(comments):
        if comment.get("text", "").startswith("usage:"):
            return json.loads(comment["text"][len("usage:") :])
    return {"tokens": -1, "seconds": 0.0, "report": ""}


def prove_gather(job_id: str, folder: str) -> dict:
    """What the gate needs from the record for one job.

    Returns changed (working-tree paths this job owns), cases (test names
    the sheet requires), kind, usage (from the last usage comment) and
    retries (from the retry label). File contents and tool output are no
    longer gathered here: check_folder reads and runs them.
    """
    info = record_show_item(job_id)
    labels = record_run(["show", job_id])[0].get("labels", [])
    return {
        "changed": changed_paths(folder, record_graph()),
        "cases": re.findall(r"- `test_(\w+)`", info["sheet"]),
        "kind": info["kind"],
        "usage": _usage(job_id),
        "retries": next((int(x[6:]) for x in labels if x.startswith("retry:")), 0),
    }
