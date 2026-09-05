import subprocess


def _run(repo, *args):
    return subprocess.run(args, cwd=repo, capture_output=True, text=True)


def commit_job(job_id: str, folder: str, repo: str = ".") -> str | None:
    """Stage and commit exactly one function folder after it passes Built and Proven."""
    add = _run(repo, "git", "add", "--", f"src/{folder}")
    if add.returncode != 0:
        raise RuntimeError(add.stderr)

    diff = _run(repo, "git", "diff", "--cached", "--quiet")
    if diff.returncode == 0:
        return None
    if diff.returncode != 1:
        raise RuntimeError(diff.stderr)

    message = f"{folder}: job {job_id} passed Built and Proven\n\nJob: {job_id}"
    commit = _run(repo, "git", "commit", "-m", message)
    if commit.returncode != 0:
        raise RuntimeError(commit.stderr)

    rev = _run(repo, "git", "rev-parse", "HEAD")
    return rev.stdout.strip()
