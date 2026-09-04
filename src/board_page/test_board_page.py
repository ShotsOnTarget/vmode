from board_page.board_page import board_page


def test_is_html():
    html = board_page()
    assert html.lower().startswith('<!doctype html>')
    assert '</html>' in html


def test_has_endpoints():
    html = board_page()
    assert '/api/intents' in html
    assert '/api/tree' in html
    assert '/api/decide' in html


def test_no_external():
    html = board_page()
    assert 'http://' not in html
    assert 'https://' not in html


def test_no_dialogs():
    html = board_page()
    assert 'alert(' not in html
    assert 'confirm(' not in html
    assert 'prompt(' not in html
