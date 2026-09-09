import os
import subprocess
from pathlib import Path

from loop_mint.loop_mint import loop_mint
from loop_snapshot.loop_snapshot import loop_snapshot
from prove_once.prove_once import prove_once
from pull_once.pull_once import pull_once
from record_graph.record_graph import record_graph
from scripted_builder.scripted_builder import scripted_builder
from scripted_engineer.scripted_engineer import scripted_engineer


def _builds(config, repo, story, recipes):
    snapshots = []
    for _ in range(12):
        prove_once(config)

        def builder(item, column):
            name = item["title"].removesuffix(" code").removesuffix(" test")
            return scripted_builder({**item, "recipe": recipes.get(name, {})}, column)

        if not pull_once("builder", config, builder):
            break
        snapshots.append(loop_snapshot("build", story, repo))
        prove_once(config)
        snapshots.append(loop_snapshot("prove", story, repo))
    return snapshots


def _prepare(repo):
    if not (Path(repo) / "pytest.ini").exists():
        script = (
            "from pathlib import Path; import subprocess; p=Path('.')"
            ";(p/'pytest.ini').write_text('[pytest]\\npythonpath = src\\n"
            "testpaths = src\\naddopts = --import-mode=importlib -p no:"
            "cacheprovider\\n')"
            ";(p/'.gitignore').write_text('__pycache__/\\n*.pyc\\n"
            ".pytest_cache/\\n.ruff_cache/\\n')"
            ";(p/'src').mkdir(exist_ok=True); subprocess.run(['git','add','-A'],"
            "check=True)"
            ";subprocess.run(['git','-c','user.name=loop','-c','user.email=loop@vmode.local',"
            "'commit','-q','-m','loop: repository prepared'],check=True)"
        )
        subprocess.run(["python", "-c", script], cwd=repo, check=True)


def _pipeline(args):
    intent, config, repo, engineer_recipe, builder_recipes = args
    story = loop_mint(intent)

    def engineer(item, column):
        return scripted_engineer({**item, "recipe": engineer_recipe}, column)

    pull_once("engineer", config, engineer)
    snapshots = [loop_snapshot("engineer", story, repo)]
    prove_once(config)
    snapshots.append(loop_snapshot("ready", story, repo))
    if not (
        record_graph()[story]["state"] == "ready"
        and not engineer_recipe.get("stop_after_ready")
    ):
        return snapshots
    snapshots.extend(_builds(config, repo, story, builder_recipes))
    return snapshots


def loop_drive(intent_id, config_path, repo, engineer_recipe, *builder_recipe_args):
    """Drive a scripted pipeline. Inputs are ids, paths, recipes; outputs snapshots."""
    _prepare(repo)
    previous = os.environ.get("PYTHONPATH")
    os.environ["PYTHONPATH"] = os.path.join(repo, "src")
    try:
        return _pipeline(
            (intent_id, config_path, repo, engineer_recipe, builder_recipe_args[0])
        )
    finally:
        os.environ.pop("PYTHONPATH", None)
        if previous is not None:
            os.environ["PYTHONPATH"] = previous
