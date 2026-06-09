"""Compile ops into rhinoscriptsyntax snippets for the live listener.

The listener stays tiny and vocabulary-free: it just executes code.
All op knowledge lives here, where it is unit-testable without Rhino.

Snippets run inside the listener's exec namespace, which provides:
  rs              rhinoscriptsyntax
  sc              scriptcontext
  __maq__         helpers: find(ids), find_one(id),
                  tag(guids, id, name, op, seq, layer), ensure_layer(path)
  __maq_created__ list; append guids you create

Created guids left untagged are auto-tagged by the listener with the
request's own id/name/layer, so simple creates need no tag calls;
copy and restore tag per object because one request makes many ids.
"""

from __future__ import annotations

from maquette import ops


def compile_entry(entry: dict) -> str | None:
    """Return Python source for Rhino, or None when Rhino has no part."""
    op = entry["op"]
    builder = _BUILDERS.get(op)
    if builder is None:
        return None
    return builder(entry)


def _r(value) -> str:
    return repr(value)


def _find(ids: list[str]) -> str:
    return "__maq__.find({0})".format(_r(list(ids)))


def _create_point(entry):
    return _line_code("g = rs.AddPoint({0})".format(_r(entry["params"]["at"])))


def _create_line(entry):
    p = entry["params"]
    return _line_code("g = rs.AddLine({0}, {1})".format(
        _r(p["start"]), _r(p["end"])))


def _create_polyline(entry):
    p = entry["params"]
    points = list(p["points"])
    if p.get("closed") and points[0] != points[-1]:
        points.append(points[0])
    return _line_code("g = rs.AddPolyline({0})".format(_r(points)))


def _create_circle(entry):
    p = entry["params"]
    return _line_code("g = rs.AddCircle({0}, {1})".format(
        _r(p["center"]), _r(p["radius"])))


def _create_arc(entry):
    p = entry["params"]
    # rs.AddArc3Pt wants (start, end, point_on_arc).
    return _line_code("g = rs.AddArc3Pt({0}, {1}, {2})".format(
        _r(p["p1"]), _r(p["p3"]), _r(p["p2"])))


def _create_rectangle(entry):
    p = entry["params"]
    return _line_code(
        "plane = rs.MovePlane(rs.WorldXYPlane(), {0})\n"
        "g = rs.AddRectangle(plane, {1}, {2})".format(
            _r(p["corner"]), _r(p["width"]), _r(p["depth"])))


def _create_curve(entry):
    p = entry["params"]
    return _line_code("g = rs.AddInterpCurve({0}, {1})".format(
        _r(p["points"]), _r(p.get("degree", 3))))


def _create_text(entry):
    p = entry["params"]
    return _line_code("g = rs.AddText({0}, {1}, {2})".format(
        _r(p["text"]), _r(p["at"]), _r(p["height"])))


def _create_box(entry):
    p = entry["params"]
    c, s = p["corner"], p["size"]
    corners = [
        [c[0], c[1], c[2]], [c[0] + s[0], c[1], c[2]],
        [c[0] + s[0], c[1] + s[1], c[2]], [c[0], c[1] + s[1], c[2]],
        [c[0], c[1], c[2] + s[2]], [c[0] + s[0], c[1], c[2] + s[2]],
        [c[0] + s[0], c[1] + s[1], c[2] + s[2]], [c[0], c[1] + s[1], c[2] + s[2]],
    ]
    return _line_code("g = rs.AddBox({0})".format(_r(corners)))


def _create_sphere(entry):
    p = entry["params"]
    return _line_code("g = rs.AddSphere({0}, {1})".format(
        _r(p["center"]), _r(p["radius"])))


def _create_cylinder(entry):
    p = entry["params"]
    return _line_code("g = rs.AddCylinder({0}, {1}, {2}, cap=True)".format(
        _r(p["base"]), _r(p["height"]), _r(p["radius"])))


def _create_cone(entry):
    p = entry["params"]
    base = p["base"]
    # rs.AddCone(base_point, apex_point, radius): base circle at the
    # first point, apex at the second.
    apex = [base[0], base[1], base[2] + p["height"]]
    return _line_code("g = rs.AddCone({0}, {1}, {2}, cap=True)".format(
        _r(base), _r(apex), _r(p["radius"])))


def _extrude(entry):
    p = entry["params"]
    vector = p["vector"]
    return _line_code(
        "src = __maq__.find_one({0})\n"
        "g = rs.ExtrudeCurveStraight(src, [0, 0, 0], {1})\n"
        "if g and rs.IsCurveClosed(src) and rs.IsCurvePlanar(src):\n"
        "    rs.CapPlanarHoles(g)".format(_r(p["source"]), _r(vector)))


def _loft(entry):
    p = entry["params"]
    return ("srcs = {0}\n"
            "made = rs.AddLoftSrf(srcs)\n"
            "if made:\n"
            "    __maq_created__.extend(made)\n".format(_find(p["sources"])))


def _revolve(entry):
    p = entry["params"]
    return _line_code(
        "src = __maq__.find_one({0})\n"
        "g = rs.AddRevSrf(src, [{1}, {2}], 0, {3})".format(
            _r(p["source"]), _r(p["axis_start"]), _r(p["axis_end"]),
            _r(p["angle"])))


def _boolean_union(entry):
    p = entry["params"]
    return ("made = rs.BooleanUnion({0})\n"
            "if made:\n"
            "    __maq_created__.extend(made)\n".format(_find(p["inputs"])))


def _boolean_difference(entry):
    p = entry["params"]
    return ("made = rs.BooleanDifference({0}, {1})\n"
            "if made:\n"
            "    __maq_created__.extend(made)\n".format(
                _find(p["keep"]), _find(p["cut"])))


def _boolean_intersection(entry):
    p = entry["params"]
    first = p["inputs"][0]
    rest = p["inputs"][1:]
    return ("made = __maq__.find({0})\n"
            "for nxt in {1}:\n"
            "    made = rs.BooleanIntersection(made, __maq__.find([nxt]))\n"
            "    if not made:\n"
            "        break\n"
            "if made:\n"
            "    __maq_created__.extend(made)\n".format(_r([first]), _r(rest)))


def _move(entry):
    p = entry["params"]
    return "rs.MoveObjects({0}, {1})\n".format(_find(p["ids"]), _r(p["vector"]))


def _rotate(entry):
    p = entry["params"]
    return ("rs.RotateObjects({0}, {1}, {2}, axis={3}, copy=False)\n".format(
        _find(p["ids"]), _r(p["center"]), _r(p["angle"]), _r(p["axis"])))


def _scale(entry):
    p = entry["params"]
    return "rs.ScaleObjects({0}, {1}, {2}, copy=False)\n".format(
        _find(p["ids"]), _r(p["center"]), _r(p["factors"]))


def _mirror(entry):
    p = entry["params"]
    return ("xf = rs.XformMirror({0}, {1})\n"
            "rs.TransformObjects({2}, xf, copy=False)\n".format(
                _r(p["plane_point"]), _r(p["plane_normal"]), _find(p["ids"])))


def _copy(entry):
    p = entry["params"]
    lines = ["srcs = {0}".format(_find(p["ids"]))]
    for batch_index, (batch_ids, batch_names) in enumerate(
            zip(p["new_ids"], p["new_names"])):
        offset = [c * (batch_index + 1) for c in p["vector"]]
        for position, (new_id, new_name) in enumerate(
                zip(batch_ids, batch_names)):
            lines.append("made = rs.CopyObjects([srcs[{0}]], {1})".format(
                position, _r(offset)))
            lines.append(
                "__maq__.tag(made, {0}, {1}, 'copy', {2}, None)".format(
                    _r(new_id), _r(new_name), _r(entry["seq"])))
            lines.append("__maq_created__.extend(made)")
    return "\n".join(lines) + "\n"


def _delete(entry):
    return "rs.DeleteObjects({0})\n".format(_find(entry["params"]["ids"]))


def _restore(entry):
    chunks = []
    for spec in entry["params"]["objects"]:
        create_entry = {"op": spec["op"], "params": spec["params"],
                        "seq": entry["seq"]}
        create_builder = _BUILDERS.get(spec["op"])
        if create_builder is None:
            continue
        chunks.append(create_builder(create_entry))
        chunks.append("made = list(__maq_created__)\n"
                      "del __maq_created__[:]\n")
        for transform in spec.get("transforms", []):
            transform_entry = {"op": transform["op"],
                               "params": dict(transform["params"],
                                              ids=["__restored__"]),
                               "seq": entry["seq"]}
            code = _BUILDERS[transform["op"]](transform_entry)
            code = code.replace(_find(["__restored__"]), "made")
            chunks.append(code)
        chunks.append(
            "__maq__.tag(made, {0}, {1}, {2}, {3}, {4})\n"
            "__maq_created__.extend(made)\n".format(
                _r(spec["id"]), _r(spec["name"]), _r(spec["op"]),
                _r(entry["seq"]), _r(spec["layer"])))
    return "".join(chunks)


def _set_name(entry):
    p = entry["params"]
    return ("for g in {0}:\n"
            "    rs.ObjectName(g, {1})\n"
            "    rs.SetUserText(g, 'MAQ_NAME', {1})\n".format(
                _find([p["id"]]), _r(p["name"])))


def _set_layer(entry):
    p = entry["params"]
    return ("__maq__.ensure_layer({0})\n"
            "for g in {1}:\n"
            "    rs.ObjectLayer(g, {0})\n".format(
                _r(p["layer"]), _find(p["ids"])))


def _create_layer(entry):
    return "__maq__.ensure_layer({0})\n".format(_r(entry["params"]["name"]))


def _group(entry):
    p = entry["params"]
    return ("rs.AddGroup({0})\n"
            "rs.AddObjectsToGroup({1}, {0})\n".format(
                _r(p["gid"]), _find(p["members"])))


def _ungroup(entry):
    return "rs.DeleteGroup({0})\n".format(_r(entry["params"]["gid"]))


def _script(entry):
    p = entry["params"]
    return ("import random\n"
            "random.seed({0})\n"
            "{1}\n".format(_r(entry.get("seq", 0)), p["code"]))


def _line_code(body: str) -> str:
    """Standard single-create wrapper: append guid g when it was made."""
    return ("{0}\n"
            "if g:\n"
            "    __maq_created__.append(g)\n".format(body))


_BUILDERS = {
    "create_point": _create_point, "create_line": _create_line,
    "create_polyline": _create_polyline, "create_circle": _create_circle,
    "create_arc": _create_arc, "create_rectangle": _create_rectangle,
    "create_curve": _create_curve, "create_text": _create_text,
    "create_box": _create_box, "create_sphere": _create_sphere,
    "create_cylinder": _create_cylinder, "create_cone": _create_cone,
    "extrude": _extrude, "loft": _loft, "revolve": _revolve,
    "boolean_union": _boolean_union,
    "boolean_difference": _boolean_difference,
    "boolean_intersection": _boolean_intersection,
    "move": _move, "rotate": _rotate, "scale": _scale, "mirror": _mirror,
    "copy": _copy, "delete": _delete, "restore": _restore,
    "set_name": _set_name, "set_layer": _set_layer,
    "create_layer": _create_layer, "group": _group, "ungroup": _ungroup,
    "script": _script,
}

# Ops with no Rhino-side work at all.
assert set(_BUILDERS) | ops.NO_UNDO_OPS == ops.ALL_OPS
