import subprocess


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
    """List changed src paths for this job's folder from git status, excluding paths
    claimed by other in-progress or checking jobs.
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
        if not path.startswith("src/"):
            continue
        parts = path.split("/")
        owner = parts[1] if len(parts) > 1 else ""
        if owner in claimed:
            continue
        kept.append(path)
    return sorted(kept)
