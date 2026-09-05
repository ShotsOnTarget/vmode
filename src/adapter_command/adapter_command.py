import json
import shutil
import tomllib

from builder_prompt.builder_prompt import builder_prompt

_TOOLS = ("Read", "Edit", "Write", "Bash", "Glob", "Grep")
_NO_TOOLS = ("Task", "Agent", "WebSearch", "WebFetch", "NotebookEdit", "TodoWrite")


def _model(tier: str, manifest: dict) -> str | None:
    name = manifest["models"].get(tier)
    if name is None:
        return None
    return name.split("/", 1)[-1]


def adapter_command(item: dict, column: str, roots: dict) -> list[str]:
    """The argv for one Builder run on the Claude Code harness.

    roots: board (roles/board.toml), manifest (roles/manifest.json), root
    (working directory), mcp (a JSON file declaring no MCP servers). The run
    is stripped: no MCP servers, six tools, so the per-turn baseline is the
    harness prompt and those tools only (measured 2026-09-05: 44k vs 105k).
    """
    exe = shutil.which("claude")
    if exe is None:
        raise RuntimeError("claude not found on PATH")
    with open(roots["board"], "rb") as f:
        board = tomllib.load(f)
    with open(roots["manifest"]) as f:
        manifest = json.load(f)
    column_config = board["columns"][column]
    prompt = builder_prompt(item, column_config["role"], roots["root"])
    argv = [exe, "-p", prompt, "--output-format", "json"]
    argv += ["--strict-mcp-config", "--mcp-config", str(roots["mcp"])]
    argv += [
        "--allowedTools",
        ",".join(_TOOLS),
        "--disallowedTools",
        ",".join(_NO_TOOLS),
    ]
    model = _model(column_config["tier"], manifest)
    if model is not None:
        argv += ["--model", model]
    return argv
