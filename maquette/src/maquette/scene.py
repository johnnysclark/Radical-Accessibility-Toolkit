"""Semantic scene state, derived deterministically from journal entries.

The scene never talks to a backend. It applies journal entries one by
one with pure math, so the same journal always produces the same scene
regardless of which backend executed the ops. Backend-measured
fingerprints recorded in entries are adopted only when they beat the
analytic prediction (quality "measured" beats "approx"/"unknown",
never "exact").
"""

from __future__ import annotations

import copy as copymod
import re

from maquette import DEFAULT_LAYER, SNAPSHOT_SCHEMA, VERSION
from maquette import geom, ids, ops


class SceneError(Exception):
    pass


_AUTO_NAME = re.compile(r"^([a-z]+) (\d+)$")
_KNOWN_KINDS = set(ops.KINDS.values())


class Scene:
    def __init__(self, project_name: str = "", units: str = "meters"):
        self.project_name = project_name
        self.units = units
        self.objects: dict[str, dict] = {}
        self.layers: list[str] = [DEFAULT_LAYER]
        self.groups: dict[str, dict] = {}
        self.counters: dict[str, int] = {}
        self.current_layer = DEFAULT_LAYER
        self.last_created: str | None = None
        self.applied_seq = 0

    # -- queries ---------------------------------------------------------

    def find(self, ref) -> dict | None:
        """Resolve an id, a name, or the word last to an object record."""
        if ref is None:
            return None
        ref = str(ref)
        if ref == "last":
            return self.objects.get(self.last_created) if self.last_created else None
        if ref in self.objects:
            return self.objects[ref]
        matches = [o for o in self.objects.values()
                   if o["name"] == ref and o["status"] == "alive"]
        if len(matches) > 1:
            raise SceneError(
                "the name {0!r} matches {1} objects: {2}. Use an id.".format(
                    ref, len(matches), ", ".join(o["id"] for o in matches)))
        return matches[0] if matches else None

    def alive_objects(self) -> list[dict]:
        return [o for o in self.objects.values() if o["status"] == "alive"]

    def pending_objects(self) -> list[dict]:
        return [o for o in self.alive_objects() if o.get("pending")]

    def extents(self):
        return geom.merge_bboxes(
            [o["fingerprint"].get("bbox") for o in self.alive_objects()])

    # -- state transitions -------------------------------------------------

    def ensure_layer(self, name: str | None) -> None:
        if name and name not in self.layers:
            self.layers.append(name)

    def apply(self, entry: dict) -> None:
        op, params = entry["op"], entry["params"]
        if op in ops.CREATE_OPS:
            self._apply_create(entry)
        elif op in ops.TRANSFORM_OPS:
            self._apply_transform(entry)
        elif op == "copy":
            self._apply_copy(entry)
        elif op == "delete":
            for object_id in params["ids"]:
                self._mark(object_id, "deleted")
        elif op == "restore":
            self._apply_restore(entry)
        elif op == "set_name":
            obj = self.objects[params["id"]]
            obj["name"] = params["name"]
            self._sync_kind_counter(params["name"])
        elif op == "set_layer":
            self.ensure_layer(params["layer"])
            for object_id in params["ids"]:
                self.objects[object_id]["layer"] = params["layer"]
        elif op == "create_layer":
            self.ensure_layer(params["name"])
        elif op == "group":
            gid = params["gid"]
            self.groups[gid] = {"name": params["name"],
                                "members": list(params["members"])}
            for object_id in params["members"]:
                self.objects[object_id]["group"] = gid
            self._sync_counter("group", gid, ids.GROUP_PREFIX)
        elif op == "ungroup":
            gid = params["gid"]
            for object_id in self.groups.get(gid, {}).get("members", []):
                if object_id in self.objects:
                    self.objects[object_id]["group"] = None
            self.groups.pop(gid, None)
        elif op == "reconcile":
            for object_id, fingerprint in params["fingerprints"].items():
                if object_id in self.objects:
                    obj = self.objects[object_id]
                    obj["fingerprint"] = dict(fingerprint, quality="measured")
                    obj["pending"] = False
        elif op == "noop":
            pass
        else:
            raise SceneError("scene cannot apply op {0}".format(op))
        self.applied_seq = entry["seq"]

    def _apply_create(self, entry: dict) -> None:
        op, params = entry["op"], entry["params"]
        predicted = ops.predict_fingerprint(op, params, self)
        fingerprint = self._better_fingerprint(predicted, entry)
        backend = entry.get("result", {}).get("backend")
        record = {
            "id": entry["id"],
            "name": entry["name"],
            "op": op,
            "kind": ops.KINDS[op],
            "params": copymod.deepcopy(params),
            "layer": entry["layer"] or DEFAULT_LAYER,
            "status": "alive",
            "group": None,
            "created_seq": entry["seq"],
            "fingerprint": fingerprint,
            "pending": op in ops.COMPUTE_OPS and backend != "live",
        }
        if op in ops.CONSUMING_OPS:
            inputs = params.get("inputs") or (params["keep"] + params["cut"])
            for object_id in inputs:
                self._mark(object_id, "consumed")
        self.objects[entry["id"]] = record
        self.ensure_layer(record["layer"])
        self._sync_counter("object", entry["id"], ids.ID_PREFIX)
        self._sync_kind_counter(entry["name"])
        self.last_created = entry["id"]

    def _apply_transform(self, entry: dict) -> None:
        op, params = entry["op"], entry["params"]
        for object_id in params["ids"]:
            obj = self.objects[object_id]
            box = obj["fingerprint"].get("bbox")
            quality = obj["fingerprint"].get("quality", "unknown")
            if op == "move":
                box = geom.translate_bbox(box, params["vector"])
            elif op == "rotate":
                box = geom.transform_bbox(box, lambda p: geom.rotate_point(
                    p, params["center"], params["angle"], params["axis"]))
                quality = _degrade(quality)
            elif op == "scale":
                box = geom.transform_bbox(box, lambda p: geom.scale_point(
                    p, params["center"], params["factors"]))
                if any(f < 0 for f in params["factors"]):
                    quality = _degrade(quality)
            elif op == "mirror":
                box = geom.transform_bbox(box, lambda p: geom.mirror_point(
                    p, params["plane_point"], params["plane_normal"]))
                quality = _degrade(quality)
            obj["fingerprint"] = {
                "objects": obj["fingerprint"].get("objects"),
                "bbox": box, "quality": quality if box else "unknown"}

    def _apply_copy(self, entry: dict) -> None:
        params = entry["params"]
        for batch_index, (batch_ids, batch_names) in enumerate(
                zip(params["new_ids"], params["new_names"])):
            offset = geom.scale_vec(params["vector"], batch_index + 1)
            for source_id, new_id, new_name in zip(
                    params["ids"], batch_ids, batch_names):
                source = self.objects[source_id]
                record = copymod.deepcopy(source)
                record["id"] = new_id
                record["name"] = new_name
                record["group"] = None
                record["created_seq"] = entry["seq"]
                record["fingerprint"] = {
                    "objects": source["fingerprint"].get("objects"),
                    "bbox": geom.translate_bbox(
                        source["fingerprint"].get("bbox"), offset),
                    "quality": source["fingerprint"].get("quality", "unknown"),
                }
                self.objects[new_id] = record
                self._sync_counter("object", new_id, ids.ID_PREFIX)
                self._sync_kind_counter(new_name)
                self.last_created = new_id
        self.ensure_layer(entry.get("layer"))

    def _apply_restore(self, entry: dict) -> None:
        for spec in entry["params"]["objects"]:
            try:
                fingerprint = ops.predict_fingerprint(spec["op"], spec["params"], self)
            except Exception:
                fingerprint = {"objects": 1, "bbox": None, "quality": "unknown"}
            for transform in spec.get("transforms", []):
                fingerprint = _transformed_fingerprint(fingerprint, transform)
            record = self.objects.get(spec["id"], {})
            record.update({
                "id": spec["id"], "name": spec["name"], "op": spec["op"],
                "kind": ops.KINDS.get(spec["op"], "object"),
                "params": copymod.deepcopy(spec["params"]),
                "layer": spec["layer"], "status": "alive",
                "group": record.get("group"),
                "created_seq": record.get("created_seq", entry["seq"]),
                "fingerprint": fingerprint,
                "pending": spec["op"] in ops.COMPUTE_OPS,
            })
            self.objects[spec["id"]] = record
            self.ensure_layer(spec["layer"])
            self._sync_counter("object", spec["id"], ids.ID_PREFIX)

    def _mark(self, object_id: str, status: str) -> None:
        obj = self.objects[object_id]
        obj["status"] = status
        gid = obj.get("group")
        if gid and gid in self.groups:
            members = self.groups[gid]["members"]
            if object_id in members:
                members.remove(object_id)
        obj["group"] = None

    def _better_fingerprint(self, predicted: dict, entry: dict) -> dict:
        measured = entry.get("result", {}).get("fingerprint")
        if predicted.get("quality") != "exact" and measured and measured.get("bbox"):
            return {"objects": measured.get("objects"),
                    "bbox": measured["bbox"], "quality": "measured"}
        return predicted

    def _sync_counter(self, key: str, identifier: str, prefix: str) -> None:
        if identifier and identifier.startswith(prefix) and identifier[1:].isdigit():
            self.counters[key] = max(self.counters.get(key, 0), int(identifier[1:]))

    def _sync_kind_counter(self, name: str | None) -> None:
        if not name:
            return
        match = _AUTO_NAME.match(name)
        if match and match.group(1) in _KNOWN_KINDS:
            key = "kind:" + match.group(1)
            self.counters[key] = max(self.counters.get(key, 0),
                                     int(match.group(2)))

    # -- snapshot round trip ----------------------------------------------

    def to_dict(self) -> dict:
        return {
            "schema": SNAPSHOT_SCHEMA,
            "upto_seq": self.applied_seq,
            "meta": {"project": self.project_name, "units": self.units,
                     "engine": VERSION},
            "objects": self.objects,
            "layers": self.layers,
            "groups": self.groups,
            "counters": self.counters,
            "current_layer": self.current_layer,
            "last_created": self.last_created,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Scene":
        scene = cls(data.get("meta", {}).get("project", ""),
                    data.get("meta", {}).get("units", "meters"))
        scene.objects = data.get("objects", {})
        scene.layers = data.get("layers", [DEFAULT_LAYER])
        scene.groups = data.get("groups", {})
        scene.counters = data.get("counters", {})
        scene.current_layer = data.get("current_layer", DEFAULT_LAYER)
        scene.last_created = data.get("last_created")
        scene.applied_seq = data.get("upto_seq", 0)
        return scene


def _degrade(quality: str) -> str:
    return "approx" if quality in ("exact", "measured", "approx") else quality


def _transformed_fingerprint(fingerprint: dict, transform: dict) -> dict:
    op, params = transform["op"], transform["params"]
    box = fingerprint.get("bbox")
    quality = fingerprint.get("quality", "unknown")
    if op == "move":
        box = geom.translate_bbox(box, params["vector"])
    elif op == "rotate":
        box = geom.transform_bbox(box, lambda p: geom.rotate_point(
            p, params["center"], params["angle"], params["axis"]))
        quality = _degrade(quality)
    elif op == "scale":
        box = geom.transform_bbox(box, lambda p: geom.scale_point(
            p, params["center"], params["factors"]))
    elif op == "mirror":
        box = geom.transform_bbox(box, lambda p: geom.mirror_point(
            p, params["plane_point"], params["plane_normal"]))
        quality = _degrade(quality)
    return {"objects": fingerprint.get("objects"), "bbox": box,
            "quality": quality if box else "unknown"}
