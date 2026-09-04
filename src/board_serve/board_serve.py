import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from board_decide.board_decide import board_decide
from board_page.board_page import board_page
from board_rollup.board_rollup import board_rollup
from board_tree.board_tree import board_tree
from record_graph.record_graph import record_graph
from record_run.record_run import RecordError, record_run


def _care():
    items = record_run(["list", "--all"])
    labels = [(it["id"], lb) for it in items for lb in it.get("labels", [])]
    return {i: lb[5:] for i, lb in labels if lb.startswith("care:")}


def _handle(self):
    def send(status, body, html=False):
        self.send_response(status)
        self.send_header("Content-Type", "text/html" if html else "application/json")
        self.end_headers()
        self.wfile.write(body.encode() if html else json.dumps(body).encode())

    path, q, m = urlparse(self.path).path, urlparse(self.path).query, self.command
    gets = {
        "/": lambda: (board_page(), True),
        "/api/intents": lambda: (board_rollup(record_graph(), _care()),),
        "/api/tree": lambda: (
            board_tree(parse_qs(q).get("id", [None])[0], record_graph()),
        ),
    }
    try:
        if m == "GET" and path in gets:
            result = 200, *gets[path]()
        elif m == "POST" and path == "/api/decide":
            b = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            result = 200, board_decide(b["intent"], b["decision"], b.get("reason", ""))
        else:
            result = 404, {"error": "not found"}
        send(*result)
    except (ValueError, RecordError) as e:
        send(400, {"error": str(e)})


class _Handler(BaseHTTPRequestHandler):
    do_GET = do_POST = _handle

    def log_message(self, *a):
        pass


def board_serve(port: int) -> None:
    ThreadingHTTPServer(("127.0.0.1", port), _Handler).serve_forever()
