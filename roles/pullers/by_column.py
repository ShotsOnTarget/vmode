"""Invoke adapter that picks the harness and model per run.

run_choice (src/run_choice) decides: an item label `harness:<name>` or
`model:<provider/model>` wins, then the column's `adapter` and tier in
roles/board.toml, then the manifest's model table for that harness. The
name is the adapter file in this folder. The adapter receives the item
with `harness` and `model` set and must use them. This keeps the puller
free of harness names while letting the Board, or a role in process, choose
a cheaper harness or model for one column or one item at a time.
"""

import importlib.util
import json
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))

from run_choice.run_choice import run_choice  # noqa: E402

_LOADED = {}


def _adapter(name: str):
    if name not in _LOADED:
        path = HERE / f"{name}.py"
        if not path.exists():
            raise RuntimeError(f"no adapter for harness: {name}")
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _LOADED[name] = module.invoke
    return _LOADED[name]


def invoke(item: dict, column: str) -> dict:
    with open(ROOT / "roles/board.toml", "rb") as f:
        board = tomllib.load(f)
    with open(ROOT / "roles/manifest.json") as f:
        manifest = json.load(f)
    choice = run_choice(item.get("labels", []), board["columns"][column], manifest)
    return _adapter(choice["harness"])({**item, **choice}, column)
