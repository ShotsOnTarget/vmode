import json
from datetime import UTC, datetime
from pathlib import Path


def transcript_write(
    events: list[dict], meta: dict, directory: str = "../vmode-runs"
) -> str | None:
    """Write one run's harness events to a transcript file, one JSON object
    per line. Inputs: events, the harness's own events for one run in
    arrival order; meta, a dict with keys item, harness, model, effort and
    role, missing keys reading as None; directory, where the file goes,
    made along with any missing parents. Outputs: the path written, or None
    when the directory or the file could not be written. Side effects:
    creates directory (and parents) if missing, and writes one file there.
    """
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        path = _free_path(Path(directory), meta["item"], stamp)
        with open(path, "w", encoding="utf-8") as f:
            for event in events:
                line = {
                    "ts": datetime.now(UTC).isoformat(),
                    "item": meta.get("item"),
                    "harness": meta.get("harness"),
                    "model": meta.get("model"),
                    "effort": meta.get("effort"),
                    "role": meta.get("role"),
                    "event": event,
                }
                f.write(json.dumps(line) + "\n")
        return str(path)
    except OSError:
        return None


def _free_path(directory: Path, item: str, stamp: str) -> Path:
    path = directory / f"{item}-{stamp}.jsonl"
    count = 2
    while path.exists():
        path = directory / f"{item}-{stamp}-{count}.jsonl"
        count += 1
    return path
