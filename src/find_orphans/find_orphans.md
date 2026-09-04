purpose: Find graph items that break structural rules (missing parent, unchecked, or checking nothing).
signature: find_orphans(graph: dict[str, dict]) -> list[dict]
inputs: graph from record_graph.
outputs: list of {'id': str, 'rule': str}, in id order; rules are 'no_parent', 'unchecked', 'checks_nothing'.
side effects: none.
work item id: 0001-2-find_orphans-code
