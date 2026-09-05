import ast

_KEYS = ("changed", "code", "fmt_out", "lint_out")

_RULES = (
    ("file_outside_folder", lambda c: c["outside"]),
    ("too_many_files", lambda c: c["many"]),
    ("over_80_lines", lambda c: c["long"]),
    ("not_one_public_function", lambda c: c["funcs"] != 1),
    ("no_docstring", lambda c: c["funcs"] == 1 and not c["doc"]),
    ("not_formatted", lambda c: c["fmt_bad"]),
    ("lint_findings", lambda c: c["lint_bad"]),
)


def gate_built(job_id: str, inputs: dict) -> list[str]:
    """Built-gate rule names that fail for one job's folder.

    inputs: changed (paths changed in the tree), code (the code file text),
    fmt_out (formatter check output), lint_out (linter output). Rules: only
    the job's folder changed, at most two files, code under 80 lines, one
    public function with a docstring, formatted, no lint findings.
    """
    for key in _KEYS:
        if key not in inputs:
            raise ValueError(f"missing key: {key}")
    folder, code, changed = f"src/{job_id}/", inputs["code"], inputs["changed"]
    lint = inputs["lint_out"]
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise ValueError("bad code") from exc
    public = [
        x
        for x in tree.body
        if isinstance(x, ast.FunctionDef) and not x.name.startswith("_")
    ]
    ctx = {
        "outside": any(not p.startswith(folder) for p in changed),
        "many": len({p for p in changed if p.startswith(folder)}) > 2,
        "long": code.count("\n") + (0 if code.endswith("\n") else 1) > 80,
        "funcs": len(public),
        "doc": bool(public) and ast.get_docstring(public[0]) is not None,
        "fmt_bad": "---" in inputs["fmt_out"] or "would reformat" in inputs["fmt_out"],
        "lint_bad": bool(lint) and not lint.startswith("All checks passed"),
    }
    return [name for name, pred in _RULES if pred(ctx)]
