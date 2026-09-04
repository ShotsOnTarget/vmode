import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from board_page.board_page import board_page
from board_rollup.board_rollup import board_rollup
from board_tree.board_tree import board_tree
from board_decide.board_decide import board_decide
from record_graph.record_graph import record_graph
from record_run.record_run import record_run, RecordError


def board_serve(port: int) -> None:
    def care_map():
        labels = [(it["id"], lb) for it in record_run(["list", "--all"]) for lb in it.get("labels", [])]
        return {i: lb.split("care:", 1)[1] for i, lb in labels if lb.startswith("care:")}

    class Handler(BaseHTTPRequestHandler):
        def _send(self, status, body, html=False):
            self.send_response(status)
            self.send_header("Content-Type", "text/html" if html else "application/json")
            self.end_headers()
            self.wfile.write(body.encode() if html else json.dumps(body).encode())

        def do_GET(self):
            p = urlparse(self.path)
            try:
                if p.path == "/":
                    return self._send(200, board_page(), True)
                if p.path == "/api/intents":
                    return self._send(200, board_rollup(record_graph(), care_map()))
                if p.path == "/api/tree":
                    iid = parse_qs(p.query).get("id", [None])[0]
                    return self._send(200, board_tree(iid, record_graph()))
                self._send(404, {"error": "not found"})
            except (ValueError, RecordError) as e:
                self._send(400, {"error": str(e)})

        def do_POST(self):
            try:
                if urlparse(self.path).path != "/api/decide":
                    return self._send(404, {"error": "not found"})
                b = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                self._send(200, board_decide(b["intent"], b["decision"], b.get("reason", "")))
            except (ValueError, RecordError) as e:
                self._send(400, {"error": str(e)})

        def log_message(self, *a):
            pass

    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
