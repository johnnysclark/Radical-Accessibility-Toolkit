# -*- coding: utf-8 -*-
"""
Exporter — Export state.json to various formats
================================================
Supports .3dm (Rhino file) and text description export.

rhino3dm is an optional dependency: pip install rhino3dm
"""

import json
import os


def export_3dm(state, output_path):
    """Export state to a Rhino .3dm file.

    Requires: pip install rhino3dm

    Args:
        state: Parsed state.json dict.
        output_path: Output file path.

    Returns:
        Output file path string.
    """
    import rhino3dm

    file3dm = rhino3dm.File3dm()
    file3dm.Settings.ModelUnitSystem = rhino3dm.UnitSystem.Feet

    site = state.get("site", {})

    # Site boundary
    corners = site.get("corners")
    if not corners:
        ox, oy = site.get("origin", [0, 0])
        w = site.get("width", 180)
        h = site.get("height", 260)
        corners = [[ox, oy], [ox + w, oy], [ox + w, oy + h], [ox, oy + h]]

    if len(corners) >= 3:
        polyline = rhino3dm.Polyline(len(corners) + 1)
        for c in corners:
            polyline.Add(c[0], c[1], 0)
        polyline.Add(corners[0][0], corners[0][1], 0)  # close
        curve = polyline.ToPolylineCurve()
        attrs = rhino3dm.ObjectAttributes()
        attrs.Name = "site_boundary"
        file3dm.Objects.AddCurve(curve, attrs)

    # Zones
    for zname, zdata in state.get("zones", {}).items():
        zcorners = zdata.get("corners", [])
        if len(zcorners) >= 3:
            polyline = rhino3dm.Polyline(len(zcorners) + 1)
            for c in zcorners:
                polyline.Add(c[0], c[1], 0)
            polyline.Add(zcorners[0][0], zcorners[0][1], 0)
            curve = polyline.ToPolylineCurve()
            attrs = rhino3dm.ObjectAttributes()
            attrs.Name = zname
            file3dm.Objects.AddCurve(curve, attrs)

    # Grid lines
    grid = state.get("grid")
    if grid and grid.get("spacing"):
        spacing = grid["spacing"]
        ox, oy = site.get("origin", [0, 0])
        w = site.get("width", 180)
        h = site.get("height", 260)

        x = ox
        while x <= ox + w:
            line = rhino3dm.LineCurve(
                rhino3dm.Point3d(x, oy, 0),
                rhino3dm.Point3d(x, oy + h, 0))
            file3dm.Objects.AddCurve(line)
            x += spacing

        y = oy
        while y <= oy + h:
            line = rhino3dm.LineCurve(
                rhino3dm.Point3d(ox, y, 0),
                rhino3dm.Point3d(ox + w, y, 0))
            file3dm.Objects.AddCurve(line)
            y += spacing

    # Bay column positions
    import math
    for bname, bay in state.get("bays", {}).items():
        gt = bay.get("grid_type", "rectangular")
        bx, by = bay["origin"]
        rot = bay.get("rotation_deg", 0)
        col_size = state.get("style", {}).get("column_size", 1.5)
        r = col_size / 2.0

        if gt == "rectangular":
            nx, ny = bay["bays"]
            sx_a = bay.get("spacing_x")
            sy_a = bay.get("spacing_y")
            if sx_a and len(sx_a) == nx:
                cx_arr = [0.0]
                for s in sx_a:
                    cx_arr.append(cx_arr[-1] + s)
            else:
                sx = bay["spacing"][0]
                cx_arr = [i * sx for i in range(nx + 1)]
            if sy_a and len(sy_a) == ny:
                cy_arr = [0.0]
                for s in sy_a:
                    cy_arr.append(cy_arr[-1] + s)
            else:
                sy = bay["spacing"][1]
                cy_arr = [j * sy for j in range(ny + 1)]

            rad = math.radians(rot)
            for x in cx_arr:
                for y in cy_arr:
                    wx = bx + x * math.cos(rad) - y * math.sin(rad)
                    wy = by + x * math.sin(rad) + y * math.cos(rad)
                    circle = rhino3dm.Circle(rhino3dm.Point3d(wx, wy, 0), r)
                    curve = rhino3dm.ArcCurve(circle)
                    attrs = rhino3dm.ObjectAttributes()
                    attrs.Name = "column_{}_{}".format(bname, "{}x{}".format(int(x), int(y)))
                    file3dm.Objects.AddCurve(curve, attrs)

    file3dm.Write(str(output_path), version=7)
    return str(output_path)


def export_text(state, output_path, describe_fn=None):
    """Export full text description to a file.

    Args:
        state: Parsed state.json dict.
        output_path: Output file path.
        describe_fn: Optional describe function reference.

    Returns:
        Output file path string.
    """
    if describe_fn:
        text = describe_fn(state)
    else:
        text = json.dumps(state, indent=2)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    return str(output_path)
