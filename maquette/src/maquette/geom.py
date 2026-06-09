"""Pure stdlib geometry math: bounding boxes, transforms, distances.

Used by the scene to keep deterministic, backend-independent
predictions of where things are. A bbox is [[minx,miny,minz],
[maxx,maxy,maxz]] or None when unknown.
"""

from __future__ import annotations

import math

Vec = list[float]
BBox = list[list[float]]


def vec3(value) -> Vec:
    """Coerce a 2 or 3 element sequence to [x, y, z] floats."""
    parts = [float(v) for v in value]
    if len(parts) == 2:
        parts.append(0.0)
    if len(parts) != 3:
        raise ValueError("expected 2 or 3 coordinates, got {0}".format(len(parts)))
    return parts


def bbox_of_points(points: list[Vec]) -> BBox:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    zs = [p[2] for p in points]
    return [[min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]]


def bbox_corners(box: BBox) -> list[Vec]:
    (x0, y0, z0), (x1, y1, z1) = box
    return [
        [x0, y0, z0], [x1, y0, z0], [x0, y1, z0], [x1, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x0, y1, z1], [x1, y1, z1],
    ]


def merge_bboxes(boxes: list[BBox | None]) -> BBox | None:
    real = [b for b in boxes if b is not None]
    if not real:
        return None
    return bbox_of_points([b[0] for b in real] + [b[1] for b in real])


def bbox_center(box: BBox) -> Vec:
    return [(box[0][i] + box[1][i]) / 2.0 for i in range(3)]


def bbox_size(box: BBox) -> Vec:
    return [box[1][i] - box[0][i] for i in range(3)]


def translate_bbox(box: BBox | None, vector: Vec) -> BBox | None:
    if box is None:
        return None
    return [[box[0][i] + vector[i] for i in range(3)],
            [box[1][i] + vector[i] for i in range(3)]]


def distance(a: Vec, b: Vec) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def add(a: Vec, b: Vec) -> Vec:
    return [a[i] + b[i] for i in range(3)]


def sub(a: Vec, b: Vec) -> Vec:
    return [a[i] - b[i] for i in range(3)]


def scale_vec(v: Vec, s: float) -> Vec:
    return [v[i] * s for i in range(3)]


def normalize(v: Vec) -> Vec:
    length = math.sqrt(sum(c * c for c in v))
    if length == 0:
        raise ValueError("zero-length vector")
    return [c / length for c in v]


def rotate_point(point: Vec, center: Vec, angle_degrees: float, axis: Vec) -> Vec:
    """Rotate a point around an axis through center (Rodrigues formula)."""
    k = normalize(axis)
    theta = math.radians(angle_degrees)
    p = sub(point, center)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    cross = [k[1] * p[2] - k[2] * p[1],
             k[2] * p[0] - k[0] * p[2],
             k[0] * p[1] - k[1] * p[0]]
    dot = sum(k[i] * p[i] for i in range(3))
    rotated = [p[i] * cos_t + cross[i] * sin_t + k[i] * dot * (1 - cos_t)
               for i in range(3)]
    return add(rotated, center)


def mirror_point(point: Vec, plane_point: Vec, plane_normal: Vec) -> Vec:
    n = normalize(plane_normal)
    d = sum((point[i] - plane_point[i]) * n[i] for i in range(3))
    return [point[i] - 2 * d * n[i] for i in range(3)]


def scale_point(point: Vec, center: Vec, factors: Vec) -> Vec:
    return [center[i] + (point[i] - center[i]) * factors[i] for i in range(3)]


def transform_bbox(box: BBox | None, point_fn) -> BBox | None:
    """Apply a point transform to a bbox's corners, return the new AABB.

    Conservative for rotations (the result bounds the rotated box).
    """
    if box is None:
        return None
    return bbox_of_points([point_fn(c) for c in bbox_corners(box)])


def fmt_num(value: float) -> str:
    """Format a number the way a person would say it: no trailing zeros."""
    rounded = round(float(value), 3)
    if rounded == int(rounded):
        return str(int(rounded))
    return "{0:g}".format(rounded)


def fmt_point(point: Vec) -> str:
    return ",".join(fmt_num(c) for c in point)
