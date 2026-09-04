# Instruction sheet

- **Job id**: 0002-2-wiki_stale-code
- **Kind**: code
- **Parent Story**: 0002-2
- **Function name**: `wiki_stale`
- **Folder**: `src/wiki_stale/`
- **Files you may change**: `src/wiki_stale/wiki_stale.py`, `src/wiki_stale/wiki_stale.md`
- **Signature**: `wiki_stale(root: str, days: int, now: str) -> list[str]`
- **Inputs**: root, days threshold, now: ISO-8601 string supplied by the caller.
- **Outputs**: sorted list of page ids whose last_used is more than `days` days before now. Empty root or missing root returns [].
- **Errors**: ValueError if a page's last_used is not ISO-8601.
- **Allowed imports**: os, datetime, from wiki_read.wiki_read import wiki_read. Nothing else.
- **Checklist items this job serves**: Story 0002-2 items 4
- **How**: Compare datetime.fromisoformat values. Only files ending in .md are pages; README.md is skipped.
- **Checks to run before reporting**:
  - `wc -l src/wiki_stale/wiki_stale.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/wiki_stale/wiki_stale.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/wiki_stale/wiki_stale.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0002-2-wiki_stale-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
