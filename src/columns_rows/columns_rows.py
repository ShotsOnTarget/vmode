from record_run.record_run import record_run

_ACTIVE = "in_progress"
_DONE = "done"


def _live_states(config: dict) -> list[str]:
    states = {_ACTIVE}
    for rules in config["columns"].values():
        states.update(s for s in rules["states"] if s != _DONE)
    return sorted(f"state:{s}" for s in states)


def _done_kinds(config: dict) -> list[str]:
    kinds = set()
    for rules in config["columns"].values():
        if _DONE in rules["states"]:
            kinds.update(rules["kinds"])
    return sorted(f"kind:{k}" for k in kinds)


def columns_rows(config: dict) -> list[dict]:
    """The record rows the board's columns can show, and nothing else.

    Inputs: config, as board_config() returns. Outputs: rows shaped as
    `bd list` returns them, holding every non-event item in a state some
    column lists (plus in_progress, which falls back to a ready column),
    and for columns that list done items only the kinds they name. Side
    effects: one record read, plus one more when a column lists done.

    A whole-record read returns mostly finished history that no column
    keeps; nine items in ten are done. Asking only for the live states
    keeps the read proportional to the work in flight."""
    base = ["list", "--all", "-n", "0", "--exclude-type", "event"]
    rows = record_run([*base, "--label-any", ",".join(_live_states(config))])
    done_kinds = _done_kinds(config)
    if done_kinds:
        rows += record_run(
            [*base, "-l", f"state:{_DONE}", "--label-any", ",".join(done_kinds)]
        )
    return list({row["id"]: row for row in rows}.values())
