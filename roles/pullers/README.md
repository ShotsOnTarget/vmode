# Pullers

A puller is one loop per role: read `roles/board.toml`, list the role's columns, claim within WIP, invoke the role, store usage, move the item on. The loop is `puller` in `src/puller/`. The only harness-specific code is the `invoke` function passed to it, one file per harness in this folder.

## The invoke contract

```
invoke(item: dict, column: str) -> {"tokens": int, "seconds": float, "report": str}
```

- `item` is the graph entry: id, kind, title, owner, state, parent, checks, needs.
- `column` is the column name the item was pulled from; it says which role skill to load.
- Runs one role on one item and returns when it is finished. Blocking is fine; the puller is single-threaded on purpose.
- `item` may carry `harness` and `model` (set by `by_column.py` from `run_choice`); an adapter uses that model when present.
- `tokens` is every token the harness bills for the run: input, cache creation, cache read and output (captured 2026-09-04: a trivial `claude -p` call reports about 105k cache creation tokens, which is the per-run baseline), or -1 if the harness reported nothing. `cost_usd` is included when the harness reports it. `seconds` is wall time. `report` is the role's final text, verbatim.
- Raises on failure to start or on a timeout. The puller releases the item and records the error.
- `turns`, `harness` and `model` are included when known; the Supervisor writes them into the Built event so cost can be compared per model.
- Never edits the record. The role does that through the work-record skill, or the puller does after invoke returns.

## Running

```
python tools/run_puller.py builder roles/pullers/claude_code.py work/stop
python tools/run_puller.py supervisor - work/stop
```

The supervisor puller needs no invoke; its work is `prove_once`. Touch `work/stop` to end every puller at its next poll.

## The Supervisor's release rule

The Supervisor runs from a git worktree at a released commit, never from the working tree, so a Builder's half-built function can never be imported into the gate. Create it once with `git worktree add --detach ../vmode-supervisor HEAD` and start it with `python ../vmode-supervisor/tools/run_puller.py supervisor -` from the main repo. Each pass it also keeps house (dead claims released, prune findings raised as notes), and when HEAD has moved and no job is in progress or checking it moves its worktree to HEAD and restarts itself. Builders run from the main tree; restart them after a release that changes the puller or the config.

Run pullers as detached processes (`just loop`, `just builders`, `just board`), never as background tasks of an agent session: a session ends or interrupts its own tasks and the pullers die with it. The justfile exports the record client path (`VMODE_BD`); a shell that starts a puller by hand must set it too, or every record call fails. Each puller writes to `work/puller-<role>.log` and `.err`; `just stop` (a file at `work/stop`) ends them all at their next poll.

## Adapters

| File | Harness | Notes |
|---|---|---|
| `by_column.py` | picks per run | `run_choice`: item labels `harness:<name>` / `model:<provider/model>`, then the column's `adapter` and tier, then the manifest; the runner's default |
| `opencode.py` | opencode CLI | `opencode run --format json`; model per tier from `opencode_models` in roles/manifest.json; tokens, turns and cost from its `step_finish` events |
| `claude_code.py` | Claude Code CLI | `claude -p` with the role's model from the manifest and JSON output for usage |
| `pi.py` | pi | not written |

## Choosing the model

Three places, most specific wins. A label on the item (`harness:opencode`, `model:opencode/glm-5.3-flash`) is how a role picks in process for one item: `bd label add <id> model:<provider/model>`. The column's `adapter` and `tier` in roles/board.toml pick for a column. The manifest maps a tier to a model per harness (`models` for Claude Code, `opencode_models` for opencode). `opencode models` lists what opencode can run; the `-free` ones cost nothing and report cost 0, tokens still counted. The Zen paid models need a payment method on the opencode workspace (that was the 401 in the first probe).
