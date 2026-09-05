import contextlib
import os
import subprocess
import tempfile

from pattern_touch.pattern_touch import pattern_touch
from record_run.record_run import RecordError
from record_set_state.record_set_state import record_set_state
from record_show_item.record_show_item import record_show_item


def _git(repo: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


def _apply(repo: str, diff: str) -> None:
    fd, path = tempfile.mkstemp(suffix=".diff", text=True)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(diff if diff.endswith("\n") else diff + "\n")
    try:
        check = _git(repo, "apply", "--check", path)
        if check.returncode != 0:
            raise ValueError("diff does not apply: " + check.stderr.strip()[:300])
        _git(repo, "apply", path)
    finally:
        os.remove(path)


def _commit(repo: str, target: str, message: str) -> str:
    _git(repo, "add", target)
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "--short", "HEAD").stdout.strip()


def proposal_apply(proposal_id: str, repo: str, today: str) -> dict:
    """Apply an accepted proposal: its diff lands on the target file, one
    commit names the proposal, the proposal is done and its pattern is
    touched. Returns {'id', 'target', 'commit'}. Raises ValueError when the
    diff does not apply cleanly; nothing is changed in that case."""
    item = record_show_item(proposal_id)
    if item["kind"] != "proposal":
        raise ValueError(f"not a proposal: {proposal_id}")
    header, _, diff = item["sheet"].partition("\n---\n")
    fields = dict(line.split(": ", 1) for line in header.splitlines() if ": " in line)
    _apply(repo, diff)
    message = f"{item['title']}\n\nProposal {proposal_id} accepted by the Board."
    commit = _commit(repo, fields["target"], message)
    record_set_state(proposal_id, "done")
    if fields.get("page", "").startswith("vm-"):
        with contextlib.suppress(ValueError, RecordError):
            pattern_touch(fields["page"], today)
    return {"id": proposal_id, "target": fields["target"], "commit": commit}
