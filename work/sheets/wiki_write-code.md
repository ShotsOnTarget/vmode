# Instruction sheet

- **Job id**: 0002-2-wiki_write-code
- **Kind**: code
- **Parent Story**: 0002-2
- **Function name**: `wiki_write`
- **Folder**: `src/wiki_write/`
- **Files you may change**: `src/wiki_write/wiki_write.py`, `src/wiki_write/wiki_write.md`
- **Signature**: `wiki_write(root: str, page: dict) -> str`
- **Inputs**: root: directory, created if missing. page: {'id': str, 'title': str, 'pattern': str, 'evidence': list[str], 'cost': int, 'fix': str, 'created': str ISO-8601, 'last_used': str ISO-8601, 'times_used': int}.
- **Outputs**: path of the written file `<root>/<id>.md`, overwriting if present.
- **Errors**: ValueError if any field is missing or extra, if evidence is empty, or if any evidence string contains 'src/' (pages never reference code).
- **Allowed imports**: json, os. Nothing else.
- **Checklist items this job serves**: Story 0002-2 items 1, 2
- **How**: File `<root>/<id>.md`: line 1 `---`; then one line per field in this order id, title, evidence, cost, created, last_used, times_used as `key: <json.dumps(value)>`; then `---`; then `## Pattern`, blank line, the pattern text, blank line, `## Fix`, blank line, the fix text, newline. Documented in wiki/README.md.
- **Checks to run before reporting**:
  - `wc -l src/wiki_write/wiki_write.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/wiki_write/wiki_write.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/wiki_write/wiki_write.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0002-2-wiki_write-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
