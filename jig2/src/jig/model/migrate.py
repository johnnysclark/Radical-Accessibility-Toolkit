"""Schema migration: best-effort up-conversion of older state files to jig_v4.

Supported sources:
- plan_layout_jig_v3.x (the original toolkit's controller schema)
- empty / unversioned dicts (treated as new)

Migration never raises on missing optional sections; it raises MigrationError
only when a file is recognizably v3 but structurally unusable.
"""

from jig.model.schema import SCHEMA_VERSION


class MigrationError(ValueError):
    pass


def migrate(raw):
    schema = raw.get("schema", "")
    if schema == SCHEMA_VERSION:
        return raw
    if schema.startswith("plan_layout_jig_v3"):
        return _from_v3(raw)
    if not schema and not raw:
        return {"schema": SCHEMA_VERSION}
    raise MigrationError(
        "cannot migrate schema {!r}; expected {} or plan_layout_jig_v3".format(
            schema, SCHEMA_VERSION))


def _from_v3(raw):
    out = {
        "schema": SCHEMA_VERSION,
        "units": "feet",
        "meta": {
            "created": raw.get("meta", {}).get("created", ""),
            "modified": raw.get("meta", {}).get("last_saved", ""),
            "name": "migrated",
            "notes": raw.get("meta", {}).get("notes", ""),
        },
    }

    site = raw.get("site", {})
    corners = site.get("corners")
    if not corners and site.get("width") and site.get("height"):
        ox, oy = site.get("origin", [0, 0])
        w, h = site["width"], site["height"]
        corners = [[ox, oy], [ox + w, oy], [ox + w, oy + h], [ox, oy + h]]
    out["site"] = {"boundary": corners or [], "label": "Site"}

    zones = []
    for idx, (name, z) in enumerate(sorted((raw.get("zones") or {}).items()), 1):
        zones.append({
            "id": "z{:02d}".format(idx),
            "name": name,
            "boundary": z.get("corners", []),
            "label": z.get("label", name),
            "kind": _zone_kind(z.get("program_type", "")),
        })
    out["zones"] = zones

    grid = raw.get("grid") or {}
    spacing = grid.get("spacing", 24.0)
    if not isinstance(spacing, (list, tuple)):
        spacing = [spacing, spacing]
    out["grid"] = {
        "enabled": bool(grid),
        "spacing": list(spacing),
        "rotation_deg": grid.get("rotation", 0.0),
        "origin": grid.get("origin", [0, 0]),
    }

    bays = []
    ap_counter = [0]
    cell_counter = [0]
    void_counter = [0]
    for idx, (name, b) in enumerate(sorted((raw.get("bays") or {}).items()), 1):
        if b.get("grid_type") == "radial":
            continue  # radial bays are deferred in v4 core
        counts = b.get("bays", [1, 1])
        nx, ny = int(counts[0]), int(counts[1])
        default = b.get("spacing", [24.0, 24.0])
        spacing_x = b.get("spacing_x") or [float(default[0])] * nx
        spacing_y = b.get("spacing_y") or [float(default[1])] * ny
        bay = {
            "id": "b{:02d}".format(idx),
            "name": name,
            "origin": b.get("origin", [0, 0]),
            "rotation_deg": b.get("rotation_deg", 0.0),
            "counts": [nx, ny],
            "spacing_x": spacing_x,
            "spacing_y": spacing_y,
            "walls": {
                "enabled": (b.get("walls") or {}).get("enabled", False),
                "thickness": (b.get("walls") or {}).get("thickness", 0.5),
            },
            "corridor": _corridor(b.get("corridor")),
            "apertures": [_aperture(a, ap_counter) for a in b.get("apertures", [])],
            "cells": _cells(b.get("cells") or {}, cell_counter),
            "voids": _voids(b, void_counter),
        }
        bays.append(bay)
    out["bays"] = bays
    return out


def _zone_kind(program_type):
    mapping = {"residential": "program", "service": "service",
               "circulation": "circulation"}
    return mapping.get(program_type, "program")


def _corridor(c):
    if not c or not c.get("enabled"):
        return None
    return {"axis": c.get("axis", "x"), "line": c.get("position", 1),
            "width": c.get("width", 8.0)}


def _aperture(a, counter):
    counter[0] += 1
    swing = "in" if a.get("swing", "positive") == "positive" else "out"
    return {
        "id": "ap{:02d}".format(counter[0]),
        "kind": a.get("type", "door"),
        "axis": a.get("axis", "x"),
        "line": a.get("gridline", 0),
        "offset": a.get("corner", 0.0),
        "width": a.get("width", 3.0),
        "hinge": a.get("hinge", "start"),
        "swing": swing,
    }


def _cells(cells, counter):
    out = []
    for key, c in sorted(cells.items()):
        counter[0] += 1
        i, j = key.split(",")
        out.append({
            "id": "c{:02d}".format(counter[0]),
            "at": [int(i), int(j)],
            "name": c.get("name", key),
            "label": c.get("label", c.get("name", key)),
        })
    return out


def _voids(b, counter):
    center = b.get("void_center")
    size = b.get("void_size")
    if not center or not size:
        return []
    counter[0] += 1
    shape = "circle" if b.get("void_shape") == "circle" else "rect"
    return [{"id": "v{:02d}".format(counter[0]), "shape": shape,
             "center": center, "size": size}]
