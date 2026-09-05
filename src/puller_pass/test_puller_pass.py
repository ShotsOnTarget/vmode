import pytest

from puller_pass.puller_pass import puller_pass


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
