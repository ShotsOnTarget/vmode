def sheet_skeleton(job: dict) -> str:
    """Build the instruction sheet text for one code or test job.

    Inputs: job, a dict with id, kind, parent, title, and optional serves.
    Outputs: the sheet text with one trailing newline.
    Side effects: none. Raises ValueError on bad kind, title, or ids.
    """
    job_id = job.get("id")
    kind = job.get("kind")
    parent = job.get("parent")
    title = job.get("title")
    serves = job.get("serves") or []
    suffix = f" {kind}"
    if isinstance(title, str) and title.endswith(suffix):
        function = title[: -len(suffix)]
    else:
        function = ""
    valid = all(
        [
            isinstance(job_id, str) and job_id != "",
            isinstance(parent, str) and parent != "",
            kind in ("code", "test"),
            function != "" and " " not in function,
        ]
    )
    if not valid:
        raise ValueError("bad job")
    serves_text = ", ".join(serves)
    lines = [
        "# Instruction sheet",
        "",
        f"- **Job id**: {job_id}",
        f"- **Kind**: {kind}",
        f"- **Parent Story**: {parent}",
        f"- **Function name**: `{function}`",
        f"- **Folder**: `src/{function}/`",
        "- **Signature**: ",
        "- **Inputs**: ",
        "- **Outputs**: ",
        f"- **Checklist items this job serves**: {serves_text}",
    ]
    if kind == "test":
        lines.append("- **Cases**:")
    return "\n".join(lines) + "\n"
