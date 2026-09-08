"""The one check. Usage: python tools/check.py src/<name> [job_id]

Prints the failed rule names, one per line, exactly as the Supervisor's
gates will name them, and exits 1 if there are any. With a job id the
job's kind picks the rules the way prove_rules does: a test job gets the
test-only gate, its own file's shape, format, lint and case names against
the sheet, and no pytest run; a code job runs the tests and is not checked
for cases, because a code sheet names none. Without a job id the kind is
unknown, so only tests_failed is reported from the tests. Same function
the gates call, called the same way: they cannot disagree.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from check_folder.check_folder import check_folder  # noqa: E402
from sheet_cases.sheet_cases import sheet_cases  # noqa: E402


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

            info = record_show_item(argv[2])
            options["kind"] = info["kind"]
            if info["kind"] == "test":
                options["cases"] = sheet_cases(info["sheet"])
    except Exception as exc:  # record not reachable: shape, lint, tests still run
        print(f"(record unavailable: {str(exc)[:80]})", file=sys.stderr)
    rules = check_folder(folder, options)
    for rule in rules:
        print(rule)
    print("clean" if not rules else f"{len(rules)} rule(s) failed")
    return 1 if rules else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
