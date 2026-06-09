"""Headless backend: real geometry into a .3dm file via rhino3dm, no Rhino.

Keeps exports/model.3dm in step with the journal, op by op. rhino3dm
stores geometry but cannot compute: booleans, lofts, and scripts stay
"recorded" (pending) until a live rebuild inside Rhino. The .3dm is
derived data - "maquette rebuild --backend headless" regenerates it
from the journal at any time.

Every object carries UserText MAQ_ID / MAQ_NAME / MAQ_OP / MAQ_SEQ so
later ops, live listeners, and humans in Rhino can find it.
"""

from __future__ import annotations

import math
import os

import rhino3dm

from maquette import ops
from maquette.backends.base import BackendAPI, BackendError, recorded

MODEL_FILE = "model.3dm"
FILE_VERSION = 8

# What this backend can realize, asserted by tests/test_capabilities.py.
# full = real geometry; approx = stand-in geometry (flagged); record =
# journaled intent pending a live rebuild.
SUPPORT = {
    "create_point": "full", "create_line": "full", "create_polyline": "full",
    "create_circle": "full", "create_arc": "full", "create_rectangle": "full",
    "create_curve": "approx", "create_text": "approx", "create_box": "full",
    "create_sphere": "full", "create_cylinder": "full", "create_cone": "full",
    "extrude": "full", "revolve": "full",
    "loft": "record", "boolean_union": "record",
    "boolean_difference": "record", "boolean_intersection": "record",
    "script": "record",
}

UNIT_SYSTEMS = {
    "meters": rhino3dm.UnitSystem.Meters,
    "millimeters": rhino3dm.UnitSystem.Millimeters,
    "centimeters": rhino3dm.UnitSystem.Centimeters,
    "feet": rhino3dm.UnitSystem.Feet,
    "inches": rhino3dm.UnitSystem.Inches,
}


def _p3(value) -> rhino3dm.Point3d:
    return rhino3dm.Point3d(value[0], value[1], value[2])


def _v3(value) -> rhino3dm.Vector3d:
    return rhino3dm.Vector3d(value[0], value[1], value[2])


class HeadlessBackend(BackendAPI):
    name = "headless"

    def __init__(self, project):
        self.project = project
        self.model_path = os.path.join(project.exports_dir, MODEL_FILE)
        self._file = None
        self._rebuilding = False

    # -- BackendAPI ----------------------------------------------------------

    def apply(self, entry: dict, scene) -> dict:
        op = entry["op"]
        try:
            if op in ops.CREATE_OPS:
                return self._apply_create(entry)
            if op in ops.TRANSFORM_OPS:
                return self._apply_transform(entry)
            handler = getattr(self, "_apply_" + op, None)
            if handler is not None:
                return handler(entry)
            return recorded(self.name)
        except BackendError:
            raise
        except Exception as exc:
            raise BackendError(
                "rhino3dm failed on {0}: {1}".format(op, exc))

    def begin_rebuild(self) -> None:
        self._file = self._fresh_file()
        self._rebuilding = True

    def finish_rebuild(self) -> dict:
        fingerprints = {}
        by_id: dict[str, list] = {}
        for obj in self._model().Objects:
            maq_id = obj.Attributes.GetUserString("MAQ_ID")
            if maq_id:
                by_id.setdefault(maq_id, []).append(obj)
        for maq_id, objects in by_id.items():
            fingerprints[maq_id] = self._fingerprint(objects)
        self._rebuilding = False
        self._save()
        return fingerprints

    def close(self) -> None:
        self._file = None

    def save_3dm(self, path: str) -> None:
        """Write the in-memory model to an arbitrary path (export)."""
        model = self._model()
        directory = os.path.dirname(os.path.abspath(path))
        os.makedirs(directory, exist_ok=True)
        tmp = path + ".tmp"
        if not model.Write(tmp, FILE_VERSION):
            raise BackendError("could not write {0}".format(path))
        os.replace(tmp, path)

    # -- op handlers ----------------------------------------------------------

    def _apply_create(self, entry: dict) -> dict:
        op, params = entry["op"], entry["params"]
        support = SUPPORT.get(op, "record")
        if support == "record":
            return recorded(self.name, self._pending_note(op, entry))
        model = self._model()
        geometries, note = self._build(op, params, model)
        if geometries is None:
            return recorded(self.name, note)
        added = []
        for geometry in geometries:
            attrs = self._attributes(model, entry)
            uuid = self._add_geometry(model, geometry, attrs)
            added.append(uuid)
        self._save()
        result = {"backend": self.name, "status": "applied",
                  "fingerprint": self._fingerprint(
                      self._find(model, [entry["id"]])),
                  "output": note}
        return result

    def _apply_transform(self, entry: dict) -> dict:
        op, params = entry["op"], entry["params"]
        model = self._model()
        found = self._find(model, params["ids"])
        if not found:
            return recorded(self.name, self._missing_note(params["ids"]))
        xform = self._xform(op, params)
        for obj in found:
            obj.Geometry.Transform(xform)
        self._save()
        return {"backend": self.name, "status": "applied",
                "fingerprint": self._fingerprint(found), "output": ""}

    def _apply_copy(self, entry: dict) -> dict:
        params = entry["params"]
        model = self._model()
        sources = {o.Attributes.GetUserString("MAQ_ID"): o
                   for o in self._find(model, params["ids"])}
        if len(sources) != len(params["ids"]):
            return recorded(self.name, self._missing_note(params["ids"]))
        created = []
        for batch_index, (batch_ids, batch_names) in enumerate(
                zip(params["new_ids"], params["new_names"])):
            offset = [c * (batch_index + 1) for c in params["vector"]]
            for source_id, new_id, new_name in zip(
                    params["ids"], batch_ids, batch_names):
                source = sources[source_id]
                geometry = source.Geometry.Duplicate()
                geometry.Transform(rhino3dm.Transform.Translation(*offset))
                attrs = self._attributes(model, {
                    "id": new_id, "name": new_name, "op": "copy",
                    "seq": entry["seq"],
                    "layer": self._layer_path(model, source)})
                self._add_geometry(model, geometry, attrs)
                created.append(new_id)
        self._save()
        return {"backend": self.name, "status": "applied",
                "fingerprint": self._fingerprint(self._find(model, created)),
                "output": ""}

    def _apply_delete(self, entry: dict) -> dict:
        model = self._model()
        found = self._find(model, entry["params"]["ids"])
        for obj in found:
            model.Objects.Delete(obj.Attributes.Id)
        self._save()
        return {"backend": self.name, "status": "applied",
                "fingerprint": None,
                "output": "" if found else self._missing_note(
                    entry["params"]["ids"])}

    def _apply_restore(self, entry: dict) -> dict:
        model = self._model()
        restored = []
        notes = []
        for spec in entry["params"]["objects"]:
            support = SUPPORT.get(spec["op"], "record")
            if support == "record":
                notes.append(self._pending_note(spec["op"], spec))
                continue
            geometries, note = self._build(spec["op"], spec["params"], model)
            if geometries is None:
                notes.append(note)
                continue
            for geometry in geometries:
                for transform in spec.get("transforms", []):
                    geometry.Transform(
                        self._xform(transform["op"], transform["params"]))
                attrs = self._attributes(model, {
                    "id": spec["id"], "name": spec["name"],
                    "op": spec["op"], "seq": entry["seq"],
                    "layer": spec["layer"]})
                self._add_geometry(model, geometry, attrs)
            restored.append(spec["id"])
        self._save()
        status = "applied" if restored else "recorded"
        return {"backend": self.name, "status": status,
                "fingerprint": self._fingerprint(self._find(model, restored)),
                "output": "; ".join(n for n in notes if n)}

    def _apply_set_name(self, entry: dict) -> dict:
        model = self._model()
        found = self._find(model, [entry["params"]["id"]])
        for obj in found:
            obj.Attributes.Name = entry["params"]["name"]
            obj.Attributes.SetUserString("MAQ_NAME", entry["params"]["name"])
        self._save()
        return {"backend": self.name, "status": "applied",
                "fingerprint": None, "output": ""}

    def _apply_set_layer(self, entry: dict) -> dict:
        model = self._model()
        index = self._ensure_layer(model, entry["params"]["layer"])
        for obj in self._find(model, entry["params"]["ids"]):
            obj.Attributes.LayerIndex = index
        self._save()
        return {"backend": self.name, "status": "applied",
                "fingerprint": None, "output": ""}

    def _apply_create_layer(self, entry: dict) -> dict:
        model = self._model()
        self._ensure_layer(model, entry["params"]["name"])
        self._save()
        return {"backend": self.name, "status": "applied",
                "fingerprint": None, "output": ""}

    # -- geometry builders -----------------------------------------------------

    def _build(self, op: str, params: dict, model):
        """Return (list of GeometryBase, note) or (None, why)."""
        if op == "create_point":
            return [rhino3dm.Point(_p3(params["at"]))], ""
        if op == "create_line":
            return [rhino3dm.LineCurve(_p3(params["start"]),
                                       _p3(params["end"]))], ""
        if op == "create_polyline":
            points = [_p3(p) for p in params["points"]]
            if params.get("closed") and params["points"][0] != params["points"][-1]:
                points.append(_p3(params["points"][0]))
            polyline = rhino3dm.Polyline(points)
            return [polyline.ToPolylineCurve()], ""
        if op == "create_rectangle":
            c = params["corner"]
            w, d = params["width"], params["depth"]
            corners = [c, [c[0] + w, c[1], c[2]], [c[0] + w, c[1] + d, c[2]],
                       [c[0], c[1] + d, c[2]], c]
            polyline = rhino3dm.Polyline([_p3(p) for p in corners])
            return [polyline.ToPolylineCurve()], ""
        if op == "create_circle":
            circle = rhino3dm.Circle(_p3(params["center"]), params["radius"])
            return [circle.ToNurbsCurve()], ""
        if op == "create_arc":
            arc = rhino3dm.Arc(_p3(params["p1"]), _p3(params["p2"]),
                               _p3(params["p3"]))
            return [arc.ToNurbsCurve()], ""
        if op == "create_curve":
            curve = rhino3dm.Curve.CreateControlPointCurve(
                [_p3(p) for p in params["points"]], params.get("degree", 3))
            if curve is None:
                return None, "could not build that curve"
            return [curve], ("control-point curve stands in for the "
                             "interpolated curve until a live rebuild")
        if op == "create_text":
            return ([rhino3dm.TextDot(params["text"], _p3(params["at"]))],
                    "a text dot stands in for sized text until a live rebuild")
        if op == "create_box":
            c, s = params["corner"], params["size"]
            bbox = rhino3dm.BoundingBox(
                _p3(c), _p3([c[0] + s[0], c[1] + s[1], c[2] + s[2]]))
            return [rhino3dm.Brep.CreateFromBox(rhino3dm.Box(bbox))], ""
        if op == "create_sphere":
            sphere = rhino3dm.Sphere(_p3(params["center"]), params["radius"])
            return [rhino3dm.Brep.CreateFromSphere(sphere)], ""
        if op == "create_cylinder":
            base = rhino3dm.Circle(_p3(params["base"]), params["radius"])
            cylinder = rhino3dm.Cylinder(base, params["height"])
            return [cylinder.ToBrep(True, True)], ""
        if op == "create_cone":
            b, radius, height = params["base"], params["radius"], params["height"]
            profile = rhino3dm.LineCurve(
                _p3([b[0] + radius, b[1], b[2]]), _p3([b[0], b[1], b[2] + height]))
            axis = rhino3dm.Line(_p3(b), _p3([b[0], b[1], b[2] + height]))
            surface = rhino3dm.RevSurface.Create(profile, axis, 0.0, 2 * math.pi)
            brep = rhino3dm.Brep.CreateFromRevSurface(surface, True, True)
            return [brep], ""
        if op == "extrude":
            return self._build_extrusion(params, model)
        if op == "revolve":
            return self._build_revolve(params, model)
        return None, self._pending_note(op, {"id": "?"})

    def _build_extrusion(self, params: dict, model):
        vector = params["vector"]
        if abs(vector[0]) > 1e-9 or abs(vector[1]) > 1e-9:
            return None, ("extruding along a slanted vector needs Rhino; "
                          "recorded for the next live rebuild")
        sources = self._find(model, [params["source"]])
        if not sources:
            return None, self._missing_note([params["source"]])
        curve = sources[0].Geometry
        if not isinstance(curve, rhino3dm.Curve):
            return None, "{0} is not a curve, so it cannot extrude here".format(
                params["source"])
        extrusion = rhino3dm.Extrusion.Create(
            curve, vector[2], getattr(curve, "IsClosed", False))
        if extrusion is None:
            return None, ("Rhino is needed to extrude that curve; recorded "
                          "for the next live rebuild")
        return [extrusion], ""

    def _build_revolve(self, params: dict, model):
        sources = self._find(model, [params["source"]])
        if not sources:
            return None, self._missing_note([params["source"]])
        curve = sources[0].Geometry
        if not isinstance(curve, rhino3dm.Curve):
            return None, "{0} is not a curve, so it cannot revolve here".format(
                params["source"])
        axis = rhino3dm.Line(_p3(params["axis_start"]), _p3(params["axis_end"]))
        surface = rhino3dm.RevSurface.Create(
            curve, axis, 0.0, math.radians(params["angle"]))
        if surface is None:
            return None, ("Rhino is needed to revolve that curve; recorded "
                          "for the next live rebuild")
        brep = rhino3dm.Brep.CreateFromRevSurface(surface, True, True)
        return [brep or surface], ""

    def _xform(self, op: str, params: dict):
        if op == "move":
            return rhino3dm.Transform.Translation(*params["vector"])
        if op == "rotate":
            return rhino3dm.Transform.Rotation(
                math.radians(params["angle"]), _v3(params["axis"]),
                _p3(params["center"]))
        if op == "scale":
            fx, fy, fz = params["factors"]
            if fx == fy == fz:
                return rhino3dm.Transform.Scale(_p3(params["center"]), fx)
            plane = rhino3dm.Plane(_p3(params["center"]),
                                   rhino3dm.Vector3d(0, 0, 1))
            return rhino3dm.Transform.Scale(plane, fx, fy, fz)
        if op == "mirror":
            return rhino3dm.Transform.Mirror(
                _p3(params["plane_point"]), _v3(params["plane_normal"]))
        raise BackendError("no transform for op {0}".format(op))

    # -- plumbing ---------------------------------------------------------------

    def _model(self):
        if self._file is None:
            if os.path.exists(self.model_path):
                self._file = rhino3dm.File3dm.Read(self.model_path)
                if self._file is None:
                    raise BackendError(
                        "could not read {0}; delete it and run "
                        "maquette rebuild --backend headless".format(
                            self.model_path))
            else:
                self._file = self._fresh_file()
        return self._file

    def _fresh_file(self):
        model = rhino3dm.File3dm()
        model.Settings.ModelUnitSystem = UNIT_SYSTEMS.get(
            self.project.units, rhino3dm.UnitSystem.Meters)
        return model

    def _save(self) -> None:
        if self._rebuilding or self._file is None:
            return
        self._write_file()

    def _write_file(self) -> None:
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        tmp = self.model_path + ".tmp"
        if not self._file.Write(tmp, FILE_VERSION):
            raise BackendError("could not write {0}".format(self.model_path))
        os.replace(tmp, self.model_path)

    def _find(self, model, maq_ids: list[str]):
        wanted = set(maq_ids)
        return [obj for obj in model.Objects
                if obj.Attributes.GetUserString("MAQ_ID") in wanted]

    def _attributes(self, model, entry: dict):
        attrs = rhino3dm.ObjectAttributes()
        attrs.Name = entry.get("name") or ""
        attrs.LayerIndex = self._ensure_layer(
            model, entry.get("layer") or "MAQ::Default")
        attrs.SetUserString("MAQ_ID", entry["id"])
        attrs.SetUserString("MAQ_NAME", entry.get("name") or "")
        attrs.SetUserString("MAQ_OP", entry.get("op") or "")
        attrs.SetUserString("MAQ_SEQ", str(entry.get("seq", "")))
        return attrs

    def _add_geometry(self, model, geometry, attrs):
        objects = model.Objects
        if isinstance(geometry, rhino3dm.Point):
            return objects.AddPoint(geometry.Location, attrs)
        if isinstance(geometry, rhino3dm.TextDot):
            return objects.AddTextDot(geometry.Text, geometry.Point, attrs)
        if isinstance(geometry, rhino3dm.Brep):
            return objects.AddBrep(geometry, attrs)
        if isinstance(geometry, rhino3dm.Extrusion):
            add_extrusion = getattr(objects, "AddExtrusion", None)
            if add_extrusion is not None:
                return add_extrusion(geometry, attrs)
            return objects.AddBrep(geometry.ToBrep(False), attrs)
        if isinstance(geometry, rhino3dm.Curve):
            return objects.AddCurve(geometry, attrs)
        if isinstance(geometry, rhino3dm.Surface):
            return objects.AddSurface(geometry, attrs)
        raise BackendError(
            "no way to store geometry of type {0}".format(type(geometry).__name__))

    def _ensure_layer(self, model, path: str) -> int:
        existing = {layer.FullPath: layer for layer in model.Layers}
        if path in existing:
            return existing[path].Index
        parent_id = None
        full = ""
        index = 0
        for segment in path.split("::"):
            full = segment if not full else full + "::" + segment
            if full in existing:
                parent_id = existing[full].Id
                index = existing[full].Index
                continue
            layer = rhino3dm.Layer()
            layer.Name = segment
            if parent_id is not None:
                layer.ParentLayerId = parent_id
            index = model.Layers.Add(layer)
            created = [l for l in model.Layers][index]
            existing[full] = created
            parent_id = created.Id
        return index

    def _layer_path(self, model, obj) -> str:
        for layer in model.Layers:
            if layer.Index == obj.Attributes.LayerIndex:
                return layer.FullPath
        return "MAQ::Default"

    def _fingerprint(self, objects) -> dict | None:
        if not objects:
            return None
        merged = None
        for obj in objects:
            box = obj.Geometry.GetBoundingBox()
            corners = [[box.Min.X, box.Min.Y, box.Min.Z],
                       [box.Max.X, box.Max.Y, box.Max.Z]]
            if merged is None:
                merged = corners
            else:
                merged = [[min(merged[0][i], corners[0][i]) for i in range(3)],
                          [max(merged[1][i], corners[1][i]) for i in range(3)]]
        merged = [[round(v, 9) for v in corner] for corner in merged]
        return {"objects": len(objects), "bbox": merged, "quality": "measured"}

    def _pending_note(self, op: str, entry: dict) -> str:
        kind = ops.KINDS.get(op, op)
        return ("the {0} needs Rhino to compute; it is journaled and will "
                "become real on the next live rebuild".format(kind))

    def _missing_note(self, maq_ids: list[str]) -> str:
        return ("{0} not in the 3dm file yet; run: maquette rebuild "
                "--backend headless".format(", ".join(maq_ids)))
