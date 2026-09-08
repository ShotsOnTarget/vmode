from pipeline_run_count.pipeline_run_count import pipeline_run_count


def test_pipeline_run_count_returns_one():
    assert pipeline_run_count() == 1


def test_pipeline_run_count_returns_int():
    assert isinstance(pipeline_run_count(), int)
