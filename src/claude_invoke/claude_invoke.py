import contextlib
import json
import tomllib

from adapter_command.adapter_command import adapter_command
from claude_fold.claude_fold import claude_fold
from harness_run.harness_run import harness_run
from role_prompt.role_prompt import role_prompt
from transcript_write.transcript_write import transcript_write


def _events(stdout: str) -> list[dict]:
    events = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("{"):
            with contextlib.suppress(json.JSONDecodeError):
                events.append(json.loads(stripped))
    return events


def _role(item: dict, column: str, roots: dict) -> str:
    role = item.get("role")
    if role is not None:
        return role
    if item["kind"] in ("code", "test"):
        return "builder"
    with open(roots["board"], "rb") as f:
        return tomllib.load(f)["columns"][column]["role"]


def claude_invoke(item: dict, column: str, root: str) -> dict:
    """Run one Builder job on the Claude Code harness and fold its result.

    Inputs: item (id, kind, optionally role, model, effort), column (the
    board column name) and root (repo path). Outputs: tokens, turns,
    cost_usd, report, seconds, harness, model, effort and transcript.
    Side effects: runs the claude CLI and writes a transcript file.
    """
    roots = {
        "board": f"{root}/roles/board.toml",
        "manifest": f"{root}/roles/manifest.json",
        "root": root,
        "mcp": f"{root}/roles/pullers/empty-mcp.json",
    }
    argv = adapter_command(item, column, roots)
    argv[argv.index("--output-format") + 1] = "stream-json"
    argv.append("--verbose")
    role = _role(item, column, roots)
    if item["kind"] not in ("code", "test"):
        argv[2] = role_prompt(item, role, root)
    effort = item.get("effort")
    if effort is not None:
        argv = argv + ["--effort", effort]
    run = harness_run(argv, root, 1800)
    if run["returncode"] != 0:
        raise RuntimeError(run["stderr"][:500] or "claude exited non-zero")
    events = _events(run["stdout"])
    fold = claude_fold(events)
    model = argv[argv.index("--model") + 1] if "--model" in argv else None
    meta = {
        "item": item["id"],
        "harness": "claude_code",
        "model": model,
        "effort": effort,
        "role": role,
    }
    transcript = transcript_write(events, meta, f"{root}/../vmode-runs")
    return {
        "tokens": fold["tokens"],
        "turns": fold["turns"],
        "cost_usd": fold["cost_usd"],
        "report": fold["report"],
        "seconds": run["seconds"],
        "harness": "claude_code",
        "model": model,
        "effort": effort,
        "transcript": transcript,
    }
