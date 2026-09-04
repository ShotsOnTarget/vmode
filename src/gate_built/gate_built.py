import ast

_KEYS = ("changed", "code", "note", "fmt_out", "lint_out")

_RULES = (
    ("file_outside_folder", lambda c: c["outside"]),
    ("too_many_files", lambda c: c["many"]),
    ("over_50_lines", lambda c: c["long"]),
    ("not_one_public_function", lambda c: c["funcs"] != 1),
    ("note_not_six_lines", lambda c: c["note_lines"] != 6),
    ("note_missing_item_id", lambda c: not c["has_id"]),
    ("not_formatted", lambda c: c["fmt_bad"]),
    ("lint_findings", lambda c: c["lint_bad"]),
)


def gate_built(job_id: str, inputs: dict) -> list[str]:
    for key in _KEYS:
        if key not in inputs:
            raise ValueError(f"missing key: {key}")
    folder, code, note = f"src/{job_id}/", inputs["code"], inputs["note"].strip()
    changed, fmt_out, lint_out = (
        inputs["changed"],
        inputs["fmt_out"],
        inputs["lint_out"],
    )
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise ValueError("bad code") from exc
    funcs = sum(
        isinstance(x, ast.FunctionDef) and not x.name.startswith("_") for x in tree.body
    )
    ctx = {
        "outside": any(not p.startswith(folder) for p in changed),
        "many": len({p for p in changed if p.startswith(folder)}) > 3,
        "long": code.count("\n") + (0 if code.endswith("\n") else 1) > 50,
        "funcs": funcs,
        "note_lines": note.count("\n") + (1 if note else 0),
        "has_id": job_id in inputs["note"],
        "fmt_bad": "---" in fmt_out or "would reformat" in fmt_out,
        "lint_bad": bool(lint_out) and not lint_out.startswith("All checks passed"),
    }
    return [name for name, pred in _RULES if pred(ctx)]
