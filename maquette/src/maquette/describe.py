"""Everything Maquette says about the model, as plain speakable text.

These functions take a scene and return lists of short lines. No
tables, no columns, no drawing characters - one fact per line.
"""

from __future__ import annotations

from maquette import geom
from maquette.journal import entry_summary
from maquette.scene import Scene


def confirmation(entry: dict, scene: Scene) -> list[str]:
    """The one-line (per object) summary printed after a mutation."""
    op, params = entry["op"], entry["params"]
    if op == "copy":
        lines = []
        for batch in params["new_ids"]:
            for new_id in batch:
                obj = scene.objects[new_id]
                lines.append("copied to {0} {1} at {2}.".format(
                    new_id, _quoted(obj["name"]), _location(obj)))
        return lines
    if op == "delete":
        return ["deleted {0}.".format(_name_list(params["ids"], scene))]
    if op == "restore":
        return ["restored {0}.".format(
            _name_list([s["id"] for s in params["objects"]], scene))]
    if op == "move":
        return ["moved {0} by {1}.".format(
            _name_list(params["ids"], scene), geom.fmt_point(params["vector"]))]
    if op == "rotate":
        return ["rotated {0} by {1} degrees around {2}.".format(
            _name_list(params["ids"], scene), geom.fmt_num(params["angle"]),
            geom.fmt_point(params["center"]))]
    if op == "scale":
        return ["scaled {0} by {1} around {2}.".format(
            _name_list(params["ids"], scene),
            ",".join(geom.fmt_num(f) for f in params["factors"]),
            geom.fmt_point(params["center"]))]
    if op == "mirror":
        return ["mirrored {0}.".format(_name_list(params["ids"], scene))]
    if op == "set_name":
        return ["renamed {0} to {1}.".format(
            params["id"], _quoted(params["name"]))]
    if op == "set_layer":
        return ["put {0} on layer {1}.".format(
            _name_list(params["ids"], scene), params["layer"])]
    if op == "create_layer":
        return ["created layer {0}.".format(params["name"])]
    if op == "group":
        return ["grouped {0} as {1} {2}.".format(
            _name_list(params["members"], scene), params["gid"],
            _quoted(params["name"]))]
    if op == "ungroup":
        return ["ungrouped {0} {1}.".format(params["gid"], _quoted(params["name"]))]
    if op == "noop":
        return [params.get("note") or "nothing to do."]
    if op == "reconcile":
        return ["reconciled {0} objects from backend {1}.".format(
            len(params["fingerprints"]), params.get("backend", "?"))]
    # Create ops, including script.
    obj = scene.objects.get(entry["id"])
    if obj is None:
        return ["{0} applied.".format(op)]
    line = "created {0} {1} ({2})".format(obj["id"], _quoted(obj["name"]),
                                          obj["kind"])
    size = _size_phrase(obj)
    if size:
        line += ", " + size
    line += ", on layer {0}.".format(obj["layer"])
    lines = [line]
    if obj.get("pending"):
        lines.append("NOTE: geometry pending; it becomes real on the next "
                     "live rebuild in Rhino.")
    return lines


def plural(count: int, word: str) -> str:
    return "{0} {1}{2}".format(count, word, "" if count == 1 else "s")


def brief(scene: Scene) -> list[str]:
    alive = scene.alive_objects()
    lines = ["project {0}, units {1}.".format(scene.project_name, scene.units),
             "{0} on {1}.".format(plural(len(alive), "object"),
                                  plural(len(scene.layers), "layer"))]
    by_layer: dict[str, int] = {}
    for obj in alive:
        by_layer[obj["layer"]] = by_layer.get(obj["layer"], 0) + 1
    for layer in scene.layers:
        if by_layer.get(layer):
            lines.append("layer {0}: {1}.".format(
                layer, plural(by_layer[layer], "object")))
    extents = scene.extents()
    if extents:
        size = geom.bbox_size(extents)
        lines.append("extents: {0} wide, {1} deep, {2} tall, from {3} to {4}.".format(
            geom.fmt_num(size[0]), geom.fmt_num(size[1]), geom.fmt_num(size[2]),
            geom.fmt_point(extents[0]), geom.fmt_point(extents[1])))
    pending = scene.pending_objects()
    if pending:
        lines.append("{0} pending live rebuild: {1}.".format(
            plural(len(pending), "object"), ", ".join(o["id"] for o in pending)))
    if scene.groups:
        for gid, group in scene.groups.items():
            lines.append("group {0} {1}: {2}.".format(
                gid, _quoted(group["name"]),
                plural(len(group["members"]), "member")))
    return lines


def full(scene: Scene) -> list[str]:
    lines = brief(scene)
    for obj in scene.alive_objects():
        lines.append(_object_line(obj))
    return lines


def object_detail(obj: dict, scene: Scene) -> list[str]:
    lines = [
        "{0} {1}.".format(obj["id"], _quoted(obj["name"])),
        "kind: {0}.".format(obj["kind"]),
        "layer: {0}.".format(obj["layer"]),
        "status: {0}.".format(obj["status"]),
    ]
    box = obj["fingerprint"].get("bbox")
    if box:
        size = geom.bbox_size(box)
        lines.append("size: {0} wide, {1} deep, {2} tall.".format(
            geom.fmt_num(size[0]), geom.fmt_num(size[1]), geom.fmt_num(size[2])))
        lines.append("from {0} to {1} ({2}).".format(
            geom.fmt_point(box[0]), geom.fmt_point(box[1]),
            obj["fingerprint"].get("quality", "unknown")))
        lines.append("center: {0}.".format(geom.fmt_point(geom.bbox_center(box))))
    else:
        lines.append("position: not known yet (needs a live rebuild).")
    if obj.get("group"):
        group = scene.groups.get(obj["group"], {})
        lines.append("in group {0} {1}.".format(
            obj["group"], _quoted(group.get("name", ""))))
    if obj.get("pending"):
        lines.append("pending: yes; geometry becomes real on the next live rebuild.")
    lines.append("created at journal step {0}.".format(obj.get("created_seq")))
    return lines


def measure(scene: Scene, ref_a: str, ref_b: str) -> list[str]:
    point_a, label_a = _as_point(scene, ref_a)
    point_b, label_b = _as_point(scene, ref_b)
    delta = geom.sub(point_b, point_a)
    lines = ["from {0} to {1}:".format(label_a, label_b),
             "distance: {0}.".format(geom.fmt_num(geom.distance(point_a, point_b)))]
    for axis, value in zip("xyz", delta):
        lines.append("{0} change: {1}.".format(axis, geom.fmt_num(value)))
    return lines


def journal_lines(entries: list[dict], last: int = 10,
                  search: str | None = None) -> list[str]:
    chosen = entries
    if search:
        needle = search.lower()
        chosen = [e for e in chosen
                  if needle in entry_summary(e).lower()]
    if last:
        chosen = chosen[-last:]
    if not chosen:
        return ["journal is empty." if not search else
                "nothing in the journal matches {0!r}.".format(search)]
    return [entry_summary(e) for e in chosen]


def _object_line(obj: dict) -> str:
    line = "{0} {1} ({2}) on {3}".format(
        obj["id"], _quoted(obj["name"]), obj["kind"], obj["layer"])
    box = obj["fingerprint"].get("bbox")
    if box:
        line += ", at {0}".format(geom.fmt_point(geom.bbox_center(box)))
    if obj.get("pending"):
        line += ", pending"
    return line + "."


def _size_phrase(obj: dict) -> str:
    box = obj["fingerprint"].get("bbox")
    if not box:
        return ""
    size = geom.bbox_size(obj["fingerprint"]["bbox"])
    if all(s == 0 for s in size):
        return "at {0}".format(geom.fmt_point(box[0]))
    return "{0} by {1} by {2}, at {3}".format(
        geom.fmt_num(size[0]), geom.fmt_num(size[1]), geom.fmt_num(size[2]),
        geom.fmt_point(box[0]))


def _location(obj: dict) -> str:
    box = obj["fingerprint"].get("bbox")
    return geom.fmt_point(box[0]) if box else "unknown position"


def _quoted(name: str) -> str:
    return '"' + (name or "") + '"'


def _name_list(object_ids: list[str], scene: Scene) -> str:
    parts = []
    for object_id in object_ids:
        obj = scene.objects.get(object_id)
        parts.append("{0} {1}".format(object_id, _quoted(obj["name"]))
                     if obj else object_id)
    if len(parts) > 4:
        return "{0} objects ({1}, ...)".format(len(parts), ", ".join(parts[:3]))
    return ", ".join(parts)


def _as_point(scene: Scene, ref: str):
    parts = ref.split(",")
    if len(parts) in (2, 3):
        try:
            return geom.vec3([float(p) for p in parts]), ref
        except ValueError:
            pass
    obj = scene.find(ref)
    if obj is None:
        raise LookupError("no object called {0!r}".format(ref))
    box = obj["fingerprint"].get("bbox")
    if box is None:
        raise LookupError(
            "{0} has no known position yet (needs a live rebuild)".format(obj["id"]))
    return geom.bbox_center(box), "{0} {1}".format(obj["id"], _quoted(obj["name"]))
