import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from board_decide.board_decide import board_decide
from board_page.board_page import board_page
from board_rollup.board_rollup import board_rollup
from board_tree.board_tree import board_tree
from record_graph.record_graph import record_graph
from record_run.record_run import RecordError, record_run


def _route(self):
    path, q, m = urlparse(self.path).path, urlparse(self.path).query, self.command
    result = 404, {"error": "not found"}
    if m == "GET" and path == "/":
        result = 200, board_page(), True
    elif m == "GET" and path == "/api/intents":
        items = record_run(["list", "--all"])
        labels = [(it["id"], lb) for it in items for lb in it.get("labels", [])]
        care = {i: lb[5:] for i, lb in labels if lb.startswith("care:")}
        result = 200, board_rollup(record_graph(), care)
    elif m == "GET" and path == "/api/tree":
        result = 200, board_tree(parse_qs(q).get("id", [None])[0], record_graph())
    elif m == "POST" and path == "/api/decide":
        b = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        result = 200, board_decide(b["intent"], b["decision"], b.get("reason", ""))
    return result


def _handle(self):
    try:
        status, body, *html = _route(self)
    except (ValueError, RecordError) as e:
        status, body, html = 400, {"error": str(e)}, [False]
    self.send_response(status)
    self.send_header("Content-Type", "text/html" if any(html) else "application/json")
    self.end_headers()
    self.wfile.write(body.encode() if any(html) else json.dumps(body).encode())


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    do_GET = do_POST = _handle


def board_serve(port: int) -> None:
    ThreadingHTTPServer(("127.0.0.1", port), _Handler).serve_forever()
