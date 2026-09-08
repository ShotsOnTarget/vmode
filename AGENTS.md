# AGENTS.md

Orientation and setup for anyone — person or agent — working in this repo.

## What this is

A tiered agentic workflow. Work goes down a "V" (Intent -> Story -> job pairs -> code)
and back up (tests -> gates -> Verification -> Validation). Five roles do the work:
Board, Architect, Engineer, Supervisor, Builder, plus an Analyst that learns from the log.

`policy/policy.md` is the authority on who does what and what counts as done.
Read it before acting in any role. It names no tools on purpose; this file names them.

## Where things live

| Path | What |
|---|---|
| `policy/policy.md` | The rules. The only source of truth for process. |
| `roles/` | One folder per role, in Agent Skills format (`SKILL.md`). |
| `roles/manifest.json` | Which model tier each role gets. The only place model names appear. |
| `roles/board.toml` | The columns: kinds, states, WIP, poll interval, tier, adapter. |
| `roles/work-record/SKILL.md` | The only sanctioned way to read or write the record. |
| `src/<function>/` | One public function per folder: the code and its tests. Nothing else. |
| `tools/` | `check.py` (the one gate check), `run_puller.py` (starts a puller). |
| `work/` | Summaries, transcripts, puller logs. Not the record. |
| `.dolt-data/` | The record's database files. Runtime state, not in git. |

## Setup

Two servers must be up before anything works.

1. **The record** (Dolt, port 3306), started from `.dolt-data`, which holds the `vm` database:

   ```
   dolt sql-server --config .dolt-data/config.yaml
   ```

   Run it from inside `.dolt-data`. Do not use `bd dolt start` — that serves
   `.beads/dolt`, a different and empty data directory, and every call then fails
   with `database "vm" not found`.

2. **The board** (HTTP, port 8080):

   ```
   just board
   ```

   Then open http://127.0.0.1:8080/columns.

Set `VMODE_BD` to the full path of the bd 1.0 client (`C:/Users/steve/code/bin/bd.exe`
on this machine). The justfile does this for you. A different `bd` on PATH cannot read
this record and every call fails.

Python runs with `PYTHONPATH=src` from the repo root.

## Running the loop

```
just loop          # Supervisor, one Engineer puller, one Analyst puller
just builders 2    # N Builder pullers, default 2
just stop          # every puller stops at its next poll
```

Each puller runs in its own window and outlives the shell that started it.

## Checks

```
pytest                        # the suite; -m integration for tests that touch the record
python tools/check.py src/<name> [job_id]   # the one check the Built gate runs
```

`tools/check.py` prints the failed rule names exactly as the gates name them and exits 1
if there are any. Run it per folder, never across the whole tree.

## Code shape

Flat, one function per folder, enforced by tools at the Built gate:

```
src/add_numbers/
  add_numbers.py        the code
  test_add_numbers.py   the tests
```

Folder name, file name and function name are the same. Exactly two files, never a third.
Nothing nested below. The public function carries a docstring saying what it is for,
what goes in, what comes out, and what else it touches. Limits (line length, complexity,
argument count) live in `pyproject.toml`, not in policy.

## Working here

- Every code change names the work item id it serves. A change with no id is rejected.
- Stories and Intents live only in the record, never drafted in a file.
- Never edit the record's files by hand, and never delete an item — set its state instead.
- After editing `roles/manifest.json`, run `python roles/gen_wrappers.py`. Never edit
  the generated wrappers under `.claude/`, `.opencode/` or `.pi/` by hand.
