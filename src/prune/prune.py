import os
import subprocess

from find_orphans.find_orphans import find_orphans

_OPEN = ("ready", "reopened", "in_progress", "checking")


def _changed_folders(repo: str) -> set[str]:
    cmd = ["git", "status", "--porcelain", "--untracked-files=all", "src"]
    out = subprocess.run(cmd, cwd=repo, capture_output=True, text=True).stdout
    paths = (line[3:].replace("\\", "/") for line in out.splitlines() if line)
    return {p.split("/")[1] for p in paths if p.startswith("src/") and p.count("/") > 1}


def _folders(repo: str) -> list[str]:
    src = os.path.join(repo, "src")
    names = sorted(os.listdir(src)) if os.path.isdir(src) else []
    return [n for n in names if os.path.isdir(os.path.join(src, n)) and n[0] != "_"]


def _finding(rule: str, target: str, parent: str | None) -> dict:
    return {"rule": rule, "target": target, "parent": parent}


def prune(graph: dict, repo: str) -> list[dict]:
    """Findings for the Supervisor to raise as notes: leftover_files (uncommitted
    changes in a folder with no open job; parent its code job), no_record_item
    (a src folder with no code job; parent None), and every orphan (parent itself).
    """
    jobs = {}
    for item in graph.values():
        if item["kind"] == "code" and item["title"].endswith(" code"):
            jobs.setdefault(item["title"][: -len(" code")], []).append(item)
    findings = []
    for folder in sorted(_changed_folders(repo)):
        owners = jobs.get(folder, [])
        if not any(j["state"] in _OPEN for j in owners):
            parent = owners[-1]["id"] if owners else None
            findings.append(_finding("leftover_files", folder, parent))
    findings += [
        _finding("no_record_item", f, None) for f in _folders(repo) if f not in jobs
    ]
    findings += [_finding(o["rule"], o["id"], o["id"]) for o in find_orphans(graph)]
    return findings
