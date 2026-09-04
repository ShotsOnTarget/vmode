# Instruction sheet

- **Job id**: 0002-4-proposal_check-code
- **Kind**: code
- **Parent Story**: 0002-4
- **Function name**: `proposal_check`
- **Folder**: `src/proposal_check/`
- **Files you may change**: `src/proposal_check/proposal_check.py`, `src/proposal_check/proposal_check.md`
- **Signature**: `proposal_check(item: dict) -> list[str]`
- **Inputs**: item: a dict as returned by record_show_item, with keys id, kind, title, owner, state, parent, sheet. Only kind and sheet are read.
- **Outputs**: list of rule names broken, in this fixed order, empty if none: 'not_proposal' (kind != 'proposal'), 'no_page' (no line starting 'page: ' with a non-empty value before the '---' line), 'no_target' (no 'target: ' line), 'bad_target' (target does not start with 'roles/' or 'policy/', or contains '..'), 'no_diff' (nothing after the first line that is exactly '---'), 'multi_file' (the diff has a number of lines starting with '+++ ' other than exactly one), 'target_mismatch' (the single '+++ ' line's path, after stripping a leading 'b/', is not equal to target).
- **Errors**: none. A missing sheet key is treated as an empty sheet.
- **Allowed imports**: none. Nothing else.
- **Checklist items this job serves**: Story 0002-4 items 1, 2, 3, 4
- **How**: Pure function over the sheet text described in roles/shared/proposal-format.md. Split the sheet at the first line that is exactly '---'; header lines before it, diff after it.
- **Checks to run before reporting**:
  - `wc -l src/proposal_check/proposal_check.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/proposal_check/proposal_check.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/proposal_check/proposal_check.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0002-4-proposal_check-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
