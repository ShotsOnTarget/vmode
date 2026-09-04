import json
import re
import subprocess

from changed_paths.changed_paths import changed_paths
from record_graph.record_graph import record_graph
from record_run.record_run import RecordError, record_run
from record_show_item.record_show_item import record_show_item


def _read(path: str) -> str:
    try:
        return open(path, encoding="utf-8").read()
    except OSError:
        return ""


def _run(cmd: list, both: bool = False) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.stdout + proc.stderr if both else proc.stdout


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
    info = record_show_item(job_id)
    labels = record_run(["show", job_id])[0].get("labels", [])
    src, base = f"src/{folder}", f"src/{folder}/{folder}"
    return {
        "changed": changed_paths(folder, record_graph()),
        "code": _read(base + ".py"),
        "note": _read(base + ".md"),
        "fmt_out": _run(["ruff", "format", "--check", "--diff", src], True),
        "lint_out": _run(["ruff", "check", src, "--output-format", "concise"]),
        "pytest_out": _run(["python", "-m", "pytest", src, "-q", "-rA"]),
        "cases": re.findall(r"- `test_(\w+)`", info["sheet"]),
        "kind": info["kind"],
        "usage": _usage(job_id),
        "retries": next((int(x[6:]) for x in labels if x.startswith("retry:")), 0),
    }
