import os
from contextlib import contextmanager

from loop_mint.loop_mint import loop_mint
from loop_snapshot.loop_snapshot import loop_snapshot
from prove_once.prove_once import prove_once
from pull_once.pull_once import pull_once
from record_graph.record_graph import record_graph
from record_labels.record_labels import record_labels
from scripted_builder.scripted_builder import scripted_builder
from scripted_engineer.scripted_engineer import scripted_engineer


def _engineer(recipe: dict):
    return lambda item, column: scripted_engineer({**item, "recipe": recipe}, column)


def _builder(recipes: dict[str, dict]):
    def invoke(item, column):
        name = item["title"].removesuffix(" code").removesuffix(" test")
        return scripted_builder({**item, "recipe": recipes.get(name, {})}, column)

    return invoke


def _rounds(config_path: str, repo: str, story_id: str, recipes: dict[str, dict]):
    snapshots = []
    invoke = _builder(recipes)
    for _ in range(12):
        prove_once(config_path)
        if not pull_once("builder", config_path, invoke):
            break
        snapshots.append(loop_snapshot("build", story_id, repo))
        prove_once(config_path)
        snapshots.append(loop_snapshot("prove", story_id, repo))
    return snapshots


@contextmanager
def _environment(repo: str):
    previous = os.environ.copy()
    os.environ["PYTHONPATH"] = os.path.join(repo, "src")
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["PYTEST_ADDOPTS"] = "-p no:cacheprovider"
    os.environ["RUFF_CACHE_DIR"] = os.path.join(os.path.dirname(repo), ".ruff-cache")
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(previous)


def loop_drive(
    intent_id: str,
    config_path: str,
    repo: str,
    engineer_recipe: dict,
    *builder_recipe_args: dict[str, dict],
) -> list[dict]:
    """Drive a minted Story through engineering, building, and proving.

    Inputs are intent, config, repo, and scripted recipes. Returns snapshots;
    drives the record and temporarily changes test environment variables.
    """
    with _environment(repo):
        os.makedirs(os.path.join(repo, "src"), exist_ok=True)
        story_id = loop_mint(intent_id)
        pull_once("engineer", config_path, _engineer(engineer_recipe))
        snapshots = [loop_snapshot("engineer", story_id, repo)]
        prove_once(config_path)
        snapshots.append(loop_snapshot("ready", story_id, repo))
        story = record_graph()[story_id]
        if (
            story["state"] != "ready"
            or engineer_recipe.get("stop_after_ready")
            or "cut" not in record_labels().get(story_id, [])
        ):
            return snapshots
        snapshots.extend(_rounds(config_path, repo, story_id, builder_recipe_args[0]))
        return snapshots
