import json
import os
import subprocess
import sys
from pathlib import Path

from questions_cli.questions_cli import questions_cli

from board_api.board_api import board_api
from record_create_item.record_create_item import record_create_item
from record_run.record_run import record_run


def _question_job():
    iid = record_run(
        [
            "create",
            "epic intent",
            "-t",
            "epic",
            "-l",
            "kind:intent,state:ready,owner:board",
            "-a",
            "board",
            "--no-inherit-labels",
        ]
    )["id"]
    sid = record_run(
        [
            "create",
            "story",
            "-t",
            "epic",
            "-l",
            "kind:story,state:ready,owner:board",
            "-a",
            "board",
            "--no-inherit-labels",
            "--parent",
            iid,
        ]
    )["id"]
    nid = record_create_item("note", "an open question", "architect", parent=sid)["id"]
    return iid, sid, nid


def _run(argv):
    return questions_cli(argv)


def test_prints_one_json_line_per_question(fake_bd, capsys):
    _, _, nid = _question_job()
    code = _run(["0"])
    out = capsys.readouterr().out
    assert code == 0
    lines = [json.loads(line) for line in out.splitlines()]
    assert lines == board_api("open_questions", {"hours": "0"}, {})
    assert any(q["id"] == nid for q in lines)


def test_no_argument_means_zero_hours(fake_bd, capsys):
    _question_job()
    _run([])
    with_arg = capsys.readouterr().out
    _run(["0"])
    zero_arg = capsys.readouterr().out
    assert with_arg == zero_arg


def test_module_runs_from_the_command_line(fake_bd):
    src = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(src)
    env["VMODE_RECORD"] = "fake"
    result = subprocess.run(
        [sys.executable, "-m", "questions_cli.questions_cli", "0"],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    for line in result.stdout.splitlines():
        obj = json.loads(line)
        assert "id" in obj
