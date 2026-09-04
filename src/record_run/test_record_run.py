import pytest

from record_run.record_run import RecordError, record_run


def test_show_returns_item(bd_repo):
    created = record_run(["create", "hello"])
    created_item = created[0] if isinstance(created, list) else created
    result = record_run(["show", created_item["id"]])
    assert isinstance(result, list)
    assert result[0]["id"] == created_item["id"]


def test_nonzero_exit_raises(bd_repo):
    with pytest.raises(RecordError):
        record_run(["show", "vm-nope"])


def test_missing_binary_raises(bd_repo, monkeypatch):
    monkeypatch.setenv("PATH", "")
    with pytest.raises(RecordError):
        record_run(["list"])


def test_json_flag_added(bd_repo):
    result = record_run(["list"])
    assert isinstance(result, list)
