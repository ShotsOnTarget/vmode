"""Entry point for the Claude Code harness. All logic is in src/claude_invoke."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from claude_invoke.claude_invoke import claude_invoke  # noqa: E402


def invoke(item: dict, column: str) -> dict:
    return claude_invoke(item, column, str(ROOT))
