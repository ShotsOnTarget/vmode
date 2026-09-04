---
id: "architect-sheet-assumes-cli-shape"
title: "Architect sheets assume CLI output shape instead of citing a captured example"
evidence: ["2026-09-04T12:05:50.414822+00:00", "2026-09-04T12:15:55.151771+00:00", "2026-09-04T12:39:14.402955+00:00", "2026-09-04T12:42:57.844471+00:00"]
cost: 1075796
created: "2026-09-04T13:51:35.150162+00:00"
last_used: "2026-09-04T13:51:35.150162+00:00"
times_used: 0
---
## Pattern

Instruction sheets for jobs that wrap a CLI or library repeatedly describe the output shape from memory or assumption rather than a captured example, and the mismatch is only caught when the test job fails. record_run was reopened once because its sheet said the show case returns a dict when the tool returns a list (2026-09-04T12:05:50.414822+00:00). record_create_item was reopened three separate times for the same underlying reason under different guises: a missing --no-inherit-labels flag surfaced only because a child inherited a label the sheet never mentioned (2026-09-04T12:15:55.151771+00:00); a probe that would have caught the next issue had its failing output redirected away so the wrong shape reached the sheet anyway (2026-09-04T12:39:14.402955+00:00); and the sheet then described the dependency shape returned by one command while the test used a different command that returns a different shape (2026-09-04T12:42:57.844471+00:00). Each reopen restarts a full Built and Proven cycle for both the code job and the test job.

## Fix

Add a rule to roles/architect/SKILL.md, under "Before you release a Story", that any sheet describing the output shape of a CLI or library call (dict vs list, field names, nesting) must name the exact command a probe captured that shape from, and that a probe used to justify a sheet must never have its output discarded or redirected away before the Architect reads it.
