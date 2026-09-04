import json
import re
import subprocess

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


def prove_gather(job_id: str, folder: str) -> dict:
    info = record_show_item(job_id)
    show = record_run(["show", job_id])[0]
    try:
        comments = record_run(["comments", job_id])
    except RecordError:
        comments = show.get("comments", [])
    usage = {"tokens": -1, "seconds": 0.0, "report": ""}
    for c in reversed(comments):
        if c.get("text", "").startswith("usage:"):
            usage = json.loads(c["text"][len("usage:") :])
            break
    labels = show.get("labels", [])
    retries = next((int(x[6:]) for x in labels if x.startswith("retry:")), 0)
    src, base = f"src/{folder}", f"src/{folder}/{folder}"
    rows = _run(["git", "status", "--porcelain"], True).splitlines()
    changed = [re.sub(r"^.*-> ", "", r[3:].strip()).replace("\\", "/") for r in rows]
    return {
        "changed": changed,
        "code": _read(base + ".py"),
        "note": _read(base + ".md"),
        "fmt_out": _run(["ruff", "format", "--check", "--diff", src], True),
        "lint_out": _run(["ruff", "check", src, "--output-format", "concise"]),
        "pytest_out": _run(["python", "-m", "pytest", src, "-q", "-rA"]),
        "cases": re.findall(r"- `test_(\w+)`", info["sheet"]),
        "kind": info["kind"],
        "usage": usage,
        "retries": retries,
    }
