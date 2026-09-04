import json
import shutil
import tomllib


def _prompt(item: dict, role: str, root: str) -> str:
    kind_note = (
        "You write your tests from the sheet; you never create or edit the code file. "
        if item["kind"] == "test"
        else "Do not write tests. "
    )
    fetch_note = (
        "Fetch it from the record with the work-record skill "
        "(roles/work-record/SKILL.md). "
    )
    return (
        f"You are the {role}. Working directory: {root}. "
        f"Read roles/{role}/SKILL.md and follow it exactly. "
        f"Your work item id is {item['id']}. "
        f"{fetch_note}"
        "Do only that item. "
        f"{kind_note}"
        "Report in roles/shared/report-format.md and nothing else."
    )


def _model(tier: str, manifest: dict) -> str | None:
    name = manifest["models"].get(tier)
    if name is None:
        return None
    return name.split("/", 1)[-1]


def adapter_command(item: dict, column: str, roots: dict) -> list[str]:
    exe = shutil.which("claude")
    if exe is None:
        raise RuntimeError("claude not found on PATH")
    with open(roots["board"], "rb") as f:
        board = tomllib.load(f)
    with open(roots["manifest"]) as f:
        manifest = json.load(f)
    column_config = board["columns"][column]
    prompt = _prompt(item, column_config["role"], roots["root"])
    argv = [exe, "-p", prompt, "--output-format", "json"]
    model = _model(column_config["tier"], manifest)
    if model is not None:
        argv += ["--model", model]
    return argv
