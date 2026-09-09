import contextlib
import json
import shutil
import tomllib

from harness_run.harness_run import harness_run
from opencode_fold.opencode_fold import opencode_fold
from role_prompt.role_prompt import role_prompt
from transcript_write.transcript_write import transcript_write


def _load_config(root: str) -> tuple[dict, dict]:
    with open(f"{root}/roles/board.toml", "rb") as f:
        board = tomllib.load(f)
    with open(f"{root}/roles/manifest.json") as f:
        manifest = json.load(f)
    return board, manifest


_RUN = ("run", "--format", "json", "--pure", "--dangerously-skip-permissions")


def _build_argv(executable: str, model, effort, prompt: str) -> list[str]:
    argv = [executable, *_RUN]
    if model is not None:
        argv += ["-m", model]
    if effort is not None:
        argv += ["--variant", effort]
    return argv + [prompt]


def _parse_events(stdout: str) -> list[dict]:
    events = []
    for line in stdout.splitlines():
        if line.startswith("{"):
            with contextlib.suppress(json.JSONDecodeError):
                events.append(json.loads(line))
    return events


def _failure(run: dict, fold: dict) -> str:
    """Why a run failed: its error events, else its stderr, else its exit code."""
    errors = [x for x in fold["report"].splitlines() if x.startswith("ERROR:")]
    text = "\n".join(errors) or run["stderr"].strip()
    return (text or f"opencode exited {run['returncode']}")[:500]


def opencode_invoke(item: dict, column: str, root: str) -> dict:
    """Run one job on opencode, write its transcript, then fold and return the
    fold plus path; the transcript lands first so a fold fault leaves evidence."""
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
    events = _parse_events(run["stdout"])
    meta = dict(
        item=item["id"], harness="opencode", model=model, effort=effort, role=role
    )
    transcript = transcript_write(events, meta, f"{root}/../vmode-runs")
    fold = opencode_fold(events)
    if run["returncode"] != 0 or fold["error"]:
        raise RuntimeError(_failure(run, fold))
    return {
        "tokens": fold["tokens"],
        "turns": fold["turns"],
        "cost_usd": fold["cost_usd"],
        "report": fold["report"],
        "seconds": run["seconds"],
        "harness": "opencode",
        "model": model,
        "effort": effort,
        "transcript": transcript,
    }
