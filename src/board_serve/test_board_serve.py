import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from board_serve.board_serve import board_serve
from record_run.record_run import record_run


def _start():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    threading.Thread(target=board_serve, args=(port,), daemon=True).start()
    for _ in range(200):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.1).close()
            return port
        except OSError:
            pass
    raise RuntimeError("board_serve did not start")


def _intent():
    return record_run(
        [
            "create",
            "I",
            "-t",
            "epic",
            "-l",
            "kind:intent,care:high",
            "-a",
            "alice",
            "--no-inherit-labels",
        ]
    )["id"]


def _validation(iid):
    vid = record_run(
        [
            "create",
            "V",
            "-t",
            "task",
            "-l",
            "kind:validation,state:waiting",
            "-a",
            "board",
            "--no-inherit-labels",
        ]
    )["id"]
    record_run(["dep", "add", vid, iid, "-t", "validates"])
    return vid


def _get(url):
    return json.loads(urllib.request.urlopen(url).read().decode())


def test_root_is_page():
    body = urllib.request.urlopen(f"http://127.0.0.1:{_start()}/").read().decode()
    assert body.lower().startswith("<!doctype html>")


def test_intents_json(fake_bd):
    port, iid = _start(), _intent()
    data = _get(f"http://127.0.0.1:{port}/api/intents")
    assert any(x["id"] == iid and x["care"] == "high" for x in data)


def test_tree_json(fake_bd):
    port, iid = _start(), _intent()
    data = _get(f"http://127.0.0.1:{port}/api/tree?id={iid}")
    assert "back" in data and "forward" in data


def test_decide_roundtrip(fake_bd):
    port, iid = _start(), _intent()
    vid = _validation(iid)
    body = json.dumps({"intent": iid, "decision": "yes", "reason": ""}).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/decide",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req)
    data = _get(f"http://127.0.0.1:{port}/api/tree?id={vid}")
    assert data["back"][0]["kind"] == "validation"


def test_columns_routes():
    port = _start()
    body = urllib.request.urlopen(f"http://127.0.0.1:{port}/columns").read().decode()
    assert "/api/columns" in body
    data = _get(f"http://127.0.0.1:{port}/api/columns")
    assert {"name", "role", "wip", "in_progress", "items"} <= data[0].keys()


def test_unknown_404():
    port = _start()
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/nope")
        pytest.fail("expected 404")
    except urllib.error.HTTPError as e:
        assert e.code == 404
