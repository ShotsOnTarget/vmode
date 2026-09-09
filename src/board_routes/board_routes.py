from board_api.board_api import board_api
from board_page.board_page import board_page
from columns_page.columns_page import columns_page
from record_run.record_run import RecordError

ROUTES = {
    ("GET", "/"): lambda q, b: (200, "text/html", board_page()),
    ("GET", "/columns"): lambda q, b: (200, "text/html", columns_page()),
    ("POST", "/api/decide"): lambda q, b: (
        200,
        "application/json",
        board_api("decide", q, b),
    ),
    ("POST", "/api/release"): lambda q, b: (
        200,
        "application/json",
        board_api("release", q, b),
    ),
}

API_NAMES = (
    "intents",
    "tree",
    "item",
    "columns",
    "timeline",
    "status",
    "open_questions",
)


def board_routes(
    method: str, path: str, query: dict, body: dict
) -> tuple[int, str, object]:
    """Dispatch HTTP requests to the board's route handlers."""
    name = path[len("/api/") :] if path.startswith("/api/") else ""
    try:
        if (method, path) in ROUTES:
            result = ROUTES[(method, path)](query, body)
        elif method == "GET" and name in API_NAMES:
            result = 200, "application/json", board_api(name, query, body)
        else:
            result = 404, "application/json", {"error": "not found"}
    except (ValueError, RecordError, KeyError) as exc:
        result = 400, "application/json", {"error": str(exc)}
    return result
