"""Invoke adapter for the opencode CLI. The one file that names this harness.

Runs `opencode run --format json --pure --dangerously-skip-permissions -m <model>`
with the same builder prompt every harness gets, then folds the JSON event
stream into the invoke contract. The model is item['model'] when the puller
chose one (see run_choice), else the manifest's `opencode_models` at the
column's tier, else opencode's own default.

Usage comes from the `step_finish` events: each carries `tokens` (total,
input, output, reasoning, cache read and write) and `cost` in USD for that
step, so turns is the count of those events. Free models report cost 0; the
tokens are still counted so the runs stay comparable across harnesses.
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


def _steps(events: list[dict]) -> list[dict]:
    return [e.get("part") or {} for e in events if e.get("type") == "step_finish"]


def _tokens(events: list[dict]) -> int:
    """Every token billed over the run: the `total` of each finished step,
    or its parts summed when a step has no total; -1 when no step reported."""
    total, seen = 0, False
    for part in _steps(events):
        block = part.get("tokens")
        if not isinstance(block, dict):
            continue
        seen = True
        if isinstance(block.get("total"), int | float):
            total += int(block["total"])
            continue
        for value in block.values():
            if isinstance(value, int | float):
                total += int(value)
            elif isinstance(value, dict):
                total += sum(int(v) for v in value.values() if isinstance(v, int | float))
    return total if seen else -1


def _cost(events: list[dict]) -> float | None:
    costs = [p["cost"] for p in _steps(events) if isinstance(p.get("cost"), int | float)]
    return round(sum(costs), 6) if costs else None


def _report(events: list[dict]) -> str:
    texts = []
    for event in events:
        part = event.get("part") or {}
        if part.get("type") == "text" and part.get("text"):
            texts.append(part["text"])
        elif event.get("type") == "error":
            texts.append("ERROR: " + json.dumps(event.get("error"))[:500])
    return "\n".join(texts)


def usage(events: list[dict], model: str | None) -> dict:
    """Fold a run's events into the invoke contract's usage (without seconds)."""
    return {
        "tokens": _tokens(events),
        "report": _report(events),
        "cost_usd": _cost(events),
        "turns": len(_steps(events)) or None,
        "harness": "opencode",
        "model": model,
    }


def _model(item: dict, column: str) -> str | None:
    if item.get("model"):
        return item["model"]
    with open(ROOT / "roles/board.toml", "rb") as f:
        board = tomllib.load(f)
    with open(ROOT / "roles/manifest.json") as f:
        manifest = json.load(f)
    tier = board["columns"][column]["tier"]
    return (manifest.get("opencode_models") or {}).get(tier)


def invoke(item: dict, column: str) -> dict:
    exe = shutil.which("opencode")
    if exe is None:
        raise RuntimeError("opencode not found on PATH")
    with open(ROOT / "roles/board.toml", "rb") as f:
        board = tomllib.load(f)
    model = _model(item, column)
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
    return {**usage(events, model), "seconds": time.time() - start}
