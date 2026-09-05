"""Start one puller. Usage: python tools/run_puller.py <role> <adapter.py or -> [stop_file]

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


def main(argv: list[str]) -> int:
    role, adapter = argv[1], argv[2]
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
