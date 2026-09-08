import subprocess

# what the pipeline writes about itself: never a job's doing
_RUNTIME = (".beads/", ".claude/", ".dolt-data/", ".opencode/", ".pi/", "work/")


def _claimed_folders(folder, graph):
    claimed = set()
    for item in graph.values():
        active = item.get("kind") in ("code", "test") and item.get("state") in (
            "ready",
            "reopened",
            "in_progress",
            "checking",
        )
        other = (item.get("title") or "").split(" ", 1)[0]
        if active and other and other != folder:
            claimed.add(other)
    return claimed


def _parse_porcelain(output):
    rests = (line[3:] for line in output.splitlines() if line)
    return [
        (r.split(" -> ", 1)[1] if " -> " in r else r).replace("\\", "/") for r in rests
    ]


def changed_paths(folder: str, graph: dict, repo: str = ".") -> list[str]:
    """List every path this job changed, from git status.

    Reports whatever the working tree shows as changed, wherever it lives, so
    the Built gate can judge it: filtering is not judging, and a path dropped
    here is one no gate can ever see. Excluded are only the directories the
    pipeline writes about itself, and src folders claimed by another job.
    """
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    claimed = _claimed_folders(folder, graph)
    paths = _parse_porcelain(result.stdout)
    kept = []
    for path in paths:
        if path.startswith(_RUNTIME):
            continue
        parts = path.split("/")
        src = path.startswith("src/") and len(parts) > 1
        if src and parts[1] in claimed:
            continue
        kept.append(path)
    return sorted(kept)
