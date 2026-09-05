"""Invoke adapter that picks the harness per column from roles/board.toml.

A column may carry `adapter = "claude_code"` or `adapter = "opencode"`; the
name is the adapter file in this folder. Without it, claude_code is used.
This keeps the puller free of harness names while letting the Board choose
a cheaper harness for one column at a time.
"""

import importlib.util
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_LOADED = {}


def _adapter(name: str):
    if name not in _LOADED:
        spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _LOADED[name] = module.invoke
    return _LOADED[name]


def invoke(item: dict, column: str) -> dict:
    with open(ROOT / "roles/board.toml", "rb") as f:
        board = tomllib.load(f)
    name = board["columns"][column].get("adapter", "claude_code")
    return _adapter(name)(item, column)
