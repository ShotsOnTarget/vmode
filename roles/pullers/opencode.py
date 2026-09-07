"""Entry point for the opencode harness. All logic is in src/opencode_invoke."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from opencode_invoke.opencode_invoke import opencode_invoke  # noqa: E402


def invoke(item: dict, column: str) -> dict:
    return opencode_invoke(item, column, str(ROOT))
