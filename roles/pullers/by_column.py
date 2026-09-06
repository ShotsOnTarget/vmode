"""Invoke adapter that picks the harness and model per run.

run_settings (src/run_settings) decides: an item label `harness:<name>`,
`model:<provider/model>` or `effort:<level>` wins, then the column's
`adapter` and tier in roles/board.toml (an item `tier` key overrides the
column's, for a run by name), then the manifest's model and effort tables.
The name is the adapter file in this folder. The adapter receives the item
with `harness`, `model` and `effort` set and must use them. This keeps the puller
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

from run_settings.run_settings import run_settings  # noqa: E402

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
    col = board["columns"][column]
    if item.get("tier"):
        col = {**col, "tier": item["tier"]}
    choice = run_settings(item.get("labels", []), col, manifest)
    return _adapter(choice["harness"])({**item, **choice}, column)
