from create_pair.create_pair import create_pair
from record_add_note.record_add_note import record_add_note
from record_run.record_run import record_run
from record_set_sheet.record_set_sheet import record_set_sheet

_FAULTS = {"no_change"}
_OWNER = "engineer"
_SERVES = ["1", "2", "5"]


def _sheet(kind, job_id, parent, opts):
    name = opts["name"]
    change = opts["change"]
    lines = [
        "# Instruction sheet",
        "",
        f"- **Job id**: {job_id}",
        f"- **Kind**: {kind}",
        f"- **Parent Story**: {parent}",
        f"- **Function name**: `{name}`",
        f"- **Folder**: `src/{name}/`",
        "- **Signature**: `f() -> None`",
        "- **Inputs**: none.",
        "- **Outputs**: returns an empty result.",
    ]
    if kind == "code" and change:
        lines.append("- **Change**: new function.")
    if kind == "test":
        lines.append("- **Cases**:")
        lines.append(f"  - `test_{name}_works`: works.")
    lines.append(f"- **Checklist items this job serves**: {', '.join(_SERVES)}")
    return "\n".join(lines) + "\n"


def scripted_engineer(item: dict, column: str) -> dict:
    """Cut a Story into code and test pairs from a recipe.

    Inputs: item, the Story dict with id, kind, state, labels, last_gate and
    a recipe dict naming the functions to cut and optional faults per
    function; column, the puller column name, ignored.
    Outputs: a usage dict with tokens, seconds, harness and model.
    Side effects: creates one code and test pair per function with sheets,
    adds a cut note and the cut label to the Story. Raises ValueError on an
    unknown fault name before writing anything.
    """
    recipe = item["recipe"]
    faults = recipe.get("faults", {})
    for fault in faults.values():
        if fault not in _FAULTS:
            raise ValueError(f"unknown fault: {fault}")
    for name in recipe["functions"]:
        pair = create_pair(item["id"], name, _OWNER)
        code = _sheet(
            "code",
            pair["code"],
            item["id"],
            {"name": name, "change": faults.get(name) != "no_change"},
        )
        test = _sheet("test", pair["test"], item["id"], {"name": name, "change": True})
        record_set_sheet(pair["code"], code)
        record_set_sheet(pair["test"], test)
    record_add_note(item["id"], "cut into pairs")
    record_run(["label", "add", item["id"], "cut"])
    return {"tokens": 0, "seconds": 0.0, "harness": "scripted", "model": "engineer"}
