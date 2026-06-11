"""Fabrication file writers: binary STL, SVG, and DXF, plus scale math.

Pure stdlib geometry-to-bytes code shared by the engine's export
paths. Everything works on plain lists of numbers, so it is fully
testable without Rhino; the live backend supplies measured meshes and
section polylines.

Paper and print units are always millimeters. A scale like 1:100
means the building is divided by 100 on the way to paper, so a
10 meter wall at 1:100 comes out 100 millimeters long.
"""

from __future__ import annotations

import math
import os
import struct

from maquette.ops import OpError

UNITS_TO_MM = {
    "meters": 1000.0,
    "millimeters": 1.0,
    "centimeters": 10.0,
    "feet": 304.8,
    "inches": 25.4,
}

DEFAULT_SCALE = "1:100"
STROKE_MM = 0.35
MARGIN_MM = 10.0
DXF_LAYER = "MAQ-DRAWING"


class DrawingError(OpError):
    pass


# -- scale ---------------------------------------------------------------


def parse_scale(spec: str | None, units: str) -> tuple[float, str]:
    """Return (millimeters per model unit, spoken form) for a scale.

    parse_scale("1:100", "meters") -> (10.0, "1 to 100"): each meter
    of building becomes 10 millimeters of paper or print.
    """
    text = (spec or DEFAULT_SCALE).strip()
    parts = text.split(":")
    try:
        if len(parts) != 2:
            raise ValueError(text)
        num, den = float(parts[0]), float(parts[1])
        if num <= 0 or den <= 0:
            raise ValueError(text)
    except ValueError:
        raise DrawingError(
            "could not read the scale {0!r}; say it like 1:100 or 1:200.".format(
                text))
    to_mm = UNITS_TO_MM.get(units)
    if to_mm is None:
        raise DrawingError(
            "no millimeter size known for units {0!r}; use meters, "
            "millimeters, centimeters, feet, or inches.".format(units))
    spoken = "{0:g} to {1:g}".format(num, den)
    return to_mm * num / den, spoken


# -- plane mapping ---------------------------------------------------------


def to_paper(axis: str, point: list[float]) -> tuple[float, float]:
    """Drop a 3D point onto the drawing plane for a cut along axis.

    Plans (axis z) keep x across and y up. Sections at x keep y across
    and z up; sections at y keep x across and z up, so up is always up.
    """
    if axis == "z":
        return point[0], point[1]
    if axis == "x":
        return point[1], point[2]
    if axis == "y":
        return point[0], point[2]
    raise DrawingError("unknown cut axis {0!r}; use x, y, or z.".format(axis))


# -- shared file plumbing -----------------------------------------------------


def _write_bytes(path: str, blob: bytes) -> None:
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "wb") as handle:
        handle.write(blob)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def _write_text(path: str, text: str) -> None:
    _write_bytes(path, text.encode("utf-8"))


def _bounds(points) -> tuple[list[float], list[float]]:
    low = [math.inf] * len(points[0])
    high = [-math.inf] * len(points[0])
    for point in points:
        for index, value in enumerate(point):
            low[index] = min(low[index], value)
            high[index] = max(high[index], value)
    return low, high


# -- STL -----------------------------------------------------------------------


def write_stl(path: str, solids: list[dict], factor: float) -> dict:
    """Write a binary STL in millimeters; return triangle count and size.

    solids: [{"vertices": [[x,y,z], ...], "faces": [[a,b,c], ...]}, ...]
    in model units; factor converts model units to millimeters.
    """
    triangles = []
    every_point = []
    for solid in solids:
        scaled = [[coord * factor for coord in vertex]
                  for vertex in solid["vertices"]]
        every_point.extend(scaled)
        for face in solid["faces"]:
            triangles.append((scaled[face[0]], scaled[face[1]],
                              scaled[face[2]]))
    if not triangles:
        raise DrawingError("no triangles to write; nothing was meshed.")
    blob = bytearray()
    blob += "Maquette binary STL, millimeters".encode("ascii").ljust(80, b" ")
    blob += struct.pack("<I", len(triangles))
    for a, b, c in triangles:
        blob += struct.pack("<12fH", *(_normal(a, b, c) + a + b + c), 0)
    _write_bytes(path, bytes(blob))
    low, high = _bounds(every_point)
    return {"triangles": len(triangles),
            "size_mm": [high[i] - low[i] for i in range(3)]}


def _normal(a: list[float], b: list[float], c: list[float]) -> list[float]:
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    n = [u[1] * v[2] - u[2] * v[1],
         u[2] * v[0] - u[0] * v[2],
         u[0] * v[1] - u[1] * v[0]]
    length = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
    if length < 1e-12:
        return [0.0, 0.0, 0.0]
    return [n[0] / length, n[1] / length, n[2] / length]


# -- SVG ------------------------------------------------------------------------


def write_svg(path: str, outlines: list[dict], title: str) -> dict:
    """Write outline curves as an SVG sheet sized in millimeters.

    outlines: [{"points": [(u, v), ...], "closed": bool}, ...] already
    in paper millimeters, v meaning up. SVG y grows downward, so v is
    flipped here and nowhere else.
    """
    points = [p for outline in outlines for p in outline["points"]]
    if not points:
        raise DrawingError("no outlines to draw.")
    low, high = _bounds(points)
    width = (high[0] - low[0]) + 2 * MARGIN_MM
    height = (high[1] - low[1]) + 2 * MARGIN_MM

    def place(point):
        u = point[0] - low[0] + MARGIN_MM
        v = (high[1] - point[1]) + MARGIN_MM
        return u, v

    paths = []
    for outline in outlines:
        steps = []
        for index, point in enumerate(outline["points"]):
            u, v = place(point)
            steps.append("{0}{1:.3f} {2:.3f}".format(
                "M" if index == 0 else "L", u, v))
        if outline.get("closed"):
            steps.append("Z")
        paths.append('<path d="{0}"/>'.format(" ".join(steps)))
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'width="{0:.1f}mm" height="{1:.1f}mm" '
        'viewBox="0 0 {0:.3f} {1:.3f}">'.format(width, height),
        "<title>{0}</title>".format(_escape(title)),
        '<g fill="none" stroke="black" stroke-width="{0}" '
        'stroke-linejoin="round" stroke-linecap="round">'.format(STROKE_MM),
    ]
    lines.extend(paths)
    lines.extend(["</g>", "</svg>", ""])
    _write_text(path, "\n".join(lines))
    return {"outlines": len(outlines), "sheet_mm": [width, height]}


def _escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


# -- DXF ------------------------------------------------------------------------


def write_dxf(path: str, outlines: list[dict], title: str = "") -> dict:
    """Write outline curves as a minimal R12 DXF, units millimeters.

    Same outline format as write_svg; v stays up because CAD y is up.
    R12 POLYLINE entities open everywhere: Rhino, Illustrator, laser
    cutter software.
    """
    points = [p for outline in outlines for p in outline["points"]]
    if not points:
        raise DrawingError("no outlines to draw.")
    rows = ["999", title or "Maquette drawing, millimeters",
            "0", "SECTION", "2", "HEADER",
            "9", "$ACADVER", "1", "AC1009",
            "0", "ENDSEC",
            "0", "SECTION", "2", "ENTITIES"]
    for outline in outlines:
        rows += ["0", "POLYLINE", "8", DXF_LAYER, "66", "1",
                 "70", "1" if outline.get("closed") else "0"]
        for u, v in outline["points"]:
            rows += ["0", "VERTEX", "8", DXF_LAYER,
                     "10", "{0:.3f}".format(u),
                     "20", "{0:.3f}".format(v),
                     "30", "0.0"]
        rows += ["0", "SEQEND"]
    rows += ["0", "ENDSEC", "0", "EOF", ""]
    _write_text(path, "\n".join(rows))
    low, high = _bounds(points)
    return {"outlines": len(outlines),
            "sheet_mm": [high[0] - low[0], high[1] - low[1]]}
