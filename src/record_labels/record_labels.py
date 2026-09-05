from record_run.record_run import record_run


def record_labels() -> dict[str, list[str]]:
    items = record_run(["list", "--all", "--exclude-type", "event"])
    return {item["id"]: item.get("labels", []) for item in items}
