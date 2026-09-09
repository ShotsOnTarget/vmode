from pathlib import Path

from record_show_item.record_show_item import record_show_item
from sheet_cases.sheet_cases import sheet_cases
from sheet_fields.sheet_fields import sheet_fields

_FAULTS = {"second_folder", "raise"}


def _name(fields: dict) -> str:
    return fields["function_name"].strip("`")


def _code(fn: str) -> str:
    return (
        f"def {fn}():\n"
        '    """Return the fixed string \'ok\'.\n'
        "\n"
        "    Inputs: none.\n"
        "    Outputs: the string 'ok'.\n"
        "    Side effects: none.\n"
        '    """\n'
        f'    return "ok"\n'
    )


def _test(fn: str, cases: list[str]) -> str:
    head = f"from {fn}.{fn} import {fn}\n\n\n"
    bodies = "".join(
        f'def test_{case}():\n    assert {fn}() == "ok"\n\n\n' for case in cases
    )
    return head + bodies.rstrip() + "\n"


def _check_fault(fault: str | None) -> None:
    if fault is not None and fault not in _FAULTS:
        raise ValueError(f"unknown fault: {fault}")
    if fault == "raise":
        raise RuntimeError("planted run fault")


def scripted_builder(item: dict, column: str) -> dict:
    """Write the file a job's sheet names, or misbehave as the recipe says.

    Inputs: item, a code or test job dict with id, kind, state, labels,
    last_gate and a recipe dict naming an optional fault; column, the puller
    column name, ignored. Outputs: a usage dict with tokens, seconds,
    harness and model. Side effects: writes the sheet-named code or test
    file under src/<folder>/ of the current directory; fault second_folder
    also writes another src folder; raises ValueError on an unknown fault
    and RuntimeError on the planted run fault, both before writing.
    """
    fault = item.get("recipe", {}).get("fault")
    _check_fault(fault)
    sheet = record_show_item(item["id"])["sheet"]
    fn = _name(sheet_fields(sheet))
    root = Path("src") / fn
    root.mkdir(parents=True, exist_ok=True)
    if item["kind"] == "code":
        (root / f"{fn}.py").write_text(_code(fn), encoding="utf-8")
    else:
        (root / f"test_{fn}.py").write_text(
            _test(fn, sheet_cases(sheet)), encoding="utf-8"
        )
    if fault == "second_folder":
        extra = Path("src") / "second" / "leftover.txt"
        extra.parent.mkdir(parents=True, exist_ok=True)
        extra.write_text("", encoding="utf-8")
    return {"tokens": 0, "seconds": 0.0, "harness": "scripted", "model": "builder"}
