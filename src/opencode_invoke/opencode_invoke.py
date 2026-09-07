import json
import shutil
import tomllib

from harness_run.harness_run import harness_run
from opencode_fold.opencode_fold import opencode_fold
from role_prompt.role_prompt import role_prompt


def _load_config(root: str) -> tuple[dict, dict]:
    with open(f"{root}/roles/board.toml", "rb") as f:
        board = tomllib.load(f)
    with open(f"{root}/roles/manifest.json") as f:
        manifest = json.load(f)
    return board, manifest


def _build_argv(executable: str, model, effort, prompt: str) -> list[str]:
    argv = [
        executable,
        "run",
        "--format",
        "json",
        "--pure",
        "--dangerously-skip-permissions",
    ]
    if model is not None:
        argv += ["-m", model]
    if effort is not None:
        argv += ["--variant", effort]
    return argv + [prompt]


def _parse_json_line(line: str):
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def _parse_events(stdout: str) -> list[dict]:
    parsed = (_parse_json_line(x) for x in stdout.splitlines() if x.startswith("{"))
    return [e for e in parsed if e is not None]


def opencode_invoke(item: dict, column: str, root: str) -> dict:
    """Run one job on the opencode harness and fold its result.

    Inputs: item (id, kind, optional role/model/effort); column (board column name);
    root (repo root). Outputs: a dict with tokens (int), turns (int or None), cost_usd
    (float or None), report (str), seconds (float), harness ('opencode'), model (str or
    None), effort (item['effort'] or None). Side effects: runs opencode.
    """
    executable = shutil.which("opencode")
    if executable is None:
        raise RuntimeError("opencode not found on PATH")

    board, manifest = _load_config(root)
    tier = board["columns"][column]["tier"]
    model = item.get("model") or manifest["opencode_models"].get(tier)
    effort = item.get("effort")
    role = item.get("role") or board["columns"][column]["role"]
    prompt = role_prompt(item, role, root)
    argv = _build_argv(executable, model, effort, prompt)

    run = harness_run(argv, root, 1800)
    fold = opencode_fold(_parse_events(run["stdout"]))
    if run["returncode"] != 0 or fold["error"]:
        msg = fold["report"][:500] or run["stderr"][:500] or "opencode failed"
        raise RuntimeError(msg)
    return {
        "tokens": fold["tokens"],
        "turns": fold["turns"],
        "cost_usd": fold["cost_usd"],
        "report": fold["report"],
        "seconds": run["seconds"],
        "harness": "opencode",
        "model": model,
        "effort": effort,
    }
