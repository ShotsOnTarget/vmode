from proposal_check.proposal_check import proposal_check


def make(kind="proposal", page="p1", target="roles/x.md", care="low", diff=""):
    header = f"page: {page}\ntarget: {target}\ncare: {care}\n---\n{diff}"
    return {"kind": kind, "sheet": header}


def test_two_files_rejected():
    diff = "--- a/roles/x.md\n+++ b/roles/x.md\n+ line\n--- a/roles/y.md\n+++ b/roles/y.md\n+ line\n"
    item = make(target="roles/x.md", diff=diff)
    result = proposal_check(item)
    assert "multi_file" in result


def test_src_target_rejected():
    item = make(
        target="src/a/a.py", diff="--- a/src/a/a.py\n+++ b/src/a/a.py\n+ line\n"
    )
    result = proposal_check(item)
    assert "bad_target" in result


def test_no_page_rejected():
    sheet = "target: roles/x.md\ncare: low\n---\n--- a/roles/x.md\n+++ b/roles/x.md\n+ line\n"
    item = {"kind": "proposal", "sheet": sheet}
    result = proposal_check(item)
    assert "no_page" in result


def test_clean_passes():
    diff = "--- a/roles/builder/SKILL.md\n+++ b/roles/builder/SKILL.md\n+ line\n"
    item = make(page="p1", target="roles/builder/SKILL.md", care="low", diff=diff)
    result = proposal_check(item)
    assert result == []


def test_wrong_kind_rejected():
    diff = "--- a/roles/x.md\n+++ b/roles/x.md\n+ line\n"
    item = make(kind="story", target="roles/x.md", diff=diff)
    result = proposal_check(item)
    assert "not_proposal" in result
