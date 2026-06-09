"""Socket tests against the REAL listener file, no Rhino required.

Outside Rhino the listener drains its queue on a worker thread, so the
whole path - accept, framing, dispatch, exec, response - is exercised
here exactly as it runs on the Mac (minus rhinoscriptsyntax).
"""

import importlib.util
import json
import os
import socket
import threading
import time

import pytest

from maquette import protocol
from maquette.netclient import ListenerClient, ListenerError

LISTENER_PATH = os.path.join(
    os.path.dirname(__file__), "..", "src", "maquette", "listener",
    "maquette_listener.py")


def load_listener_module():
    spec = importlib.util.spec_from_file_location(
        "maquette_listener_under_test", os.path.abspath(LISTENER_PATH))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


listener_mod = load_listener_module()


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


@pytest.fixture
def server():
    instance = listener_mod.ListenerServer(port=free_port())
    assert instance.start()
    yield instance
    instance.stop()


@pytest.fixture
def client(server):
    connected = ListenerClient("127.0.0.1", server.port)
    connected.connect()
    yield connected
    connected.close()


def test_listener_imports_without_rhino():
    assert listener_mod.RHINO is False
    assert listener_mod.SERVER_NAME == protocol.SERVER_NAME
    assert listener_mod.PROTO_VERSION == protocol.PROTO_VERSION
    assert listener_mod.DEFAULT_PORT == 6270


def test_handshake_reports_server_identity(client):
    info = client.server_info
    assert info["server"] == "maquette-listener"
    assert info["proto"] == 1
    assert info["rhino"] == "none (test mode)"


def test_ping(client):
    response = client.request("ping", {})
    assert response["status"] == "ok"
    assert "uptime_s" in response["result"]
    assert "queue_depth" in response["result"]


def test_exec_code_runs_and_captures(client):
    response = client.request("exec_code", {
        "code": "print('hello model')\n__maq_result__ = {'answer': 42}\n",
        "tag": {"id": "m1"}})
    result = response["result"]
    assert "hello model" in result["output"]
    assert result["value"] == {"answer": 42}
    assert result["created"] == []


def test_exec_code_error_returns_trace_and_keeps_listener_alive(client):
    with pytest.raises(ListenerError) as exc:
        client.request("exec_code", {"code": "raise ValueError('boom')",
                                     "tag": {}})
    assert "boom" in str(exc.value)
    # The listener survives bad requests.
    assert client.request("ping", {})["status"] == "ok"


def test_request_timeout_speaks_and_closes(server):
    client = ListenerClient("127.0.0.1", server.port)
    client.connect()
    with pytest.raises(ListenerError) as exc:
        client.request("exec_code",
                       {"code": "import time\ntime.sleep(3)\n", "tag": {}},
                       timeout=0.4)
    assert "did not answer" in str(exc.value)
    assert not client.connected


def test_unknown_request_type(client):
    with pytest.raises(ListenerError) as exc:
        client.request("frobnicate", {})
    assert "unknown request type" in str(exc.value)


def test_proto_mismatch_is_refused(server):
    with socket.create_connection(("127.0.0.1", server.port), timeout=3) as raw:
        raw.sendall(protocol.encode(protocol.make_request(
            "r1", "hello", {"proto": 99, "client": "test"})))
        framer = protocol.LineFramer()
        responses = []
        while not responses:
            responses = framer.feed(raw.recv(65536))
        assert responses[0]["status"] == "error"
        assert responses[0]["result"]["code"] == "proto_mismatch"


def test_bad_frame_gets_error_response(server):
    with socket.create_connection(("127.0.0.1", server.port), timeout=3) as raw:
        raw.sendall(b"this is not json\n")
        framer = protocol.LineFramer()
        responses = []
        while not responses:
            data = raw.recv(65536)
            if not data:
                break
            responses = framer.feed(data)
        assert responses and responses[0]["status"] == "error"
        assert responses[0]["result"]["code"] == "bad_frame"


def test_client_refuses_foreign_server():
    port = free_port()

    def imposter():
        with socket.socket() as listening:
            listening.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listening.bind(("127.0.0.1", port))
            listening.listen(1)
            conn, _ = listening.accept()
            with conn:
                conn.recv(65536)
                conn.sendall(json.dumps({
                    "id": "r1", "status": "ok",
                    "result": {"server": "someone-else", "proto": 1},
                    "message": ""}).encode() + b"\n")
                time.sleep(0.2)

    thread = threading.Thread(target=imposter, daemon=True)
    thread.start()
    time.sleep(0.1)
    client = ListenerClient("127.0.0.1", port)
    with pytest.raises(ListenerError) as exc:
        client.connect()
    assert "something else is listening" in str(exc.value)


def test_unreachable_port_message():
    client = ListenerClient("127.0.0.1", free_port())
    started = time.time()
    with pytest.raises(ListenerError) as exc:
        client.connect()
    elapsed = time.time() - started
    assert "not reachable" in str(exc.value)
    assert "maquette doctor" in str(exc.value)
    assert elapsed >= 3.0  # backoff retries happened (0.5 + 1 + 2)


def test_shutdown_request_stops_server(server):
    client = ListenerClient("127.0.0.1", server.port)
    client.connect()
    client.request("shutdown", {})
    time.sleep(0.3)
    # No listener service remains: a fresh handshake must fail. (The TCP
    # handshake itself may still complete from the kernel backlog.)
    fresh = ListenerClient("127.0.0.1", server.port)
    with pytest.raises(ListenerError):
        fresh.connect()


def test_framers_agree_on_split_frames():
    ours = protocol.LineFramer()
    theirs = listener_mod.LineFramer()
    payload = (protocol.encode({"id": "a", "type": "ping", "params": {}})
               + protocol.encode({"id": "b", "type": "ping", "params": {}}))
    for framer in (ours, theirs):
        collected = []
        for index in range(0, len(payload), 7):  # drip-feed in 7-byte chunks
            collected.extend(framer.feed(payload[index:index + 7]))
        assert [m["id"] for m in collected] == ["a", "b"]


def test_two_clients_interleave(server):
    first = ListenerClient("127.0.0.1", server.port)
    second = ListenerClient("127.0.0.1", server.port)
    first.connect()
    second.connect()
    assert first.request("ping", {})["status"] == "ok"
    assert second.request("ping", {})["status"] == "ok"
    assert first.request("exec_code", {"code": "x = 1", "tag": {}})[
        "status"] == "ok"
    first.close()
    second.close()
