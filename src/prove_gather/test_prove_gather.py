import os
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

    assert "code" not in result and "note" not in result
    assert result["cases"] == ["a"]
    assert result["kind"] == "code"


def test_changed_filtered(bd_repo):
    placeholder = pathlib.Path("src") / "placeholder.txt"
    placeholder.parent.mkdir(parents=True, exist_ok=True)
    placeholder.write_text("placeholder\n")
    os.system("git add src")
    os.system('git commit -q -m "seed src"')

    sheet = "- `test_a`:"
    item_id = _create("x code", sheet)
    x_folder = pathlib.Path("src") / "x"
    x_folder.mkdir(parents=True)
    (x_folder / "x.py").write_text("def x():\n    pass\n")
    (x_folder / "x.md").write_text("# x\n")

    _create("y code", sheet)
    y_folder = pathlib.Path("src") / "y"
    y_folder.mkdir(parents=True)
    (y_folder / "y.py").write_text("def y():\n    pass\n")

    outside = pathlib.Path("outside.txt")
    outside.write_text("dirty\n")

    result = prove_gather(item_id, "x")

    assert result["changed"]
    for path in result["changed"]:
        assert path.startswith("src/x/")


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
