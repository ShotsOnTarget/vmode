from modal_status.modal_status import modal_status


def test_has_endpoint():
    assert "/api/status" in modal_status()


def test_defines_loader():
    assert "window.loadStatus" in modal_status()


def test_has_status_box():
    text = modal_status()
    assert "modalStatus" in text
    assert "modalDecision" in text


def test_shows_job_and_run_fields():
    text = modal_status()
    for field in ("function", "state", "retries", "claimed"):
        assert field in text
    for field in ("gate", "rule", "tokens", "turns", "usd", "harness", "model"):
        assert field in text


def test_reads_only():
    text = modal_status()
    assert "POST" not in text
    assert text.count("/api/") == text.count("/api/status")


def test_no_dialogs_no_external():
    text = modal_status()
    assert not any(bad in text for bad in ("alert(", "confirm(", "prompt(", "http"))
