import re

from sheet_fields.sheet_fields import sheet_fields

_F = {
    "allowed_imports",
    "how",
    "checks_to_run_before_reporting",
    "note_file",
    "out_of_scope",
    "files_you_may_change",
}
_P = ["raise clear", "add remove", "open close", "set unset", "create delete"]


def _mm(cf: dict, tf: dict) -> str | None:
    c = cf.get("function_name", "").replace("`", "").strip()
    t = tf.get("function_name", "").replace("`", "").strip()
    return None if c and t and c == t else "function_mismatch"


def _fm(cf: dict, tf: dict) -> str | None:
    for f in (cf, tf):
        n = f.get("function_name", "").replace("`", "").strip()
        d = f.get("folder", "").replace("`", "").strip().rstrip("/").strip()
        if not n or d != f"src/{n}":
            return "folder_mismatch"
    return None


def _nc(tf: dict) -> str | None:
    return "no_cases" if not tf.get("cases", []) else None


def _fb(cf: dict, tf: dict) -> str | None:
    if _F & set(cf) or _F & set(tf):
        return "forbidden_field"
    return None


def _od(cf: dict, tf: dict) -> str | None:
    w = set(re.findall(r"\w+", cf.get("outputs", "").lower()))
    v = set(re.findall(r"\w+", " ".join(tf.get("cases", [])).lower().replace("_", " ")))
    for p in _P:
        a, b = p.split()
        if {a, b} <= w and not {a, b} <= v:
            return "one_direction"
    return None


def _va(cf: dict) -> str | None:
    toks = re.findall(r"\w+", cf.get("outputs", "").lower())
    n = sum(1 for t in toks if t in ("raise", "raises"))
    return "validate_and_operate" if n >= 3 else None


def _ex(cf: dict, tf: dict, existing: dict[str, list[str]]) -> list[str]:
    n = cf.get("function_name", "").replace("`", "").strip()
    if n not in existing:
        return []
    if "change" not in cf:
        return ["exists_without_change"]
    known = existing[n] if isinstance(existing, dict) else []
    present = set(tf.get("cases", []))
    return [f"existing_case_missing:{x}" for x in known if x not in present]


def sheet_check(code: str, test: str, existing: dict[str, list[str]]) -> list[str]:
    """Name the faults in a code and test sheet pair.
    Inputs: code and test sheet texts, and existing: test names per
    function as a dict, or the bare function names as a list, in which
    case only exists_without_change can fire, never existing_case_missing.
    Outputs: sorted distinct rule names, [] when clean.
    Side effects: none."""
    cf = sheet_fields(code)
    tf = sheet_fields(test)
    checks = (_mm(cf, tf), _fm(cf, tf), _nc(tf), _fb(cf, tf), _od(cf, tf), _va(cf))
    return sorted({c for c in checks if c} | set(_ex(cf, tf, existing)))
