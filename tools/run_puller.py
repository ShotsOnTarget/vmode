"""Start one puller. Usage: python tools/run_puller.py <role> <adapter.py or -> [stop_file]

Loads the adapter file's `invoke` by path so the puller code never names a
harness. `-` means no adapter (the supervisor role).
"""

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
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
    passes = puller(role, "roles/board.toml", load_invoke(adapter), stop)
    print(f"{role}: {passes} passes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
