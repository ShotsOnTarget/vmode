# Proposal

The sheet field of a proposal item. Exactly this shape.

```
page: <wiki page id>
target: <one path under roles/ or policy/>
care: low | high
---
<a unified diff touching only the target file>
```

Rules the gate checks: page present, target under `roles/` or `policy/`, diff touches exactly one file and it is the target. Any change to a file under `roles/*/SKILL.md` is high care whatever the line says.
