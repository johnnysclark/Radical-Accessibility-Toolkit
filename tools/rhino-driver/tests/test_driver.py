"""Tests for RhinoDriver: the N->1 unification and honest (never silent) status."""

import json
import socket
import threading
import time

from tasc.core.model import Bay, Site, TASCModel, Zone
from tasc.rhino.connector import MCPClient

from rhino_driver import driver as driver_module
from rhino_driver import rhinocode as rc_module
from rhino_driver.driver import RhinoDriver


def _model() -> TASCModel:
    model = TASCModel()
    model.site = Site.rectangle(200, 150)
    model.add_zone(Zone.rectangle("living", 50, 40, at=(10, 10)))
    model.add_bay(Bay(name="A", origin=(18, 8), grid=(6, 3), spacing=(24, 24)))
    return model


class MockRhinoServer:
    """Minimal newline-delimited-JSON server that records commands and replies OK."""

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("127.0.0.1", 0))
        self.port = self.server.getsockname()[1]
        self.server.listen(1)
        self.received = []
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self):
        self.server.settimeout(1.0)
        while self._running:
            try:
                conn, _ = self.server.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            self._handle(conn)

    def _handle(self, conn):
        conn.settimeout(2.0)
        buffer = ""
        while self._running:
            try:
                data = conn.recv(4096).decode("utf-8")
            except (socket.timeout, OSError):
                break
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                self.received.append(json.loads(line))
                conn.sendall((json.dumps({"status": "success", "result": {}}) + "\n").encode("utf-8"))
        conn.close()

    def stop(self):
        self._running = False
        self.server.close()
        if self._thread:
            self._thread.join(timeout=3)


class TestUnification:
    def test_one_script_command_per_redraw(self):
        server = MockRhinoServer()
        server.start()
        try:
            d = RhinoDriver(host="127.0.0.1", port=server.port, timeout=5.0)
            assert d.connect() == "mcp"
            result = d.run_model(_model())
            d.disconnect()
            time.sleep(0.1)

            assert result["status"] == "ok"
            assert len(server.received) == 1  # N objects -> exactly ONE message
            cmd = server.received[0]
            assert cmd["type"] == "execute_rhinoscript_python_code"
            assert "rs.AddPolyline(" in cmd["params"]["code"]
        finally:
            server.stop()


class TestOffline:
    def test_offline_never_reports_drawn(self, monkeypatch):
        monkeypatch.setattr(MCPClient, "connect", lambda self: False)
        monkeypatch.setattr(rc_module, "find_rhinocode", lambda: None)

        d = RhinoDriver(port=59999, timeout=1.0)
        assert d.connect() == "offline"
        result = d.run_model(_model())
        assert result["status"] == "offline"
        assert "nothing was drawn" in result["output"].lower()


class TestStatus:
    def test_status_offline_recommends_install(self, monkeypatch):
        monkeypatch.setattr(MCPClient, "connect", lambda self: False)
        monkeypatch.setattr(driver_module, "_is_wsl2", lambda: False)
        monkeypatch.setattr(rc_module, "find_rhinocode", lambda: None)

        info = RhinoDriver(timeout=1.0).status()
        assert info["mode"] == "offline"
        assert info["socket_reachable"] is False
        assert "Install Rhino" in info["recommendation"]

    def test_status_rhinocode_found_but_no_server(self, monkeypatch):
        monkeypatch.setattr(MCPClient, "connect", lambda self: False)
        monkeypatch.setattr(driver_module, "_is_wsl2", lambda: False)
        monkeypatch.setattr(rc_module, "find_rhinocode", lambda: "/fake/rhinocode")

        class _Proc:
            stdout = "no instances"
            stderr = ""
            returncode = 0

        monkeypatch.setattr(rc_module.subprocess, "run", lambda *a, **k: _Proc())
        info = RhinoDriver(timeout=1.0).status()
        assert info["mode"] == "offline"
        assert "StartScriptServer" in info["recommendation"]

    def test_status_rhinocode_live(self, monkeypatch):
        monkeypatch.setattr(MCPClient, "connect", lambda self: False)
        monkeypatch.setattr(driver_module, "_is_wsl2", lambda: False)
        monkeypatch.setattr(rc_module, "find_rhinocode", lambda: "/fake/rhinocode")

        class _Proc:
            stdout = "rhinocode_remotepipe_9 Rhino 8"
            stderr = ""
            returncode = 0

        monkeypatch.setattr(rc_module.subprocess, "run", lambda *a, **k: _Proc())
        info = RhinoDriver(timeout=1.0).status()
        assert info["mode"] == "rhinocode"
        assert "rhinocode_remotepipe_9" in info["recommendation"]
