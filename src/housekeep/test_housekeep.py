import subprocess

from housekeep.housekeep import housekeep
from record_graph.record_graph import record_graph
from record_run.record_run import record_run


def _item(title, labels, parent=None, assignee=None):
    args = ["create", title, "-t", "task", "-l", labels, "--no-inherit-labels"]
    if parent:
        args += ["--parent", parent]
    if assignee:
        args += ["-a", assignee]
    return record_run(args)["id"]


def test_dead_claim_released(fake_bd):
    subprocess.run(["git", "init", "-q"], check=True)
    job = _item("w code", "kind:code,state:in_progress", assignee="builder-99999")
    result = housekeep(".")
    assert job in result["released"]
    assert record_graph()[job]["state"] == "ready"


def test_leftover_raised_once(fake_bd):
    subprocess.run(["git", "init", "-q"], check=True)
    intent = _item("I", "kind:intent,state:done")
    job = _item("w code", "kind:code,state:done", parent=intent)
    (fake_bd / "src" / "w").mkdir(parents=True)
    (fake_bd / "src" / "w" / "w.py").write_text("def w():\n    pass\n")
    first = housekeep(".")
    second = housekeep(".")
    notes = [
        i
        for i in record_graph().values()
        if i["kind"] == "note"
        and i["parent"] == job
        and i["title"].startswith("leftover")
    ]
    assert len(first["notes"]) >= 1 and second["notes"] == []
    assert len(notes) == 1
