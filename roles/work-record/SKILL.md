---
name: work-record
description: The one way any role reads or writes the work record. Use whenever a role skill says read the record, fetch a sheet, set state, set owner, add a note, or list ready work.
---

# Work record

Every work item lives here. This skill is the only place that knows what the record is. Field mapping is in `CONVENTIONS.md` next to this file.

Requirements: a running record server (see Setup) and the repo root as working directory. All commands run with no network and no credentials.

## The seven operations

Each is one Python call, or one command line. Output is always JSON.

| Operation | Python | Command line |
|---|---|---|
| Create item | `record_create_item(kind, title, owner, parent=None)` | `python -c "from record_create_item.record_create_item import *; import json,sys; print(json.dumps(record_create_item(*sys.argv[1:])))" KIND TITLE OWNER [PARENT]` |
| Add link | `record_add_link(link, src, dst)` | same shape with `record_add_link` |
| List ready | `record_list_kind(kind)` then keep items with state `ready` | same shape with `record_list_kind` |
| Show item | `record_show_item(item_id)` | same shape with `record_show_item` |
| Set state | `record_set_state(item_id, state)` | same shape with `record_set_state` |
| Set owner | `record_set_owner(item_id, owner)` | same shape with `record_set_owner` |
| Add note | `record_add_note(item_id, text)` | same shape with `record_add_note` |

Run Python with `PYTHONPATH=src` from the repo root. The command-line form is for harnesses without a Python tool; the Python form is preferred.

Values: kind is one of intent, story, code, test, verification, validation. link is one of parent_of, needs_first, checks. state is one of waiting, ready, in_progress, blocked, checking, done, reopened. Anything else is rejected before touching the record.

## Fetching your instruction sheet

A Builder given job id X runs `record_show_item(X)` and reads the `sheet` field. That is the whole instruction sheet. Nothing else is needed.

## Traces

`record_graph()` loads the whole record once. `trace_back(id, graph)`, `trace_forward(id, graph)` and `find_orphans(graph)` are pure functions over it. `python -m find_orphans.find_orphans` exits non-zero if any orphan exists.

## Setup

The record runs on a local Dolt server. Start it once per machine session from the repo root:

```
dolt sql-server --host 127.0.0.1 --port 3306 --data-dir .dolt-data
```

The client is bd 1.0. Set `VMODE_BD` to its full path (on this machine `C:/Users/steve/code/bin/bd.exe`; the justfile does it) so every shell and harness resolves the same client; a different bd on PATH cannot read this record and every call fails.

First time only, in the repo root: `bd init --prefix vm --non-interactive --server --server-port 3306`.

## Never

Never call the underlying tool directly from a role skill. Never edit the record's files by hand. Never delete an item; set its state instead.
