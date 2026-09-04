from columns_page.columns_page import columns_page


def test_is_html():
    html = columns_page()
    assert html.lower().startswith("<!doctype html>")
    assert "</html>" in html


def test_has_endpoint():
    html = columns_page()
    assert "/api/columns" in html


def test_no_external():
    html = columns_page()
    assert "http://" not in html
    assert "https://" not in html


def test_no_dialogs():
    html = columns_page()
    assert "alert(" not in html
    assert "confirm(" not in html
    assert "prompt(" not in html
