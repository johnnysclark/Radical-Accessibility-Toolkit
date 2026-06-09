"""Live backend: drive a running Rhino through the Maquette listener.

Each op compiles to a rhinoscriptsyntax snippet (compiler.py) and runs
inside Rhino over the socket. Rhino reports created guids and a
measured bounding box, which lands in the journal entry as the op's
fingerprint.
"""

from __future__ import annotations

from maquette import compiler, ops
from maquette.backends.base import BackendAPI, recorded
from maquette.netclient import ListenerClient

SLOW_OPS = {"script", "loft", "revolve", "boolean_union",
            "boolean_difference", "boolean_intersection"}
SLOW_TIMEOUT = 120.0


class LiveBackend(BackendAPI):
    name = "live"

    def __init__(self, project):
        self.project = project
        host, port = project.listener_address
        self._client = ListenerClient(host, port)

    def apply(self, entry: dict, scene) -> dict:
        code = compiler.compile_entry(entry)
        if code is None:
            return recorded(self.name)
        params = {
            "code": code,
            "tag": {"id": entry.get("id"), "name": entry.get("name"),
                    "op": entry["op"], "seq": entry["seq"],
                    "layer": entry.get("layer")},
            "affected_ids": self._affected(entry),
            "capture": True,
        }
        timeout = SLOW_TIMEOUT if entry["op"] in SLOW_OPS else None
        response = self._connected().request("exec_code", params,
                                             timeout=timeout)
        result = response.get("result", {})
        return {
            "backend": self.name,
            "status": "applied",
            "fingerprint": result.get("fingerprint"),
            "output": (result.get("output") or "").strip(),
        }

    def begin_rebuild(self) -> None:
        self._connected().request("clear_all", {})

    def finish_rebuild(self) -> dict:
        response = self._connected().request("query", {"what": "tagged"})
        fingerprints: dict[str, dict] = {}
        for obj in response.get("result", {}).get("objects", []):
            maq_id = obj.get("maq_id")
            if not maq_id:
                continue
            existing = fingerprints.get(maq_id)
            box = obj.get("bbox")
            if existing is None:
                fingerprints[maq_id] = {"objects": 1, "bbox": box,
                                        "quality": "measured"}
            else:
                existing["objects"] += 1
                if box and existing.get("bbox"):
                    existing["bbox"] = [
                        [min(existing["bbox"][0][i], box[0][i])
                         for i in range(3)],
                        [max(existing["bbox"][1][i], box[1][i])
                         for i in range(3)]]
                elif box:
                    existing["bbox"] = box
        return fingerprints

    def close(self) -> None:
        self._client.close()

    def _connected(self) -> ListenerClient:
        if not self._client.connected:
            self._client.connect()
        return self._client

    def _affected(self, entry: dict) -> list[str]:
        params = entry["params"]
        if entry["op"] in ops.TRANSFORM_OPS or entry["op"] in (
                "set_layer", "group", "ungroup"):
            return list(params.get("ids") or params.get("members") or [])
        if entry["op"] == "set_name":
            return [params["id"]]
        return []
