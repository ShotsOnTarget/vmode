import inspect
import json
from datetime import datetime
from pathlib import Path

from transcript_write.transcript_write import transcript_write

CC_EVENT = {
    "type": "assistant",
    "timestamp": "2026-09-07T19:06:06.098Z",
    "message": {
        "content": [{"type": "tool_use", "id": "toolu_01", "name": "Bash", "input": {}}]
    },
}
OC_EVENT = {
    "type": "tool_use",
    "timestamp": 1788798827685,
    "part": {
        "type": "tool",
        "tool": "glob",
        "callID": "call_01",
        "state": {"status": "completed"},
    },
}
META = {
    "item": "vm-qkxel.7",
    "harness": "claude_code",
    "model": "sonnet",
    "effort": None,
    "role": "builder",
}


def _lines(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def test_one_line_per_event(tmp_path):
    path = transcript_write([CC_EVENT, OC_EVENT], META, str(tmp_path))

    with open(path, encoding="utf-8") as f:
        assert len(f.readlines()) == 2


def test_every_line_parses_as_json(tmp_path):
    path = transcript_write([CC_EVENT, OC_EVENT], META, str(tmp_path))

    for line in _lines(path):
        assert isinstance(line, dict)


def test_a_line_carries_the_seven_keys(tmp_path):
    path = transcript_write([CC_EVENT], META, str(tmp_path))

    assert set(_lines(path)[0].keys()) == {
        "ts",
        "item",
        "harness",
        "model",
        "effort",
        "role",
        "event",
    }


def test_the_meta_fields_come_from_meta(tmp_path):
    path = transcript_write([CC_EVENT], META, str(tmp_path))

    line = _lines(path)[0]
    assert line["item"] == META["item"]
    assert line["harness"] == META["harness"]
    assert line["model"] == META["model"]
    assert line["effort"] == META["effort"]
    assert line["role"] == META["role"]


def test_a_meta_key_that_is_missing_reads_as_none(tmp_path):
    meta = {"item": "vm-qkxel.7", "harness": "claude_code"}

    path = transcript_write([CC_EVENT], meta, str(tmp_path))

    line = _lines(path)[0]
    assert line["model"] is None
    assert line["effort"] is None
    assert line["role"] is None


def test_the_harness_event_is_kept_whole(tmp_path):
    path = transcript_write([CC_EVENT, OC_EVENT], META, str(tmp_path))

    lines = _lines(path)
    assert lines[0]["event"] == CC_EVENT
    assert lines[1]["event"] == OC_EVENT


def test_the_timestamp_is_iso_8601_utc(tmp_path):
    path = transcript_write([CC_EVENT], META, str(tmp_path))

    ts = datetime.fromisoformat(_lines(path)[0]["ts"])
    assert ts.tzinfo.utcoffset(ts).total_seconds() == 0


def test_the_file_name_carries_the_item_id(tmp_path):
    path = transcript_write([CC_EVENT], META, str(tmp_path))

    name = path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    assert name.startswith(META["item"])
    assert name.endswith(".jsonl")


def test_a_missing_directory_is_made(tmp_path):
    directory = tmp_path / "missing" / "nested"

    path = transcript_write([CC_EVENT], META, str(directory))

    assert Path(path).exists()


def test_two_runs_of_one_item_leave_two_files(tmp_path):
    first = transcript_write([CC_EVENT], META, str(tmp_path))
    second = transcript_write([OC_EVENT], META, str(tmp_path))

    assert first != second
    assert Path(first).exists()
    assert Path(second).exists()


def test_the_second_run_does_not_overwrite_the_first(tmp_path):
    first = transcript_write([CC_EVENT], META, str(tmp_path))
    transcript_write([OC_EVENT], META, str(tmp_path))

    lines = _lines(first)
    assert len(lines) == 1
    assert lines[0]["event"] == CC_EVENT


def test_no_events_still_leaves_a_file(tmp_path):
    path = transcript_write([], META, str(tmp_path))

    assert Path(path).exists()
    assert _lines(path) == []


def test_an_unwritable_directory_gives_none(tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")

    assert transcript_write([CC_EVENT], META, str(blocker)) is None


def test_the_default_directory_is_outside_the_working_tree():
    default = inspect.signature(transcript_write).parameters["directory"].default
    assert default == "../vmode-runs"
