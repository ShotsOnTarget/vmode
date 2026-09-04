"""Generate thin harness wrappers from roles/manifest.json.

Each wrapper is frontmatter plus one line pointing at the role SKILL.md.
Model and harness settings live here, never in the skills.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((ROOT / "roles" / "manifest.json").read_text())
BODY = "Load and follow the skill at `roles/{name}/SKILL.md`. Nothing else applies.\n"


def claude_code(name, role, model):
    fm = [f"name: {name}", f"description: {role['description']}"]
    if model:
        fm.append(f"model: {model.split('/')[-1]}")
    return "---\n" + "\n".join(fm) + "\n---\n" + BODY.format(name=name)


def opencode(name, role, model):
    fm = [f"description: {role['description']}", f"mode: {role['mode']}"]
    if model:
        fm.append(f"model: {model}")
    return "---\n" + "\n".join(fm) + "\n---\n" + BODY.format(name=name)


def pi(name, role, model):
    fm = [f"description: {role['description']}"]
    return "---\n" + "\n".join(fm) + "\n---\n" + BODY.format(name=name)


TARGETS = {
    ".claude/agents": claude_code,
    ".opencode/agents": opencode,
    ".pi/prompts": pi,
}


def main():
    for name, role in MANIFEST["roles"].items():
        model = MANIFEST["models"][role["model"]]
        for rel, fn in TARGETS.items():
            out = ROOT / rel / f"{name}.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(fn(name, role, model), newline="\n")
            print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
