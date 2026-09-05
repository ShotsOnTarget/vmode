from puller_pids.puller_pids import puller_pids


def test_returns_set_of_digit_strings():
    pids = puller_pids()
    assert isinstance(pids, set)
    assert all(p.isdigit() for p in pids)


def test_does_not_raise_without_table(monkeypatch):
    import subprocess

    def boom(*a, **k):
        raise OSError("no wmic")

    monkeypatch.setattr(subprocess, "run", boom)
    assert puller_pids() == set()
