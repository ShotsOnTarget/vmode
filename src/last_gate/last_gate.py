from record_run.record_run import RecordError, record_run

_SAID = ("ready:", "bounce:", "release:")


def _comments(item_id: str) -> list:
    try:
        return record_run(["comments", item_id])
    except RecordError:
        return record_run(["show", item_id])[0].get("comments", [])


def last_gate(item_id: str) -> str:
    """The last thing a gate or a failed run said about an item, or ''.

    Inputs: item_id. Reads the item's comments newest first and returns the
    first that the Ready gate wrote (ready:), the Built or Proven gate wrote
    (bounce:), or a failed run left (release:). A finished run (usage:)
    that came after any of those ends the search empty: the item's last
    word was a run that finished, so there is nothing to carry forward.
    Outputs: that comment's text, or '' when there is none. Side effects:
    one read of the record.
    """
    for comment in reversed(_comments(item_id)):
        text = comment.get("text", "")
        if text.startswith("usage:"):
            return ""
        if text.startswith(_SAID):
            return text
    return ""
