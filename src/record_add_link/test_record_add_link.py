import pytest

from record_add_link.record_add_link import record_add_link
from record_run.record_run import record_run


def _item(title):
    return record_run(['create', title, '-t', 'task'])['id']


def test_parent_of_reads_back(bd_repo):
    src = _item('src')
    dst = _item('dst')
    record_add_link('parent_of', src, dst)
    deps = record_run(['dep', 'list', dst])
    assert any(d['id'] == src for d in deps)


def test_needs_first_reads_back(bd_repo):
    src = _item('src')
    dst = _item('dst')
    record_add_link('needs_first', src, dst)
    deps = record_run(['dep', 'list', src])
    assert any(d['id'] == dst for d in deps)


def test_checks_reads_back(bd_repo):
    src = _item('src')
    dst = _item('dst')
    record_add_link('checks', src, dst)
    deps = record_run(['dep', 'list', src])
    assert any(d['id'] == dst and d['dependency_type'] == 'validates' for d in deps)


def test_fourth_link_rejected(bd_repo):
    with pytest.raises(ValueError):
        record_add_link('related', 'vm-1', 'vm-2')
