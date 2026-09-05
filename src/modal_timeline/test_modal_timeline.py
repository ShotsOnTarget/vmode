from modal_timeline.modal_timeline import modal_timeline


def test_has_endpoint():
    assert "/api/timeline" in modal_timeline()


def test_defines_loader():
    assert "window.loadTimeline" in modal_timeline()


def test_no_dialogs_no_external():
    text = modal_timeline()
    assert not any(bad in text for bad in ("alert(", "confirm(", "prompt(", "http"))
