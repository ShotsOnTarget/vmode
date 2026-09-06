from run_choice.run_choice import run_choice


def run_settings(labels: list[str], column: dict, manifest: dict) -> dict:
    """Harness, model, and effort one run gets.

    Inputs: labels is the item's labels; column is one column config with
    tier and optionally adapter; manifest holds model and effort tables.
    Outputs: {'harness': str, 'model': str | None, 'effort': str | None}
    where harness and model match run_choice for the same inputs and
    effort is the last non-empty effort label or the manifest table.
    Side effects: none.
    """
    choice = run_choice(labels, column, manifest)
    effort = None
    for label in labels:
        if label.startswith("effort:") and label[7:]:
            effort = label[7:]
    if effort is None:
        effort = (manifest.get("efforts") or {}).get(column["tier"])
    return {"harness": choice["harness"], "model": choice["model"], "effort": effort}
