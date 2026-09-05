import subprocess


def puller_pids() -> set[str]:
    """Process ids of every running puller on this machine, as strings.

    Reads the process table (Windows wmic) and keeps python processes whose
    command line names run_puller. Used to tell a live claim from a dead one.
    Returns an empty set when the table cannot be read, which releases
    nothing: the safe direction.
    """
    try:
        out = subprocess.run(
            [
                "wmic",
                "process",
                "where",
                "name='python.exe'",
                "get",
                "processid,commandline",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return set()
    pids = set()
    for line in out.splitlines():
        if "run_puller" in line:
            parts = line.split()
            if parts and parts[-1].isdigit():
                pids.add(parts[-1])
    return pids
