"""Maquette listener: runs INSIDE Rhino 8, executes snippets over TCP.

Install once with: maquette install-listener
Auto-start by adding this Rhino startup command (Settings > General):
    _-ScriptEditor _R "<path printed by install-listener>"

Design notes
- One self-contained file: no imports from the maquette package, so
  it can be copied anywhere Rhino can see. The wire framing mirrors
  maquette/protocol.py; tests keep the two in step.
- Crash-only: if Rhino dies the OS reaps the socket. Nothing to clean
  up. If the port is taken, a listener is already running; we say so
  and leave quietly, which makes restarts idempotent.
- Threading: a daemon thread accepts connections and parses frames;
  every Rhino API call happens on Rhino's UI thread, drained from a
  queue by a RhinoApp.Idle handler (rhinoscriptsyntax is not thread
  safe). Set MAQUETTE_USE_INVOKE=1 to use RhinoApp.InvokeOnUiThread
  instead if Idle proves unreliable on some build.
- Outside Rhino (CI), a plain worker thread drains the queue so the
  whole socket path is testable; exec_code then runs without rs.
"""

import io
import json
import os
import queue
import socket
import threading
import time
import traceback

try:
    import Rhino  # noqa: N813 (Rhino's own casing)
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
    RHINO = True
except ImportError:
    Rhino = rs = sc = None
    RHINO = False

PROTO_VERSION = 1
SERVER_NAME = "maquette-listener"
DEFAULT_PORT = 6270
MAX_LINE_BYTES = 16 * 1024 * 1024
IDLE_BUDGET_SECONDS = 0.2

BAD_FRAME = "bad_frame"
PROTO_MISMATCH = "proto_mismatch"
UNKNOWN_TYPE = "unknown_type"
EXEC_ERROR = "exec_error"


def log(message):
    line = "[Maquette] " + message
    if RHINO:
        Rhino.RhinoApp.WriteLine(line)
    else:
        print(line)


# -- framing (mirror of maquette/protocol.py) --------------------------------


class LineFramer:
    def __init__(self, max_line=MAX_LINE_BYTES):
        self.max_line = max_line
        self._buffer = b""

    def feed(self, data):
        self._buffer += data
        if len(self._buffer) > self.max_line:
            self._buffer = b""
            raise ValueError("line too long")
        messages = []
        while b"\n" in self._buffer:
            line, self._buffer = self._buffer.split(b"\n", 1)
            line = line.strip()
            if not line:
                continue
            messages.append(json.loads(line.decode("utf-8")))
        return messages


def encode(obj):
    return json.dumps(obj, separators=(",", ":")).encode("utf-8") + b"\n"


def make_response(request_id, status, result=None, message="", trace=""):
    response = {"id": request_id, "status": status,
                "result": result or {}, "message": message}
    if trace:
        response["trace"] = trace
    return response


# -- Rhino helpers exposed to snippets as __maq__ -----------------------------


class MaqHelpers:
    def find(self, maq_ids):
        wanted = set(maq_ids)
        found = []
        for guid in rs.AllObjects() or []:
            if rs.GetUserText(guid, "MAQ_ID") in wanted:
                found.append(guid)
        return found

    def find_one(self, maq_id):
        found = self.find([maq_id])
        if not found:
            raise LookupError("no object tagged {0} in Rhino; run: "
                              "maquette rebuild".format(maq_id))
        return found[0]

    def tag(self, guids, maq_id, name, op, seq, layer):
        for guid in guids or []:
            rs.SetUserText(guid, "MAQ_ID", maq_id)
            rs.SetUserText(guid, "MAQ_NAME", name or "")
            rs.SetUserText(guid, "MAQ_OP", op or "")
            rs.SetUserText(guid, "MAQ_SEQ", str(seq))
            if name:
                rs.ObjectName(guid, name)
            if layer:
                self.ensure_layer(layer)
                rs.ObjectLayer(guid, layer)

    def ensure_layer(self, path):
        if path and not rs.IsLayer(path):
            rs.AddLayer(path)
        return path

    def bbox(self, guids):
        if not guids:
            return None
        corners = rs.BoundingBox(guids)
        if not corners:
            return None
        low, high = corners[0], corners[6]
        return [[low[0], low[1], low[2]], [high[0], high[1], high[2]]]


# -- request handling (always on the UI thread when RHINO) --------------------


class Handler:
    def __init__(self, server):
        self.server = server
        self.helpers = MaqHelpers() if RHINO else None
        self.started = time.time()

    def handle(self, request):
        request_id = request.get("id")
        request_type = request.get("type")
        params = request.get("params") or {}
        try:
            if request_type == "hello":
                return self._hello(request_id, params)
            if request_type == "ping":
                return make_response(request_id, "ok", {
                    "uptime_s": int(time.time() - self.started),
                    "queue_depth": self.server.requests.qsize()})
            if request_type == "exec_code":
                return self._exec_code(request_id, params)
            if request_type == "query":
                return self._query(request_id, params)
            if request_type == "delete_by_ids":
                return self._delete_by_ids(request_id, params)
            if request_type == "clear_all":
                return self._clear_all(request_id)
            if request_type == "shutdown":
                self.server.stop()
                return make_response(request_id, "ok", {"stopped": True})
            return make_response(request_id, "error",
                                 {"code": UNKNOWN_TYPE},
                                 "unknown request type {0!r}".format(request_type))
        except Exception as exc:  # never let one request kill the listener
            return make_response(request_id, "error", {"code": EXEC_ERROR},
                                 str(exc) or type(exc).__name__,
                                 traceback.format_exc())

    def _hello(self, request_id, params):
        if params.get("proto") != PROTO_VERSION:
            return make_response(
                request_id, "error", {"code": PROTO_MISMATCH},
                "listener speaks protocol {0}, client asked for {1}".format(
                    PROTO_VERSION, params.get("proto")))
        result = {
            "server": SERVER_NAME,
            "proto": PROTO_VERSION,
            "python": ".".join(str(n) for n in __import__("sys").version_info[:3]),
            "uptime_s": int(time.time() - self.started),
        }
        if RHINO:
            result["rhino"] = str(Rhino.RhinoApp.Version)
            result["doc"] = sc.doc.Name or "untitled"
        else:
            result["rhino"] = "none (test mode)"
            result["doc"] = "none"
        return make_response(request_id, "ok", result)

    def _exec_code(self, request_id, params):
        code = params.get("code") or ""
        tag = params.get("tag") or {}
        affected = params.get("affected_ids") or []
        namespace = {
            "rs": rs, "sc": sc, "Rhino": Rhino,
            "__maq__": self.helpers, "__maq_created__": [],
        }
        before = self._all_guids()
        output = io.StringIO()
        import contextlib
        try:
            with contextlib.redirect_stdout(output):
                exec(code, namespace)  # noqa: S102 - executing snippets is the job
        except Exception as exc:
            return make_response(
                request_id, "error", {"code": EXEC_ERROR,
                                      "output": output.getvalue()[-4000:]},
                str(exc) or type(exc).__name__, traceback.format_exc())
        after = self._all_guids()
        created = [g for g in after if g not in before]
        deleted = [g for g in before if g not in after]
        result = {
            "created": [str(g) for g in created],
            "deleted": [str(g) for g in deleted],
            "output": output.getvalue()[-4000:],
            "fingerprint": None,
        }
        value = namespace.get("__maq_result__")
        if value is not None:
            try:
                json.dumps(value)
                result["value"] = value
            except (TypeError, ValueError):
                result["value"] = str(value)
        if RHINO:
            self._tag_untagged(created, tag)
            target = created or (self.helpers.find(affected) if affected else [])
            box = self.helpers.bbox(target)
            if box or target:
                result["fingerprint"] = {"objects": len(target), "bbox": box,
                                         "quality": "measured"}
        return make_response(request_id, "ok", result)

    def _tag_untagged(self, created, tag):
        if not tag.get("id"):
            return
        untagged = [g for g in created if not rs.GetUserText(g, "MAQ_ID")]
        self.helpers.tag(untagged, tag.get("id"), tag.get("name"),
                         tag.get("op"), tag.get("seq", 0), tag.get("layer"))

    def _all_guids(self):
        if not RHINO:
            return []
        return rs.AllObjects() or []

    def _query(self, request_id, params):
        if not RHINO:
            return make_response(request_id, "ok", {"objects": []})
        what = params.get("what", "tagged")
        if what == "doc":
            return make_response(request_id, "ok", {
                "doc": sc.doc.Name or "untitled",
                "object_count": len(self._all_guids())})
        wanted = params.get("ids")
        objects = []
        for guid in self._all_guids():
            maq_id = rs.GetUserText(guid, "MAQ_ID")
            if not maq_id:
                continue
            if wanted and maq_id not in wanted:
                continue
            objects.append({
                "maq_id": maq_id,
                "name": rs.ObjectName(guid) or "",
                "layer": rs.ObjectLayer(guid),
                "bbox": self.helpers.bbox([guid]),
            })
        return make_response(request_id, "ok", {"objects": objects})

    def _delete_by_ids(self, request_id, params):
        if not RHINO:
            return make_response(request_id, "ok", {"deleted": 0})
        found = self.helpers.find(params.get("ids") or [])
        count = rs.DeleteObjects(found) if found else 0
        return make_response(request_id, "ok", {"deleted": count or 0})

    def _clear_all(self, request_id):
        if not RHINO:
            return make_response(request_id, "ok", {"deleted": 0})
        tagged = [g for g in self._all_guids() if rs.GetUserText(g, "MAQ_ID")]
        count = rs.DeleteObjects(tagged) if tagged else 0
        return make_response(request_id, "ok", {"deleted": count or 0})


# -- server -------------------------------------------------------------------


class ListenerServer:
    def __init__(self, host="127.0.0.1", port=None):
        self.host = host
        self.port = port or int(os.environ.get("MAQUETTE_PORT", DEFAULT_PORT))
        self.requests = queue.Queue()
        self.handler = Handler(self)
        self.socket = None
        self.running = False
        self._idle_subscribed = False

    # accept thread -> reader threads -> queue -> UI thread pump

    def start(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(4)
        except OSError:
            log("Already running on port {0}.".format(self.port))
            return False
        self.running = True
        accept_thread = threading.Thread(target=self._accept_loop,
                                         name="maquette-accept")
        accept_thread.daemon = True
        accept_thread.start()
        self._start_pump()
        log("Listening on {0}:{1}.".format(self.host, self.port))
        return True

    def stop(self):
        self.running = False
        if RHINO and self._idle_subscribed:
            try:
                Rhino.RhinoApp.Idle -= self._on_idle
            except Exception:
                pass
            self._idle_subscribed = False
        if self.socket is not None:
            try:
                # shutdown() wakes a blocked accept(); plain close() can
                # leave it sleeping with the port half-alive on Linux.
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self.socket.close()
            except OSError:
                pass
            self.socket = None
        log("Stopped.")

    def _start_pump(self):
        if RHINO and not os.environ.get("MAQUETTE_USE_INVOKE"):
            # Module-global subscription target; sc.sticky keeps the
            # server (and so this bound method) referenced, or .NET
            # would garbage-collect the delegate behind Rhino's back.
            Rhino.RhinoApp.Idle += self._on_idle
            self._idle_subscribed = True
        elif not RHINO:
            pump = threading.Thread(target=self._thread_pump,
                                    name="maquette-pump")
            pump.daemon = True
            pump.start()
        # When MAQUETTE_USE_INVOKE is set, readers push work to the UI
        # thread themselves; nothing to start here.

    def _on_idle(self, sender, args):
        deadline = time.time() + IDLE_BUDGET_SECONDS
        while time.time() < deadline:
            try:
                conn, request = self.requests.get_nowait()
            except queue.Empty:
                return
            self._respond(conn, self.handler.handle(request))

    def _thread_pump(self):
        while self.running:
            try:
                conn, request = self.requests.get(timeout=0.2)
            except queue.Empty:
                continue
            self._respond(conn, self.handler.handle(request))

    def _respond(self, conn, response):
        try:
            conn.sendall(encode(response))
        except OSError:
            pass  # client went away; its problem, journal has the truth

    def _accept_loop(self):
        while self.running:
            try:
                conn, _addr = self.socket.accept()
            except OSError:
                return
            reader = threading.Thread(target=self._read_loop, args=(conn,),
                                      name="maquette-reader")
            reader.daemon = True
            reader.start()

    def _read_loop(self, conn):
        framer = LineFramer()
        use_invoke = RHINO and os.environ.get("MAQUETTE_USE_INVOKE")
        while self.running:
            try:
                data = conn.recv(65536)
            except OSError:
                break
            if not data:
                break
            try:
                messages = framer.feed(data)
            except ValueError as exc:
                self._respond(conn, make_response(
                    None, "error", {"code": BAD_FRAME}, str(exc)))
                break
            for request in messages:
                if use_invoke:
                    self._invoke_on_ui(conn, request)
                else:
                    self.requests.put((conn, request))
        try:
            conn.close()
        except OSError:
            pass

    def _invoke_on_ui(self, conn, request):
        import System

        def work():
            self._respond(conn, self.handler.handle(request))
        Rhino.RhinoApp.InvokeOnUiThread(System.Action(work))


def start(port=None):
    server = ListenerServer(port=port)
    if server.start() and RHINO:
        # Keep a live reference; without it .NET may collect the Idle
        # delegate and the listener silently dies.
        sc.sticky["maquette_listener"] = server
    return server


if __name__ == "__main__":
    start()
