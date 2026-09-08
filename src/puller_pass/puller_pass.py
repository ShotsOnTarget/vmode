import os

from record_graph.record_graph import record_graph
from record_run.record_run import RecordError
from release_supervisor.release_supervisor import release_supervisor


def _release(role: str, worktree: str) -> bool:
    if role != "supervisor":
        return False
    return release_supervisor(os.getcwd(), worktree, record_graph())


def puller_pass(role: str, run, worktree: str) -> bool:
    """One puller pass. Returns True when the Supervisor released itself and
    must restart; False otherwise.

    run() does the pass. A ValueError from it, such as a config the running
    code cannot load, tries the release first: when HEAD has moved the
    worktree follows it and the caller restarts on the new code; when it has
    not, the error propagates. A RecordError is the record itself failing for
    a moment, which is not this puller's fault and not fatal: it is printed
    and the pass ends, so the next one tries again. Before this, one such
    failure killed the Supervisor and with it every gate, silently. After a
    clean pass the release is tried too.
    """
    try:
        run()
    except ValueError:
        if _release(role, worktree):
            return True
        raise
    except RecordError as exc:
        print(f"{role}: record error, retrying next pass: {exc}", flush=True)
        return False
    return _release(role, worktree)
