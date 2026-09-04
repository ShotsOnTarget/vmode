# Intent 0003: the Supervisor, as a pull board

- **Id**: 0003
- **What we want**: work is pulled, not pushed. Every step down and up the V is a column on one board. Each role has a puller that watches its columns, claims one item, does it, and moves it on. The Supervisor is code that enforces gates on every move and the WIP limits per column, and logs every decision with its cost. Nobody waits on anybody.
- **Why**: two Intents were run by a person pushing jobs and waiting for them, which idled the most expensive role and broke rules twice. Pull removes the waiting structurally, WIP limits cap spend per hour, and gates on moves make the policy enforced rather than remembered.
- **Care level**: High. It gates everything.
- **How the Board will say yes**: shown the board with all columns live, a Story moving from sheet_todo to done with no human action except the Board's own column, and the config file changed live to lower a WIP limit with the effect visible on the next poll.
- **Out of scope**: any model call inside the Supervisor. The Board screen's columns view is a later Story of 0001, not here.

## Architect decisions

**The column is derived, never stored.** An item's column is a pure function of its kind, state and labels, defined by `roles/board.toml`. Moving an item means changing its state through the record. There is no second source of truth.

**One config file.** `roles/board.toml` holds, per column: which kinds and states land there, which role pulls, which model tier, WIP, and poll interval. Plus global limits: a hard cap on parallel model runs and a claim timeout. Tier names resolve to models in `manifest.json`. Changing the file changes behaviour on the next poll; no restart.

**Claim is atomic and is the only exit from a column.** A puller claims with the record's atomic claim (assignee set, state in_progress, in one operation). Two pullers cannot take the same item. A claim older than the timeout with no result returns to its column.

**Gates run on moves, by the Supervisor, never by the mover.** A Builder marks a job checking. The prove column's puller is the Supervisor: it gathers the git diff, formatter, linter, shape and test outputs and applies the gate functions. Pass moves the item to done; fail bounces it to ready with the failing rule attached and the retry count up; three fails moves it to blocked with a summary.

**Pullers are thin and harness-specific; everything else is not.** A puller is a loop: read config, list column, respect WIP, claim, invoke role, wait, release. The invoke step is the only line that knows the harness. One puller script per harness under `roles/pullers/`, each under a page. The Supervisor's own puller runs no model.

**Failure rules are a table**, as before: (state, event) to (action, next state), replayed against the 0001 and 0002 logs.

**No judgement in the Supervisor.** Anything needing judgement is a verification or validation item in a human or Architect column.

## Column flow

```
Board          Architect        Architect        Builder    Builder    Supervisor   Architect   Board       Analyst
intent_new --> story_todo  -->  sheet_todo  -->  build  -->  test  -->  prove  -->  verify  --> validate --> learn --> done
                                                   ^          ^          |
                                                   +----------+----------+  fail: back one column, retry+1; 3 fails: blocked
```

Down the V, an item is decomposed: intent to stories to job pairs. Up the V, the same items are checked: prove per job, verify per story, validate per intent. The learn column is the Analyst reading every Verified Story. The blocked column is visible to everyone and pulled by nobody.

## Board decisions

All three accepted by the Board 2026-09-04 as recommended: first puller on this harness; WIP counts claimed items only; the Supervisor applies accepted diffs itself (policy section 6 amended).

As asked:

1. First puller harness. Recommendation: the one this repo is built in, then pi and opencode as Low care Stories.
2. Whether WIP counts claimed items only, or claimed plus ready. Recommendation: claimed only; ready is a queue and queues are allowed to be long.
3. Whether the Supervisor may apply an accepted proposal diff itself. Recommendation: yes, policy section 6 amended: a diff is applied mechanically, a Builder only when a proposal is not a diff.

## Stories

### Story 0003-1: gates as pure functions

- **Parent Intent**: 0003
- **One thing it must do**: each gate is a function that takes data and returns the rules broken, with no side effects and no model.
- **Customer**: the prove puller (0003-4). The Architect, who can run any gate by hand.
- **Supplier**: Builders.
- **Inputs**: gate_ready: story id, graph, sheet texts. gate_built: job id, changed file list from git, code text, note text, formatter and linter outputs. gate_proven: job id, pytest output, sheet case names.
- **Outputs**: `list[str]` of fixed rule names, empty when the gate passes.
- **Contract**:
  - `gate_ready(story_id, graph, sheets: dict[str, str]) -> list[str]`: `no_intent`, `code_without_test`, `test_without_code`, `sheet_missing`, `orphan`.
  - `gate_built(job_id, changed, code, note, fmt_out, lint_out) -> list[str]`: `file_outside_folder`, `too_many_files`, `over_50_lines`, `not_one_public_function`, `note_not_six_lines`, `note_missing_item_id`, `not_formatted`, `lint_findings`.
  - `gate_proven(job_id, pytest_output, cases) -> list[str]`: `tests_failed`, `case_missing`, `case_extra`.
  - Pure. The puller gathers inputs; gates never touch files or the record.
- **Checklist**:
  1. Code job without a test job fails gate_ready with `code_without_test`. [testing]
  2. Changed list with a file outside the folder fails gate_built with `file_outside_folder`. [testing]
  3. Non-empty formatter diff fails with `not_formatted`; non-empty lint output with `lint_findings`. [testing]
  4. Failing pytest output fails gate_proven with `tests_failed`; missing named case with `case_missing`. [testing]
  5. Clean inputs return [] for all three. [testing]
- **Job pairs**: `gate_ready`, `gate_built`, `gate_proven`
- **Needs first**: none

### Story 0003-2: the board config and column functions

- **Parent Intent**: 0003
- **One thing it must do**: the config file is loaded and validated, and any item's column, any column's contents, and WIP headroom can be computed from it.
- **Customer**: every puller. The Board screen later.
- **Supplier**: Builders. The Architect owns `roles/board.toml`.
- **Inputs**: the TOML file; the graph; for claims, an item id and an owner.
- **Outputs**: `board_config(path) -> dict` validated: every column has kinds, states, role, tier, wip int > 0, poll_seconds int >= 0; tier is one of the manifest's tiers or none; unknown key or missing field raises ValueError. `column_of(item, config) -> str | None`: the single column whose kinds, states and label rules match, None if no column, ValueError if more than one. `column_items(name, graph, config) -> list[dict]`: items in that column, needs_first satisfied first, then by id. `wip_headroom(name, graph, config) -> int`: wip minus items in the column claimed (state in_progress with that column's kinds), never negative. `claim_item(item_id, owner) -> dict`: atomic claim through the record; raises RecordError if already claimed.
- **Contract**:
  - Two columns matching one item is a config error, raised at load, not at runtime.
  - `column_items` never returns an item whose needs_first has an unfinished item.
  - `claim_item` uses the record's atomic claim; it never reads then writes.
  - Config is re-read on every call that takes a path; pullers pass the path, so edits take effect on the next poll.
- **Checklist**:
  1. The shipped `roles/board.toml` loads clean. [testing]
  2. A config with two columns matching (code, ready) raises ValueError at load. [testing]
  3. A story in state waiting maps to sheet_todo; a test in state ready maps to test; a story done with label learned maps to None. [testing]
  4. column_items excludes an item whose needs_first target is not done. [testing]
  5. wip_headroom is 0 when claimed items equal wip, and never negative. [testing]
  6. Two claim_item calls on one item: the second raises. [testing]
- **Job pairs**: `board_config`, `column_of`, `column_items`, `wip_headroom`, `claim_item`
- **Needs first**: none

### Story 0003-3: the failure table

- **Parent Intent**: 0003
- **One thing it must do**: given a state and an event, return the action and next state from one table, never from code paths.
- **Customer**: the prove puller.
- **Supplier**: Builders.
- **Inputs**: `step(state: str, event: str, retries: int) -> tuple[str, str, int]`.
- **Outputs**: action, next state, new retry count, from a module-level table.
- **Contract**:
  - Unknown (state, event) raises ValueError.
  - checking + gate_pass -> done. checking + gate_fail with retries < 3 -> ready, retries + 1. checking + gate_fail with retries 3 -> blocked. blocked + sheet_changed -> waiting, retries 0. in_progress + claim_timeout -> ready, retries unchanged. Any left-side item + edited -> reopened for each checker.
  - `replay_log(path, item_id) -> str` replays the log's events for an item through step and returns the end state; for every item in the 0001 and 0002 logs it equals the logged end state.
- **Checklist**:
  1. checking + gate_fail, retries 2 -> ready, 3. [testing]
  2. checking + gate_fail, retries 3 -> blocked. [testing]
  3. blocked + sheet_changed -> waiting, 0. [testing]
  4. Unknown pair raises. [testing]
  5. replay_log agrees with the log for two named items. [testing]
- **Job pairs**: `step`, `replay_log`
- **Needs first**: none

### Story 0003-4: pullers

- **Parent Intent**: 0003
- **One thing it must do**: one loop per role that watches its columns, claims within WIP, invokes the role on the harness, and hands the result to the Supervisor's prove column.
- **Customer**: the Board, who starts pullers. A cron, later.
- **Supplier**: Builders for the loop and the prove logic; the Architect writes the first harness invoke script and `roles/pullers/README.md`.
- **Inputs**: a role name and the config path. For prove: the working tree, tool outputs, the log.
- **Outputs**: `pull_once(role, config_path, invoke) -> list[str]`: one pass over the role's columns, returning the ids it claimed; `invoke` is a function (item, column) -> usage dict {tokens, seconds, report}, injected so the loop knows no harness. `prove_once(config_path) -> list[str]`: for every job in prove, gather inputs, run gates, apply step, write the log line with cost from the usage the puller stored on the item as a note, move the item. `puller(role, config_path)`: loops pull_once every poll_seconds for that role's columns until a stop file exists.
- **Contract**:
  - pull_once claims at most wip_headroom items per column and never more than the global model-run cap across columns.
  - Every claim is followed by exactly one of: a note with usage and a move to checking, or a release back to ready on invoke failure.
  - prove_once is idempotent: with no items in prove it writes nothing.
  - The Supervisor's puller runs no model; its invoke is prove_once.
  - The invoke script for a harness is under a page and is the only file that names the harness.
- **Checklist**:
  1. Fixture record, build column with two ready jobs, wip 1: pull_once claims one; second pull_once claims none while the first is in progress. [testing]
  2. A fake invoke returning usage: the item ends in checking with a usage note. [testing]
  3. A fake invoke raising: the item is back in ready, unclaimed. [testing]
  4. prove_once on a job with a clean tree and passing tests moves it to done and logs Built and Proven lines carrying the usage tokens. [testing]
  5. prove_once on a job whose tree has an out-of-folder change bounces it to ready with retry 1 and the rule in the log. [testing]
  6. Three bounces put it in blocked with a summary file in `work/summaries/`. [testing]
  7. Lowering wip in the config file between two pull_once calls reduces claims on the second call. [testing]
  8. The first harness invoke script, given a real ready job, runs a Builder and stores usage. [showing]
- **Job pairs**: `pull_once`, `prove_once`, `puller`
- **Needs first**: 0003-1, 0003-2, 0003-3

### Story 0003-5: the first unattended Story

- **Parent Intent**: 0003
- **One thing it must do**: a real Story goes from sheet_todo to done with pullers running for Builder, Supervisor and Architect, the Board touching only its own column.
- **Customer**: the Board.
- **Supplier**: every role.
- **Inputs**: a Low care Story with two pairs, chosen by the Architect.
- **Outputs**: the log for that Story and `work/0003-comparison.md` comparing it line by line with the hand-run log of Story 0002-2.
- **Contract**:
  - No human edits the record or the log during the run.
  - Cost per line for the Story goes in the 0002-5 table, closing 0002-5 if under target.
  - During the run the Board lowers one WIP limit in the config and the next poll respects it.
- **Checklist**:
  1. Comparison file exists; every difference explained in one line. [reasoning]
  2. Shown: pullers starting, the board columns changing, the WIP edit taking effect, the verification appearing in the Architect column. [showing]
  3. The 0002-5 table has the row. [looking]
- **Job pairs**: none.
- **Needs first**: 0003-4

## Order

0003-1, 0003-2, 0003-3 in parallel. Then 0003-4. Then 0003-5, which also closes 0002-5.

## Status

Rewritten 2026-09-04 for pull. Config at `roles/board.toml`. Loaded into the record. Board decisions 1 to 3 accepted; 0003-2 and 0003-4 unblocked.
