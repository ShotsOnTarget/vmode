from datetime import datetime


def run_steps(events: list[dict]) -> list[float]:
    """Seconds between each pair of consecutive lines in a transcript.

    events is one transcript's lines as run_events returns them, in order;
    only each line's ts (an ISO 8601 string with a UTC offset) is read. The
    result has one entry per consecutive pair, each rounded to three
    decimals, one shorter than events. Fewer than two lines gives an empty
    list. A pair whose second line is stamped before the first gives a
    negative number, unchanged.
    """
    times = [datetime.fromisoformat(event["ts"]) for event in events]
    return [
        round((later - earlier).total_seconds(), 3)
        for earlier, later in zip(times, times[1:], strict=False)
    ]
