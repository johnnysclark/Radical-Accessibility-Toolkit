"""The engine: validate, journal, apply, confirm.

Every frontend (CLI, MCP server, chat REPL) routes mutations through
here. The engine takes the write lock, derives fresh state from disk,
validates, runs the backend, appends the journal entry, and returns
speakable confirmation lines. If anything fails before the journal
append, nothing happened.
"""

from __future__ import annotations

import os

from maquette import describe, grammar, ops, snapshot, undo
from maquette import journal as journal_mod
from maquette.backends import choose_backend, headless_available, make_backend
from maquette.backends.base import BackendError
from maquette.grammar import GrammarError
from maquette.journal import JournalError
from maquette.ops import OpError
from maquette.project import Project, ProjectError, atomic_write
from maquette.scene import Scene, SceneError

USER_ERRORS = (OpError, GrammarError, ProjectError, SceneError,
               BackendError, JournalError, LookupError)

DRIFT_TOLERANCE = 0.001


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

    def export(self, path: str, fmt: str | None = None) -> dict:
        fmt = (fmt or os.path.splitext(path)[1].lstrip(".") or "text").lower()
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
        raise OpError("unknown export format {0!r}; use 3dm or text".format(fmt))

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
