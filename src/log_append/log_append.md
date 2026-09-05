purpose: record one gate event against a work item as an event bead
signature: log_append(entry: dict) -> str
inputs: entry: dict with exactly the keys item, gate, rule, inputs, state, tokens, seconds, actor. item: the target item id. gate: Built, Proven, Verified, Validated, Ready, Board, Lesson, Correction or Backfill. tokens: int (-1 unknown). seconds: float >= 0. actor: non-empty str.
outputs: the id of the event bead created via record_run
side effects: creates an event bead in the record through the `bd` CLI
work item id: 0005-1-log_append-code
