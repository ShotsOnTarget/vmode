import json

import pytest
from claude_invoke.claude_invoke import claude_invoke

from role_prompt.role_prompt import role_prompt

ROOT = "R"

RESULT = {
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


def _adapter(monkeypatch, argv):
    calls = {}

    def fake(item, column, roots):
        calls["item"] = item
        calls["column"] = column
        return list(argv)

    monkeypatch.setattr("claude_invoke.claude_invoke.adapter_command", fake)
    return calls


def _run(monkeypatch, seconds=12.3, stdout=None, returncode=0, stderr=""):
    calls = {}
    body = stdout if stdout is not None else json.dumps(RESULT)

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


def test_argv_comes_from_adapter_command(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    calls = _run(monkeypatch)
    claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert calls["argv"][0] == "claude"


def test_a_code_item_keeps_the_prompt_it_was_given(monkeypatch):
    argv = ["claude", "-p", "original prompt", "--output-format", "json"]
    _adapter(monkeypatch, argv)
    calls = _run(monkeypatch)
    claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert calls["argv"][2] == "original prompt"


def test_a_non_builder_item_gets_the_role_prompt(monkeypatch):
    argv = ["claude", "-p", "adapter prompt", "--output-format", "json"]
    _adapter(monkeypatch, argv)
    calls = _run(monkeypatch)
    item = {"id": "vm-9", "kind": "story", "role": "engineer"}
    claude_invoke(item, "build", ROOT)
    assert calls["argv"][2] == role_prompt(item, "engineer", ROOT)


def test_effort_is_appended_to_argv(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    calls = _run(monkeypatch)
    item = {"id": "vm-1", "kind": "code", "effort": "high"}
    claude_invoke(item, "build", ROOT)
    assert calls["argv"][-2:] == ["--effort", "high"]


def test_no_effort_leaves_argv_alone(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    calls = _run(monkeypatch)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert "--effort" not in calls["argv"]
    assert result["effort"] is None


def test_tokens_turns_cost_and_report_come_from_the_fold(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert result["tokens"] == 120
    assert result["turns"] == 1
    assert result["cost_usd"] == 0.0222415
    assert result["report"] == "ok"


def test_seconds_comes_from_the_run(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch, seconds=42.5)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert result["seconds"] == 42.5


def test_harness_is_claude_code(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert result["harness"] == "claude_code"


def test_model_is_read_from_argv(monkeypatch):
    argv = ["claude", "-p", "prompt", "--output-format", "json", "--model", "sonnet"]
    _adapter(monkeypatch, argv)
    _run(monkeypatch)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert result["model"] == "sonnet"


def test_model_is_none_without_a_model_flag(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch)
    result = claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
    assert result["model"] is None


def test_the_error_key_is_not_on_the_result(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch)
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
    }


def test_nonzero_returncode_ends_in_runtimeerror(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch, returncode=1, stderr="boom")
    with pytest.raises(RuntimeError, match="boom"):
        claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)


def test_nonzero_returncode_with_no_stderr_says_so(monkeypatch):
    _adapter(monkeypatch, ["claude", "-p", "prompt", "--output-format", "json"])
    _run(monkeypatch, returncode=1, stderr="")
    with pytest.raises(RuntimeError, match="claude exited non-zero"):
        claude_invoke({"id": "vm-1", "kind": "code"}, "build", ROOT)
