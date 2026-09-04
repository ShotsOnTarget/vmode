# Intent 0003: the Supervisor

- **Id**: 0003
- **What we want**: the Supervisor as code, so that no person or model runs the gates by hand any more. It picks the next job, hands it to a Builder on any harness, checks every gate by rule, counts retries, escalates, logs every decision with its cost, and triggers the Analyst.
- **Why**: two Intents have been run with a person acting as Supervisor. That person broke the rules twice (passed an unverified symptom, trusted a report instead of a diff) and copied cost figures by hand, which left gaps. A rulebook does not get tired or curious. Until it is code, the policy is not enforced, it is remembered.
- **Care level**: High. It gates everything.
- **How the Board will say yes**: shown one Story taken from Ready to Verified with no human action between the Board's start command and the Architect's verification prompt, and the log for that run compared line by line with the hand-run log for a Story of the same shape.
- **Out of scope**: the Architect, Analyst and Board roles as code. Any model call inside the Supervisor. A daemon or scheduler; each run is one tick started by a command.

## Architect decisions

**Shape.** A tick, not a process. `python -m supervise.supervise <intent_id>` reads the record and the log, does every mechanical action that is now possible, writes the log, and exits. Running it again with nothing changed does nothing. The Board or a cron starts ticks. No state lives outside the record and the log.

**Builders on any harness.** The Supervisor does not know what a harness is. It writes a dispatch file per job: job id, role, model tier, the exact command the Builder must run to fetch its sheet. A harness adapter, one tiny script per harness under `roles/adapters/`, turns a dispatch file into that harness's invocation and writes a usage file back: tokens, seconds, and the Builder's report text. The Supervisor reads usage files. That is the whole contract, and it is what keeps the policy free of tool names.

**Gates are pure functions over files and the record.** Every gate takes data and returns the list of rules broken. No gate shells out to a model. The Built gate reads the git diff, not the report.

**Failure rules are a table.** The state machine is a dict from (state, event) to (action, next state), written down in one file, tested by replaying the 0001 and 0002 logs.

**No judgement.** If a rule needs judgement to evaluate, it is not a Supervisor rule; it moves to a verification item for the Architect.

## State machine

Events come from the record, the file system, and usage files. States are the policy's seven.

| State | Event | Action | Next state |
|---|---|---|---|
| waiting | all needs_first items done and Ready gate passes | write dispatch file | ready |
| ready | tick | mark owner, in_progress | in_progress |
| in_progress | usage file present, report says done | run Built gate (code) or Built then Proven (test) | checking |
| checking | gate passes | log done; if pair complete and Story pairs all done, create verification prompt for Architect | done |
| checking | gate fails, retries < 3 | log, attach failing rule to dispatch, retry count +1 | in_progress |
| checking | gate fails, retries = 3 | write summary for Architect | blocked |
| blocked | sheet field changed | retry count 0 | waiting |
| any left-side item edited | | reopen every item that checks it | reopened |
| reopened | tick | same as waiting | ready or waiting |
| story done (all pairs Verified) | | write Analyst dispatch | unchanged |

## Board decisions needed

1. Which harness adapter is written first. Recommendation: the one this repo is being built in, then pi and opencode as Low care Stories later.
2. Whether a tick may dispatch more than one job at a time. Recommendation: yes, up to a number in the manifest, since Builders never share files.
3. Whether the Supervisor may apply an accepted proposal diff itself. Recommendation: yes; policy section 6 amended to say a diff is applied mechanically, a Builder only when a proposal is not a diff.

## Stories

### Story 0003-1: gates as pure functions

- **Parent Intent**: 0003
- **One thing it must do**: each gate is a function that takes data and returns the rules broken, with no side effects and no model.
- **Customer**: the tick (0003-4). The Architect, who can run a gate by hand on any item.
- **Supplier**: Builders.
- **Inputs**: gate_ready: a story id and the graph. gate_built: a job id, the list of files changed since the job started, the code and note file contents. gate_proven: a job id and the pytest output text plus the sheet's case names.
- **Outputs**: `list[str]` of rule names broken, empty if the gate passes. Rule names are fixed strings documented in the note file.
- **Contract**:
  - `gate_ready(story_id, graph) -> list[str]`: rules `no_intent`, `checklist_item_without_method` (needs the sheet text via the graph or a passed dict), `code_without_test`, `test_without_code`, `orphan` (reuses find_orphans).
  - `gate_built(job_id, changed: list[str], code: str, note: str) -> list[str]`: rules `file_outside_folder`, `too_many_files`, `over_50_lines`, `not_one_public_function`, `note_not_six_lines`, `note_missing_item_id`.
  - `gate_proven(job_id, pytest_output: str, cases: list[str]) -> list[str]`: rules `tests_failed`, `case_missing`, `case_extra`.
  - Pure. Same inputs, same output. No file or record access inside; the tick gathers inputs.
- **Checklist**:
  1. A story with a code job lacking its test job fails gate_ready with `code_without_test`. [testing]
  2. A job whose changed list includes a file outside its folder fails gate_built with `file_outside_folder`. [testing]
  3. A 51-line code file fails with `over_50_lines`. [testing]
  4. pytest output with a failure fails gate_proven with `tests_failed`; a missing named case with `case_missing`. [testing]
  5. Clean inputs return [] for all three. [testing]
- **Job pairs**: `gate_ready`, `gate_built`, `gate_proven`
- **Needs first**: none

### Story 0003-2: dispatch and usage files

- **Parent Intent**: 0003
- **One thing it must do**: the Supervisor hands a job to any harness through a file, and reads cost and report back through a file.
- **Customer**: harness adapters. The tick.
- **Supplier**: Builders for the two functions; the Architect writes the first adapter script and `roles/adapters/README.md`.
- **Inputs**: dispatch_write: job id, role, tier, retry count, optional failing rule text. usage_read: a job id.
- **Outputs**: dispatch_write writes `work/dispatch/<job_id>.json` with keys job, role, tier, retry, failing_rule, fetch_command, and returns the path. usage_read reads `work/usage/<job_id>.json` with keys job, tokens, seconds, report, finished_at, and returns the dict or None if absent.
- **Contract**:
  - fetch_command is the exact one-line Python command that prints the job's sheet, as in the work-record skill.
  - A dispatch file is overwritten on retry with the new retry count and failing rule.
  - usage_read validates keys and types; tokens must be int (-1 allowed), seconds float. Malformed raises ValueError.
  - The adapter contract in `roles/adapters/README.md` fits on one page and names no harness in the Supervisor code.
- **Checklist**:
  1. dispatch_write then json.load gives the six keys with the given values. [testing]
  2. usage_read on a missing file returns None. [testing]
  3. usage_read with tokens as a string raises ValueError. [testing]
  4. The first adapter script, given a dispatch file, produces a usage file after running a Builder. [showing]
  5. `roles/adapters/README.md` states the contract in under thirty lines. [looking]
- **Job pairs**: `dispatch_write`, `usage_read`
- **Needs first**: none

### Story 0003-3: the failure table

- **Parent Intent**: 0003
- **One thing it must do**: given a state and an event, return the action and next state from one table, never from code paths.
- **Customer**: the tick.
- **Supplier**: Builders.
- **Inputs**: `step(state: str, event: str, retries: int) -> tuple[str, str, int]` returning action, next state, new retry count.
- **Outputs**: exactly the table in this Intent.
- **Contract**:
  - Unknown (state, event) raises ValueError; nothing is guessed.
  - The table is a module-level dict; the function is a lookup plus the retry arithmetic.
  - Retries reset to 0 on `sheet_changed`.
  - Replaying every (state, event) sequence recorded in the 0001 and 0002 logs produces the same end states as the log shows.
- **Checklist**:
  1. checking + gate_fail with retries 2 -> retry, in_progress, 3. [testing]
  2. checking + gate_fail with retries 3 -> escalate, blocked, 3. [testing]
  3. blocked + sheet_changed -> reset, waiting, 0. [testing]
  4. Unknown pair raises ValueError. [testing]
  5. Replay of the log's recorded transitions for two named items ends in the logged state. [testing]
- **Job pairs**: `step`, `replay_log`
- **Needs first**: none

### Story 0003-4: the tick

- **Parent Intent**: 0003
- **One thing it must do**: one command advances every item under an Intent as far as the rules allow, logs each decision with cost, and exits.
- **Customer**: the Board, who starts it. A cron, later.
- **Supplier**: Builders.
- **Inputs**: an intent id. The record, the log, dispatch and usage directories, the working tree.
- **Outputs**: updated record states, new log lines, new dispatch files, verification prompts written to `work/prompts/<story_id>.md` when a Story's pairs are all done, an Analyst dispatch when a Story is Verified. Exit 0 when nothing is blocked, 2 when at least one item is blocked awaiting a person.
- **Contract**:
  - Idempotent: a second tick with no new usage files and no record changes writes no log lines and changes nothing.
  - Never calls a model. Never edits a sheet. Never reads code for meaning; it passes file contents to gates.
  - Every log line carries tokens and seconds from the usage file, or 0 for gate-only decisions.
  - The Built gate's changed-file list comes from `git status --porcelain` filtered to the job's folder, plus any other changed path, which fails the gate.
  - Dispatches at most `max_parallel` jobs from the manifest per tick.
- **Checklist**:
  1. Fixture record with one ready pair: first tick writes two dispatch files and sets in_progress; second tick writes nothing. [testing]
  2. Given usage files reporting done and a clean working tree, tick moves the pair to done and logs two Built lines and one Proven line with the usage tokens. [testing]
  3. Given a usage file and an out-of-folder change in the working tree, tick logs `file_outside_folder`, rewrites the dispatch with retry 1. [testing]
  4. After three failures the item is blocked, a summary file exists in `work/summaries/`, and exit code is 2. [testing]
  5. When all pairs of a Story are done, `work/prompts/<story>.md` exists and asks the Architect to verify by checklist. [testing]
- **Job pairs**: `tick_gather`, `tick_apply`, `supervise` (the entry point that calls both)
- **Needs first**: 0003-1, 0003-2, 0003-3

### Story 0003-5: the first unattended Story

- **Parent Intent**: 0003
- **One thing it must do**: a real Story goes from Ready to Verified with the Supervisor as code, the Board starting ticks, the Architect only answering the verification prompt.
- **Customer**: the Board.
- **Supplier**: every role.
- **Inputs**: a Low care Story with two pairs, chosen by the Architect from Intent 0002's remaining work or a small new one.
- **Outputs**: the log for that Story, and a line-by-line comparison against the hand-run log of Story 0002-2 in `work/0003-comparison.md`.
- **Contract**:
  - No human edits the record, dispatch, usage or log during the run.
  - Cost per line for the Story is entered in the 0002-5 table, closing 0002-5 if under target.
- **Checklist**:
  1. Comparison file exists and every difference is explained in one line each. [reasoning]
  2. Shown to the Board: the tick command, the dispatch files appearing, the Builders running, the verification prompt. [showing]
  3. The 0002-5 table has the row. [looking]
- **Job pairs**: none.
- **Needs first**: 0003-4

## Order

0003-1, 0003-2, 0003-3 in parallel. Then 0003-4. Then 0003-5, which also closes 0002-5.

## Status

Written 2026-09-04. Loaded into the record. Blocked on Board decisions 1 to 3 above.
