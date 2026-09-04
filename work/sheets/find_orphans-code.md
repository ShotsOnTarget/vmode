# Instruction sheet

- **Job id**: 0001-2-find_orphans-code
- **Kind**: code
- **Parent Story**: 0001-2
- **Function name**: `find_orphans`
- **Folder**: `src/find_orphans/`
- **Files you may change**: `src/find_orphans/find_orphans.py`, `src/find_orphans/find_orphans.md`
- **Signature**: `find_orphans(graph: dict[str, dict]) -> list[dict]`
- **Inputs**: graph from record_graph.
- **Outputs**: list of {'id': str, 'rule': str}, id order. rules, exact strings: 'no_parent' (kind is not intent and parent is None), 'unchecked' (kind in intent, story, code and no other item's checks contains this id), 'checks_nothing' (kind in validation, verification, test and checks is empty). An item can appear once per rule it breaks.
- **Errors**: none. Return [] for an empty graph.
- **Allowed imports**: json, sys. Nothing else.
- **Checklist items this job serves**: Story 0001-2 items 3, 4, 5, 6, 7
- **How**: Pure function. Add an `if __name__ == '__main__':` block (not a function) that builds the graph via `from record_graph.record_graph import record_graph`, prints json.dumps of the result, and calls sys.exit(1 if result else 0). The import of record_graph goes inside that block only.
- **Checks to run before reporting**:
  - `wc -l src/find_orphans/find_orphans.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/find_orphans/find_orphans.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/find_orphans/find_orphans.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-2-find_orphans-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
