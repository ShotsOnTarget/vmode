import json

import pytest

from claude_invoke.claude_invoke import claude_invoke
from role_prompt.role_prompt import role_prompt

ROOT = "R"

SYSTEM_EVENT = {"type": "system", "subtype": "init"}
ASSISTANT_EVENT = {
    "type": "assistant",
    "timestamp": "2026-09-07T19:06:06.098Z",
    "message": {
        "content": [{"type": "tool_use", "id": "toolu_01", "name": "Bash", "input": {}}]
    },
}
RESULT_EVENT = {
    "type": "result",
    "subtype": "success",
    "is_error": False,
    "num_turns": 1,
    "total_cost_usd": 0.0222415,
    "result": "ok",
    "usage": {
        "input_tokens": 4,
        "cache_creation_input_tokens": 10,
        "cache_read_input_tokens": 100,
        "output_tokens": 6,
    },
}
STREAM = [SYSTEM_EVENT, ASSISTANT_EVENT, RESULT_EVENT]


def _adapter(monkeypatch, argv):
    def fake(item, column, roots):
        return list(argv)

    monkeypatch.setattr("claude_invoke.claude_invoke.adapter_command", fake)


def _run(monkeypatch, seconds=12.3, stdout=None, returncode=0, stderr=""):
    calls = {}
    body = stdout if stdout is not None else "\n".join(json.dumps(e) for e in STREAM)

    def fake(argv, root, timeout):
        calls["argv"] = argv
        calls["root"] = root
        calls["timeout"] = timeout
        return {
            "stdout": body,
            "stderr": stderr,
            "returncode": returncode,
            "seconds": seconds,
        }

    monkeypatch.setattr("claude_invoke.claude_invoke.harness_run", fake)
    return calls


def _transcript(monkeypatch, path="R/../vmode-runs/vm-1-x.jsonl"):
    calls = {}

    def fake(events, meta, directory):
        calls["events"] = events
        calls["meta"] = meta
        calls["directory"] = directory
        return path

    monkeypatch.setattr("claude_invoke.claude_invoke.transcript_write", fake)
    return calls


def test_argv_comes_from_adapter_command(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    calls = _run(monkeypatch)
    _transcript(monkeypatch)
    claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert calls["argv"][0] == "claude"


def test_the_output_format_is_stream_json(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    calls = _run(monkeypatch)
    _transcript(monkeypatch)
    claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    argv = calls["argv"]
    assert argv[argv.index("--output-format") + 1] == "stream-json"


def test_verbose_is_on_argv(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    calls = _run(monkeypatch)
    _transcript(monkeypatch)
    claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert "--verbose" in calls["argv"]


def test_a_code_item_keeps_the_prompt_it_was_given(monkeypatch):
    _adapter(
        monkeypatch, ["claude", "-p", "original prompt", "--output-format", "json"]
    )
    calls = _run(monkeypatch)
    _transcript(monkeypatch)
    claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert calls["argv"][2] == "original prompt"


def test_a_non_builder_item_gets_the_role_prompt(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "adapter prompt", "--output-format", "json"])
    calls = _run(monkeypatch)
    _transcript(monkeypatch)
    item = {"id": "vm-9", "kind": "story", "role": "engineer"}
    claude_invoke(item, "build", ROOT)
    assert calls["argv"][2] == role_prompt(item, "engineer", ROOT)


def test_effort_is_appended_to_argv(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    calls = _run(monkeypatch)
    _transcript(monkeypatch)
    item = {"id": "vm-1", "kind": "code", "effort": "high"}
    claude_invoke(item, "build", ROOT)
    assert calls["argv"][-2:] == ["--effort", "high"]


def test_no_effort_leaves_argv_alone(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    calls = _run(monkeypatch)
    _transcript(monkeypatch)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert "--effort" not in calls["argv"]
    assert result["effort"] is None


def test_tokens_turns_cost_and_report_come_from_the_fold(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch)
    _transcript(monkeypatch)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert result["tokens"] == 120
    assert result["turns"] == 1
    assert result["cost_usd"] == 0.0222415
    assert result["report"] == "ok"


def test_a_stdout_line_that_is_not_json_is_skipped(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    body = "hello\n" + "\n".join(json.dumps(e) for e in STREAM)
    _run(monkeypatch, stdout=body)
    _transcript(monkeypatch)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert result["tokens"] == 120


def test_seconds_comes_from_the_run(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch, seconds=42.5)
    _transcript(monkeypatch)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert result["seconds"] == 42.5


def test_harness_is_claude_code(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch)
    _transcript(monkeypatch)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert result["harness"] == "claude_code"


def test_model_is_read_from_argv(monkeypatch):
    argv = ["claude", "-p", "prompt", "--output-format", "json", "--model", "sonnet"]
    _adapter(monkeypatch, argv)
    _run(monkeypatch)
    _transcript(monkeypatch)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert result["model"] == "sonnet"


def test_model_is_none_without_a_model_flag(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch)
    _transcript(monkeypatch)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert result["model"] is None


def test_the_error_key_is_not_on_the_result(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch)
    _transcript(monkeypatch)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert set(result.keys()) == {
        "tokens",
        "turns",
        "cost_usd",
        "report",
        "seconds",
        "harness",
        "model",
        "effort",
        "transcript",
    }


def test_the_transcript_gets_every_event(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch)
    calls = _transcript(monkeypatch)
    claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert calls["events"] == STREAM


def test_the_transcript_meta_names_the_run(monkeypatch):
    argv = ["claude", "-p", "prompt", "--output-format", "json", "--model", "sonnet"]
    _adapter(monkeypatch, argv)
    _run(monkeypatch)
    calls = _transcript(monkeypatch)
    item = {"id": "vm-1", "kind": "code", "effort": "high"}
    claude_invoke(item, "build", ROOT)
    assert calls["meta"] == {
        "item": "vm-1",
        "harness": "claude_code",
        "model": "sonnet",
        "effort": "high",
        "role": "builder",
    }


def test_the_transcript_role_is_builder_for_a_code_item(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch)
    calls = _transcript(monkeypatch)
    claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert calls["meta"]["role"] == "builder"


def test_the_transcript_directory_is_outside_the_repo(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch)
    calls = _transcript(monkeypatch)
    claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert calls["directory"] == "R/../vmode-runs"


def test_the_transcript_path_is_on_the_result(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch)
    _transcript(monkeypatch, path="R/../vmode-runs/vm-1-20260101T000000000000.jsonl")
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert result["transcript"] == "R/../vmode-runs/vm-1-20260101T000000000000.jsonl"


def test_an_unwritable_transcript_does_not_fail_the_run(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch)
    _transcript(monkeypatch, path=None)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert result["transcript"] is None
    assert result["tokens"] == 120
    assert result["turns"] == 1
    assert result["cost_usd"] == 0.0222415
    assert result["report"] == "ok"
    assert result["seconds"] == 12.3
    assert result["harness"] == "claude_code"
    assert result["model"] is None
    assert result["effort"] is None


def test_nonzero_returncode_ends_in_runtimeerror(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch, returncode=1, stderr="boom")
    _transcript(monkeypatch)
    with pytest.raises(RuntimeError, match="boom"):
        claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)


def test_nonzero_returncode_with_no_stderr_says_so(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch, returncode=1, stderr="")
    _transcript(monkeypatch)
    with pytest.raises(RuntimeError, match="claude exited non-zero"):
        claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
