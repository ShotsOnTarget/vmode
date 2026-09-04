# Instruction sheet

- **Job id**: 0002-2-wiki_read-code
- **Kind**: code
- **Parent Story**: 0002-2
- **Function name**: `wiki_read`
- **Folder**: `src/wiki_read/`
- **Files you may change**: `src/wiki_read/wiki_read.py`, `src/wiki_read/wiki_read.md`
- **Signature**: `wiki_read(root: str, page_id: str) -> dict`
- **Inputs**: root directory and page id.
- **Outputs**: the page dict {'id': str, 'title': str, 'pattern': str, 'evidence': list[str], 'cost': int, 'fix': str, 'created': str ISO-8601, 'last_used': str ISO-8601, 'times_used': int}, exactly equal to what wiki_write was given.
- **Errors**: FileNotFoundError if the page does not exist. ValueError if the front matter is malformed.
- **Allowed imports**: json, os. Nothing else.
- **Checklist items this job serves**: Story 0002-2 items 1
- **How**: Parse the format in work/sheets/wiki_write-code.md (How line): front matter lines are `key: <json>`; pattern is the text between '## Pattern' and '## Fix', stripped; fix is the text after '## Fix', stripped. Do not import wiki_write; parse the file directly.
- **Checks to run before reporting**:
  - `wc -l src/wiki_read/wiki_read.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/wiki_read/wiki_read.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/wiki_read/wiki_read.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0002-2-wiki_read-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
