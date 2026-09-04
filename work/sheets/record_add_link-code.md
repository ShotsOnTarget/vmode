# Instruction sheet

- **Job id**: 0001-1-record_add_link-code
- **Kind**: code
- **Parent Story**: 0001-1
- **Function name**: `record_add_link`
- **Folder**: `src/record_add_link/`
- **Files you may change**: `src/record_add_link/record_add_link.py`, `src/record_add_link/record_add_link.md`
- **Signature**: `record_add_link(link: str, src: str, dst: str) -> dict`
- **Inputs**: link: one of parent_of, needs_first, checks. src, dst: existing ids. parent_of: src is parent, dst is child. needs_first: src needs dst done first. checks: src checks dst.
- **Outputs**: {'link': str, 'src': str, 'dst': str}.
- **Errors**: raise ValueError before calling bd if link is not one of the three. RecordError propagates.
- **Allowed imports**: from record_run.record_run import record_run, RecordError. Nothing else.
- **Checklist items this job serves**: Story 0001-1 items 5
- **How**: Commands: parent_of -> ['dep','add',dst,src,'-t','parent-child']. needs_first -> ['dep','add',src,'--blocked-by',dst]. checks -> ['dep','add',src,dst,'-t','validates'].
- **Checks to run before reporting**:
  - `wc -l src/record_add_link/record_add_link.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/record_add_link/record_add_link.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/record_add_link/record_add_link.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-1-record_add_link-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
