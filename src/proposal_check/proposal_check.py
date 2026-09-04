def proposal_check(item: dict) -> list[str]:
    broken = []
    if item.get("kind") != "proposal":
        broken.append("not_proposal")

    lines = (item.get("sheet") or "").splitlines()
    split_index = next((i for i, l in enumerate(lines) if l == "---"), None)
    header = lines if split_index is None else lines[:split_index]
    diff = [] if split_index is None else lines[split_index + 1 :]

    if not any(l.startswith("page: ") and l[len("page: ") :].strip() for l in header):
        broken.append("no_page")

    target = next(
        (l[len("target: ") :].strip() for l in header if l.startswith("target: ")), None
    )
    if target is None:
        broken.append("no_target")
    elif (
        not (target.startswith("roles/") or target.startswith("policy/"))
        or ".." in target
    ):
        broken.append("bad_target")

    if split_index is None or not diff:
        broken.append("no_diff")

    plus_lines = [l for l in diff if l.startswith("+++ ")]
    if len(plus_lines) != 1:
        broken.append("multi_file")
    elif target is not None:
        path = plus_lines[0][len("+++ ") :].strip()
        path = path[2:] if path.startswith("b/") else path
        if path != target:
            broken.append("target_mismatch")

    return broken
