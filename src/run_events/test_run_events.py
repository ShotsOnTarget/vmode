import pytest

from run_events.run_events import run_events

LINE = (
    '{"ts": "2026-09-07T19:06:06.098000+00:00", "item": "vm-qkxel.7", '
    '"harness": "claude_code", "model": "sonnet", "effort": null, '
    '"role": "builder", "event": {"type": "assistant"}}'
)


def _write(path, text):
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_reads_every_line_in_order(tmp_path):
    lines = [LINE.replace('"assistant"', f'"e{i}"') for i in range(3)]
    path = _write(tmp_path / "t.jsonl", "\n".join(lines) + "\n")

    result = run_events(path)

    assert [r["event"]["type"] for r in result] == ["e0", "e1", "e2"]


def test_a_line_keeps_its_stamped_keys(tmp_path):
    path = _write(tmp_path / "t.jsonl", LINE + "\n")

    result = run_events(path)

    assert result[0] == {
        "ts": "2026-09-07T19:06:06.098000+00:00",
        "item": "vm-qkxel.7",
        "harness": "claude_code",
        "model": "sonnet",
        "effort": None,
        "role": "builder",
        "event": {"type": "assistant"},
    }


def test_a_blank_line_is_skipped(tmp_path):
    path = _write(tmp_path / "t.jsonl", LINE + "\n\n" + LINE + "\n")

    result = run_events(path)

    assert len(result) == 2


def test_a_line_that_is_not_json_is_skipped(tmp_path):
    path = _write(tmp_path / "t.jsonl", LINE + "\nnot json\n" + LINE + "\n")

    result = run_events(path)

    assert len(result) == 2


def test_a_json_line_that_is_not_an_object_is_skipped(tmp_path):
    path = _write(tmp_path / "t.jsonl", LINE + "\n[1, 2]\n" + LINE + "\n")

    result = run_events(path)

    assert len(result) == 2


def test_an_empty_file_gives_an_empty_list(tmp_path):
    path = _write(tmp_path / "t.jsonl", "")

    assert run_events(path) == []


def test_a_missing_file_ends_in_filenotfounderror(tmp_path):
    path = tmp_path / "missing.jsonl"

    with pytest.raises(FileNotFoundError):
        run_events(str(path))
