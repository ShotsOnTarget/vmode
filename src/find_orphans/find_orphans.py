import json
import sys


def _collect_checked_ids(graph: dict[str, dict]) -> set:
    checked_ids = set()
    for item in graph.values():
        for c in item.get("checks", []):
            checked_ids.add(c)
    return checked_ids


def _rules_for_item(item_id: str, item: dict, checked_ids: set) -> list[dict]:
    kind = item.get("kind")
    rules = []

    if kind not in ("intent", "note") and item.get("parent") is None:
        rules.append({"id": item_id, "rule": "no_parent"})

    if kind in ("intent", "story", "code", "proposal") and item_id not in checked_ids:
        rules.append({"id": item_id, "rule": "unchecked"})

    if kind in ("validation", "verification", "test") and not item.get("checks"):
        rules.append({"id": item_id, "rule": "checks_nothing"})

    return rules


def find_orphans(graph: dict[str, dict]) -> list[dict]:
    checked_ids = _collect_checked_ids(graph)

    results = []
    for item_id, item in graph.items():
        results.extend(_rules_for_item(item_id, item, checked_ids))

    return results


if __name__ == "__main__":
    from record_graph.record_graph import record_graph

    graph = record_graph()
    result = find_orphans(graph)
    print(json.dumps(result))
    sys.exit(1 if result else 0)
