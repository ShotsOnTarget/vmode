import importlib

import pipeline_run_count.pipeline_run_count as _module


def count_written() -> int:
    """The run count the code holds now, read fresh from disk.

    Inputs: none. Outputs: the integer pipeline_run_count() returns after
    reloading it. Side effects: reloads that module.

    The smoke harness imports pipeline_run_count to work out the target
    before the run, so by the time the run is judged Python still holds the
    value from before the Builders changed it. Reading it any other way
    answers with the old number and a changed count looks unchanged.
    """
    return importlib.reload(_module).pipeline_run_count()
