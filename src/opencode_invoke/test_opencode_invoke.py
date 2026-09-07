import json
import pathlib

import pytest
from opencode_invoke.opencode_invoke import opencode_invoke

ROOT = pathlib.Path(__file__).resolve().parents[2]

TEXT_EVENT = json.dumps({"type": "text", "part": {"type": "text", "text": "ok"}})
FINISH_EVENT = json.dumps(
    {"type": "step_finish", "part": {"tokens": {"total": 120}, "cost": 0.25}}
)
OK_STDOUT = TEXT_EVENT + "\n" + FINISH_EVENT
ERROR_EVENT = json.dumps({"type": "error", "error": "nope"})


def _patch_which(monkeypatch, path="/usr/bin/opencode"):
    monkeypatch.setattr(
        "opencode_invoke.opencode_invoke.shutil.which", lambda name: path
    )


def _patch_prompt(monkeypatch, text="THE PROMPT"):
    monkeypatch.setattr(
        "opencode_invoke.opencode_invoke.role_prompt", lambda *a, **k: text
    )


def _patch_harness(monkeypatch, stdout=OK_STDOUT, stderr="", returncode=0, seconds=1.5):
    calls = []

    def fake_harness_run(argv, root, timeout):
        calls.append({"argv": argv, "root": root, "timeout": timeout})
        return {
            "stdout": stdout,
            "stderr": stderr,
            "returncode": returncode,
            "seconds": seconds,
        }

    monkeypatch.setattr("opencode_invoke.opencode_invoke.harness_run", fake_harness_run)
    return calls


def _pair_in(argv, first, second):
    return any(argv[i] == first and argv[i + 1] == second for i in range(len(argv) - 1))


def test_missing_executable_ends_in_runtimeerror(monkeypatch):
    monkeypatch.setattr(
        "opencode_invoke.opencode_invoke.shutil.which", lambda name: None
    )
    with pytest.raises(RuntimeError) as excinfo:
        opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert str(excinfo.value) == "opencode not found on PATH"


def test_argv_starts_with_the_run_flags(monkeypatch):
    _patch_which(monkeypatch)
    _patch_prompt(monkeypatch)
    calls = _patch_harness(monkeypatch)
    opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    argv = calls[0]["argv"]
    assert argv[0] == "/usr/bin/opencode"
    assert argv[1:6] == [
        "run",
        "--format",
        "json",
        "--pure",
        "--dangerously-skip-permissions",
    ]


def test_the_prompt_is_the_last_argument(monkeypatch):
    _patch_which(monkeypatch)
    _patch_prompt(monkeypatch, "THE PROMPT TEXT")
    calls = _patch_harness(monkeypatch)
    opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert calls[0]["argv"][-1] == "THE PROMPT TEXT"


def test_the_items_model_wins(monkeypatch):
    _patch_which(monkeypatch)
    _patch_prompt(monkeypatch)
    calls = _patch_harness(monkeypatch)
    result = opencode_invoke(
        {"id": "vm-x", "kind": "code", "model": "x/y"}, "build", str(ROOT)
    )
    assert _pair_in(calls[0]["argv"], "-m", "x/y")
    assert result["model"] == "x/y"


def test_the_manifest_model_is_used_when_the_item_has_none(monkeypatch):
    _patch_which(monkeypatch)
    _patch_prompt(monkeypatch)
    _patch_harness(monkeypatch)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert result["model"] == "opencode/muse-spark-1.3-contributor-free"


def test_no_model_flag_when_the_tier_has_none(monkeypatch):
    _patch_which(monkeypatch)
    _patch_prompt(monkeypatch)
    calls = _patch_harness(monkeypatch)
    result = opencode_invoke({"id": "vm-x", "kind": "story"}, "story_todo", str(ROOT))
    assert "-m" not in calls[0]["argv"]
    assert result["model"] is None


def test_effort_adds_a_variant_flag(monkeypatch):
    _patch_which(monkeypatch)
    _patch_prompt(monkeypatch)
    calls = _patch_harness(monkeypatch)
    result = opencode_invoke(
        {"id": "vm-x", "kind": "code", "effort": "high"}, "build", str(ROOT)
    )
    assert _pair_in(calls[0]["argv"], "--variant", "high")
    assert result["effort"] == "high"


def test_no_effort_leaves_argv_alone(monkeypatch):
    _patch_which(monkeypatch)
    _patch_prompt(monkeypatch)
    calls = _patch_harness(monkeypatch)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert "--variant" not in calls[0]["argv"]
    assert result["effort"] is None


def test_tokens_turns_cost_and_report_come_from_the_fold(monkeypatch):
    _patch_which(monkeypatch)
    _patch_prompt(monkeypatch)
    _patch_harness(monkeypatch, stdout=OK_STDOUT)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert result["tokens"] == 120
    assert result["turns"] == 1
    assert result["cost_usd"] == 0.25
    assert result["report"] == "ok"


def test_lines_that_are_not_json_are_skipped(monkeypatch):
    _patch_which(monkeypatch)
    _patch_prompt(monkeypatch)
    stdout = "starting opencode\n" + OK_STDOUT
    _patch_harness(monkeypatch, stdout=stdout)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert result["tokens"] == 120
    assert result["report"] == "ok"


def test_seconds_comes_from_the_run(monkeypatch):
    _patch_which(monkeypatch)
    _patch_prompt(monkeypatch)
    _patch_harness(monkeypatch, seconds=42.5)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert result["seconds"] == 42.5


def test_harness_is_opencode(monkeypatch):
    _patch_which(monkeypatch)
    _patch_prompt(monkeypatch)
    _patch_harness(monkeypatch)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert result["harness"] == "opencode"


def test_the_error_key_is_not_on_the_result(monkeypatch):
    _patch_which(monkeypatch)
    _patch_prompt(monkeypatch)
    _patch_harness(monkeypatch)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
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
    _patch_which(monkeypatch)
    _patch_prompt(monkeypatch)
    _patch_harness(monkeypatch, stdout="", stderr="boom", returncode=1)
    with pytest.raises(RuntimeError) as excinfo:
        opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert "boom" in str(excinfo.value)


def test_an_error_event_ends_in_runtimeerror(monkeypatch):
    _patch_which(monkeypatch)
    _patch_prompt(monkeypatch)
    _patch_harness(monkeypatch, stdout=ERROR_EVENT)
    with pytest.raises(RuntimeError) as excinfo:
        opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert "nope" in str(excinfo.value)
