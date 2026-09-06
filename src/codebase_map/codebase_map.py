import ast
import os
from pathlib import Path


def _one(arg: ast.arg) -> str:
    if arg.annotation is not None:
        return f"{arg.arg}: {ast.unparse(arg.annotation)}"
    return arg.arg


def _format(name: str, func: ast.FunctionDef) -> str:
    args = func.args
    params = ", ".join(
        _one(a) for a in [*args.posonlyargs, *args.args, *args.kwonlyargs]
    )
    ret = f" -> {ast.unparse(func.returns)}" if func.returns is not None else ""
    lines = (ast.get_docstring(func) or "").splitlines()
    first = lines[0] if lines else ""
    return f"{name}({params}){ret}: {first}"


def _describe(name: str, path: str) -> str:
    try:
        tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return f"{name}: unparsable"
    func = next(
        (
            n
            for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name
        ),
        None,
    )
    if func is None:
        return f"{name}: no public function"
    return _format(name, func)


def _line(name: str, path: str) -> str:
    if not os.path.isfile(path):
        return f"{name}: missing"
    return _describe(name, path)


def codebase_map(root: str) -> list[str]:
    """Map each immediate subfolder of <root>/src to a summary line.

    Inputs: root, a directory path holding a src folder. Outputs: one
    string per immediate subfolder of <root>/src, sorted by folder name.
    Side effects: reads files only, writes nothing. Raises ValueError
    when <root>/src is not a directory.
    """
    src = os.path.join(root, "src")
    if not os.path.isdir(src):
        raise ValueError(f"not a directory: {src}")
    names = sorted(
        n
        for n in os.listdir(src)
        if not n.startswith(("_", ".")) and os.path.isdir(os.path.join(src, n))
    )
    return [_line(n, os.path.join(src, n, f"{n}.py")) for n in names]
