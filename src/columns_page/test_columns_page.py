from columns_modal.columns_modal import columns_modal
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


def test_side_by_side():
    html = columns_page()
    assert "display:flex" in html or "display: flex" in html


def test_no_overflow_rules():
    html = columns_page()
    assert "text-overflow" in html
    assert "word-break" in html
    assert "overflow-x" in html


def test_narrow_columns():
    html = columns_page()
    assert "144px" in html


def test_modal_and_decide():
    html = columns_page()
    modal = columns_modal()
    assert modal in html
    assert "openItem" in html


def test_no_dialogs():
    html = columns_page()
    assert "alert(" not in html
    assert "confirm(" not in html
    assert "prompt(" not in html
