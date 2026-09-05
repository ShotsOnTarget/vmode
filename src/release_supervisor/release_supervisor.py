import subprocess


def _head(path: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True
    ).stdout.strip()


def _busy(graph: dict) -> bool:
    return any(
        item["kind"] in ("code", "test")
        and item["state"] in ("in_progress", "checking")
        for item in graph.values()
    )


def release_supervisor(repo: str, worktree: str, graph: dict) -> bool:
    """Move the Supervisor's worktree to the repo's HEAD when it is safe.

    Safe means: the worktree is a different path from the repo, HEAD has
    moved, and no code or test job is in progress or checking, so the
    Supervisor is not mid-gate on code its new self might read differently.
    Returns True when the worktree moved; the caller then restarts itself.
    """
    if not worktree or worktree == repo:
        return False
    head = _head(repo)
    if not head or head == _head(worktree) or _busy(graph):
        return False
    subprocess.run(
        ["git", "checkout", "-q", "--detach", head], cwd=worktree, check=True
    )
    return True
