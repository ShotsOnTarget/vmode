import pathlib

from count_written.count_written import count_written
from pipeline_run_count.pipeline_run_count import pipeline_run_count

_CHANGED = 'def pipeline_run_count() -> int:\n    """Doc."""\n    return 4242\n'


def test_reads_the_count_the_code_holds():
    assert count_written() == pipeline_run_count()


def test_reads_it_again_after_the_file_changes():
    import pipeline_run_count.pipeline_run_count as module

    source = pathlib.Path(module.__file__)
    original = source.read_text(encoding="utf-8")
    try:
        source.write_text(_CHANGED, encoding="utf-8")
        assert count_written() == 4242
    finally:
        source.write_text(original, encoding="utf-8")
        count_written()
