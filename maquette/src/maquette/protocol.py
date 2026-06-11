"""Wire protocol for the live Rhino listener.

JSON lines over TCP, both directions: exactly one JSON object per
newline-terminated UTF-8 line. Requests carry a client-chosen id that
the response echoes. The first request must be hello, which checks
server identity and protocol version.

Request:  {"id": "r1", "type": "exec_code", "params": {...}}
Response: {"id": "r1", "status": "ok"|"error", "result": {...},
           "message": "one line", "trace": "optional traceback"}

The listener embeds its own copy of this framing (it must be a single
self-contained file inside Rhino); tests assert the two stay in step.
"""

from __future__ import annotations

import json

PROTO_VERSION = 1
SERVER_NAME = "maquette-listener"
MAX_LINE_BYTES = 16 * 1024 * 1024

# Error codes carried in result["code"] on status "error".
BAD_FRAME = "bad_frame"
PROTO_MISMATCH = "proto_mismatch"
UNKNOWN_TYPE = "unknown_type"
EXEC_ERROR = "exec_error"

REQUEST_TYPES = ("hello", "ping", "exec_code", "query", "delete_by_ids",
                 "clear_all", "shutdown")


class ProtocolError(Exception):
    pass


def encode(obj: dict) -> bytes:
    return json.dumps(obj, separators=(",", ":")).encode("utf-8") + b"\n"


def make_request(request_id: str, request_type: str, params: dict) -> dict:
    return {"id": request_id, "type": request_type, "params": params}


def make_response(request_id, status: str, result: dict | None = None,
                  message: str = "", trace: str = "") -> dict:
    response = {"id": request_id, "status": status,
                "result": result or {}, "message": message}
    if trace:
        response["trace"] = trace
    return response


def make_hello_params(client: str) -> dict:
    return {"proto": PROTO_VERSION, "client": client}


class LineFramer:
    """Buffer bytes, emit complete JSON objects, refuse runaway lines."""

    def __init__(self, max_line: int = MAX_LINE_BYTES):
        self.max_line = max_line
        self._buffer = b""

    def feed(self, data: bytes) -> list[dict]:
        self._buffer += data
        if len(self._buffer) > self.max_line:
            self._buffer = b""
            raise ProtocolError("line too long; dropping the connection buffer")
        messages = []
        while b"\n" in self._buffer:
            line, self._buffer = self._buffer.split(b"\n", 1)
            line = line.strip()
            if not line:
                continue
            try:
                messages.append(json.loads(line.decode("utf-8")))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ProtocolError("unreadable frame: {0}".format(exc))
        return messages


def check_hello_result(result: dict) -> None:
    """Validate the listener's hello response; raise with a fix message."""
    server = result.get("server")
    if server != SERVER_NAME:
        raise ProtocolError(
            "something else is listening on that port (it answers as "
            "{0!r}). Change the port in maquette.json or stop the other "
            "service.".format(server))
    proto = result.get("proto")
    if proto != PROTO_VERSION:
        raise ProtocolError(
            "the listener speaks protocol {0} but this maquette speaks {1}. "
            "Run: maquette install-listener, then restart Rhino.".format(
                proto, PROTO_VERSION))
