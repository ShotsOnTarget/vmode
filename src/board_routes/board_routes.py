import pathlib

from board_columns.board_columns import board_columns
from board_config.board_config import board_config
from board_decide.board_decide import board_decide
from board_page.board_page import board_page
from board_rollup.board_rollup import board_rollup
from board_tree.board_tree import board_tree
from columns_page.columns_page import columns_page
from record_graph.record_graph import record_graph
from record_labels.record_labels import record_labels
from record_run.record_run import RecordError

CONFIG = pathlib.Path(__file__).resolve().parents[2] / "roles" / "board.toml"


def _api(q, b, kind):
    if kind == "tree":
        result = board_tree(q.get("id", ""), record_graph())
    elif kind == "columns":
        cfg = board_config(str(CONFIG))
        result = board_columns(record_graph(), record_labels(), cfg)
    elif kind == "decide":
        result = board_decide(*[b.get(k, "") for k in ("intent", "decision", "reason")])
    else:
        lbl = record_labels()
        care = {i: v[5:] for i, vs in lbl.items() for v in vs if v.startswith("care:")}
        result = board_rollup(record_graph(), care)
    return 200, "application/json", result


ROUTES = {
    ("GET", "/"): lambda q, b: (200, "text/html", board_page()),
    ("GET", "/columns"): lambda q, b: (200, "text/html", columns_page()),
    ("GET", "/api/intents"): lambda q, b: _api(q, b, "intents"),
    ("GET", "/api/tree"): lambda q, b: _api(q, b, "tree"),
    ("GET", "/api/columns"): lambda q, b: _api(q, b, "columns"),
    ("POST", "/api/decide"): lambda q, b: _api(q, b, "decide"),
}


def board_routes(
    method: str, path: str, query: dict, body: dict
) -> tuple[int, str, object]:
    try:
        if (method, path) not in ROUTES:
            return 404, "application/json", {"error": "not found"}
        return ROUTES[(method, path)](query, body)
    except (ValueError, RecordError) as exc:
        return 400, "application/json", {"error": str(exc)}
