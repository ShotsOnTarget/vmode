from find_orphans.find_orphans import find_orphans
from story_jobs.story_jobs import story_jobs


def _no_intent(sj, _sheets, _orphans, _under):
    return "no_intent" if not sj["has_intent"] else None


def _code_without_test(sj, _sheets, _orphans, _under):
    return "code_without_test" if any(not sj["tests"][c] for c in sj["code"]) else None


def _test_without_code(_sj, _sheets, _orphans, _under):
    return None


def _sheet_missing(sj, sheets, _orphans, _under):
    ids = set(sj["code"]) | {t for ts in sj["tests"].values() for t in ts}
    return "sheet_missing" if any(not sheets.get(i) for i in ids) else None


def _orphan(_sj, _sheets, orphans, under):
    return "orphan" if any(o["id"] in under for o in orphans) else None


_RULES = (_no_intent, _code_without_test, _test_without_code, _sheet_missing, _orphan)


def gate_ready(story_id: str, graph: dict, sheets: dict[str, str]) -> list[str]:
    """Check whether a story's items satisfy the graph rules needed to close it."""
    if story_id not in graph or graph[story_id].get("kind") != "story":
        raise ValueError("story_id not in graph or not a story")

    sj = story_jobs(story_id, graph)
    orphans = find_orphans(graph)
    tests = {t for ts in sj["tests"].values() for t in ts}
    under = {story_id, *sj["code"], *tests}

    broken = (rule(sj, sheets, orphans, under) for rule in _RULES)
    return [name for name in broken if name]
