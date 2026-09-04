# Instruction sheet

- **Job id**: 0001-3-board_page-code
- **Kind**: code
- **Parent Story**: 0001-3
- **Function name**: `board_page`
- **Folder**: `src/board_page/`
- **Files you may change**: `src/board_page/board_page.py`, `src/board_page/board_page.md`
- **Signature**: `board_page() -> str`
- **Inputs**: none.
- **Outputs**: a complete HTML document as a string. It fetches GET /api/intents and renders a table with id, title, state, care, stories done/total; clicking a row fetches GET /api/tree?id=<id> and renders 'forward' as nested lists and 'back' as a breadcrumb line; every item shows its id; clicking any id in the tree loads that item's tree; two buttons Yes and No (No prompts for a reason with a text input, not window.prompt) POST JSON {'intent','decision','reason'} to /api/decide and then reload the intent list.
- **Errors**: none.
- **Allowed imports**: none. Nothing else.
- **Checklist items this job serves**: Story 0001-3 items 2, 3, 4, 5
- **How**: Return one triple-quoted string. Plain HTML and vanilla JS, no external resources, no framework. Fit the whole file in 50 lines: put the JS on few dense lines, it is allowed to be terse. Do not use alert, confirm or prompt.
- **Checks to run before reporting**:
  - `wc -l src/board_page/board_page.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/board_page/board_page.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/board_page/board_page.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-3-board_page-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
