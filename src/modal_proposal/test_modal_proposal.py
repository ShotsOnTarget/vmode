from modal_proposal.modal_proposal import modal_proposal


def test_defines_show_proposal():
    assert "window.showProposal" in modal_proposal()


def test_reads_pattern_and_folds_diff():
    text = modal_proposal()
    assert "/api/item" in text and "<details>" in text and "care" in text


def test_no_dialogs_no_external():
    text = modal_proposal()
    assert not any(bad in text for bad in ("alert(", "confirm(", "prompt(", "http"))
