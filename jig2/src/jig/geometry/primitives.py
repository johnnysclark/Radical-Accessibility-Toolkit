"""Drawing primitives: dumb, frozen, backend-agnostic.

All geometry is 2D in the world XY plane (z = 0 implied). Points are
(x, y) tuples. A ScenePlan is a dict mapping layer name -> list of
primitives, emitted in deterministic order.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Polyline:
    points: tuple  # tuple of (x, y) tuples
    closed: bool = False
    weight_mm: float = 0.0  # 0 = hairline; backends may map to print width

    def __post_init__(self):
        object.__setattr__(self, "points",
                           tuple((float(x), float(y)) for x, y in self.points))


@dataclass(frozen=True)
class Circle:
    center: tuple
    radius: float

    def __post_init__(self):
        object.__setattr__(self, "center", (float(self.center[0]), float(self.center[1])))
        object.__setattr__(self, "radius", float(self.radius))


@dataclass(frozen=True)
class Arc:
    center: tuple
    radius: float
    start_deg: float
    end_deg: float  # counter-clockwise from start_deg

    def __post_init__(self):
        object.__setattr__(self, "center", (float(self.center[0]), float(self.center[1])))


@dataclass(frozen=True)
class TextLabel:
    text: str
    at: tuple
    height: float = 2.0

    def __post_init__(self):
        object.__setattr__(self, "at", (float(self.at[0]), float(self.at[1])))


def arc_three_points(arc):
    """Start, mid, end points of an Arc primitive, for 3-point arc backends
    (rs.AddArc3Pt and rhino3dm.Arc both take start, interior, end)."""
    import math
    cx, cy = arc.center

    def at(deg):
        rad = math.radians(deg)
        return (cx + arc.radius * math.cos(rad), cy + arc.radius * math.sin(rad))

    sweep = (arc.end_deg - arc.start_deg) % 360.0
    return at(arc.start_deg), at(arc.start_deg + sweep / 2.0), at(arc.start_deg + sweep)


def plan_counts(plan):
    """Object count per layer of a ScenePlan, plus a total. Deterministic."""
    counts = {layer: len(prims) for layer, prims in sorted(plan.items())}
    counts["total"] = sum(counts.values())
    return counts


def plan_bbox(plan):
    """Axis-aligned bounding box of every primitive: (min_x, min_y, max_x, max_y)."""
    xs, ys = [], []
    for prims in plan.values():
        for p in prims:
            if isinstance(p, Polyline):
                xs += [pt[0] for pt in p.points]
                ys += [pt[1] for pt in p.points]
            elif isinstance(p, (Circle, Arc)):
                xs += [p.center[0] - p.radius, p.center[0] + p.radius]
                ys += [p.center[1] - p.radius, p.center[1] + p.radius]
            elif isinstance(p, TextLabel):
                xs.append(p.at[0])
                ys.append(p.at[1])
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))
