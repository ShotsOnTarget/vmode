# 0003-5 comparison: hand-run Story 0002-2 vs unattended Story 0001-6

Both are Low care Stories built on 2026-09-04. 0002-2 had four pairs run by a person acting as Supervisor. 0001-6 had two pairs run by pullers through the Claude Code adapter, gated by prove_once, committed by commit_job.

| | 0002-2 hand-run | 0001-6 unattended |
|---|---|---|
| Pairs | 4 | 2 |
| Builder runs | 8 | 4 (plus 1 wasted on a stale-state job, plus 2 failed passes that ran no Builder) |
| Tokens counted | 943,990 | 13,880,272 |
| Lines code+test | 305 | 149 |
| Tokens per line | 3,095 | 93,156 |
| Retries | 0 | 0 real; 1 false bounce by the gate, cleared |
| Human actions inside the run | every gate, every state change, every commit | none between the tick commands and this verification |

Every difference in one line each:

1. Tokens per line is far higher in the unattended run because the harness reports the true billed figure including cache reads on every turn (about 105k per turn), while the hand-run figures came from the subagent tool's summary which counts only the run's own tokens. The two columns are not comparable and the 0002-5 target must be restated on the harness figure once every Story is measured the same way.
2. Two passes ran no Builder at all (claim slot collision, then executable lookup); both defects were invisible to unit tests and only a live pass found them.
3. The gate produced one false bounce (working tree read too widely) which cost no Builder run but did cost a Supervisor reopen.
4. One Builder run was wasted on a job left in state ready by hand gating; the puller cannot know a person already checked it.
5. The Story moved to the verify column on the second tick, not the first, because prove_once reads the graph before it moves jobs.
6. No item leaked into the live record and no person committed code.

Target for 0002-5: 3,826 tokens per line was set on the summary figures. On harness figures the baseline does not exist yet. Decision for the Board: adopt the harness figure as the only cost figure from now on, and let 0002-5 close on the next unattended Story measured against 0001-6's 93,156.
