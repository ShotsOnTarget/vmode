def _manifest_model(harness: str, tier: str, manifest: dict) -> str | None:
    table = "models" if harness == "claude_code" else f"{harness}_models"
    return (manifest.get(table) or {}).get(tier)


def run_choice(labels: list[str], column: dict, manifest: dict) -> dict:
    """Which harness and model one run gets, most specific source first.

    An item label `harness:<name>` names the adapter file in roles/pullers;
    without it the column's `adapter` (default claude_code). An item label
    `model:<provider/model>` names the model; without it the manifest's
    table for that harness (`models` for claude_code, `<harness>_models`
    otherwise) at the column's tier, or None for the harness default.
    Labels let an orchestrating role pick per item, in process, without
    editing any config. Returns {'harness': str, 'model': str | None}.
    """
    harness = column.get("adapter", "claude_code")
    model = None
    for label in labels:
        if label.startswith("harness:") and label[8:]:
            harness = label[8:]
        elif label.startswith("model:") and label[6:]:
            model = label[6:]
    if model is None:
        model = _manifest_model(harness, column["tier"], manifest)
    return {"harness": harness, "model": model}
