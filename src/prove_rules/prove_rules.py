from gate_built.gate_built import gate_built
from gate_proven.gate_proven import gate_proven


def prove_rules(gathered: dict) -> list[str]:
    folder = gathered["folder"]
    built = gate_built(
        folder,
        {
            "changed": gathered["changed"],
            "code": gathered["code"],
            "note": gathered["note"],
            "fmt_out": gathered["fmt_out"],
            "lint_out": gathered["lint_out"],
        },
    )
    if gathered["kind"] != "test":
        return built
    proven = gate_proven(folder, gathered["pytest_out"], gathered["cases"])
    return built + proven
