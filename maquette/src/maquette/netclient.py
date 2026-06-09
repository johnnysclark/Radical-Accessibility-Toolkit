"""TCP client for the live Rhino listener."""

from __future__ import annotations

import socket
import time

from maquette import VERSION, protocol
from maquette.backends.base import BackendError

CONNECT_TIMEOUT = 3.0
CONNECT_BACKOFF = (0.5, 1.0, 2.0)
DEFAULT_TIMEOUT = 10.0
EXEC_TIMEOUT = 120.0


class ListenerError(BackendError):
    pass


class ListenerClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._sock: socket.socket | None = None
        self._framer = protocol.LineFramer()
        self._counter = 0
        self.server_info: dict = {}

    # -- lifecycle ---------------------------------------------------------

    def connect(self) -> dict:
        """Connect with backoff and run the hello handshake."""
        last_error = None
        for attempt, wait in enumerate((0.0,) + CONNECT_BACKOFF):
            if wait:
                time.sleep(wait)
            try:
                self._sock = socket.create_connection(
                    (self.host, self.port), timeout=CONNECT_TIMEOUT)
                break
            except OSError as exc:
                last_error = exc
                self._sock = None
        if self._sock is None:
            raise ListenerError(
                "Rhino listener not reachable on {0} port {1} ({2}). "
                "Run: maquette doctor".format(self.host, self.port, last_error))
        response = self.request(
            "hello", protocol.make_hello_params("maquette/" + VERSION))
        try:
            protocol.check_hello_result(response.get("result", {}))
        except protocol.ProtocolError as exc:
            self.close()
            raise ListenerError(str(exc))
        self.server_info = response["result"]
        return self.server_info

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    @property
    def connected(self) -> bool:
        return self._sock is not None

    # -- requests -----------------------------------------------------------

    def request(self, request_type: str, params: dict,
                timeout: float | None = None) -> dict:
        """Send one request and wait for its response.

        Mutations are never retried automatically: the journal already
        holds the intent, and maquette rebuild reconciles.
        """
        if self._sock is None:
            raise ListenerError("not connected to the Rhino listener")
        if timeout is None:
            timeout = EXEC_TIMEOUT if request_type == "exec_code" \
                else DEFAULT_TIMEOUT
        self._counter += 1
        request_id = "r{0}".format(self._counter)
        message = protocol.make_request(request_id, request_type, params)
        try:
            self._sock.settimeout(timeout)
            self._sock.sendall(protocol.encode(message))
            while True:
                data = self._sock.recv(65536)
                if not data:
                    raise ListenerError(
                        "the Rhino listener closed the connection. "
                        "Run: maquette doctor")
                for response in self._framer.feed(data):
                    if response.get("id") == request_id:
                        return self._checked(response, request_type)
        except socket.timeout:
            self.close()
            raise ListenerError(
                "the Rhino listener did not answer within {0} seconds. "
                "Rhino may be busy; check it, then run: maquette doctor".format(
                    int(timeout)))
        except (OSError, protocol.ProtocolError) as exc:
            self.close()
            raise ListenerError(
                "connection to the Rhino listener failed: {0}".format(exc))

    def _checked(self, response: dict, request_type: str) -> dict:
        if response.get("status") == "error":
            message = response.get("message") or "unknown listener error"
            trace = response.get("trace", "")
            detail = message if not trace else \
                message + " (full trace in the journal entry)"
            raise ListenerError(
                "Rhino could not run {0}: {1}".format(request_type, detail))
        return response
