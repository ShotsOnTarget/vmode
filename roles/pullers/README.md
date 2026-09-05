# Pullers

A puller is one loop per role: read `roles/board.toml`, list the role's columns, claim within WIP, invoke the role, store usage, move the item on. The loop is `puller` in `src/puller/`. The only harness-specific code is the `invoke` function passed to it, one file per harness in this folder.

## The invoke contract

```
invoke(item: dict, column: str) -> {"tokens": int, "seconds": float, "report": str}
```

- `item` is the graph entry: id, kind, title, owner, state, parent, checks, needs.
- `column` is the column name the item was pulled from; it says which role skill to load.
- Runs one role on one item and returns when it is finished. Blocking is fine; the puller is single-threaded on purpose.
- `tokens` is every token the harness bills for the run: input, cache creation, cache read and output (captured 2026-09-04: a trivial `claude -p` call reports about 105k cache creation tokens, which is the per-run baseline), or -1 if the harness reported nothing. `cost_usd` is included when the harness reports it. `seconds` is wall time. `report` is the role's final text, verbatim.
- Raises on failure to start or on a timeout. The puller releases the item and records the error.
- Never edits the record. The role does that through the work-record skill, or the puller does after invoke returns.

## Running

```
python tools/run_puller.py builder roles/pullers/claude_code.py work/stop
python tools/run_puller.py supervisor - work/stop
```

The supervisor puller needs no invoke; its work is `prove_once`. Touch `work/stop` to end every puller at its next poll.

## The Supervisor's release rule

The Supervisor runs from a git worktree at a released commit, never from the working tree, so a Builder's half-built function can never be imported into the gate. Create it once with `git worktree add --detach ../vmode-supervisor HEAD` and start it with `python ../vmode-supervisor/tools/run_puller.py supervisor -` from the main repo. Each pass it also keeps house (dead claims released, prune findings raised as notes), and when HEAD has moved and no job is in progress or checking it moves its worktree to HEAD and restarts itself. Builders run from the main tree; restart them after a release that changes the puller or the config.

## Adapters

| File | Harness | Notes |
|---|---|---|
| `claude_code.py` | Claude Code CLI | `claude -p` with the role's model from the manifest and JSON output for usage |
| `pi.py` | pi | not written |
| `opencode.py` | opencode | not written |
