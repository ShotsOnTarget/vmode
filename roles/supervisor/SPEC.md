# Supervisor specification

The Supervisor is code, not a model. It never uses judgement. This spec is what that code must do. The rules come from `../../policy/policy.md`, sections 4, 6, 7 and 10.

## Responsibilities

1. Pick the next job. Only jobs whose "needs first" links are all done.
2. Run the Ready gate on a Story before any job under it is handed out.
3. Hand one job to one Builder with its instruction sheet.
4. Run the Built and Proven gates on each returned job.
5. Count retries per pair. On the third failure, block and escalate.
6. Tell the Architect when a Story is ready to verify.
7. Tell the Board when an Intent is ready to validate.
8. Check trace back and trace forward at every gate. Any orphan fails the gate.
9. Write a log entry for every decision.

## States

waiting, ready, in progress, blocked, checking, done, reopened.

## Gate rules, as the code checks them

| Gate | Checks |
|---|---|
| Ready | Story has an Intent parent. Every checklist item has a check method. Every code job has a paired test job with the same function name. No orphans. |
| Built | Only the named files changed. Size and shape checker passes. Note file has the six required lines. Work item id present. |
| Proven | Test runner passes. Every named case is present in the test file. |
| Verified | Architect has recorded a tick on every checklist item. |
| Validated | Board has recorded yes. For High care, a "shown" entry exists in the log. |

## Failure rules

| Event | Action |
|---|---|
| Built or Proven gate fails | Return to the same Builder with the failing rule. Retry count +1. |
| Retry count reaches 3 | State: blocked. Send Architect a summary in `../shared/summary-format.md`. Reset count when the Architect changes the sheet. |
| Architect marks it unfixable | Send Board a summary. |
| Left-side item edited | Reopen every item that checks it. |

## Log entry

One line of structured data per decision: timestamp, work item id, gate, rule checked, raw inputs (tool output, test output, retry count), resulting state, tokens, seconds. Append only.

Cost fields: `tokens` is the total tokens the harness reports for the Builder run that produced the decision (input plus output), `seconds` its wall time. Gate decisions with no Builder run carry tokens 0 and seconds 0.0. A run whose cost the harness did not report is logged with tokens -1, never omitted. `cost_rollup` sums per item, per Story, per Intent by id prefix.

## What the Supervisor never does

Decide scope. Write or edit an instruction sheet. Read code for meaning. Summarise with judgement. Skip a gate. Delete a log line.
