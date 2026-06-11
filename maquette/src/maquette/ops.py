"""The op vocabulary: validation, fingerprint prediction, inverse planning.

Every mutation in Maquette is one of these ops. An op dict is
{"op": name, "params": {...}} plus optional "name" and "layer".
Validation resolves references, allocates ids, freezes defaults
(like rotation centers) so journal entries are self-contained and
replay deterministically.

Canonical param shapes (all coordinates are [x, y, z]):
  create_point      {at}
  create_line       {start, end}
  create_polyline   {points, closed}
  create_circle     {center, radius}          world XY plane
  create_arc        {p1, p2, p3}              through three points
  create_rectangle  {corner, width, depth}    world XY plane
  create_curve      {points, degree}          interpolated
  create_text       {text, at, height}
  create_box        {corner, size}            size [w, d, h]
  create_sphere     {center, radius}
  create_cylinder   {base, radius, height}    axis +Z
  create_cone       {base, radius, height}    axis +Z, apex up
  extrude           {source, vector}          source: object id
  loft              {sources}
  revolve           {source, axis_start, axis_end, angle}
  boolean_union     {inputs}
  boolean_difference{keep, cut}
  boolean_intersection {inputs}
  move              {ids, vector}
  rotate            {ids, center, angle, axis}
  scale             {ids, center, factors}
  mirror            {ids, plane_point, plane_normal}
  copy              {ids, vector, count, new_ids, new_names}
  delete            {ids}
  restore           {objects: [{id,name,layer,op,params,transforms}]}
  set_name          {id, name, old_name}
  set_layer         {ids, layer, old_layers}
  create_layer      {name}
  group             {gid, name, members}
  ungroup           {gid, name, members}
  script            {code, intent}
  reconcile         {fingerprints, backend}   written by rebuild
  noop              {note}
"""

from __future__ import annotations

import copy as copymod

from maquette import DEFAULT_LAYER
from maquette import geom, ids


class OpError(Exception):
    """Validation failure. The message is read aloud; make it teach."""


def normalize_layer(name: str) -> str:
    """Layers live under the MAQ:: namespace, like JIG:: in the old tools."""
    name = name.strip()
    if not name:
        raise OpError("layer name cannot be empty")
    if not name.startswith("MAQ::"):
        name = "MAQ::" + name
    return name


# Spoken kind per op (used for auto-names and describe output).
KINDS = {
    "create_point": "point", "create_line": "line",
    "create_polyline": "polyline", "create_circle": "circle",
    "create_arc": "arc", "create_rectangle": "rectangle",
    "create_curve": "curve", "create_text": "text",
    "create_box": "box", "create_sphere": "sphere",
    "create_cylinder": "cylinder", "create_cone": "cone",
    "extrude": "extrusion", "loft": "loft", "revolve": "revolve",
    "boolean_union": "union", "boolean_difference": "difference",
    "boolean_intersection": "intersection", "script": "script",
}

CREATE_OPS = set(KINDS)
# Ops whose real geometry needs Rhino (or stays a recorded intent).
COMPUTE_OPS = {"loft", "revolve", "boolean_union", "boolean_difference",
               "boolean_intersection", "script"}
# Booleans consume their inputs (Rhino deletes them).
CONSUMING_OPS = {"boolean_union", "boolean_difference", "boolean_intersection"}
TRANSFORM_OPS = {"move", "rotate", "scale", "mirror"}
# Ops the undo walker skips entirely.
NO_UNDO_OPS = {"reconcile", "noop"}

ALL_OPS = CREATE_OPS | TRANSFORM_OPS | {
    "copy", "delete", "restore", "set_name", "set_layer", "create_layer",
    "group", "ungroup", "reconcile", "noop",
}


def _vec(params: dict, key: str, default=None) -> list[float]:
    value = params.get(key, default)
    if value is None:
        raise OpError("missing {0}".format(key))
    try:
        return geom.vec3(value)
    except (TypeError, ValueError):
        raise OpError("{0} must be 2 or 3 numbers, got {1!r}".format(key, value))


def _num(params: dict, key: str, default=None, positive=False) -> float:
    value = params.get(key, default)
    if value is None:
        raise OpError("missing {0}".format(key))
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise OpError("{0} must be a number, got {1!r}".format(key, value))
    if positive and value <= 0:
        raise OpError("{0} must be greater than zero".format(key))
    return value


def _points(params: dict, key: str, minimum: int) -> list[list[float]]:
    raw = params.get(key)
    if not isinstance(raw, list) or len(raw) < minimum:
        raise OpError("{0} needs at least {1} points".format(key, minimum))
    return [geom.vec3(p) for p in raw]


def _resolve_refs(scene, refs, label="ids") -> list[str]:
    """Resolve a list of ids or names to alive object ids."""
    if not refs:
        raise OpError("no objects given for {0}".format(label))
    resolved = []
    for ref in refs:
        obj = scene.find(ref)
        if obj is None:
            raise OpError("no object called {0!r}. Try: maquette describe".format(ref))
        if obj["status"] != "alive":
            raise OpError("{0} ({1}) is {2}, not alive".format(
                obj["id"], obj["name"], obj["status"]))
        if obj["id"] not in resolved:
            resolved.append(obj["id"])
    return resolved


def _center_of(scene, object_ids: list[str], explicit) -> list[float]:
    """Freeze a transform center: explicit wins, else merged bbox center."""
    if explicit is not None:
        return geom.vec3(explicit)
    boxes = [scene.objects[i]["fingerprint"].get("bbox") for i in object_ids]
    merged = geom.merge_bboxes(boxes)
    if merged is None:
        raise OpError(
            "these objects have no known bounding box yet, so I cannot pick "
            "a center for you. Say the center, like: around 0,0,0")
    return geom.bbox_center(merged)


def validate(op_dict: dict, scene) -> dict:
    """Validate and normalize an op against the current scene.

    Returns entry fields {op, params, id, name, layer}. Does not
    mutate the scene; id and name allocation simulates on a copy of
    the counters (scene.apply re-derives the same values).
    """
    op = op_dict.get("op")
    if op not in ALL_OPS:
        raise OpError("unknown op {0!r}".format(op))
    params = copymod.deepcopy(op_dict.get("params", {}))
    counters = dict(scene.counters)
    entry = {"op": op, "params": params, "id": None, "name": None, "layer": None}

    if op in CREATE_OPS:
        _validate_create(op, params, scene)
        kind = KINDS[op]
        entry["id"] = ids.next_object_id(counters)
        entry["name"] = op_dict.get("name") or ids.auto_name(counters, kind)
        layer = op_dict.get("layer")
        entry["layer"] = normalize_layer(layer) if layer else scene.current_layer
    elif op in TRANSFORM_OPS:
        _validate_transform(op, params, scene)
    elif op == "copy":
        _validate_copy(params, scene, counters, op_dict.get("name"))
    elif op == "delete":
        if params.get("all"):
            params["ids"] = [o["id"] for o in scene.alive_objects()]
            params.pop("all", None)
            if not params["ids"]:
                raise OpError("nothing to delete; the scene is empty")
        else:
            params["ids"] = _resolve_refs(scene, params.get("ids"))
    elif op == "restore":
        if not params.get("objects"):
            raise OpError("restore needs object specs")
    elif op == "set_name":
        resolved = _resolve_refs(scene, [params.get("id")], "id")
        params["id"] = resolved[0]
        new_name = params.get("name")
        if not new_name:
            raise OpError("set_name needs the new name")
        params["old_name"] = scene.objects[params["id"]]["name"]
        entry["name"] = new_name
    elif op == "set_layer":
        params["ids"] = _resolve_refs(scene, params.get("ids"))
        if not params.get("layer"):
            raise OpError("set_layer needs a layer name")
        params["layer"] = normalize_layer(params["layer"])
        params["old_layers"] = {
            i: scene.objects[i]["layer"] for i in params["ids"]}
        entry["layer"] = params["layer"]
    elif op == "create_layer":
        if not params.get("name"):
            raise OpError("create_layer needs a layer name")
        params["name"] = normalize_layer(params["name"])
        if params["name"] in scene.layers:
            raise OpError("layer {0} already exists".format(params["name"]))
        entry["layer"] = params["name"]
    elif op == "group":
        params["members"] = _resolve_refs(scene, params.get("members"), "members")
        params["gid"] = params.get("gid") or ids.next_group_id(counters)
        params["name"] = params.get("name") or params["gid"]
        entry["id"] = params["gid"]
        entry["name"] = params["name"]
    elif op == "ungroup":
        gid = params.get("gid")
        group = scene.groups.get(gid)
        if group is None:
            # Allow ungrouping by group name.
            matches = [g for g, rec in scene.groups.items()
                       if rec["name"] == gid]
            if len(matches) != 1:
                raise OpError("no group called {0!r}".format(gid))
            gid = matches[0]
            group = scene.groups[gid]
        params["gid"] = gid
        params["name"] = group["name"]
        params["members"] = list(group["members"])
    elif op == "reconcile":
        if "fingerprints" not in params:
            raise OpError("reconcile needs fingerprints")
    elif op == "noop":
        params.setdefault("note", "")

    if op == "script":
        if not params.get("code", "").strip():
            raise OpError("script needs code")
        if not params.get("intent", "").strip():
            raise OpError(
                "script needs an intent: one plain sentence saying what the "
                "code does. It is what gets read aloud from the journal.")
    return entry


def _validate_create(op: str, params: dict, scene) -> None:
    if op == "create_point":
        params["at"] = _vec(params, "at")
    elif op == "create_line":
        params["start"] = _vec(params, "start")
        params["end"] = _vec(params, "end")
    elif op == "create_polyline":
        params["points"] = _points(params, "points", 2)
        params["closed"] = bool(params.get("closed", False))
    elif op == "create_circle":
        params["center"] = _vec(params, "center")
        params["radius"] = _num(params, "radius", positive=True)
    elif op == "create_arc":
        for key in ("p1", "p2", "p3"):
            params[key] = _vec(params, key)
    elif op == "create_rectangle":
        params["corner"] = _vec(params, "corner", [0, 0, 0])
        params["width"] = _num(params, "width", positive=True)
        params["depth"] = _num(params, "depth", positive=True)
    elif op == "create_curve":
        params["points"] = _points(params, "points", 3)
        params["degree"] = int(params.get("degree", 3))
    elif op == "create_text":
        if not params.get("text"):
            raise OpError("text needs the text string")
        params["at"] = _vec(params, "at")
        params["height"] = _num(params, "height", 1.0, positive=True)
    elif op == "create_box":
        params["corner"] = _vec(params, "corner", [0, 0, 0])
        size = params.get("size")
        if not isinstance(size, list) or len(size) != 3:
            raise OpError("box size must be three numbers: width depth height")
        params["size"] = [_num({"s": s}, "s", positive=True) for s in size]
    elif op == "create_sphere":
        params["center"] = _vec(params, "center", [0, 0, 0])
        params["radius"] = _num(params, "radius", positive=True)
    elif op in ("create_cylinder", "create_cone"):
        params["base"] = _vec(params, "base", [0, 0, 0])
        params["radius"] = _num(params, "radius", positive=True)
        params["height"] = _num(params, "height", positive=True)
    elif op == "extrude":
        params["source"] = _resolve_refs(scene, [params.get("source")], "source")[0]
        if "vector" in params and params["vector"] is not None:
            params["vector"] = _vec(params, "vector")
        else:
            height = _num(params, "height")
            params["vector"] = [0, 0, height]
        params.pop("height", None)
    elif op == "loft":
        params["sources"] = _resolve_refs(scene, params.get("sources"), "sources")
        if len(params["sources"]) < 2:
            raise OpError("loft needs at least two curves")
    elif op == "revolve":
        params["source"] = _resolve_refs(scene, [params.get("source")], "source")[0]
        params["axis_start"] = _vec(params, "axis_start")
        params["axis_end"] = _vec(params, "axis_end")
        params["angle"] = _num(params, "angle", 360.0)
    elif op == "boolean_union":
        params["inputs"] = _resolve_refs(scene, params.get("inputs"), "inputs")
        if len(params["inputs"]) < 2:
            raise OpError("union needs at least two solids")
    elif op == "boolean_difference":
        params["keep"] = _resolve_refs(scene, params.get("keep"), "keep")
        params["cut"] = _resolve_refs(scene, params.get("cut"), "cut")
        overlap = set(params["keep"]) & set(params["cut"])
        if overlap:
            raise OpError("cannot keep and cut the same object: {0}".format(
                ", ".join(sorted(overlap))))
    elif op == "boolean_intersection":
        params["inputs"] = _resolve_refs(scene, params.get("inputs"), "inputs")
        if len(params["inputs"]) < 2:
            raise OpError("intersection needs at least two solids")


def _validate_transform(op: str, params: dict, scene) -> None:
    params["ids"] = _resolve_refs(scene, params.get("ids"))
    if op == "move":
        params["vector"] = _vec(params, "vector")
    elif op == "rotate":
        params["angle"] = _num(params, "angle")
        params["axis"] = geom.normalize(_vec(params, "axis", [0, 0, 1]))
        params["center"] = _center_of(scene, params["ids"], params.get("center"))
    elif op == "scale":
        factors = params.get("factors")
        if isinstance(factors, (int, float)):
            factors = [factors] * 3
        if not isinstance(factors, list) or len(factors) not in (1, 3):
            raise OpError("scale needs one factor or three factors")
        if len(factors) == 1:
            factors = factors * 3
        factors = [float(f) for f in factors]
        if any(f == 0 for f in factors):
            raise OpError("scale factors cannot be zero")
        params["factors"] = factors
        params["center"] = _center_of(scene, params["ids"], params.get("center"))
    elif op == "mirror":
        params["plane_point"] = _vec(params, "plane_point")
        params["plane_normal"] = geom.normalize(_vec(params, "plane_normal"))


def _validate_copy(params: dict, scene, counters: dict, name: str | None) -> None:
    params["ids"] = _resolve_refs(scene, params.get("ids"))
    params["vector"] = _vec(params, "vector")
    count = int(params.get("count", 1))
    if count < 1:
        raise OpError("copy count must be at least 1")
    params["count"] = count
    new_ids, new_names = [], []
    for _ in range(count):
        batch_ids, batch_names = [], []
        for source_id in params["ids"]:
            source = scene.objects[source_id]
            batch_ids.append(ids.next_object_id(counters))
            if name and count == 1 and len(params["ids"]) == 1:
                batch_names.append(name)
            else:
                batch_names.append(ids.auto_name(counters, source["kind"]))
        new_ids.append(batch_ids)
        new_names.append(batch_names)
    params["new_ids"] = new_ids
    params["new_names"] = new_names


def predict_fingerprint(op: str, params: dict, scene) -> dict:
    """Deterministic, backend-independent fingerprint for a create op."""
    bbox, quality, count = None, "unknown", 1
    if op == "create_point":
        bbox, quality = geom.bbox_of_points([params["at"]]), "exact"
    elif op == "create_line":
        bbox, quality = geom.bbox_of_points([params["start"], params["end"]]), "exact"
    elif op == "create_polyline":
        bbox, quality = geom.bbox_of_points(params["points"]), "exact"
    elif op in ("create_curve", "create_arc"):
        pts = params.get("points") or [params["p1"], params["p2"], params["p3"]]
        bbox, quality = geom.bbox_of_points(pts), "approx"
    elif op == "create_circle":
        c, r = params["center"], params["radius"]
        bbox = [[c[0] - r, c[1] - r, c[2]], [c[0] + r, c[1] + r, c[2]]]
        quality = "exact"
    elif op == "create_rectangle":
        c = params["corner"]
        bbox = [c, [c[0] + params["width"], c[1] + params["depth"], c[2]]]
        quality = "exact"
    elif op == "create_text":
        at, h = params["at"], params["height"]
        width = h * 0.6 * len(params["text"])
        bbox = [at, [at[0] + width, at[1] + h, at[2]]]
        quality = "approx"
    elif op == "create_box":
        c, s = params["corner"], params["size"]
        bbox = [c, [c[0] + s[0], c[1] + s[1], c[2] + s[2]]]
        quality = "exact"
    elif op == "create_sphere":
        c, r = params["center"], params["radius"]
        bbox = [[c[i] - r for i in range(3)], [c[i] + r for i in range(3)]]
        quality = "exact"
    elif op in ("create_cylinder", "create_cone"):
        b, r, h = params["base"], params["radius"], params["height"]
        bbox = [[b[0] - r, b[1] - r, b[2]], [b[0] + r, b[1] + r, b[2] + h]]
        quality = "exact"
    elif op == "extrude":
        source = scene.objects[params["source"]]["fingerprint"]
        base = source.get("bbox")
        bbox = geom.merge_bboxes([base, geom.translate_bbox(base, params["vector"])])
        quality = source.get("quality", "unknown") if bbox else "unknown"
    elif op == "loft":
        boxes = [scene.objects[i]["fingerprint"].get("bbox")
                 for i in params["sources"]]
        bbox, quality = geom.merge_bboxes(boxes), "approx"
    elif op == "boolean_union":
        boxes = [scene.objects[i]["fingerprint"].get("bbox")
                 for i in params["inputs"]]
        bbox = geom.merge_bboxes(boxes)
        qualities = [scene.objects[i]["fingerprint"].get("quality")
                     for i in params["inputs"]]
        quality = "exact" if bbox and all(q == "exact" for q in qualities) else "approx"
    elif op == "boolean_difference":
        keep = [scene.objects[i]["fingerprint"].get("bbox") for i in params["keep"]]
        bbox, quality = geom.merge_bboxes(keep), "approx"
    elif op == "boolean_intersection":
        boxes = [scene.objects[i]["fingerprint"].get("bbox")
                 for i in params["inputs"]]
        if all(b is not None for b in boxes):
            lo = [max(b[0][i] for b in boxes) for i in range(3)]
            hi = [min(b[1][i] for b in boxes) for i in range(3)]
            if all(lo[i] <= hi[i] for i in range(3)):
                bbox, quality = [lo, hi], "approx"
    elif op in ("revolve", "script"):
        bbox, quality, count = None, "unknown", 1
        if op == "script":
            count = None
    return {"objects": count, "bbox": bbox, "quality": quality}


def plan_inverse(entry: dict, scene, journal_entries: list[dict]) -> list[dict]:
    """Plan compensating op dicts that undo one journal entry.

    Returns a list (usually one op; booleans return two). Raises
    OpError when the entry cannot be undone.
    """
    op, params = entry["op"], entry["params"]
    if op in CREATE_OPS and op not in CONSUMING_OPS:
        return [{"op": "delete", "params": {"ids": [entry["id"]]}}]
    if op in CONSUMING_OPS:
        input_ids = params.get("inputs") or (params["keep"] + params["cut"])
        specs = [_restore_spec(i, scene, journal_entries) for i in input_ids]
        return [{"op": "delete", "params": {"ids": [entry["id"]]}},
                {"op": "restore", "params": {"objects": specs}}]
    if op == "copy":
        flat = [i for batch in params["new_ids"] for i in batch]
        return [{"op": "delete", "params": {"ids": flat}}]
    if op == "move":
        return [{"op": "move", "params": {
            "ids": params["ids"],
            "vector": [-v for v in params["vector"]]}}]
    if op == "rotate":
        return [{"op": "rotate", "params": {
            "ids": params["ids"], "center": params["center"],
            "angle": -params["angle"], "axis": params["axis"]}}]
    if op == "scale":
        return [{"op": "scale", "params": {
            "ids": params["ids"], "center": params["center"],
            "factors": [1.0 / f for f in params["factors"]]}}]
    if op == "mirror":
        return [{"op": "mirror", "params": dict(params)}]
    if op == "delete":
        specs = [_restore_spec(i, scene, journal_entries) for i in params["ids"]]
        return [{"op": "restore", "params": {"objects": specs}}]
    if op == "restore":
        return [{"op": "delete", "params": {
            "ids": [spec["id"] for spec in params["objects"]]}}]
    if op == "set_name":
        return [{"op": "set_name", "params": {
            "id": params["id"], "name": params["old_name"],
            "old_name": params["name"]}}]
    if op == "set_layer":
        steps = []
        by_layer: dict[str, list[str]] = {}
        for obj_id, old in params["old_layers"].items():
            by_layer.setdefault(old, []).append(obj_id)
        for layer, obj_ids in by_layer.items():
            steps.append({"op": "set_layer", "params": {
                "ids": obj_ids, "layer": layer,
                "old_layers": {i: params["layer"] for i in obj_ids}}})
        return steps
    if op == "create_layer":
        return [{"op": "noop", "params": {
            "note": "layer {0} kept; layers are never auto-deleted".format(
                params["name"])}}]
    if op == "group":
        return [{"op": "ungroup", "params": dict(params)}]
    if op == "ungroup":
        return [{"op": "group", "params": dict(params)}]
    raise OpError("cannot undo op {0}".format(op))


def _restore_spec(object_id: str, scene, journal_entries: list[dict]) -> dict:
    """Build a self-contained spec to resurrect a deleted object.

    Uses the object's creation params plus every transform that
    touched it since, so the restored geometry lands where it was.
    """
    obj = scene.objects.get(object_id)
    if obj is None:
        raise OpError("cannot restore unknown object {0}".format(object_id))
    transforms = []
    for past in journal_entries:
        if past["op"] in TRANSFORM_OPS and object_id in past["params"].get("ids", []):
            transforms.append({"op": past["op"], "params": {
                key: value for key, value in past["params"].items() if key != "ids"}})
    return {
        "id": obj["id"], "name": obj["name"], "layer": obj["layer"],
        "op": obj["op"], "params": copymod.deepcopy(obj["params"]),
        "transforms": transforms,
    }
