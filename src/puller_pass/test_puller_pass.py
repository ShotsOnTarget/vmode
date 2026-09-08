import pytest

from puller_pass.puller_pass import puller_pass
from record_run.record_run import RecordError


def test_clean_pass_no_release(monkeypatch):
    monkeypatch.setattr("puller_pass.puller_pass.release_supervisor", lambda *a: False)
    monkeypatch.setattr("puller_pass.puller_pass.record_graph", lambda: {})
    assert puller_pass("supervisor", lambda: None, "C:/wt") is False


def test_config_error_releases(monkeypatch):
    monkeypatch.setattr("puller_pass.puller_pass.release_supervisor", lambda *a: True)
    monkeypatch.setattr("puller_pass.puller_pass.record_graph", lambda: {})

    def broken():
        raise ValueError("patterns: kinds: must be a non-empty list of allowed kinds")

    assert puller_pass("supervisor", broken, "C:/wt") is True


def test_error_propagates_when_no_release(monkeypatch):
    monkeypatch.setattr("puller_pass.puller_pass.release_supervisor", lambda *a: False)
    monkeypatch.setattr("puller_pass.puller_pass.record_graph", lambda: {})

    def broken():
        raise ValueError("bad")

    with pytest.raises(ValueError):
        puller_pass("supervisor", broken, "C:/wt")


def test_builder_never_releases():
    assert puller_pass("builder", lambda: None, "") is False


def test_record_error_ends_the_pass_without_killing_the_puller():
    """A record hiccup must not take the Supervisor, and every gate, with it.

    Seen 2026-09-08: the Supervisor died on one `bd exited non-zero` while
    removing a label. Nothing gated anything afterwards, and the only sign
    was a smoke run stalling half an hour later.
    """

    def run():
        raise RecordError("bd exited non-zero", "")

    assert puller_pass("supervisor", run, "") is False


def test_record_error_prints_what_the_record_said(capsys):
    def run():
        raise RecordError(
            "failed to run bd", "[WinError 206] The filename or extension is too long"
        )

    puller_pass("builder", run, "")
    assert "WinError 206" in capsys.readouterr().out
