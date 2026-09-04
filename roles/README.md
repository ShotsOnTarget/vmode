# Roles

One folder per role, written once in the Agent Skills format (`SKILL.md`), usable unchanged by Claude Code, pi, opencode and any other harness that reads the standard.

- `board/`, `architect/`, `builder/`: skills. They point at `policy/policy.md` and never restate it.
- `supervisor/SPEC.md`: the Supervisor is code, not a model. This is what the code must do.
- `shared/`: the templates every role fills in or reads.
- `manifest.json`: which model and mode each role gets. The only place model names appear.
- `gen_wrappers.py`: writes thin wrappers into `.claude/agents/`, `.opencode/agents/` and `.pi/prompts/`. Run it after editing the manifest. Never edit the wrappers by hand.

```
python roles/gen_wrappers.py
```
