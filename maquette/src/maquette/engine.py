"""The engine: validate, journal, apply, confirm.

Every frontend (CLI, MCP server, chat REPL) routes mutations through
here. The engine takes the write lock, derives fresh state from disk,
validates, runs the backend, appends the journal entry, and returns
speakable confirmation lines. If anything fails before the journal
append, nothing happened.
"""

from __future__ import annotations

import os

from maquette import describe, drawing, grammar, ops, snapshot, undo
from maquette import journal as journal_mod
from maquette.backends import (choose_backend, headless_available,
                               listener_reachable, make_backend)
from maquette.backends.base import BackendError
from maquette.grammar import GrammarError
from maquette.journal import JournalError
from maquette.ops import OpError
from maquette.project import Project, ProjectError, atomic_write
from maquette.scene import Scene, SceneError

USER_ERRORS = (OpError, GrammarError, ProjectError, SceneError,
               BackendError, JournalError, LookupError)

DRIFT_TOLERANCE = 0.001

# Kinds with no volume to mesh or cut; everything else goes to Rhino.
FLAT_KINDS = {"point", "line", "polyline", "circle", "arc", "rectangle",
              "curve", "text"}
AXIS_INDEX = {"x": 0, "y": 1, "z": 2}


class Engine:
    def __init__(self, project: Project, backend: str = "auto",
                 actor: str = "cli"):
        self.project = project
        self.requested_backend = backend
        self.actor = actor
        self._backend = None
        self._backend_note_given = False

    # -- reads -------------------------------------------------------------

    def scene(self) -> Scene:
        return snapshot.load_scene(self.project)

    def entries(self) -> list[dict]:
        return list(journal_mod.read_entries(self.project.journal_path))

    # -- mutations ----------------------------------------------------------

    def run_text(self, text: str) -> dict:
        return self.run_op(grammar.parse(text))

    def run_op(self, op_dict: dict) -> dict:
        with self.project.write_lock():
            scene = self.scene()
            fields = ops.validate(op_dict, scene)
            entry, result_warnings = self._execute(fields, scene)
            snapshot.maybe_write_snapshot(self.project, scene)
        return {"lines": describe.confirmation(entry, scene),
                "warnings": self._collect_warnings(result_warnings)}

    def undo_steps(self, steps: int = 1) -> dict:
        lines, warnings = [], []
        with self.project.write_lock():
            scene = self.scene()
            entries = self.entries()
            undone = 0
            for _ in range(max(1, steps)):
                target = undo.pick_undo_target(entries)
                if target is None:
                    if undone == 0:
                        raise OpError("nothing to undo")
                    break
                planned = ops.plan_inverse(target, scene, entries)
                lines.append("undoing step {0}: {1}.".format(
                    target["seq"], journal_mod.entry_summary(target)))
                for op_dict in planned:
                    fields = ops.validate(op_dict, scene)
                    entry, result_warnings = self._execute(
                        fields, scene, undo_of=target["seq"])
                    entries.append(entry)
                    lines.extend(describe.confirmation(entry, scene))
                    warnings.extend(result_warnings)
                undone += 1
            snapshot.maybe_write_snapshot(self.project, scene)
        return {"lines": lines, "warnings": self._collect_warnings(warnings)}

    def rebuild(self, backend_name: str | None = None) -> dict:
        name = backend_name or self.requested_backend
        if name == "auto":
            backend, note = choose_backend(self.project, "auto")
        else:
            backend, note = make_backend(name, self.project), ""
        warnings = [note] if note else []
        with self.project.write_lock():
            entries = self.entries()
            backend.begin_rebuild()
            replay = Scene(self.project.name, self.project.units)
            realized_steps = 0
            for entry in entries:
                try:
                    result = backend.apply(entry, replay)
                except BackendError as exc:
                    warnings.append("step {0} failed on backend {1}: {2}".format(
                        entry["seq"], backend.name, exc))
                    result = {"backend": backend.name, "status": "recorded",
                              "fingerprint": None, "output": str(exc)}
                drift = self._drift(entry, result)
                if drift:
                    warnings.append(drift)
                if result.get("status") == "applied":
                    realized_steps += 1
                replay.apply(entry)
            fingerprints = backend.finish_rebuild()
            lines = ["rebuilt {0} journal steps on backend {1}.".format(
                len(entries), backend.name),
                "{0} steps produced geometry; {1} objects realized.".format(
                    realized_steps, len(fingerprints))]
            if fingerprints:
                fields = ops.validate({"op": "reconcile", "params": {
                    "fingerprints": fingerprints,
                    "backend": backend.name}}, replay)
                scene = self.scene()
                entry, _ = self._execute_prevalidated(fields, scene,
                                                      backend_result={
                                                          "backend": backend.name,
                                                          "status": "applied",
                                                          "fingerprint": None,
                                                          "output": ""})
                snapshot.write_snapshot(self.project, scene)
            backend.close()
        return {"lines": lines, "warnings": self._collect_warnings(warnings)}

    def export(self, path: str, fmt: str | None = None,
               scale: str | None = None) -> dict:
        fmt = (fmt or os.path.splitext(path)[1].lstrip(".") or "text").lower()
        if fmt == "stl":
            return self._export_stl(path, scale)
        if fmt in ("txt", "text"):
            scene = self.scene()
            text = "\n".join(describe.full(scene)) + "\n"
            atomic_write(path, text)
            return {"lines": ["wrote text description to {0}.".format(path)],
                    "warnings": []}
        if fmt == "3dm":
            if not headless_available():
                raise OpError(
                    "exporting 3dm needs the rhino3dm package. "
                    "Run: pip install 'maquette[headless]'")
            from maquette.backends.headless import HeadlessBackend
            backend = HeadlessBackend(self.project)
            backend.begin_rebuild()
            replay = Scene(self.project.name, self.project.units)
            skipped = []
            for entry in self.entries():
                result = backend.apply(entry, replay)
                if (result.get("status") == "recorded"
                        and entry["op"] in ops.CREATE_OPS):
                    skipped.append(entry["id"])
                replay.apply(entry)
            backend.save_3dm(path)
            backend.close()
            lines = ["wrote {0}.".format(path)]
            warnings = []
            if skipped:
                warnings.append(
                    "{0} objects need Rhino to compute and are not in the "
                    "file: {1}. Run a live rebuild to realize them.".format(
                        len(skipped), ", ".join(skipped)))
            return {"lines": lines, "warnings": warnings}
        raise OpError(
            "unknown export format {0!r}; use 3dm, stl, or txt. For 2D "
            "drawings, use: maquette plan or maquette section.".format(fmt))

    # -- fabrication outputs: STL, plans, sections ----------------------------

    def export_plan(self, height, path: str, scale: str | None = None) -> dict:
        """Cut a horizontal plane and write a 2D plan (.svg or .dxf)."""
        return self._export_cut("z", height, path, scale)

    def export_section(self, axis: str, position, path: str,
                       scale: str | None = None) -> dict:
        """Cut a vertical plane at x or y and write a 2D section."""
        axis = (axis or "").lower()
        if axis not in ("x", "y"):
            raise OpError(
                "say which way to cut: maquette section x POSITION PATH "
                "cuts across x; maquette section y POSITION PATH cuts "
                "across y.")
        return self._export_cut(axis, position, path, scale)

    def _export_cut(self, axis: str, position, path: str,
                    scale: str | None) -> dict:
        position = self._number(position, "the cut position")
        factor, spoken_scale = drawing.parse_scale(scale, self.project.units)
        extension = os.path.splitext(path)[1].lower()
        if extension not in (".svg", ".dxf"):
            raise OpError(
                "end the drawing path in .svg or .dxf, like "
                "exports/plan.svg")
        scene = self.scene()
        candidates = [o for o in scene.alive_objects()
                      if o["kind"] not in FLAT_KINDS]
        if not candidates:
            raise OpError(
                "nothing to cut yet: the model has no solids or surfaces. "
                "Make a box, extrusion, or other volume first.")
        queries = self._live_queries("cutting plans and sections")
        origin = [0.0, 0.0, 0.0]
        normal = [0.0, 0.0, 0.0]
        origin[AXIS_INDEX[axis]] = position
        normal[AXIS_INDEX[axis]] = 1.0
        outlines = []
        cut_count = 0
        missing, notes = [], []
        for obj in candidates:
            data = queries.query_section(obj["id"], origin, normal)
            if not data.get("found"):
                missing.append(self._spoken_ref(obj))
                continue
            for why in data.get("skipped") or []:
                notes.append("{0} {1}.".format(self._spoken_ref(obj), why))
            polylines = data.get("polylines") or []
            if polylines:
                cut_count += 1
            for polyline in polylines:
                points = list(polyline["points"])
                if polyline.get("closed") and points and points[0] != points[-1]:
                    points.append(points[0])
                outlines.append({
                    "points": [tuple(value * factor for value in
                                     drawing.to_paper(axis, point))
                               for point in points],
                    "closed": bool(polyline.get("closed")),
                })
        if not outlines:
            if missing and len(missing) == len(candidates):
                raise OpError(
                    "none of the model is in Rhino yet. Run: maquette "
                    "rebuild, then try again.")
            raise OpError(self._empty_cut_message(axis, position, scene))
        kind_word = "plan" if axis == "z" else "section"
        where = "height" if axis == "z" else axis
        title = "Maquette {0} of {1}, cut at {2} {3:g} {4}, scale {5}".format(
            kind_word, self.project.name, where, position,
            self.project.units, spoken_scale)
        if extension == ".svg":
            stats = drawing.write_svg(path, outlines, title)
        else:
            stats = drawing.write_dxf(path, outlines, title)
        lines = [
            "wrote {0}.".format(path),
            "{0} cut at {1} {2:g} {3} through {4} objects; "
            "{5} outlines.".format(kind_word, where, position,
                                   self.project.units, cut_count,
                                   stats["outlines"]),
            "scale {0}; sheet {1:g} by {2:g} millimeters.".format(
                spoken_scale, round(stats["sheet_mm"][0], 1),
                round(stats["sheet_mm"][1], 1)),
        ]
        warnings = list(notes)
        if missing:
            warnings.append(
                "not in Rhino, so not in the drawing: {0}. Run: maquette "
                "rebuild.".format(", ".join(missing)))
        return {"lines": lines, "warnings": warnings}

    def _export_stl(self, path: str, scale: str | None) -> dict:
        factor, spoken_scale = drawing.parse_scale(scale, self.project.units)
        scene = self.scene()
        candidates = [o for o in scene.alive_objects()
                      if o["kind"] not in FLAT_KINDS]
        if not candidates:
            raise OpError(
                "nothing printable yet: the model has no solids. Make a "
                "box, cylinder, extrusion, or other volume first.")
        queries = self._live_queries("STL export")
        solids, open_shells, missing, notes = [], [], [], []
        for obj in candidates:
            data = queries.query_mesh(obj["id"])
            if not data.get("found"):
                missing.append(self._spoken_ref(obj))
                continue
            for why in data.get("skipped") or []:
                notes.append("{0} {1}.".format(self._spoken_ref(obj), why))
            if not data.get("faces"):
                continue
            solids.append({"vertices": data["vertices"],
                           "faces": data["faces"]})
            if not data.get("closed"):
                open_shells.append(self._spoken_ref(obj))
        if not solids:
            if missing and len(missing) == len(candidates):
                raise OpError(
                    "none of the model is in Rhino yet. Run: maquette "
                    "rebuild, then export again.")
            raise OpError(
                "nothing in the model could be meshed for printing." +
                (" " + " ".join(notes) if notes else ""))
        stats = drawing.write_stl(path, solids, factor)
        size = [round(value, 1) for value in stats["size_mm"]]
        lines = [
            "wrote {0}.".format(path),
            "{0} solids, {1} triangles, scale {2}, millimeters.".format(
                len(solids), stats["triangles"], spoken_scale),
            "print size: {0:g} by {1:g} by {2:g} millimeters.".format(
                size[0], size[1], size[2]),
        ]
        warnings = list(notes)
        if open_shells:
            warnings.append(
                "not watertight: {0} {1} open edges. Slicers usually "
                "repair this, but a clean print wants closed solids; "
                "try union, or cap the shape in Rhino.".format(
                    ", ".join(open_shells),
                    "has" if len(open_shells) == 1 else "have"))
        else:
            lines.append("watertight: yes, every shell is closed.")
        if missing:
            warnings.append(
                "not in Rhino, so not in the file: {0}. Run: maquette "
                "rebuild, then export again.".format(", ".join(missing)))
        return {"lines": lines, "warnings": warnings}

    def _live_queries(self, purpose: str):
        """Return a connected live backend, or say exactly what is wrong.

        Meshing and plane cuts are Rhino's math; record and headless
        backends cannot do them, so this never downgrades silently.
        """
        if self.requested_backend in ("record", "headless"):
            raise OpError(
                "{0} needs the live Rhino connection and cannot run on "
                "backend {1}. Open Rhino and run again without "
                "--backend.".format(purpose, self.requested_backend))
        host, port = self.project.listener_address
        if not listener_reachable(host, port):
            raise OpError(
                "{0} needs Rhino running with the Maquette listener: "
                "Rhino does the geometry math. Open Rhino, then check "
                "with: maquette connect".format(purpose))
        from maquette.backends.live import LiveBackend
        return LiveBackend(self.project)

    def _spoken_ref(self, obj: dict) -> str:
        if obj.get("name"):
            return '{0} "{1}"'.format(obj["id"], obj["name"])
        return obj["id"]

    def _empty_cut_message(self, axis: str, position: float,
                           scene: Scene) -> str:
        where = "height" if axis == "z" else axis
        box = scene.extents()
        if box:
            index = AXIS_INDEX[axis]
            return ("the plane at {0} {1:g} does not cut anything; the "
                    "model spans {2} {3:g} to {4:g} {5}.".format(
                        where, position, where, box[0][index],
                        box[1][index], self.project.units))
        return ("the plane at {0} {1:g} does not cut anything in the "
                "model.".format(where, position))

    def _number(self, value, label: str) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            raise OpError("{0} must be a number, like 1.2 - got "
                          "{1!r}.".format(label, value))

    # -- internals -----------------------------------------------------------

    def _execute(self, fields: dict, scene: Scene,
                 undo_of: int | None = None) -> tuple[dict, list[str]]:
        backend = self._get_backend()
        seq = scene.applied_seq + 1
        entry = journal_mod.make_entry(
            seq, fields["op"], fields["params"], self.actor,
            obj_id=fields.get("id"), name=fields.get("name"),
            layer=fields.get("layer"), undo_of=undo_of)
        result = backend.apply(entry, scene)
        entry["result"] = result
        journal_mod.append(self.project.journal_path, entry)
        scene.apply(entry)
        warnings = []
        output = result.get("output")
        if output:
            warnings.append(output)
        return entry, warnings

    def _execute_prevalidated(self, fields: dict, scene: Scene,
                              backend_result: dict) -> tuple[dict, list[str]]:
        seq = scene.applied_seq + 1
        entry = journal_mod.make_entry(
            seq, fields["op"], fields["params"], self.actor,
            obj_id=fields.get("id"), name=fields.get("name"),
            layer=fields.get("layer"))
        entry["result"] = backend_result
        journal_mod.append(self.project.journal_path, entry)
        scene.apply(entry)
        return entry, []

    def _get_backend(self):
        if self._backend is None:
            self._backend, self._backend_note = choose_backend(
                self.project, self.requested_backend)
        return self._backend

    def _collect_warnings(self, warnings: list[str]) -> list[str]:
        out = list(dict.fromkeys(w for w in warnings if w))
        if not self._backend_note_given and self._backend is not None:
            note = getattr(self, "_backend_note", "")
            if note:
                out.insert(0, note)
            self._backend_note_given = True
        return out

    def _drift(self, entry: dict, new_result: dict) -> str | None:
        old = (entry.get("result") or {}).get("fingerprint")
        new = new_result.get("fingerprint")
        if not old or not new:
            return None
        old_box, new_box = old.get("bbox"), new.get("bbox")
        if old_box and new_box:
            for corner_old, corner_new in zip(old_box, new_box):
                for a, b in zip(corner_old, corner_new):
                    if abs(a - b) > DRIFT_TOLERANCE:
                        return ("drift at step {0} ({1} {2}): geometry moved "
                                "since it was first recorded.".format(
                                    entry["seq"], entry["op"],
                                    entry.get("id") or ""))
        if (old.get("objects") and new.get("objects")
                and old["objects"] != new["objects"]):
            return ("drift at step {0} ({1} {2}): object count changed "
                    "from {3} to {4}.".format(
                        entry["seq"], entry["op"], entry.get("id") or "",
                        old["objects"], new["objects"]))
        return None
