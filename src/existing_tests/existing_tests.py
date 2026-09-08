import ast
from pathlib import Path


def existing_tests(folder: str, repo: str) -> list[str]:
    """List the test function names in one folder's test file, in file order.

    Inputs: folder, a function folder name under src; repo, the repository
    root. Outputs: the full names, test_ prefix included, of the test
    functions defined in src/<folder>/test_<folder>.py, in file order;
    [] when the file is absent. Side effects: reads the test file, only.
    """
    path = Path(repo) / "src" / folder / f"test_{folder}.py"
    if not path.is_file():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    ]
