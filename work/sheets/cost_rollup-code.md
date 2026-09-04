# Instruction sheet

- **Job id**: 0002-1-cost_rollup-code
- **Kind**: code
- **Parent Story**: 0002-1
- **Function name**: `cost_rollup`
- **Folder**: `src/cost_rollup/`
- **Files you may change**: `src/cost_rollup/cost_rollup.py`, `src/cost_rollup/cost_rollup.md`
- **Signature**: `cost_rollup(path: str, item_id: str) -> dict`
- **Inputs**: path: log file. item_id: an id such as '0001', '0001-1', or '0001-1-record_run-code'.
- **Outputs**: {'item': item_id, 'tokens': int, 'seconds': float, 'runs': int}. A line counts if its item equals item_id or starts with item_id + '-'. tokens sums max(tokens, 0) so -1 and missing count as 0; seconds sums seconds with missing as 0.0; runs is the number of matching lines.
- **Errors**: ValueError if a line is not valid JSON. Missing file returns zeros.
- **Allowed imports**: json, os. Nothing else.
- **Checklist items this job serves**: Story 0002-1 items 2
- **How**: Pure read, never writes. Old lines without tokens or seconds are valid and count as zero.
- **Checks to run before reporting**:
  - `wc -l src/cost_rollup/cost_rollup.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/cost_rollup/cost_rollup.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/cost_rollup/cost_rollup.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0002-1-cost_rollup-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
