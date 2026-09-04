"""One-off: load Intents 0001 and 0002 into the record through the wrappers.

Run from repo root with PYTHONPATH=src. Idempotent only in the sense that a
second run creates duplicates, so run once on an empty record.
"""

import sys
from record_create_item.record_create_item import record_create_item as create
from record_add_link.record_add_link import record_add_link as link
from record_set_state.record_set_state import record_set_state as set_state
from record_add_note.record_add_note import record_add_note as note

ARCH, BOARD, SUP = "architect", "board", "supervisor"

INTENTS = {
    "0001 work tracking system": {
        "care": "High",
        "state": "checking",
        "stories": {
            "0001-1 the record exists and holds the six kinds": (
                "done",
                [
                    "record_run",
                    "record_init",
                    "record_create_item",
                    "record_add_link",
                    "record_set_state",
                    "record_list_kind",
                ],
            ),
            "0001-2 trace both ways and find orphans": (
                "done",
                ["record_graph", "trace_back", "trace_forward", "find_orphans"],
            ),
            "0001-3 the Board screen": ("in_progress", []),
            "0001-4 agents read and write the record through one skill": (
                "done",
                ["record_show_item", "record_set_owner", "record_add_note"],
            ),
            "0001-5 the log": ("done", ["log_append", "log_read_item"]),
        },
    },
    "0002 the Analyst": {
        "care": "High",
        "state": "waiting",
        "stories": {
            "0002-1 cost is recorded": ("waiting", ["cost_rollup"]),
            "0002-2 the wiki exists and has a shape": (
                "waiting",
                ["wiki_write", "wiki_read", "wiki_touch", "wiki_stale"],
            ),
            "0002-3 the Analyst role skill": ("waiting", []),
            "0002-4 proposals pass a gate": ("waiting", ["proposal_check"]),
            "0002-5 first measured loop": ("waiting", []),
        },
    },
}


def main():
    ids = {}
    for ititle, intent in INTENTS.items():
        i = create("intent", ititle, BOARD)["id"]
        v = create("validation", f"validate {ititle[:4]}", BOARD, parent=i)[
            "id"
        ]  # parent = item it checks
        note(i, f"care level: {intent['care']}. Source: work/{ititle[:4]}-*.md")
        set_state(i, intent["state"])
        set_state(v, "waiting")
        ids[ititle[:4]] = i
        for stitle, (sstate, jobs) in intent["stories"].items():
            s = create("story", stitle, ARCH, parent=i)["id"]
            ver = create("verification", f"verify {stitle[:6]}", ARCH, parent=s)["id"]
            set_state(s, sstate)
            set_state(ver, sstate)
            for fn in jobs:
                c = create("code", f"{fn} code", SUP, parent=s)["id"]
                t = create("test", f"{fn} test", SUP, parent=c)[
                    "id"
                ]  # checks the code job
                note(c, f"sheet: work/sheets/{fn}-code.md")
                note(t, f"sheet: work/sheets/{fn}-test.md")
                set_state(c, sstate)
                set_state(t, sstate)
            ids[stitle[:6]] = s
    # needs_first between stories, from the Intent files
    for a, b in [
        ("0001-2", "0001-1"),
        ("0001-4", "0001-1"),
        ("0001-3", "0001-2"),
        ("0002-3", "0002-1"),
        ("0002-3", "0002-2"),
        ("0002-4", "0002-2"),
        ("0002-5", "0002-3"),
        ("0002-5", "0002-4"),
    ]:
        link("needs_first", ids[a], ids[b])
    print(ids)


if __name__ == "__main__":
    sys.exit(main())
