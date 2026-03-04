"""Tests for Rhino connector with mock socket server."""

import json
import socket
import threading
import time

import pytest

from tasc_core.rhino.connector import MCPClient, RhinoCodeClient, RhinoConnector
from tasc_core.rhino.protocol import (
    create_layer_cmd,
    create_line_cmd,
    create_polyline_cmd,
    create_text_cmd,
    delete_all_cmd,
    delete_by_name_cmd,
    execute_script_cmd,
    make_command,
    parse_response,
    set_layer_cmd,
)


class TestProtocol:
    def test_make_command(self):
        data = make_command("create_object", {"type": "LINE"})
        assert isinstance(data, bytes)
        parsed = json.loads(data.decode("utf-8").strip())
        assert parsed["type"] == "create_object"
        assert parsed["params"]["type"] == "LINE"

    def test_parse_response_complete(self):
        buffer = '{"status": "success", "result": {}}'
        response, remaining = parse_response(buffer)
        assert response is not None
        assert response["status"] == "success"
        assert remaining == ""

    def test_parse_response_partial(self):
        buffer = '{"status": "ok'
        response, remaining = parse_response(buffer)
        assert response is None
        assert remaining == buffer

    def test_parse_response_with_remainder(self):
        buffer = '{"status": "ok"}{"next": true}'
        response, remaining = parse_response(buffer)
        assert response["status"] == "ok"
        assert '{"next": true}' in remaining

    def test_create_polyline_cmd(self):
        cmds = create_polyline_cmd(
            points=[(0, 0), (10, 0), (10, 10), (0, 10)],
            name="test",
            layer="TASC_Site",
            closed=True,
        )
        # Returns [set_layer_cmd, create_object_cmd]
        assert len(cmds) == 2
        assert cmds[0]["type"] == "get_or_set_current_layer"
        assert cmds[1]["type"] == "create_object"
        assert cmds[1]["params"]["type"] == "POLYLINE"
        assert len(cmds[1]["params"]["params"]["points"]) == 5  # 4 + closed

    def test_create_line_cmd(self):
        cmds = create_line_cmd((0, 0), (10, 10), "TASC_Grid")
        assert len(cmds) == 2
        assert cmds[1]["type"] == "create_object"
        assert cmds[1]["params"]["type"] == "LINE"
        assert cmds[1]["params"]["params"]["start"] == [0, 0, 0]

    def test_create_text_cmd(self):
        cmds = create_text_cmd("Living", (25, 25), "TASC_Labels")
        assert len(cmds) == 2
        assert cmds[1]["params"]["name"] == "Living"

    def test_create_layer_cmd(self):
        cmd = create_layer_cmd("TASC_Site", (0, 0, 0))
        assert cmd["type"] == "create_layer"
        assert cmd["params"]["name"] == "TASC_Site"

    def test_set_layer_cmd(self):
        cmd = set_layer_cmd("TASC_Zones")
        assert cmd["type"] == "get_or_set_current_layer"
        assert cmd["params"]["name"] == "TASC_Zones"

    def test_delete_all_cmd(self):
        cmd = delete_all_cmd()
        assert cmd["type"] == "delete_object"
        assert cmd["params"]["all"] is True

    def test_delete_by_name_cmd(self):
        cmd = delete_by_name_cmd("site_boundary")
        assert cmd["type"] == "delete_object"
        assert cmd["params"]["name"] == "site_boundary"

    def test_execute_script_cmd(self):
        cmd = execute_script_cmd("import rhinoscriptsyntax as rs\nrs.AddLine((0,0,0),(1,1,1))")
        assert cmd["type"] == "execute_rhinoscript_python_code"
        assert "rs.AddLine" in cmd["params"]["code"]


class MockRhinoServer:
    """Simple TCP server that echoes back OK responses."""

    def __init__(self, host="127.0.0.1", port=0):
        self.host = host
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.port = self.server.getsockname()[1]
        self.server.listen(1)
        self._running = False
        self._thread = None
        self.received_commands = []

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self):
        self.server.settimeout(1.0)
        while self._running:
            try:
                conn, _ = self.server.accept()
                self._handle(conn)
            except socket.timeout:
                continue
            except OSError:
                break

    def _handle(self, conn):
        conn.settimeout(2.0)
        buffer = ""
        while self._running:
            try:
                data = conn.recv(4096).decode("utf-8")
                if not data:
                    break
                buffer += data
                # Try to parse commands
                while buffer:
                    try:
                        # Find newline-delimited JSON
                        nl = buffer.index("\n")
                        line = buffer[:nl]
                        buffer = buffer[nl + 1:]
                        cmd = json.loads(line)
                        self.received_commands.append(cmd)
                        response = json.dumps({"status": "success", "result": {}}) + "\n"
                        conn.sendall(response.encode("utf-8"))
                    except (ValueError, json.JSONDecodeError):
                        break
            except socket.timeout:
                break
            except OSError:
                break
        conn.close()

    def stop(self):
        self._running = False
        self.server.close()
        if self._thread:
            self._thread.join(timeout=3)


class TestMCPClient:
    def test_connect_to_mock(self):
        server = MockRhinoServer()
        server.start()
        try:
            client = MCPClient(host="127.0.0.1", port=server.port, timeout=5.0)
            assert client.connect() is True
            client.close()
        finally:
            server.stop()

    def test_connect_failure(self):
        client = MCPClient(host="127.0.0.1", port=19999, timeout=1.0)
        assert client.connect() is False

    def test_send_command(self):
        server = MockRhinoServer()
        server.start()
        try:
            client = MCPClient(host="127.0.0.1", port=server.port, timeout=5.0)
            client.connect()
            response = client.send_command("create_layer", {"name": "test"})
            assert response["status"] == "success"
            client.close()
            time.sleep(0.1)
            assert len(server.received_commands) == 1
            assert server.received_commands[0]["type"] == "create_layer"
        finally:
            server.stop()


class TestRhinoConnector:
    def test_offline_fallback(self):
        connector = RhinoConnector(port=19999, timeout=1.0)
        mode = connector.connect()
        # Without Rhino or rhinocode, should be offline
        assert mode in ("offline", "rhinocode")

    def test_connect_to_mock_mcp(self):
        server = MockRhinoServer()
        server.start()
        try:
            connector = RhinoConnector(port=server.port, timeout=5.0)
            mode = connector.connect()
            assert mode == "mcp"
            assert connector.is_live is True
            result = connector.send("create_layer", {"name": "test"})
            assert result["status"] == "success"
            connector.disconnect()
        finally:
            server.stop()

    def test_offline_send(self):
        connector = RhinoConnector(port=19999, timeout=1.0)
        connector.mode = "offline"
        result = connector.send("create_layer", {"name": "test"})
        assert result["status"] == "offline"

    def test_is_connected(self):
        connector = RhinoConnector()
        assert connector.is_connected is False
        connector.mode = "offline"
        assert connector.is_connected is True

    def test_is_live(self):
        connector = RhinoConnector()
        connector.mode = "offline"
        assert connector.is_live is False
        connector.mode = "mcp"
        assert connector.is_live is True
