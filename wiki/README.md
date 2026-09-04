# Wiki

One file per pattern. The Analyst writes, the Architect reads before writing sheets. Evidence is log line references only, never code.

File `wiki/<id>.md`: front matter between `---` lines, one `key: <json>` line each for id, title, evidence, cost, created, last_used, times_used; then:

```
## Pattern

One paragraph: what keeps happening and why.

## Fix

One paragraph: the change, naming a file under roles/ or policy/.
```

Pages unused for 90 days are listed by `wiki_stale` for removal.
