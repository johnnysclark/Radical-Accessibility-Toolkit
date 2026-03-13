"""Extract plan, section, and elevation views from 3dm geometry.

Renders geometry to 2D B&W PIL images suitable for PIAF tactile printing.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image, ImageDraw

if TYPE_CHECKING:
    from model_reader.core.reader import BBox, ModelInfo


# Default rendering parameters
DEFAULT_DPI = 150
DEFAULT_MARGIN_INCHES = 0.5
DEFAULT_LINE_WIDTH = 2
LETTER_WIDTH_INCHES = 8.5
LETTER_HEIGHT_INCHES = 11.0


def _canvas_setup(
    content_width: float,
    content_height: float,
    dpi: int = DEFAULT_DPI,
    margin_inches: float = DEFAULT_MARGIN_INCHES,
):
    """Compute canvas size and scale for a given content extent.

    Returns (image_width_px, image_height_px, scale, offset_x, offset_y).
    """
    margin_px = int(margin_inches * dpi)
    max_w_px = int(LETTER_WIDTH_INCHES * dpi) - 2 * margin_px
    max_h_px = int(LETTER_HEIGHT_INCHES * dpi) - 2 * margin_px

    if content_width <= 0 or content_height <= 0:
        return (2 * margin_px, 2 * margin_px, 1.0, margin_px, margin_px)

    scale = min(max_w_px / content_width, max_h_px / content_height)

    img_w = int(content_width * scale) + 2 * margin_px
    img_h = int(content_height * scale) + 2 * margin_px

    return (img_w, img_h, scale, margin_px, margin_px)


def _sample_curve_points(curve, num_samples: int = 200) -> list[tuple[float, float, float]]:
    """Sample points along a rhino3dm curve.

    Returns list of (x, y, z) tuples.
    """
    points = []
    domain = curve.Domain
    t_start = domain.T0
    t_end = domain.T1

    if abs(t_end - t_start) < 1e-12:
        return points

    for i in range(num_samples + 1):
        t = t_start + (t_end - t_start) * i / num_samples
        pt = curve.PointAt(t)
        points.append((pt.X, pt.Y, pt.Z))

    return points


def _get_mesh_edges(mesh) -> list[tuple[tuple[float, float, float], tuple[float, float, float]]]:
    """Extract all edges from a rhino3dm mesh as pairs of (x,y,z) tuples."""
    edges = []
    vertices = mesh.Vertices
    faces = mesh.Faces

    for fi in range(len(faces)):
        face = faces[fi]
        # face is (A, B, C) or (A, B, C, D)
        indices = [face[0], face[1], face[2]]
        if face[3] != face[2]:  # quad face
            indices.append(face[3])

        for j in range(len(indices)):
            i0 = indices[j]
            i1 = indices[(j + 1) % len(indices)]
            v0 = vertices[i0]
            v1 = vertices[i1]
            edges.append(
                ((v0.X, v0.Y, v0.Z), (v1.X, v1.Y, v1.Z))
            )
    return edges


def _collect_wireframe_segments(file3dm) -> list[list[tuple[float, float, float]]]:
    """Collect all drawable geometry as polyline segments.

    Each segment is a list of (x, y, z) points.
    """
    segments = []

    for obj in file3dm.Objects:
        geo = obj.Geometry
        if geo is None:
            continue

        type_name = type(geo).__name__

        # Curves — sample points along the curve
        if hasattr(geo, "Domain") and hasattr(geo, "PointAt"):
            pts = _sample_curve_points(geo)
            if pts:
                segments.append(pts)

        # Meshes — extract edges
        elif "Mesh" in type_name and hasattr(geo, "Vertices") and hasattr(geo, "Faces"):
            edges = _get_mesh_edges(geo)
            for p0, p1 in edges:
                segments.append([p0, p1])

        # Breps — get wireframe edges
        elif "Brep" in type_name and hasattr(geo, "Edges"):
            for edge in geo.Edges:
                pts = _sample_curve_points(edge)
                if pts:
                    segments.append(pts)

        # Points — store as single-point segment (will render as dot)
        elif hasattr(geo, "Location"):
            loc = geo.Location
            segments.append([(loc.X, loc.Y, loc.Z)])

        # Extrusions — try to get wireframe curves
        elif "Extrusion" in type_name:
            try:
                brep = geo.ToBrep()
                if brep is not None:
                    for edge in brep.Edges:
                        pts = _sample_curve_points(edge)
                        if pts:
                            segments.append(pts)
            except Exception:
                pass

    return segments


def _project_xy(segments):
    """Project segments onto XY plane (plan view). Returns list of [(x,y), ...] polylines."""
    return [[(p[0], p[1]) for p in seg] for seg in segments]


def _project_xz(segments):
    """Project segments onto XZ plane (front elevation). Returns list of [(x,z), ...] polylines."""
    return [[(p[0], p[2]) for p in seg] for seg in segments]


def _project_yz(segments):
    """Project segments onto YZ plane (side elevation). Returns list of [(y,z), ...] polylines."""
    return [[(p[1], p[2]) for p in seg] for seg in segments]


def _compute_2d_bounds(polylines_2d):
    """Compute bounding box of 2D polylines. Returns (min_x, min_y, max_x, max_y)."""
    all_x = []
    all_y = []
    for poly in polylines_2d:
        for x, y in poly:
            if math.isfinite(x) and math.isfinite(y):
                all_x.append(x)
                all_y.append(y)
    if not all_x:
        return (0, 0, 1, 1)
    return (min(all_x), min(all_y), max(all_x), max(all_y))


def _render_2d(polylines_2d, dpi=DEFAULT_DPI, line_width=DEFAULT_LINE_WIDTH, flip_y=True):
    """Render 2D polylines to a B&W PIL Image.

    Args:
        polylines_2d: List of [(x,y), ...] polylines in model coords.
        dpi: Output resolution.
        line_width: Stroke width in pixels.
        flip_y: If True, flip Y axis (standard for plan views where Y goes up).

    Returns:
        PIL Image in mode '1' (1-bit B&W).
    """
    min_x, min_y, max_x, max_y = _compute_2d_bounds(polylines_2d)
    content_w = max_x - min_x
    content_h = max_y - min_y

    # Ensure minimum size
    if content_w < 1e-6:
        content_w = 1.0
    if content_h < 1e-6:
        content_h = 1.0

    img_w, img_h, scale, ox, oy = _canvas_setup(content_w, content_h, dpi)

    # Create white image
    img = Image.new("L", (img_w, img_h), 255)
    draw = ImageDraw.Draw(img)

    def to_px(x, y):
        px = int((x - min_x) * scale + ox)
        if flip_y:
            py = int((max_y - y) * scale + oy)
        else:
            py = int((y - min_y) * scale + oy)
        return (px, py)

    for poly in polylines_2d:
        if len(poly) < 2:
            # Single point — draw a dot
            if poly:
                px, py = to_px(poly[0][0], poly[0][1])
                r = max(1, line_width)
                draw.ellipse([px - r, py - r, px + r, py + r], fill=0)
            continue

        pixel_coords = [to_px(x, y) for x, y in poly]
        draw.line(pixel_coords, fill=0, width=line_width)

    # Convert to 1-bit
    return img.convert("1")


def _intersect_segments_with_plane(segments, axis_index, position):
    """Find intersection points where 3D segments cross a plane.

    Args:
        segments: List of [(x,y,z), ...] polylines.
        axis_index: 0=X, 1=Y, 2=Z — which axis the plane is perpendicular to.
        position: The coordinate value on that axis where the plane sits.

    Returns:
        List of [(a, b), ...] 2D polyline segments in the cut plane's coordinate system.
        For Z cuts: returns (x, y) pairs.
        For X cuts: returns (y, z) pairs.
        For Y cuts: returns (x, z) pairs.
    """
    cut_segments = []

    for seg in segments:
        # Walk consecutive point pairs, find crossings
        crossing_points = []
        for i in range(len(seg) - 1):
            p0 = seg[i]
            p1 = seg[i + 1]
            v0 = p0[axis_index]
            v1 = p1[axis_index]

            # Check if this edge crosses the plane
            if (v0 - position) * (v1 - position) < 0:
                # Linear interpolation to find crossing
                dv = v1 - v0
                if abs(dv) < 1e-12:
                    continue
                t = (position - v0) / dv
                cx = p0[0] + t * (p1[0] - p0[0])
                cy = p0[1] + t * (p1[1] - p0[1])
                cz = p0[2] + t * (p1[2] - p0[2])

                if axis_index == 2:  # Z cut -> (x, y)
                    crossing_points.append((cx, cy))
                elif axis_index == 0:  # X cut -> (y, z)
                    crossing_points.append((cy, cz))
                else:  # Y cut -> (x, z)
                    crossing_points.append((cx, cz))

            # Also include points that lie exactly on the plane
            elif abs(v0 - position) < 1e-6:
                if axis_index == 2:
                    crossing_points.append((p0[0], p0[1]))
                elif axis_index == 0:
                    crossing_points.append((p0[1], p0[2]))
                else:
                    crossing_points.append((p0[0], p0[2]))

        if len(crossing_points) >= 2:
            cut_segments.append(crossing_points)
        elif len(crossing_points) == 1:
            # Single crossing — render as point
            cut_segments.append(crossing_points)

    return cut_segments


def extract_plan(info: "ModelInfo", height: float | None = None, dpi: int = DEFAULT_DPI) -> Image.Image:
    """Extract a plan view (top-down XY projection).

    Args:
        info: ModelInfo from load_3dm.
        height: Optional Z height to filter — only include geometry that
                exists at or crosses this height. None means project everything.
        dpi: Output resolution.

    Returns:
        PIL Image in B&W.
    """
    segments = _collect_wireframe_segments(info.file3dm)

    if height is not None:
        # Filter: only keep segments where at least one point is near the height
        # or the segment crosses the height
        tolerance = 0.5  # half a unit tolerance
        filtered = []
        for seg in segments:
            for i in range(len(seg)):
                z = seg[i][2]
                if abs(z - height) < tolerance:
                    filtered.append(seg)
                    break
            else:
                # Check if any edge crosses the height
                for i in range(len(seg) - 1):
                    z0 = seg[i][2]
                    z1 = seg[i + 1][2]
                    if (z0 - height) * (z1 - height) <= 0:
                        filtered.append(seg)
                        break
        segments = filtered

    projected = _project_xy(segments)
    return _render_2d(projected, dpi=dpi)


def extract_section(
    info: "ModelInfo",
    axis: str = "z",
    position: float = 0.0,
    dpi: int = DEFAULT_DPI,
) -> Image.Image:
    """Extract a section cut through the model.

    Args:
        info: ModelInfo from load_3dm.
        axis: 'x', 'y', or 'z' — the axis perpendicular to the cut plane.
        position: Coordinate value on that axis where the cut occurs.
        dpi: Output resolution.

    Returns:
        PIL Image in B&W showing the section cut.
    """
    axis_map = {"x": 0, "y": 1, "z": 2}
    axis_index = axis_map.get(axis.lower())
    if axis_index is None:
        raise ValueError(f"Axis must be 'x', 'y', or 'z', got '{axis}'")

    segments = _collect_wireframe_segments(info.file3dm)
    cut_2d = _intersect_segments_with_plane(segments, axis_index, position)

    if not cut_2d:
        # Return empty white image with a note
        img = Image.new("1", (200, 100), 1)
        return img

    # For Z cuts, flip_y=True (plan-like). For X/Y cuts, flip_y=True (elevation-like).
    return _render_2d(cut_2d, dpi=dpi, flip_y=True)


def extract_elevation(
    info: "ModelInfo",
    direction: str = "north",
    dpi: int = DEFAULT_DPI,
) -> Image.Image:
    """Extract an elevation view.

    Args:
        info: ModelInfo from load_3dm.
        direction: 'north' (looking from +Y), 'south' (from -Y),
                   'east' (from +X), 'west' (from -X).
        dpi: Output resolution.

    Returns:
        PIL Image in B&W showing the elevation.
    """
    segments = _collect_wireframe_segments(info.file3dm)

    direction_lower = direction.lower()
    if direction_lower in ("north", "south"):
        # Looking along Y axis → project onto XZ
        projected = _project_xz(segments)
    elif direction_lower in ("east", "west"):
        # Looking along X axis → project onto YZ
        projected = _project_yz(segments)
    else:
        raise ValueError(
            f"Direction must be 'north', 'south', 'east', or 'west', got '{direction}'"
        )

    # For south/west views, we mirror by negating the horizontal axis
    if direction_lower == "south":
        projected = [[(-x, y) for x, y in poly] for poly in projected]
    elif direction_lower == "west":
        projected = [[(-x, y) for x, y in poly] for poly in projected]

    return _render_2d(projected, dpi=dpi, flip_y=True)
