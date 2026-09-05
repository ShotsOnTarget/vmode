import os

from log_read_item.log_read_item import log_read_item
from prove_apply.prove_apply import prove_apply
from record_run.record_run import record_run
from record_show_item.record_show_item import record_show_item


def _job_repo(tmp_path, folder, code, note, test=None):
    repo = tmp_path / "job_repo"
    repo.mkdir()
    os.system(f'git -C "{repo}" init -q')
    os.system(f'git -C "{repo}" config user.email "builder@example.com"')
    os.system(f'git -C "{repo}" config user.name "Builder"')
    src = repo / "src" / folder
    src.mkdir(parents=True)
    (src / f"{folder}.py").write_text(code)
    (src / f"{folder}.md").write_text(note)
    if test:
        (src / f"test_{folder}.py").write_text(test)
    return str(repo)


def _last_commit_message(repo):
    return os.popen(f'git -C "{repo}" log -1 --pretty=%B').read()


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


def _assignee(item_id):
    row = record_run(["show", item_id])
    row = row[0] if isinstance(row, list) else row
    return row.get("assignee") or ""


_GOOD_CODE = "def widget(x: int) -> int:" + chr(10) + "    return x + 1" + chr(10)

_GOOD_NOTE = "widget\nline two\nline three\nline four\nline five\nline six"


def _base_gathered(tmp_path, **overrides):
    folder = overrides.get("folder", "widget")
    code = overrides.get("code", _GOOD_CODE)
    note = overrides.get("note", _GOOD_NOTE)
    gathered = {
        "folder": folder,
        "changed": [f"src/{folder}/{folder}.py", f"src/{folder}/{folder}.md"],
        "code": code,
        "note": note,
        "fmt_out": "",
        "lint_out": "All checks passed!",
        "kind": "code",
        "retries": 0,
        "usage": {"tokens": -1, "seconds": 1.0},
        "pytest_out": "",
        "cases": [],
        "repo": _job_repo(tmp_path, folder, code, note, overrides.get("test")),
    }
    gathered.update(overrides)
    return gathered


def test_pass_moves_done(bd_repo, tmp_path):
    item_id = _create("code")
    gathered = _base_gathered(tmp_path, usage={"tokens": 7, "seconds": 1.0})

    result = prove_apply(item_id, gathered)

    assert result == "done"
    assert "state:done" in _labels(item_id)
    entries = log_read_item(item_id)
    built = [e for e in entries if e["gate"] == "built"]
    assert built
    assert built[0]["tokens"] == 7
    message = _last_commit_message(gathered["repo"])
    assert item_id in message


def test_fail_bounces(bd_repo, tmp_path):
    item_id = _create("code")
    gathered = _base_gathered(tmp_path, code="import os" + chr(10) + _GOOD_CODE)

    result = prove_apply(item_id, gathered)

    assert result == "ready"
    assert "retry:1" in _labels(item_id)
    show = record_show_item(item_id)
    assert show["state"] == "ready"
    row = record_run(["show", item_id])
    row = row[0] if isinstance(row, list) else row
    comments = row.get("comments", [])
    texts = [c.get("text", "") if isinstance(c, dict) else str(c) for c in comments]
    assert any(t.startswith("bounce:") for t in texts)


def test_third_fail_blocks(bd_repo, tmp_path):
    item_id = _create("code")
    gathered = _base_gathered(
        tmp_path, code="import os" + chr(10) + _GOOD_CODE, retries=3
    )

    result = prove_apply(item_id, gathered)

    assert result == "blocked"
    rows = record_run(["list", "--all"])
    notes = [i for i in rows if i.get("title", "").startswith("escalate:")]
    assert notes


def test_usage_extra_keys_ignored(bd_repo, tmp_path):
    item_id = _create("code")
    gathered = _base_gathered(
        tmp_path,
        usage={"tokens": 5, "seconds": 1.0, "report": "x", "cost_usd": 0.2},
    )

    result = prove_apply(item_id, gathered)

    assert result == "done"
    entries = log_read_item(item_id)
    built = [e for e in entries if e["gate"] == "built"]
    assert built
    assert built[0]["tokens"] == 5
    assert "report" not in built[0]


def test_test_kind_runs_proven(bd_repo, tmp_path):
    item_id = _create("test")
    gathered = _base_gathered(
        tmp_path,
        kind="test",
        test="def test_a():" + chr(10) + "    assert False" + chr(10),
        cases=["a"],
    )

    result = prove_apply(item_id, gathered)

    assert result == "ready"
    entries = log_read_item(item_id)
    proven = [e for e in entries if e["gate"] == "proven"]
    assert proven
    assert "tests_failed" in proven[0]["rule"]


def test_bounce_clears_claim(bd_repo, tmp_path):
    item_id = _create("code")
    record_run(["update", item_id, "--claim", "--actor", "tester"])
    gathered = _base_gathered(tmp_path, code="import os" + chr(10) + _GOOD_CODE)

    result = prove_apply(item_id, gathered)

    assert result == "ready"
    assert _assignee(item_id) == ""
