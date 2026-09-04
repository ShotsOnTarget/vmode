import pathlib

from prove_gather.prove_gather import prove_gather

from record_run.record_run import record_run


def _create(title, sheet, extra_labels=None):
    labels = "kind:code,state:in_progress"
    if extra_labels:
        labels = labels + "," + extra_labels
    return record_run(
        [
            "create",
            title,
            "-t",
            "task",
            "--no-inherit-labels",
            "-l",
            labels,
            "-d",
            sheet,
        ]
    )["id"]


def test_gathers_files(bd_repo):
    sheet = "- `test_a`:"
    item_id = _create("x code", sheet)
    folder = pathlib.Path("src") / "x"
    folder.mkdir(parents=True)
    (folder / "x.py").write_text("def x():\n    pass\n")
    (folder / "x.md").write_text("# x\n")

    result = prove_gather(item_id, "x")

    assert result["code"] == "def x():\n    pass\n"
    assert result["note"] == "# x\n"
    assert result["cases"] == ["a"]
    assert result["kind"] == "code"


def test_usage_from_note(bd_repo):
    sheet = "- `test_a`:"
    item_id = _create("x code", sheet)
    record_run(
        ["comment", item_id, 'usage: {"tokens": 5, "seconds": 1.0, "report": "ok"}']
    )

    result = prove_gather(item_id, "x")

    assert result["usage"]["tokens"] == 5


def test_retry_label(bd_repo):
    sheet = "- `test_a`:"
    item_id = _create("x code", sheet)
    record_run(["label", "add", item_id, "retry:2"])

    result = prove_gather(item_id, "x")

    assert result["retries"] == 2


def test_no_usage_default(bd_repo):
    sheet = "- `test_a`:"
    item_id = _create("x code", sheet)

    result = prove_gather(item_id, "x")

    assert result["usage"]["tokens"] == -1
