# Intent 0002: the Analyst

- **Id**: 0002
- **What we want**: a fifth role, the Analyst, that learns from every journey up and down the V and turns what it learns into cheaper journeys next time.
- **Why**: Intent 0001 cost over three million tokens for about five hundred lines of code, and most retries traced back to instruction sheets. Nothing today reads the log and reports and changes how we work. Every mistake is paid for again.
- **Care level**: High. The Analyst proposes changes to skills and templates, which shape every later piece.
- **How the Board will say yes**: shown one pattern page with evidence from the 0001 log, one proposed change that came from it, the gate that approved it, and a cost table per Story before and after.
- **Out of scope**: model fine-tuning, changing the policy itself, anything the Analyst applies without a gate.

## Architect decision: role shape

| | Analyst |
|---|---|
| Tier | Cheap. It reads structured records and writes short pages. |
| Runs | After every Story is Verified, and on request from the Board. |
| Reads | The Supervisor log, Builder reports, instruction sheets, Stories, the wiki. Never code, never test files. |
| Writes | Pattern pages in the wiki. Proposal work items. Nothing else directly. |
| Never | Edits a skill, template, convention, or sheet. Talks to a Builder. Reads code. |

Why not the Supervisor: it is a rulebook and this is judgement. Why not the Architect: it is the expensive tier, it must not read Builder output, and it would be judging its own sheets.

The three layers, mapped onto what exists:

| Layer | What it is here | Owner |
|---|---|---|
| Raw | Supervisor log, Builder reports, gate results. Append-only, already exists. | Supervisor |
| Wiki | `wiki/` folder of pattern pages. Each page: pattern, evidence (log line ids), cost, proposed fix, last used. | Analyst |
| Skill | Role skills, shared templates, conventions. | Architect, changed only through gated proposals |

## Board decisions

None pending. Naming decided by the Board 2026-09-04: Analyst, not Historian.

## Stories

### Story 0002-1: cost is recorded

- **Parent Intent**: 0002
- **One thing it must do**: every job and every gate decision carries tokens used and wall time, so the Analyst can measure.
- **Customer**: the Analyst. The Board, for the before and after table.
- **Supplier**: Builders, extending the log; the Supervisor spec, extended by the Architect.
- **Inputs**: a Builder report plus the harness figures for that run: input tokens, output tokens, seconds.
- **Outputs**: two new fields on every log line, `tokens` (int) and `seconds` (float), and a function that sums them per item, per Story, per Intent.
- **Contract**:
  - `log_append` rejects a line missing either new field. Existing lines without them are read as zero.
  - `cost_rollup(path, item_id)` returns `{'item': id, 'tokens': int, 'seconds': float, 'runs': int}` for that id and every id under it by prefix.
  - Pure read, never writes.
- **Checklist**:
  1. Append without tokens or seconds is rejected. [testing]
  2. Rollup of an intent equals the sum of its stories, which equal the sum of their jobs. [testing]
  3. The Supervisor spec says where the figures come from and that a run with unknown cost is logged with tokens -1, never omitted. [looking]
  4. Intent 0001's log is back-filled from the run notes in this repo's history where the figures are known. [looking]
- **Job pairs**: `log_append` (the existing pair under 0001-5, reopened; a function has one folder), `cost_rollup`
- **Needs first**: none

### Story 0002-2: the wiki exists and has a shape

- **Parent Intent**: 0002
- **One thing it must do**: a pattern page can be created, read, and marked used, and stale pages can be listed.
- **Customer**: the Analyst writes it. The Architect reads it before writing sheets. The Board reads it when asked to approve a proposal.
- **Supplier**: Builders.
- **Inputs**: page fields: id, title, pattern (one paragraph), evidence (list of log line references), cost (tokens wasted, from the log), fix (one paragraph), created, last_used, times_used.
- **Outputs**: one markdown file per page in `wiki/` with a fixed front matter, and three functions.
- **Contract**:
  - `wiki_write(root, page: dict) -> str` writes or overwrites `<root>/<id>.md` and returns the path. Rejects a page missing any field or citing code.
  - `wiki_read(root, id) -> dict` parses it back exactly.
  - `wiki_touch(root, id, now)` sets last_used to now and increments times_used.
  - `wiki_stale(root, days, now) -> list[str]` returns ids not used in that many days. Callers pass the clock; the functions have none.
  - A page never references code. Evidence is log line references only.
- **Checklist**:
  1. Write then read returns an equal dict. [testing]
  2. Missing field rejected. [testing]
  3. Touch increments times_used and moves last_used forward. [testing]
  4. Stale lists a page older than the threshold and not a newer one. [testing]
  5. The page format is documented in `wiki/README.md` in under twenty lines. [looking]
- **Job pairs**: `wiki_write`, `wiki_read`, `wiki_touch`, `wiki_stale`
- **Needs first**: none

### Story 0002-3: the Analyst role skill

- **Parent Intent**: 0002
- **One thing it must do**: an Analyst given a Verified Story id produces pattern pages and proposals, and nothing else.
- **Customer**: the Board and the Architect, who consume what it produces.
- **Supplier**: the Architect writes `roles/analyst/SKILL.md` and the manifest entry. No code.
- **Inputs**: a Story id. Through the work-record skill: the log lines for every item under it, the Builder reports, the sheets. The wiki.
- **Outputs**: zero or more wiki pages. Zero or more proposal work items (Story 0002-4). A one-paragraph report to the Board.
- **Contract**:
  - The skill lists what the Analyst reads and forbids code and test files by name.
  - Every pattern page cites at least two log lines or it is not written.
  - Every proposal names the wiki page it comes from and the file it would change.
  - The Analyst may run on any harness; the skill names no tool.
- **Checklist**:
  1. `roles/analyst/SKILL.md` exists, same shape as the other role skills. [looking]
  2. Manifest has an analyst entry on the cheap tier and the wrapper generator emits it for all three harnesses. [looking]
  3. Run on Story 0001-1's log: produces at least one page about the label inheritance retry or the sheet errors, with cited lines. [showing]
- **Job pairs**: none. Skill and manifest are looking items.
- **Needs first**: 0002-1, 0002-2

### Story 0002-4: proposals pass a gate

- **Parent Intent**: 0002
- **One thing it must do**: a change to a skill, template, or convention proposed by the Analyst lands only after a gate.
- **Customer**: the Architect, whose sheets get better. The Board, who stays in control of the skill layer.
- **Supplier**: the Architect extends the policy section 6 gate table; Builders write the check.
- **Inputs**: a proposal work item: kind `proposal`, wiki page id, target file, the exact change as a diff in the sheet field.
- **Outputs**: an accepted proposal applied by a Builder as a normal code job, or a rejected one closed with a reason.
- **Contract**:
  - A proposal is a seventh item kind. It has a parent Story (the one it learned from) and is checked by a `validation` for High care or a `verification` for Low.
  - Low care: Architect approves. High care, or any change to a role skill: Board approves.
  - The diff must touch exactly one file, and that file must be under `roles/` or `policy/` never `src/`.
  - `proposal_check(item) -> list[str]` returns the rules broken, empty if none.
- **Checklist**:
  1. Proposal with a diff touching two files is rejected. [testing]
  2. Proposal targeting `src/` is rejected. [testing]
  3. Proposal without a wiki page id is rejected. [testing]
  4. Clean proposal returns []. [testing]
  5. Policy section 6 has a Proposal gate row and section 3 lists the seventh kind. [looking]
- **Job pairs**: `proposal_check`, `record_create_item` (reopened, seventh kind)
- **Needs first**: 0002-2

### Story 0002-5: first measured loop

- **Parent Intent**: 0002
- **One thing it must do**: one full cycle: Analyst runs on Intent 0001, at least one proposal is accepted and applied, and the next Story built after it costs less per line than 0001's average.
- **Customer**: the Board.
- **Supplier**: every role.
- **Inputs**: Intent 0001's log with costs back-filled.
- **Outputs**: a cost table per Story, before and after.
- **Contract**:
  - Cost per line = tokens across all runs for a Story divided by lines of code plus test.
  - "Less" means at least ten percent lower on the next comparable Story. If not, the Analyst writes a page about why.
- **Checklist**:
  1. Table exists with 0001 rows filled. [looking]
  2. At least one proposal from 0001 accepted and applied. [looking]
  3. Next Story's cost per line is in the table with the comparison. [showing]
- **Job pairs**: none. This is the demonstration.
- **Needs first**: 0002-3, 0002-4

## Order

0002-1 and 0002-2 in parallel. Then 0002-3 and 0002-4. Then 0002-5. First candidate patterns the Analyst should find, from the 0001 run, so the Board can check it is looking in the right place: every Builder run costs about 115k tokens regardless of size, so batching two small jobs per Builder may halve cost; three of five retries were caused by sheets or setup lines, not code; each test starts its own server at about five seconds.

## Status

0002-1 and 0002-2 started 2026-09-04 through the record: sheets live in each job's sheet field, Builders receive a job id only.
