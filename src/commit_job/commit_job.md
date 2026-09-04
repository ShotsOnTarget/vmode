Purpose: stage and commit exactly one function folder after it passes Built and Proven.
Signature: commit_job(job_id: str, folder: str, repo: str = ".") -> str | None
Inputs: job_id (record id of the job that passed its gate), folder (function folder name), repo (path of the git working tree).
Outputs: the new commit hash, or None if there was nothing to commit.
Side effects: runs `git add -- src/<folder>` and `git commit` in the given repo, creating a commit.
Work item id: 0003-4-commit_job-code
