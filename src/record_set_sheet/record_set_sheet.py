import json
import os
import sys
import tempfile

from record_run.record_run import record_run


def record_set_sheet(item_id: str, text: str) -> dict:
    """Set an item's instruction sheet (its description field).

    Writes text through the record client: a temp file is created holding
    text, `update <id> --body-file <path>` sends it to the record, then the
    temp file is removed. Raises ValueError when text is empty or
    whitespace. Returns {'id': item_id, 'sheet': text}.

    From a shell, pipe the sheet in: `python -m record_set_sheet.record_set_sheet
    <id>` reads the whole of stdin as the text, so a PowerShell here-string
    carries a multi-line sheet in one command with no quoting (the Engineer
    lost a third of a run to `python -c` quoting on 2026-09-09).
    """
    if not text.strip():
        raise ValueError("text must not be empty")

    fd, path = tempfile.mkstemp(suffix=".md")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        record_run(["update", item_id, "--body-file", path])
    finally:
        os.remove(path)

    return {"id": item_id, "sheet": text}


def _main(argv: list[str], stream) -> dict:
    """The command line: the item id as the one argument, the sheet on stdin,
    read as UTF-8 and stripped of the byte-order mark Windows PowerShell puts
    in front of a piped here-string."""
    if len(argv) != 1:
        raise ValueError(
            "usage: python -m record_set_sheet.record_set_sheet <id> < sheet"
        )
    raw = stream.buffer.read() if hasattr(stream, "buffer") else stream.read()
    text = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw
    return record_set_sheet(argv[0], text.lstrip("﻿"))


if __name__ == "__main__":
    print(json.dumps(_main(sys.argv[1:], sys.stdin)))
