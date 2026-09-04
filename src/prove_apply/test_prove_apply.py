import pathlib

from log_read_item.log_read_item import log_read_item
from prove_apply.prove_apply import prove_apply
from record_run.record_run import record_run
from record_show_item.record_show_item import record_show_item


def _create(kind):
    return record_run(
        [
            "create",
            "x " + kind,
            "-t",
            "task",
            "--no-inherit-labels",
            "-l",
            f"kind:{kind},state:checking",
        ]
    )["id"]


def _labels(item_id):
    names = []
    for label in record_run(["label", "list", item_id]):
        names.append(label if isinstance(label, str) else label.get("name", ""))
    return names


_GOOD_CODE = (
    "def x():\n"
    "    a = 1\n"
    "    b = 2\n"
    "    c = 3\n"
    "    d = 4\n"
    "    e = 5\n"
    "    f = 6\n"
    "    g = 7\n"
    "    h = 8\n"
    "    return a\n"
)

_GOOD_NOTE = "widget\nline two\nline three\nline four\nline five\nline six"


def _base_gathered(**overrides):
    gathered = {
        "folder": "widget",
        "changed": ["src/widget/widget.py", "src/widget/widget.md"],
        "code": _GOOD_CODE,
        "note": _GOOD_NOTE,
        "fmt_out": "",
        "lint_out": "All checks passed!",
        "kind": "code",
        "retries": 0,
        "usage": {"tokens": -1, "seconds": 1.0},
        "pytest_out": "",
        "cases": [],
    }
    gathered.update(overrides)
    return gathered


def test_pass_moves_done(bd_repo, tmp_path):
    item_id = _create("code")
    log_path = str(tmp_path / "log.jsonl")
    gathered = _base_gathered(usage={"tokens": 7, "seconds": 1.0})

    result = prove_apply(item_id, gathered, log_path)

    assert result == "done"
    assert "state:done" in _labels(item_id)
    entries = log_read_item(log_path, item_id)
    built = [e for e in entries if e["gate"] == "Built"]
    assert built
    assert built[0]["tokens"] == 7


def test_fail_bounces(bd_repo, tmp_path):
    item_id = _create("code")
    log_path = str(tmp_path / "log.jsonl")
    gathered = _base_gathered(lint_out="x.py:1:1: E501")

    result = prove_apply(item_id, gathered, log_path)

    assert result == "ready"
    assert "retry:1" in _labels(item_id)
    show = record_show_item(item_id)
    assert show["state"] == "ready"
    row = record_run(["show", item_id])
    row = row[0] if isinstance(row, list) else row
    comments = row.get("comments", [])
    texts = [c.get("text", "") if isinstance(c, dict) else str(c) for c in comments]
    assert any(t.startswith("bounce:") for t in texts)


def test_third_fail_blocks(bd_repo):
    item_id = _create("code")
    log_path = "log.jsonl"
    gathered = _base_gathered(lint_out="x.py:1:1: E501", retries=3)
    pathlib.Path("work/summaries").mkdir(parents=True)

    result = prove_apply(item_id, gathered, log_path)

    assert result == "blocked"
    assert pathlib.Path(f"work/summaries/{item_id}.md").is_file()


def test_test_kind_runs_proven(bd_repo, tmp_path):
    item_id = _create("test")
    log_path = str(tmp_path / "log.jsonl")
    gathered = _base_gathered(
        kind="test",
        pytest_out="FAILED src/x/test_x.py::test_a - AssertionError",
        cases=["a"],
    )

    result = prove_apply(item_id, gathered, log_path)

    assert result == "ready"
    entries = log_read_item(log_path, item_id)
    proven = [e for e in entries if e["gate"] == "Proven"]
    assert proven
    assert "tests_failed" in proven[0]["rule"]
