"""The 15 model-facing functions shared by the MCP server and chat REPL.

Each returns one plain-text string whose first line starts with OK: or
ERROR: - the same contract as the CLI, because the model reads what
the user hears. stdlib-only; the frontends wrap these in FastMCP or
Agent SDK tooling.
"""

from __future__ import annotations

import contextlib
import io

from maquette import describe, ops
from maquette.engine import Engine, USER_ERRORS
from maquette.project import Project

CREATE_BATCH_OPS = ops.CREATE_OPS - {"script"}
EDIT_OPS = ops.TRANSFORM_OPS | {"copy", "delete", "set_name", "set_layer",
                                "create_layer", "group", "ungroup"}


class MaquetteService:
    def __init__(self, project: Project, backend: str = "auto",
                 actor: str = "mcp"):
        self.project = project
        self.backend = backend
        self.actor = actor

    def _engine(self) -> Engine:
        return Engine(self.project, backend=self.backend, actor=self.actor)

    # -- mutations ------------------------------------------------------------

    def create_objects(self, ops: list[dict]) -> str:
        return self._run_batch(ops, CREATE_BATCH_OPS, "create ops")

    def edit_objects(self, ops: list[dict]) -> str:
        return self._run_batch(ops, EDIT_OPS, "edit ops")

    def run_script(self, code: str, intent: str, name: str | None = None) -> str:
        op = {"op": "script", "params": {"code": code, "intent": intent}}
        if name:
            op["name"] = name
        return self._run_batch([op], {"script"}, "script")

    def undo(self, steps: int = 1) -> str:
        try:
            return _format(self._engine().undo_steps(int(steps)))
        except USER_ERRORS as exc:
            return "ERROR: " + str(exc)

    def rebuild(self, backend: str | None = None) -> str:
        try:
            return _format(self._engine().rebuild(backend))
        except USER_ERRORS as exc:
            return "ERROR: " + str(exc)

    def export_model(self, path: str, format: str | None = None,
                     scale: str | None = None) -> str:
        try:
            return _format(self._engine().export(path, format, scale))
        except USER_ERRORS as exc:
            return "ERROR: " + str(exc)

    def export_plan(self, height, path: str, scale: str | None = None) -> str:
        try:
            return _format(self._engine().export_plan(height, path, scale))
        except USER_ERRORS as exc:
            return "ERROR: " + str(exc)

    def export_section(self, axis: str, position, path: str,
                       scale: str | None = None) -> str:
        try:
            return _format(self._engine().export_section(
                axis, position, path, scale))
        except USER_ERRORS as exc:
            return "ERROR: " + str(exc)

    # -- queries ---------------------------------------------------------------

    def query_scene(self, layer: str | None = None, kind: str | None = None,
                    name_contains: str | None = None) -> str:
        try:
            scene = self._engine().scene()
        except USER_ERRORS as exc:
            return "ERROR: " + str(exc)
        matches = []
        for obj in scene.alive_objects():
            if layer and obj["layer"] != layer \
                    and obj["layer"] != "MAQ::" + layer:
                continue
            if kind and obj["kind"] != kind:
                continue
            if name_contains and name_contains.lower() not in obj["name"].lower():
                continue
            matches.append(obj)
        lines = ["OK: {0} matching objects.".format(len(matches))]
        by_kind: dict[str, int] = {}
        for obj in matches:
            by_kind[obj["kind"]] = by_kind.get(obj["kind"], 0) + 1
        for kind_name in sorted(by_kind):
            lines.append("{0}: {1}".format(kind_name, by_kind[kind_name]))
        for obj in matches[:50]:
            lines.append('{0} "{1}" ({2}) on {3}'.format(
                obj["id"], obj["name"], obj["kind"], obj["layer"]))
        if len(matches) > 50:
            lines.append("and {0} more.".format(len(matches) - 50))
        return "\n".join(lines)

    def describe_scene(self, level: str = "brief") -> str:
        try:
            scene = self._engine().scene()
        except USER_ERRORS as exc:
            return "ERROR: " + str(exc)
        lines = describe.full(scene) if level == "full" else describe.brief(scene)
        return "OK: " + "\n".join(lines)

    def describe_object(self, ref: str) -> str:
        try:
            scene = self._engine().scene()
            obj = scene.find(ref)
        except USER_ERRORS as exc:
            return "ERROR: " + str(exc)
        if obj is None:
            return ("ERROR: no object called {0!r}. Use query_scene to list "
                    "objects.".format(ref))
        return "OK: " + "\n".join(describe.object_detail(obj, scene))

    def measure(self, a: str, b: str) -> str:
        try:
            return "OK: " + "\n".join(
                describe.measure(self._engine().scene(), a, b))
        except USER_ERRORS as exc:
            return "ERROR: " + str(exc)

    def journal_show(self, last: int = 10, search: str | None = None) -> str:
        try:
            entries = self._engine().entries()
        except USER_ERRORS as exc:
            return "ERROR: " + str(exc)
        return "OK: " + "\n".join(
            describe.journal_lines(entries, last=int(last), search=search))

    def doctor(self) -> str:
        from maquette import doctor as doctor_mod
        buffer = io.StringIO()
        payload: dict = {}
        with contextlib.redirect_stdout(buffer):
            code = doctor_mod.run({"project": self.project.root}, payload)
        body = buffer.getvalue().rstrip()
        prefix = "OK: setup looks good.\n" if code == 0 else \
            "ERROR: setup needs attention.\n"
        return prefix + body

    def project_info(self) -> str:
        try:
            engine = self._engine()
            scene = engine.scene()
            entries = engine.entries()
        except USER_ERRORS as exc:
            return "ERROR: " + str(exc)
        lines = ["OK: project {0} at {1}.".format(self.project.name,
                                                  self.project.root),
                 "units: {0}.".format(self.project.units),
                 "journal: {0} steps.".format(len(entries)),
                 "objects alive: {0}.".format(len(scene.alive_objects())),
                 "pending live rebuild: {0}.".format(
                     len(scene.pending_objects()))]
        if entries:
            from maquette.journal import entry_summary
            lines.append("last step: {0}.".format(entry_summary(entries[-1])))
        host, port = self.project.listener_address
        lines.append("listener address: {0} port {1}.".format(host, port))
        return "\n".join(lines)

    # -- internals ---------------------------------------------------------------

    def _run_batch(self, op_list: list[dict], allowed: set, label: str) -> str:
        if not isinstance(op_list, list) or not op_list:
            return "ERROR: give a list of op dicts ({0}).".format(label)
        engine = self._engine()
        lines: list[str] = []
        for index, op_dict in enumerate(op_list):
            if not isinstance(op_dict, dict) or op_dict.get("op") not in allowed:
                lines.append(
                    "ERROR: item {0} is not one of the allowed {1}: {2}. "
                    "Stopped there.".format(
                        index + 1, label, ", ".join(sorted(allowed))))
                break
            try:
                result = engine.run_op(op_dict)
            except USER_ERRORS as exc:
                lines.append("ERROR: item {0}: {1} Stopped there.".format(
                    index + 1, exc))
                break
            lines.extend(result["lines"])
            lines.extend("WARNING: " + w for w in result["warnings"])
        if not lines:
            return "ERROR: nothing ran."
        if lines[0].startswith(("ERROR:", "WARNING:")):
            return "\n".join(lines)
        return "OK: " + "\n".join(lines)


def _format(result: dict) -> str:
    lines = list(result.get("lines") or ["done."])
    lines.extend("WARNING: " + w for w in result.get("warnings", []))
    return "OK: " + "\n".join(lines)
