from columns_modal.columns_modal import columns_modal


def test_has_endpoints():
    html = columns_modal()
    assert "/api/item" in html
    assert "/api/decide" in html


def test_has_open_function():
    html = columns_modal()
    assert "openItem" in html


def test_has_escape_and_close():
    html = columns_modal()
    assert "Escape" in html
    assert "Close" in html


def test_no_dialogs_no_external():
    html = columns_modal()
    assert "alert(" not in html
    assert "confirm(" not in html
    assert "prompt(" not in html
    assert "http://" not in html
    assert "https://" not in html
