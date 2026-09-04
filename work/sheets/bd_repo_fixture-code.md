# Instruction sheet

- **Job id**: 0001-1-bd_repo_fixture-code
- **Kind**: code
- **Parent Story**: 0001-1
- **Function name**: `bd_repo` (a pytest fixture; this is shared test infrastructure, so it lives in `src/conftest.py`, not its own folder)
- **Folder**: `src/`
- **Files you may change**: `src/conftest.py`
- **Signature**: `bd_repo(tmp_path, monkeypatch) -> pathlib.Path` decorated with `@pytest.fixture`
- **Inputs**: pytest's tmp_path and monkeypatch.
- **Outputs**: yields the path of a fresh git repo where `bd` commands work, with cwd already changed to it.
- **Errors**: if the server does not accept connections within 15 seconds, fail with a clear message.
- **Allowed imports**: pytest, subprocess, socket, time, pathlib, os. Nothing else.
- **Checklist items this job serves**: Story 0001-1, all testing items depend on it.
- **How**: the embedded Dolt engine is unavailable in this bd build, so use server mode. Steps: pick a free TCP port with socket; make `tmp_path/'dolt'` and `tmp_path/'repo'`; start `dolt sql-server --host 127.0.0.1 --port <port> --data-dir <tmp_path/'dolt'>` with subprocess.Popen, stdout and stderr to DEVNULL; poll the port with socket until it accepts (max 15 s); `git init -q` in the repo dir; run `bd init --prefix vm --non-interactive --server --server-port <port>` with cwd=repo; monkeypatch.chdir(repo); yield repo; finally terminate the server process and wait for it.
- **Checks to run before reporting**:
  - `wc -l src/conftest.py`   (must print 50 or less)
  - `python -m pytest src/record_run -q`   (tests there use a fixture named bd_repo; report the result honestly, a failure inside the tests themselves is not your job, a failure inside the fixture is)
- **Out of scope**: any other file, any test, any bd command other than init.
