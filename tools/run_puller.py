"""Start one puller. Usage: python tools/run_puller.py <role> <adapter.py or -> [stop_file]

Run one role once on one named item, without a column claiming or moving it:
    python tools/run_puller.py <role> <adapter.py> --item <id> [--column <name>] [--tier <tier>]
The usage note is written on the item as a pulled run's would be; the role's
skill sets the item's state. --column names the config column whose adapter
and tier apply (default: the first column of that role, else sheet_todo);
--tier overrides its tier (for example engineer).

Loads the adapter file's `invoke` by path so the puller code never names a
harness. `-` means no adapter (the supervisor role). Run the supervisor from
a worktree at a released commit (see roles/pullers/README.md); when it moves
its worktree forward it restarts itself on the new code.
"""

import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from puller.puller import puller  # noqa: E402


def load_invoke(path: str):
    if path == "-":
        return None
    spec = importlib.util.spec_from_file_location("adapter", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.invoke


def run_item(role: str, adapter: str, args: list[str]) -> int:
    import json
    import tomllib

    from record_add_note.record_add_note import record_add_note
    from record_run.record_run import record_run
    from record_show_item.record_show_item import record_show_item

    opts = dict(zip(args[::2], args[1::2]))
    with open(ROOT / "roles/board.toml", "rb") as f:
        columns = tomllib.load(f)["columns"]
    column = opts.get("--column") or next(
        (n for n, c in columns.items() if c["role"] == role), "sheet_todo"
    )
    item = record_show_item(opts["--item"])
    labels = record_run(["label", "list", item["id"]])
    item["labels"] = [x if isinstance(x, str) else x.get("name", "") for x in labels]
    item["role"] = role
    if opts.get("--tier"):
        item["tier"] = opts["--tier"]
    # Claim for the run, as a puller would: a claimed item is skipped by every
    # gate, so the usage note lands before the Ready gate reads it.
    prior = item["state"]
    record_run(["update", item["id"], "--claim", "--actor", f"{role}-item-{os.getpid()}"])
    try:
        usage = load_invoke(adapter)(item, column)
    finally:
        record_run(["update", item["id"], "-a", ""])
    record_add_note(item["id"], "usage: " + json.dumps(usage))
    if record_show_item(item["id"])["state"] == "in_progress":
        from record_set_state.record_set_state import record_set_state

        record_set_state(item["id"], prior)
    print(json.dumps({k: v for k, v in usage.items() if k != "report"}))
    print(usage.get("report", ""))
    return 0


def main(argv: list[str]) -> int:
    role, adapter = argv[1], argv[2]
    if "--item" in argv:
        return run_item(role, adapter, argv[3:])
    stop = argv[3] if len(argv) > 3 else "work/stop"
    options = {"stop_file": stop, "worktree": str(ROOT)}
    passes = puller(role, "roles/board.toml", load_invoke(adapter), options)
    if passes == -1:
        print(f"{role}: released, restarting on the new commit", flush=True)
        os.execv(sys.executable, [sys.executable, *argv])
    print(f"{role}: {passes} passes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
