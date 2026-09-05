"""Invoke adapter for the Claude Code CLI. The one file that names this harness."""

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from adapter_command.adapter_command import adapter_command  # noqa: E402

KEYS = (
    "input_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "output_tokens",
)


def invoke(item: dict, column: str) -> dict:
    roots = {
        "board": ROOT / "roles/board.toml",
        "manifest": ROOT / "roles/manifest.json",
        "root": str(ROOT),
        "mcp": ROOT / "roles/pullers/empty-mcp.json",
    }
    cmd = adapter_command(item, column, roots)
    start = time.time()
    proc = subprocess.run(
        cmd, cwd=ROOT, capture_output=True, text=True, timeout=1800, check=False
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[:500] or "claude exited non-zero")
    out = json.loads(proc.stdout)
    usage = out.get("usage") or {}
    tokens = sum(usage.get(k, 0) for k in KEYS) if usage else -1
    return {
        "tokens": tokens,
        "seconds": time.time() - start,
        "report": out.get("result", ""),
        "cost_usd": out.get("total_cost_usd"),
        "turns": out.get("num_turns"),
    }
