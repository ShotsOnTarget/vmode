import pytest
from scripted_builder.scripted_builder import scripted_builder

from check_folder.check_folder import check_folder
from record_create_item.record_create_item import record_create_item
from record_set_sheet.record_set_sheet import record_set_sheet


def _story():
    intent = record_create_item("intent", "I", "board")
    return record_create_item("story", "S", "architect", intent["id"])["id"]


def _sheet(job_id, story, fn, kind, cases=None):
    lines = [
        "# Instruction sheet",
        "",
        f"- **Job id**: {job_id}",
        f"- **Kind**: {kind}",
        f"- **Parent Story**: {story}",
        f"- **Function name**: `{fn}`",
        f"- **Folder**: `src/{fn}/`",
        "- **Signature**: ",
        "- **Inputs**: ",
        "- **Outputs**: ",
        "- **Checklist items this job serves**: ",
    ]
    if cases is not None:
        lines.append("- **Cases**:")
        lines.extend(f"- `test_{c}`: ok" for c in cases)
    return "\n".join(lines) + "\n"


def _code_job(story, fn="frob"):
    job = record_create_item("code", f"{fn} code", "engineer", story)["id"]
    record_set_sheet(job, _sheet(job, story, fn, "code"))
    return job


def _item(job_id, kind, recipe):
    return {
        "id": job_id,
        "kind": kind,
        "state": "waiting",
        "labels": [f"kind:{kind}", "state:waiting"],
        "last_gate": "",
        "recipe": recipe,
    }


def test_writes_code_and_test_files_cleanly(fake_bd):
    (fake_bd / "pytest.ini").write_text(
        "[pytest]\npythonpath = src\naddopts = --import-mode=importlib\n"
    )
    story = _story()
    code = _code_job(story)
    test = record_create_item("test", "frob test", "engineer", code)["id"]
    record_set_sheet(test, _sheet(test, story, "frob", "test", ["x", "y"]))

    scripted_builder(_item(code, "code", {}), "built")
    scripted_builder(_item(test, "test", {}), "built")

    code_file = fake_bd / "src" / "frob" / "frob.py"
    test_file = fake_bd / "src" / "frob" / "test_frob.py"
    assert code_file.exists()
    assert test_file.exists()
    text = test_file.read_text()
    assert "def test_x" in text
    assert "def test_y" in text
    changed = ["src/frob/frob.py", "src/frob/test_frob.py"]
    assert check_folder("frob", {"changed": changed}) == []


def test_writes_second_folder_for_planted_fault(fake_bd):
    story = _story()
    code = _code_job(story)

    scripted_builder(_item(code, "code", {"fault": "second_folder"}), "built")

    written = [
        str(p.relative_to(fake_bd)) for p in (fake_bd / "src").rglob("*") if p.is_file()
    ]
    outside = [p for p in written if not p.startswith("src/frob/")]
    assert outside
    rules = check_folder("frob", {"changed": [outside[0]]})
    assert "file_outside_folder" in rules


def test_raises_before_writing_for_planted_run_fault(fake_bd):
    story = _story()
    code = _code_job(story)

    with pytest.raises(RuntimeError):
        scripted_builder(_item(code, "code", {"fault": "raise"}), "built")

    assert not (fake_bd / "src").exists()


def test_rejects_unknown_fault_before_writing(fake_bd):
    story = _story()
    code = _code_job(story)

    with pytest.raises(ValueError):
        scripted_builder(_item(code, "code", {"fault": "bogus"}), "built")

    assert not (fake_bd / "src").exists()
