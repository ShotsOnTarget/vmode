# Instruction sheet

- **Job id**: 0003-4-claude_code_adapter-code
- **Kind**: code (harness adapter; lives under roles/pullers, not src)
- **Parent Story**: 0003-4
- **Function name**: `invoke`
- **Folder**: `roles/pullers/`
- **Files you may change**: `roles/pullers/claude_code.py`
- **Signature**: `invoke(item: dict, column: str) -> dict`
- **Inputs**: item: graph entry. column: column name.
- **Outputs**: {'tokens': int, 'seconds': float, 'report': str, 'cost_usd': float | None} per roles/pullers/README.md. Build the command with `adapter_command(item, column, {'board': ROOT/'roles/board.toml', 'manifest': ROOT/'roles/manifest.json', 'root': str(ROOT)})` from src/adapter_command (ROOT is the repo root, two parents above this file). Run it with subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=1800, check=False). Non-zero exit -> RuntimeError with the first 500 chars of stderr. Parse stdout as JSON; tokens = sum of input_tokens, cache_creation_input_tokens, cache_read_input_tokens, output_tokens from the usage object (captured 2026-09-04), or -1 if usage is absent; report = result field; cost_usd = total_cost_usd.
- **Errors**: RuntimeError from adapter_command (claude missing) or from a non-zero exit propagates.
- **Allowed imports**: json, subprocess, sys, time, pathlib, and `from adapter_command.adapter_command import adapter_command` after inserting ROOT/'src' on sys.path. Nothing else.
- **Checklist items this job serves**: Story 0003-4 item 8
- **How**: replace the whole file. Keep the module docstring saying this is the one file that names the harness. No PROMPT text in this file; the prompt lives in adapter_command. Under 50 lines, the policy limit.
- **Checks to run before reporting**:
  - `ruff format roles/pullers/claude_code.py` then `ruff check roles/pullers/claude_code.py` (both clean; no noqa)
  - `PYTHONPATH=src python -c "import importlib.util; s=importlib.util.spec_from_file_location('a','roles/pullers/claude_code.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(callable(m.invoke))"`   (must print True)
- **Out of scope**: any other file, running a real Builder, any behaviour not listed.
