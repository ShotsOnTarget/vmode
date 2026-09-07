import json
import tomllib

from adapter_command.adapter_command import adapter_command
from claude_fold.claude_fold import claude_fold
from harness_run.harness_run import harness_run
from role_prompt.role_prompt import role_prompt


def claude_invoke(item: dict, column: str, root: str) -> dict:
    """Run one Builder job on the Claude Code harness and fold its result.

    Inputs: item, one work item as the puller holds it (id, kind, and
    optionally role, model, effort); column, the board column name the run
    is for; root, the repo root as a string. Outputs: a dict with tokens
    (int), turns (int or None), cost_usd (float or None), report (str),
    seconds (float), harness (always 'claude_code'), model (str or None,
    read from argv), and effort (item['effort'] or None). Side effects:
    runs the claude CLI as a subprocess.
    """
    roots = {
        "board": f"{root}/roles/board.toml",
        "manifest": f"{root}/roles/manifest.json",
        "root": root,
        "mcp": f"{root}/roles/pullers/empty-mcp.json",
    }
    argv = adapter_command(item, column, roots)
    if item["kind"] not in ("code", "test"):
        role = item.get("role")
        if role is None:
            with open(roots["board"], "rb") as f:
                board = tomllib.load(f)
            role = board["columns"][column]["role"]
        argv[2] = role_prompt(item, role, root)
    effort = item.get("effort")
    if effort is not None:
        argv = argv + ["--effort", effort]

    run = harness_run(argv, root, 1800)
    if run["returncode"] != 0:
        raise RuntimeError(run["stderr"][:500] or "claude exited non-zero")

    fold = claude_fold(json.loads(run["stdout"]))
    model = argv[argv.index("--model") + 1] if "--model" in argv else None

    return {
        "tokens": fold["tokens"],
        "turns": fold["turns"],
        "cost_usd": fold["cost_usd"],
        "report": fold["report"],
        "seconds": run["seconds"],
        "harness": "claude_code",
        "model": model,
        "effort": effort,
    }
