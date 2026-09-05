from record_run.record_run import record_run

_METHODS = ("[looking]", "[reasoning]", "[showing]", "[testing]")


def record_set_checklist(item_id: str, items: list[str]) -> dict:
    """Write a Story's checklist as its acceptance text.

    Inputs: item_id, a Story's id. items, checklist lines, each ending
    with a bracketed check method: [looking], [reasoning], [showing]
    or [testing].
    Outputs: {'id': item_id, 'checklist': items}. Side effect: writes
    the numbered checklist as the item's acceptance through the record
    client. Raises ValueError when items is empty or any item lacks a
    bracketed check method from the four.
    """
    if not items:
        raise ValueError("items must not be empty")
    for item in items:
        if not item.rstrip().endswith(_METHODS):
            raise ValueError(f"item lacks a check method: {item}")
    text = " ".join(f"{i}. {item}" for i, item in enumerate(items, start=1))
    record_run(["update", item_id, "--acceptance", text])
    return {"id": item_id, "checklist": items}
