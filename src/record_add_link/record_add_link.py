from record_run.record_run import record_run


def record_add_link(link: str, src: str, dst: str) -> dict:
    if link not in ("parent_of", "needs_first", "checks"):
        raise ValueError("link must be one of parent_of, needs_first, checks")

    if link == "parent_of":
        args = ["dep", "add", dst, src, "-t", "parent-child"]
    elif link == "needs_first":
        args = ["dep", "add", src, "--blocked-by", dst]
    else:
        args = ["dep", "add", src, dst, "-t", "validates"]

    record_run(args)

    return {"link": link, "src": src, "dst": dst}
