# Wiki

One file per pattern, written by the Analyst, read by the Architect before writing sheets. Never references code; evidence is log line references only.

File `wiki/<id>.md`:

```
---
id: "<id>"
title: "<short title>"
evidence: ["<log item id or ts>", "..."]
cost: <tokens wasted, int>
created: "<ISO-8601>"
last_used: "<ISO-8601>"
times_used: <int>
---
## Pattern

One paragraph: what keeps happening and why.

## Fix

One paragraph: the proposed change, naming the target file under roles/ or policy/.
```

Front matter values are JSON. Pages unused for 90 days are candidates for removal, listed by `wiki_stale`.
