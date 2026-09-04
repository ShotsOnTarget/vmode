"""Invoke adapter for the Claude Code CLI. The one file that names this harness.

Usage: pass the `invoke` function to `puller`. Reads the model for the column's
tier from roles/manifest.json and roles/board.toml, runs `claude -p` with the
role skill and the job id, and returns usage in the puller contract shape.
"""

import json
import subprocess
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPT = (
    "You are the {role}. Working directory: {root}. Read roles/{role}/SKILL.md and "
    "follow it exactly. Your work item id is {item}. Fetch it from the record with "
    "the work-record skill (roles/work-record/SKILL.md). Do only that item. "
    "{extra}Report in roles/shared/report-format.md and nothing else."
)
EXTRA = {
    "test": "You write your tests from the sheet; you never create or edit the code file. ",
    "code": "Do not write tests. ",
}


def _model(column: str) -> str | None:
    board = tomllib.loads((ROOT / "roles/board.toml").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "roles/manifest.json").read_text(encoding="utf-8"))
    tier = board["columns"][column]["tier"]
    name = manifest["models"].get(tier)
    return name.split("/")[-1] if name else None


def invoke(item: dict, column: str) -> dict:
    board = tomllib.loads((ROOT / "roles/board.toml").read_text(encoding="utf-8"))
    role = board["columns"][column]["role"]
    prompt = PROMPT.format(
        role=role, root=ROOT, item=item["id"], extra=EXTRA.get(item["kind"], "")
    )
    cmd = ["claude", "-p", prompt, "--output-format", "json"]
    model = _model(column)
    if model:
        cmd += ["--model", model]
    start = time.time()
    proc = subprocess.run(
        cmd, cwd=ROOT, capture_output=True, text=True, timeout=1800, check=False
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[:500] or "claude exited non-zero")
    out = json.loads(proc.stdout)
    usage = out.get("usage") or {}
    fields = (
        "input_tokens",
        "cache_creation_input_tokens",
        "cache_read_input_tokens",
        "output_tokens",
    )
    tokens = sum(usage.get(f, 0) for f in fields) if usage else -1
    return {
        "tokens": tokens,
        "seconds": time.time() - start,
        "report": out.get("result", ""),
        "cost_usd": out.get("total_cost_usd"),
    }
