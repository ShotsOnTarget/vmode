from last_gate.last_gate import last_gate
from record_add_note.record_add_note import record_add_note
from record_run.record_run import record_run


def _job():
    labels = "kind:code,state:ready"
    return record_run(["create", "J", "-l", labels, "--no-inherit-labels"])["id"]


def test_no_comments_is_empty(fake_bd):
    assert last_gate(_job()) == ""


def test_a_bounce_is_returned(fake_bd):
    job = _job()
    record_add_note(job, "usage: {}")
    record_add_note(job, "bounce: case_missing,case_extra")
    assert last_gate(job) == "bounce: case_missing,case_extra"


def test_a_ready_failure_is_returned(fake_bd):
    job = _job()
    record_add_note(job, "ready: sheet_exists_without_change")
    assert last_gate(job) == "ready: sheet_exists_without_change"


def test_a_release_is_returned(fake_bd):
    job = _job()
    record_add_note(job, "release: timed out after 1800 seconds")
    assert last_gate(job) == "release: timed out after 1800 seconds"


def test_a_finished_run_after_the_gate_ends_the_search_empty(fake_bd):
    job = _job()
    record_add_note(job, "bounce: lint_findings")
    record_add_note(job, "usage: {}")
    assert last_gate(job) == ""


def test_the_newest_gate_word_wins(fake_bd):
    job = _job()
    record_add_note(job, "bounce: lint_findings")
    record_add_note(job, "Story cut into 2 pairs")
    record_add_note(job, "bounce: over_80_lines")
    assert last_gate(job) == "bounce: over_80_lines"
