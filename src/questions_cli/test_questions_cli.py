import json
import os
import subprocess
import sys
from pathlib import Path

from board_api.board_api import board_api
from questions_cli.questions_cli import questions_cli
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


def _ids(out):
    return [json.loads(line)["id"] for line in out.splitlines()]


def test_prints_one_json_line_per_question(fake_bd, capsys):
    _question_job()
    code = questions_cli(["0"])
    out = capsys.readouterr().out
    assert code == 0
    expected = board_api("open_questions", {"hours": "0"}, {})
    assert _ids(out) == [q["id"] for q in expected]


def test_no_argument_means_zero_hours(fake_bd, capsys):
    _question_job()
    questions_cli([])
    no_arg = _ids(capsys.readouterr().out)
    questions_cli(["0"])
    zero_arg = _ids(capsys.readouterr().out)
    assert no_arg == zero_arg


def test_module_runs_from_the_command_line(fake_bd):
    _question_job()
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
        assert "id" in json.loads(line)
