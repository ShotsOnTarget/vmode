# Instruction sheet

- **Job id**: 0002-2-wiki_touch-code
- **Kind**: code
- **Parent Story**: 0002-2
- **Function name**: `wiki_touch`
- **Folder**: `src/wiki_touch/`
- **Files you may change**: `src/wiki_touch/wiki_touch.py`, `src/wiki_touch/wiki_touch.md`
- **Signature**: `wiki_touch(root: str, page_id: str, now: str) -> dict`
- **Inputs**: root, page id, now: ISO-8601 timestamp string supplied by the caller (no clock inside the function).
- **Outputs**: the updated page dict, with last_used == now and times_used incremented by one, and the file rewritten.
- **Errors**: FileNotFoundError propagates from wiki_read.
- **Allowed imports**: from wiki_read.wiki_read import wiki_read; from wiki_write.wiki_write import wiki_write. Nothing else.
- **Checklist items this job serves**: Story 0002-2 items 3
- **How**: read, update two fields, write. Under fifteen lines.
- **Checks to run before reporting**:
  - `wc -l src/wiki_touch/wiki_touch.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/wiki_touch/wiki_touch.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/wiki_touch/wiki_touch.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0002-2-wiki_touch-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
