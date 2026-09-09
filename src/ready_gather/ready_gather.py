import json

from checklist_items.checklist_items import checklist_items
from codebase_map.codebase_map import codebase_map
from existing_tests.existing_tests import existing_tests
from record_graph.record_graph import record_graph
from record_run.record_run import RecordError, record_run
from record_show_item.record_show_item import record_show_item


def _existing(root: str) -> list[str]:
    names = []
    for line in codebase_map(root):
        paren = line.find("(")
        colon = line.find(":")
        cut = len(line)
        if paren != -1:
            cut = paren
        if colon != -1 and colon < cut:
            cut = colon
        names.append(line[:cut])
    return names


def _usage(story_id: str) -> dict:
    try:
        comments = record_run(["comments", story_id])
    except RecordError:
        comments = record_run(["show", story_id])[0].get("comments", []) or []
    for comment in reversed(comments):
        if comment.get("text", "").startswith("usage:"):
            return json.loads(comment["text"][len("usage:") :])
    return {}


def _existing_tests(root: str, names: list[str]) -> dict:
    return {name: existing_tests(name, root) for name in names}


def ready_gather(story_id: str, root: str) -> dict:
    """Collect what the Ready gate needs for one story.

    Args:
        story_id: A Story item id.
        root: Repo root directory holding `src`.

    Returns:
        Dict with graph, jobs, sheets, checklist, existing, usage and
        existing_tests, which maps each existing function to the ordered
        test function names in its test file.

    Side effects:
        Reads the record and the tree; writes nothing.
    """
    graph = record_graph()
    item = graph.get(story_id)
    if item is None or item.get("kind") != "story":
        raise ValueError(f"not a story: {story_id}")
    jobs = sorted(
        job_id
        for job_id, job in graph.items()
        if job.get("parent") == story_id and job.get("kind") in ("code", "test")
    )
    sheets = {job_id: record_show_item(job_id).get("sheet") or "" for job_id in jobs}
    text = record_run(["show", story_id])[0].get("acceptance_criteria") or ""
    existing = _existing(root)
    return {
        "graph": graph,
        "jobs": jobs,
        "sheets": sheets,
        "checklist": checklist_items(text),
        "existing": existing,
        "existing_tests": _existing_tests(root, existing),
        "usage": _usage(story_id),
    }
