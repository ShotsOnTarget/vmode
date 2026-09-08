import pytest

from summary_for.summary_for import summary_for


def test_role_of_sheet_todo():
    config = {"columns": {"sheet_todo": {"role": "architect"}}}
    assert summary_for(config) == "architect"


def test_engineer_when_configured():
    config = {"columns": {"sheet_todo": {"role": "engineer"}}}
    assert summary_for(config) == "engineer"


def test_missing_column_raises():
    config = {"columns": {"build": {"role": "builder"}}}
    with pytest.raises(ValueError):
        summary_for(config)


def test_role_none_raises():
    config = {"columns": {"sheet_todo": {"role": "none"}}}
    with pytest.raises(ValueError):
        summary_for(config)
