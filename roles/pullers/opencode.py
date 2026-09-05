"""Invoke adapter for the opencode CLI. The one file that names this harness.

Runs `opencode run --format json --pure --dangerously-skip-permissions -m <model>`
with the same builder prompt every harness gets, then folds the JSON event
stream into the invoke contract. The model per tier comes from
roles/manifest.json under "opencode_models" (provider/model as opencode
names it); when the tier has none, opencode's own default is used.
"""

import json
import shutil
import subprocess
import sys
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from builder_prompt.builder_prompt import builder_prompt  # noqa: E402


def _events(stdout: str) -> list[dict]:
    out = []
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def _tokens(events: list[dict]) -> int:
    total, seen = 0, False
    for event in events:
        for key in ("tokens", "usage"):
            block = event.get(key) or (event.get("part") or {}).get(key)
            if isinstance(block, dict):
                seen = True
                for name, value in block.items():
                    if isinstance(value, int | float) and "cost" not in name:
                        total += int(value)
                    elif isinstance(value, dict):
                        total += sum(int(v) for v in value.values() if isinstance(v, int | float))
    return total if seen else -1


def _report(events: list[dict]) -> str:
    texts = []
    for event in events:
        part = event.get("part") or {}
        if part.get("type") == "text" and part.get("text"):
            texts.append(part["text"])
        elif event.get("type") == "error":
            texts.append("ERROR: " + json.dumps(event.get("error"))[:500])
    return "\n".join(texts)


def invoke(item: dict, column: str) -> dict:
    exe = shutil.which("opencode")
    if exe is None:
        raise RuntimeError("opencode not found on PATH")
    with open(ROOT / "roles/board.toml", "rb") as f:
        board = tomllib.load(f)
    with open(ROOT / "roles/manifest.json") as f:
        manifest = json.load(f)
    tier = board["columns"][column]["tier"]
    model = (manifest.get("opencode_models") or {}).get(tier)
    prompt = builder_prompt(item, board["columns"][column]["role"], str(ROOT))
    cmd = [exe, "run", "--format", "json", "--pure", "--dangerously-skip-permissions"]
    if model:
        cmd += ["-m", model]
    cmd.append(prompt)
    start = time.time()
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=1800, check=False)
    events = _events(proc.stdout)
    if proc.returncode != 0 or any(e.get("type") == "error" for e in events):
        raise RuntimeError(_report(events)[:500] or proc.stderr[:500] or "opencode failed")
    return {"tokens": _tokens(events), "seconds": time.time() - start, "report": _report(events)}
