import subprocess

from record_graph.record_graph import record_graph
from record_labels.record_labels import record_labels
from record_run.record_run import record_run


def _comment_texts(item_id: str) -> list[str]:
    return [row.get("text", "") for row in record_run(["comments", item_id])]


def _git_log(repo: str) -> list[str]:
    result = subprocess.run(
        ["git", "log", "--format=%s"],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return []
    return result.stdout.splitlines()


def loop_snapshot(step: str, story_id: str, repo: str) -> dict:
    """Snapshot the record and repository after one loop step.

    Inputs: step, a label for the step just taken; story_id, a Story in the
    record; repo, a directory holding a git repository. Outputs: a dict with
    the step and story id, the Story's state, its labels, each code and test
    job under it with its state, the repository's commit subject lines in git
    order, and one string joining the Story's and jobs' comment texts and the
    titles of note items under them by newlines. Side effects: reads the
    record and runs git; never writes.
    """
    graph = record_graph()
    story = graph[story_id]
    jobs = [
        item["id"]
        for item in graph.values()
        if item["kind"] in ("code", "test") and item["parent"] == story_id
    ]
    notes = _comment_texts(story_id)
    for job in jobs:
        notes.extend(_comment_texts(job))
    notes.extend(
        item["title"]
        for item in graph.values()
        if item["kind"] == "note" and item["parent"] in (story_id, *jobs)
    )
    return {
        "step": step,
        "story_id": story_id,
        "story_state": story["state"],
        "story_labels": record_labels()[story_id],
        "job_states": {job: graph[job]["state"] for job in jobs},
        "git_log": _git_log(repo),
        "notes": "\n".join(notes),
    }
