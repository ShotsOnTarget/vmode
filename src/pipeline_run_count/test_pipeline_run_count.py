from pipeline_run_count.pipeline_run_count import pipeline_run_count


def test_pipeline_run_count_returns_ten():
    assert pipeline_run_count() == 10
