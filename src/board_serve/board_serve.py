import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from board_routes.board_routes import board_routes


def _handle(self):
    parsed = urlparse(self.path)
    query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
    body = {}
    if self.command == "POST":
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
    status, content_type, payload = board_routes(self.command, parsed.path, query, body)
    self.send_response(status)
    self.send_header("Content-Type", content_type)
    self.end_headers()
    out = payload if content_type == "text/html" else json.dumps(payload)
    self.wfile.write(out.encode())


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    do_GET = do_POST = _handle


def board_serve(port: int) -> None:
    """Serve HTTP requests for the board, delegating all routing to board_routes."""
    ThreadingHTTPServer(("127.0.0.1", port), _Handler).serve_forever()
