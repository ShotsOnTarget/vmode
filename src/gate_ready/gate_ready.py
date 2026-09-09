from find_orphans.find_orphans import find_orphans
from sheet_check.sheet_check import sheet_check
from story_jobs.story_jobs import story_jobs

_METHODS = ("[looking]", "[reasoning]", "[showing]", "[testing]")


def _no_intent(sj, _sheets, _orphans, _under):
    return "no_intent" if not sj["has_intent"] else None


def _code_without_test(sj, _sheets, _orphans, _under):
    return "code_without_test" if any(not sj["tests"][c] for c in sj["code"]) else None


def _sheet_missing(sj, sheets, _orphans, _under):
    ids = set(sj["code"]) | {t for ts in sj["tests"].values() for t in ts}
    return "sheet_missing" if any(not sheets.get(i) for i in ids) else None


def _orphan(_sj, _sheets, orphans, under):
    return "orphan" if any(o["id"] in under for o in orphans) else None


_RULES = (_no_intent, _code_without_test, _sheet_missing, _orphan)


def _landed(graph, code, test):
    return all(graph.get(j, {}).get("state") == "done" for j in (code, test))


def _sheet_names(sj, sheets, extras, graph):
    existing = extras.get("existing", [])
    mapping = extras.get("existing_tests")
    if isinstance(mapping, dict):
        existing = mapping
    pairs = [
        (c, t)
        for c in sj["code"]
        if sheets.get(c) and sj["tests"][c]
        for t in sj["tests"][c]
        if sheets.get(t) and not _landed(graph, c, t)
    ]
    names = set()
    for code, test in pairs:
        for name in sheet_check(sheets[code], sheets[test], existing):
            names.add(f"sheet_{name}")
    return sorted(names)


def gate_ready(
    story_id: str, graph: dict, sheets: dict[str, str], extras: dict | None = None
) -> list[str]:
    """List the Ready-gate rules a story fails, [] when ready.

    Inputs: story_id, graph as record_graph returns, sheets by job id,
        extras None or with checklist items, existing function names,
        and the gathered existing test names by function.
    Outputs: ordered distinct failed rule names; extras None runs only
        the four graph rules. The sheet rules skip a pair whose jobs are
        both done: a re-armed Story is not refused for landed work.
    Side effects: none. Pure.
    """
    if story_id not in graph or graph[story_id].get("kind") != "story":
        raise ValueError("story_id not in graph or not a story")
    sj = story_jobs(story_id, graph)
    orphans = find_orphans(graph)
    tests = {t for ts in sj["tests"].values() for t in ts}
    under = {story_id, *sj["code"], *tests}
    broken = [name for name in (r(sj, sheets, orphans, under) for r in _RULES) if name]
    if extras is None:
        return broken
    checklist = extras.get("checklist", [])
    if not checklist:
        broken.append("no_checklist")
    if any(not i.strip().endswith(_METHODS) for i in checklist):
        broken.append("checklist_method")
    broken.extend(_sheet_names(sj, sheets, extras, graph))
    return broken
