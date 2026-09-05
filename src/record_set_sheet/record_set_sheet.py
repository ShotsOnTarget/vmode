import os
import tempfile

from record_run.record_run import record_run


def record_set_sheet(item_id: str, text: str) -> dict:
    """Set an item's instruction sheet (its description field).

    Writes text through the record client: a temp file is created holding
    text, `update <id> --body-file <path>` sends it to the record, then the
    temp file is removed. Raises ValueError when text is empty or
    whitespace. Returns {'id': item_id, 'sheet': text}.
    """
    if not text.strip():
        raise ValueError("text must not be empty")

    fd, path = tempfile.mkstemp(suffix=".md")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
        record_run(["update", item_id, "--body-file", path])
    finally:
        os.remove(path)

    return {"id": item_id, "sheet": text}
