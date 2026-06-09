"""Render a TASC model to a single deterministic RhinoPython script.

This is the heart of the driver. Instead of pushing one socket command per
object (which is slow over the socket and, on macOS via ``rhinocode``, never
worked at all), we collect the *entire* model into one ordered list of RhinoMCP
protocol commands and translate that list into one RhinoPython script. The
script is a full rebuild: it clears prior TASC geometry, recreates the layers,
and draws everything. The same script runs over any transport.

Why reuse ``tasc.rhino.commands.RhinoDrawer`` instead of re-deriving geometry?
Because the bay/grid/column/corridor/void math already lives there and is the
single source of truth. We hand the drawer a *collecting* connector that records
the protocol commands it would have sent, then translate those commands here.
No geometry is duplicated, and the script stays in lock-step with the existing
socket path.

The translator reads the protocol's *real* command shapes (see
``tasc.rhino.protocol``): ``create_object`` carries ``params["type"]`` (e.g.
``"POLYLINE"``) with geometry nested under ``params["params"]``. The previous
macOS translator read ``params["object_type"]``/``params["points"]`` and so
silently produced nothing. Every string is embedded with :func:`json.dumps`, so
a zone named ``O'Brien`` or a Braille label can never break the generated source.
"""

from __future__ import annotations

import json
from typing import Any


def _s(value: Any) -> str:
    """Embed a value as an ASCII-only Python string literal.

    ``json.dumps`` double-quotes the string and escapes quotes, backslashes, and
    every non-ASCII codepoint as ``\\uXXXX``. The result is valid Python source
    under both CPython 3 and IronPython 2.7 (Rhino runs either), needs no source
    encoding declaration, and is injection-proof for names and labels.
    """
    return json.dumps(str(value), ensure_ascii=True)


def _n(value: Any) -> str:
    """Embed a coordinate/number as a Python literal."""
    return repr(value)


def _pt(point: Any) -> str:
    """Format a 2D or 3D point as a ``[x, y, z]`` literal (z defaults to 0)."""
    seq = list(point)
    if len(seq) == 2:
        seq = [seq[0], seq[1], 0]
    return "[{0}, {1}, {2}]".format(_n(seq[0]), _n(seq[1]), _n(seq[2]))


def _color(color: Any) -> str:
    """Format an RGB triple as a ``[r, g, b]`` literal."""
    seq = list(color)
    return "[{0}, {1}, {2}]".format(int(seq[0]), int(seq[1]), int(seq[2]))


def _create_object_lines(params: dict) -> list[str]:
    """Translate one ``create_object`` command's params into RhinoPython."""
    obj_type = str(params.get("type", "")).upper()
    name = params.get("name", "")
    color = params.get("color")
    geo = params.get("params", {}) or {}
    lines: list[str] = []

    if obj_type == "POLYLINE":
        pts = geo.get("points", [])
        pts_literal = ", ".join(_pt(p) for p in pts)
        lines.append("_id = rs.AddPolyline([{0}])".format(pts_literal))
    elif obj_type == "LINE":
        start = geo.get("start", [0, 0, 0])
        end = geo.get("end", [0, 0, 0])
        lines.append("_id = rs.AddLine({0}, {1})".format(_pt(start), _pt(end)))
    elif obj_type == "CIRCLE":
        center = geo.get("center", [0, 0, 0])
        radius = geo.get("radius", 0)
        lines.append("_id = rs.AddCircle({0}, {1})".format(_pt(center), _n(radius)))
    elif obj_type == "POINT":
        loc = geo.get("location", [0, 0, 0])
        if name:
            # A named point is a label; render it as a visible text dot so it
            # survives the Pen-mode viewport capture used for tactile output.
            lines.append("_id = rs.AddTextDot({0}, {1})".format(_s(name), _pt(loc)))
        else:
            lines.append("_id = rs.AddPoint({0})".format(_pt(loc)))
    else:
        # Unknown object type: record it as a comment rather than silently
        # dropping it, so the generated script is auditable.
        return ["# skipped unsupported create_object type: {0}".format(obj_type)]

    if name and obj_type != "POINT":
        lines.append("if _id: rs.ObjectName(_id, {0})".format(_s(name)))
    if color is not None:
        lines.append("if _id: rs.ObjectColor(_id, {0})".format(_color(color)))
    return lines


def _delete_object_lines(params: dict) -> list[str]:
    """Translate one ``delete_object`` command into RhinoPython."""
    if params.get("all"):
        return [
            "_objs = rs.AllObjects()",
            "if _objs: rs.DeleteObjects(_objs)",
        ]
    if params.get("name"):
        return [
            "_objs = rs.ObjectsByName({0})".format(_s(params["name"])),
            "if _objs: rs.DeleteObjects(_objs)",
        ]
    if params.get("id"):
        return ["rs.DeleteObject({0})".format(_s(params["id"]))]
    return ["# delete_object with no target; ignored"]


def commands_to_script(commands: list[dict]) -> str:
    """Translate a list of RhinoMCP protocol commands into one RhinoPython script.

    Handles the full vocabulary emitted by ``tasc.rhino.protocol``:
    ``get_or_set_current_layer``, ``create_layer``, ``create_object``
    (POLYLINE/LINE/CIRCLE/POINT), ``delete_object``, and
    ``execute_rhinoscript_python_code`` (inlined verbatim). Returns valid Python
    source under both CPython 3 and IronPython 2.7.
    """
    lines: list[str] = [
        "# Generated by rhino-driver: deterministic full rebuild of the TASC model.",
        "import rhinoscriptsyntax as rs",
        "",
    ]
    for cmd in commands:
        cmd_type = cmd.get("type", "")
        params = cmd.get("params", {}) or {}

        if cmd_type == "get_or_set_current_layer":
            name = params.get("name", "")
            lines.append("if not rs.IsLayer({0}): rs.AddLayer({0})".format(_s(name)))
            lines.append("rs.CurrentLayer({0})".format(_s(name)))
        elif cmd_type == "create_layer":
            name = params.get("name", "")
            color = params.get("color")
            if color is not None:
                lines.append(
                    "if not rs.IsLayer({0}): rs.AddLayer({0}, {1})".format(_s(name), _color(color))
                )
            else:
                lines.append("if not rs.IsLayer({0}): rs.AddLayer({0})".format(_s(name)))
        elif cmd_type == "create_object":
            lines.extend(_create_object_lines(params))
        elif cmd_type == "delete_object":
            lines.extend(_delete_object_lines(params))
        elif cmd_type == "execute_rhinoscript_python_code":
            # Inline the block as top-level statements. We drop its own
            # ``import rhinoscriptsyntax as rs`` line because the combined script
            # already imports it once at the top; any other imports are kept.
            code = params.get("code", "")
            lines.append("")
            for code_line in code.split("\n"):
                if code_line.strip() == "import rhinoscriptsyntax as rs":
                    continue
                lines.append(code_line.rstrip())
            lines.append("")
        else:
            lines.append("# skipped unsupported command: {0}".format(cmd_type))

    return "\n".join(lines) + "\n"


class CollectingConnector:
    """A drop-in connector that records protocol commands instead of sending them.

    Presents exactly the surface ``RhinoDrawer`` touches (``is_live`` and
    ``send``), so we can drive the real drawer offline and capture the full
    command stream for a model. ``send`` returns an OK-shaped dict so the
    drawer's ``execute_rhinoscript_python_code`` helpers behave normally.
    """

    is_live = True

    def __init__(self) -> None:
        self.commands: list[dict] = []

    def send(self, command_type: str, params: dict) -> dict:
        self.commands.append({"type": command_type, "params": params})
        return {"status": "ok", "output": ""}


def model_to_commands(model) -> list[dict]:
    """Collect the full ordered command stream for a TASC model (clear + rebuild).

    Reuses ``tasc.rhino.commands.RhinoDrawer.redraw`` for all geometry, so the
    output matches the live socket path exactly.
    """
    from tasc.rhino.commands import RhinoDrawer

    connector = CollectingConnector()
    drawer = RhinoDrawer(connector)
    drawer.redraw(model)
    return connector.commands


def render_model(model) -> str:
    """Render a TASC model to one deterministic RhinoPython script string."""
    return commands_to_script(model_to_commands(model))
