from columns_page.columns_page import columns_page
from pipeline_run_count.pipeline_run_count import pipeline_run_count


def test_columns_page_shows_labelled_pipeline_run_count():
    html = columns_page()
    assert "Pipeline runs" in html
    assert str(pipeline_run_count()) in html


def test_columns_page_uses_pipeline_run_count(monkeypatch):
    monkeypatch.setattr("columns_page.columns_page.pipeline_run_count", lambda: 41)
    low = columns_page()
    monkeypatch.setattr("columns_page.columns_page.pipeline_run_count", lambda: 42)
    high = columns_page()

    assert "41" in low
    assert "42" in high
    assert low != high
