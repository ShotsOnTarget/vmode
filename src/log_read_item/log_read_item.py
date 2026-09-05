import json

from record_run.record_run import record_run


def log_read_item(item_id: str) -> list[dict]:
    """Read every gate event recorded against a work item, in order."""
    events = record_run(["list", "--all", "--type", "event"])
    matches = sorted(
        (event for event in events if event.get("target") == item_id),
        key=lambda event: event["created_at"],
    )
    results = []
    for event in matches:
        try:
            payload = json.loads(event["payload"])
        except json.JSONDecodeError as err:
            raise ValueError(f"invalid JSON payload for event {event['id']}") from err
        entry = {
            "id": event["id"],
            "ts": event["created_at"],
            "actor": event["actor"],
            "gate": event["event_kind"],
            "item": event["target"],
        }
        entry.update(payload)
        results.append(entry)
    return results
