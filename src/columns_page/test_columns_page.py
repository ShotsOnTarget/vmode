from columns_page.columns_page import columns_page


def test_columns_page_shows_labelled_pipeline_run_count():
    html = columns_page()
    assert "Pipeline runs" in html
    assert "1" in html


def test_columns_page_uses_pipeline_run_count(monkeypatch):
    baseline = columns_page()
    monkeypatch.setattr("columns_page.columns_page.pipeline_run_count", lambda: 7)
    html = columns_page()
    assert "Pipeline runs" in html
    assert "7" in html
    assert html != baseline
