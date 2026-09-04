def _split_header_diff(sheet: str) -> tuple[list[str], list[str]]:
    lines = sheet.splitlines()
    split_index = next((i for i, line in enumerate(lines) if line == "---"), None)
    header = lines if split_index is None else lines[:split_index]
    diff = [] if split_index is None else lines[split_index + 1 :]
    return header, diff


def _check_page(header: list[str]) -> str | None:
    ok = any(h.startswith("page: ") and h[len("page: ") :].strip() for h in header)
    return None if ok else "no_page"


def _find_target(header: list[str]) -> str | None:
    p = "target: "
    return next((h[len(p) :].strip() for h in header if h.startswith(p)), None)


def _check_target(target: str | None) -> str | None:
    if target is None:
        return "no_target"
    ok = target.startswith(("roles/", "policy/")) and ".." not in target
    return None if ok else "bad_target"


def _check_file_match(diff: list[str], target: str | None) -> str | None:
    plus_lines = [line for line in diff if line.startswith("+++ ")]
    if len(plus_lines) != 1:
        return "multi_file"
    path = plus_lines[0][len("+++ ") :].strip().removeprefix("b/")
    return None if target is None or path == target else "target_mismatch"


def proposal_check(item: dict) -> list[str]:
    header, diff = _split_header_diff(item.get("sheet") or "")
    target = _find_target(header)
    checks = (
        None if item.get("kind") == "proposal" else "not_proposal",
        _check_page(header),
        _check_target(target),
        None if diff else "no_diff",
        _check_file_match(diff, target),
    )
    return [c for c in checks if c is not None]
