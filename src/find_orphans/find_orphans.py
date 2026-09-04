import json
import sys


def find_orphans(graph: dict[str, dict]) -> list[dict]:
    checked_ids = set()
    for item in graph.values():
        for c in item.get("checks", []):
            checked_ids.add(c)

    results = []
    for item_id, item in graph.items():
        kind = item.get("kind")

        if kind != "intent" and item.get("parent") is None:
            results.append({"id": item_id, "rule": "no_parent"})

        if (
            kind in ("intent", "story", "code", "proposal")
            and item_id not in checked_ids
        ):
            results.append({"id": item_id, "rule": "unchecked"})

        if kind in ("validation", "verification", "test") and not item.get("checks"):
            results.append({"id": item_id, "rule": "checks_nothing"})

    return results


if __name__ == "__main__":
    from record_graph.record_graph import record_graph

    graph = record_graph()
    result = find_orphans(graph)
    print(json.dumps(result))
    sys.exit(1 if result else 0)
