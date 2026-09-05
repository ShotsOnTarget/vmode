purpose: replay an old JSON-lines gate log into the record as event beads
signature: log_migrate(path: str) -> int
inputs: path: the old JSON-lines log file (keys ts, item, gate, rule, inputs, state, and optionally tokens, seconds)
outputs: the number of events created, one per line, via log_append with actor 'migrated' (or inputs['actor'] when present), tokens defaulting to -1 and seconds to 0.0; the original ts is kept inside the payload under 'ts_original'
side effects: creates one event bead per valid line through log_append; raises ValueError on a malformed line before creating an event for it, leaving earlier events created
work item id: 0005-1-log_migrate-code
