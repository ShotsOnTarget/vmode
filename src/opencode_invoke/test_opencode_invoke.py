import json
import pathlib

import pytest

from opencode_invoke.opencode_invoke import opencode_invoke

ROOT = pathlib.Path(__file__).resolve().parents[2]

TEXT_EVENT = {"type": "text", "part": {"type": "text", "text": "ok"}}
TOOL_EVENT = {
    "type": "tool_use",
    "timestamp": 1788798827685,
    "part": {
        "type": "tool",
        "tool": "glob",
        "callID": "call_01",
        "state": {"status": "completed"},
    },
}
FINISH_EVENT = {
    "type": "step_finish",
    "part": {"tokens": {"total": 120}, "cost": 0.25},
}
ERROR_EVENT = {"type": "error", "error": "nope"}

EVENTS = [TEXT_EVENT, TOOL_EVENT, FINISH_EVENT]
OK_STDOUT = "\n".join(json.dumps(e) for e in EVENTS)
ERROR_STDOUT = json.dumps(ERROR_EVENT)
TRANSCRIPT_PATH = "/vmode-runs/vm-x/opencode.json"
CHEAP_MODEL = json.loads((ROOT / "roles" / "manifest.json").read_text())[
    "opencode_models"
]["cheap"]

RESULT_KEYS = {
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


def _patch_all(
    monkeypatch,
    *,
    which_path="/usr/bin/opencode",
    prompt="THE PROMPT",
    stdout=OK_STDOUT,
    stderr="",
    returncode=0,
    seconds=1.5,
    transcript_answer=TRANSCRIPT_PATH,
):
    monkeypatch.setattr(
        "opencode_invoke.opencode_invoke.shutil.which", lambda name: which_path
    )
    monkeypatch.setattr(
        "opencode_invoke.opencode_invoke.role_prompt", lambda *a, **k: prompt
    )

    harness_calls = []

    def fake_harness_run(argv, root, timeout):
        harness_calls.append({"argv": argv, "root": root, "timeout": timeout})
        return {
            "stdout": stdout,
            "stderr": stderr,
            "returncode": returncode,
            "seconds": seconds,
        }

    monkeypatch.setattr("opencode_invoke.opencode_invoke.harness_run", fake_harness_run)

    transcript_calls = []

    def fake_transcript_write(events, meta, directory):
        transcript_calls.append(
            {"events": events, "meta": meta, "directory": directory}
        )
        return transcript_answer

    monkeypatch.setattr(
        "opencode_invoke.opencode_invoke.transcript_write", fake_transcript_write
    )

    return harness_calls, transcript_calls


def _pair_in(argv, first, second):
    return any(argv[i] == first and argv[i + 1] == second for i in range(len(argv) - 1))


def test_missing_executable_ends_in_runtimeerror(monkeypatch):
    _patch_all(monkeypatch, which_path=None)
    with pytest.raises(RuntimeError) as excinfo:
        opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert str(excinfo.value) == "opencode not found on PATH"


def test_argv_starts_with_the_run_flags(monkeypatch):
    calls, _ = _patch_all(monkeypatch)
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
    calls, _ = _patch_all(monkeypatch, prompt="THE PROMPT TEXT")
    opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert calls[0]["argv"][-1] == "THE PROMPT TEXT"


def test_the_items_model_wins(monkeypatch):
    calls, _ = _patch_all(monkeypatch)
    result = opencode_invoke(
        {"id": "vm-x", "kind": "code", "model": "x/y"}, "build", str(ROOT)
    )
    assert _pair_in(calls[0]["argv"], "-m", "x/y")
    assert result["model"] == "x/y"


def test_the_manifest_model_is_used_when_the_item_has_none(monkeypatch):
    calls, _ = _patch_all(monkeypatch)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert result["model"] == CHEAP_MODEL
    assert _pair_in(calls[0]["argv"], "-m", CHEAP_MODEL)


def test_no_model_flag_when_the_tier_has_none(monkeypatch):
    calls, _ = _patch_all(monkeypatch)
    result = opencode_invoke({"id": "vm-x", "kind": "story"}, "story_todo", str(ROOT))
    assert "-m" not in calls[0]["argv"]
    assert result["model"] is None


def test_effort_adds_a_variant_flag(monkeypatch):
    calls, _ = _patch_all(monkeypatch)
    result = opencode_invoke(
        {"id": "vm-x", "kind": "code", "effort": "high"}, "build", str(ROOT)
    )
    assert _pair_in(calls[0]["argv"], "--variant", "high")
    assert result["effort"] == "high"


def test_no_effort_leaves_argv_alone(monkeypatch):
    calls, _ = _patch_all(monkeypatch)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert "--variant" not in calls[0]["argv"]
    assert result["effort"] is None


def test_tokens_turns_cost_and_report_come_from_the_fold(monkeypatch):
    _patch_all(monkeypatch, stdout=OK_STDOUT)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert result["tokens"] == 120
    assert result["turns"] == 1
    assert result["cost_usd"] == 0.25
    assert result["report"] == "ok"


def test_lines_that_are_not_json_are_skipped(monkeypatch):
    stdout = "noise\n" + OK_STDOUT
    _patch_all(monkeypatch, stdout=stdout)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert result["tokens"] == 120
    assert result["report"] == "ok"


def test_seconds_comes_from_the_run(monkeypatch):
    _patch_all(monkeypatch, seconds=42.5)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert result["seconds"] == 42.5


def test_harness_is_opencode(monkeypatch):
    _patch_all(monkeypatch)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert result["harness"] == "opencode"


def test_the_error_key_is_not_on_the_result(monkeypatch):
    _patch_all(monkeypatch)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert set(result.keys()) == RESULT_KEYS


def test_the_transcript_gets_every_event(monkeypatch):
    _, transcript_calls = _patch_all(monkeypatch)
    opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert transcript_calls[0]["events"] == EVENTS


def test_the_transcript_meta_names_the_run(monkeypatch):
    _, transcript_calls = _patch_all(monkeypatch)
    opencode_invoke(
        {"id": "vm-x", "kind": "code", "model": "m1", "effort": "high"},
        "build",
        str(ROOT),
    )
    meta = transcript_calls[0]["meta"]
    assert meta["item"] == "vm-x"
    assert meta["harness"] == "opencode"
    assert meta["model"] == "m1"
    assert meta["effort"] == "high"
    assert meta["role"] == "builder"


def test_the_transcript_directory_is_outside_the_repo(monkeypatch):
    _, transcript_calls = _patch_all(monkeypatch)
    opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert transcript_calls[0]["directory"].endswith("/../vmode-runs")


def test_the_transcript_path_is_on_the_result(monkeypatch):
    _patch_all(monkeypatch, transcript_answer=TRANSCRIPT_PATH)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert result["transcript"] == TRANSCRIPT_PATH


def test_an_unwritable_transcript_does_not_fail_the_run(monkeypatch):
    _patch_all(monkeypatch, transcript_answer=None)
    result = opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert result["transcript"] is None
    assert result["tokens"] == 120
    assert result["turns"] == 1
    assert result["cost_usd"] == 0.25
    assert result["report"] == "ok"
    assert result["harness"] == "opencode"
    assert result["effort"] is None


def test_a_failed_run_still_writes_its_transcript(monkeypatch):
    _, transcript_calls = _patch_all(
        monkeypatch, stdout="", stderr="boom", returncode=1
    )
    with pytest.raises(RuntimeError):
        opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert len(transcript_calls) == 1


def test_nonzero_returncode_ends_in_runtimeerror(monkeypatch):
    _patch_all(monkeypatch, stdout="", stderr="boom", returncode=1)
    with pytest.raises(RuntimeError) as excinfo:
        opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert "boom" in str(excinfo.value)


def test_an_error_event_ends_in_runtimeerror(monkeypatch):
    _patch_all(monkeypatch, stdout=ERROR_STDOUT)
    with pytest.raises(RuntimeError) as excinfo:
        opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert "nope" in str(excinfo.value)


def test_a_failed_run_names_the_error_not_the_prose(monkeypatch):
    prose = {"type": "text", "part": {"type": "text", "text": "I will read the sheet"}}
    stdout = "\n".join(json.dumps(e) for e in (prose, ERROR_EVENT))
    _patch_all(monkeypatch, stdout=stdout)
    with pytest.raises(RuntimeError) as caught:
        opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert str(caught.value).startswith("ERROR:")
    assert "I will read" not in str(caught.value)


def test_a_timed_out_run_says_so(monkeypatch):
    _patch_all(monkeypatch, returncode=-1, stderr="timed out after 1800 seconds\n")
    with pytest.raises(RuntimeError) as caught:
        opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert str(caught.value).startswith("timed out after 1800 seconds")


def test_a_silent_nonzero_exit_names_the_code(monkeypatch):
    _patch_all(monkeypatch, returncode=7, stderr="")
    with pytest.raises(RuntimeError) as caught:
        opencode_invoke({"id": "vm-x", "kind": "code"}, "build", str(ROOT))
    assert str(caught.value) == "opencode exited 7"
