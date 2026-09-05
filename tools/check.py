"""The one check. Usage: python tools/check.py src/<name> [job_id]

Prints the failed rule names, one per line, exactly as the Supervisor's
gates will name them, and exits 1 if there are any. With a job id the
sheet's cases are checked too; without one only tests_failed is reported
from the tests. Same function the gates call: they cannot disagree.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from check_folder.check_folder import check_folder  # noqa: E402


def main(argv: list[str]) -> int:
    folder = Path(argv[1]).name
    options = {}
    try:
        from changed_paths.changed_paths import changed_paths
        from record_graph.record_graph import record_graph

        graph = record_graph()
        options["changed"] = changed_paths(folder, graph)
        if len(argv) > 2:
            from record_show_item.record_show_item import record_show_item

            sheet = record_show_item(argv[2])["sheet"]
            options["cases"] = re.findall(r"- `test_(\w+)`", sheet)
    except Exception as exc:  # record not reachable: shape, lint, tests still run
        print(f"(record unavailable: {str(exc)[:80]})", file=sys.stderr)
    rules = check_folder(folder, options)
    for rule in rules:
        print(rule)
    print("clean" if not rules else f"{len(rules)} rule(s) failed")
    return 1 if rules else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
