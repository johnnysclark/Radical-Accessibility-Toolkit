"""State schema jig_v4: dataclasses with dict round-tripping.

Conventions:
- All coordinates are 2D [x, y] in model units (state.units, default feet).
- Every addressable entity carries a stable ``id`` minted once and never
  renamed; ``name`` is the human/voice handle.
- A bay is a rectangular structural grid: counts = [nx, ny] bays (intervals),
  spacing_x has nx entries, spacing_y has ny entries, so there are nx+1
  gridlines across x and ny+1 across y. Walls run along gridlines.
- An aperture sits on the wall that runs along ``axis`` at gridline ``line``
  (axis "x", line 0 is the south wall), ``offset`` units from the line start.
"""

from dataclasses import dataclass, field
from datetime import datetime

SCHEMA_VERSION = "jig_v4"

APERTURE_KINDS = ("door", "window", "portal")
AXES = ("x", "y")
HINGES = ("start", "end")
SWINGS = ("in", "out")
ZONE_KINDS = ("program", "circulation", "service", "open")


class ModelError(ValueError):
    """Raised for invalid model values; message must be speakable."""


def _pt(value):
    if not (isinstance(value, (list, tuple)) and len(value) == 2):
        raise ModelError("point must be two numbers, got {!r}".format(value))
    return [float(value[0]), float(value[1])]


def _polygon(value):
    pts = [_pt(p) for p in value]
    if pts and len(pts) < 3:
        raise ModelError("polygon needs at least 3 points, got {}".format(len(pts)))
    return pts


def now_stamp():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


@dataclass
class Meta:
    created: str = ""
    modified: str = ""
    name: str = "untitled"
    notes: str = ""

    def to_dict(self):
        return {"created": self.created, "modified": self.modified,
                "name": self.name, "notes": self.notes}

    @classmethod
    def from_dict(cls, d):
        d = d or {}
        return cls(created=d.get("created", ""), modified=d.get("modified", ""),
                   name=d.get("name", "untitled"), notes=d.get("notes", ""))


@dataclass
class Site:
    boundary: list = field(default_factory=list)  # polygon, empty = no site yet
    label: str = "Site"

    def __post_init__(self):
        self.boundary = _polygon(self.boundary)

    @property
    def width(self):
        if not self.boundary:
            return 0.0
        xs = [p[0] for p in self.boundary]
        return max(xs) - min(xs)

    @property
    def depth(self):
        if not self.boundary:
            return 0.0
        ys = [p[1] for p in self.boundary]
        return max(ys) - min(ys)

    def to_dict(self):
        return {"boundary": self.boundary, "label": self.label}

    @classmethod
    def from_dict(cls, d):
        d = d or {}
        return cls(boundary=d.get("boundary", []), label=d.get("label", "Site"))


@dataclass
class Zone:
    id: str
    name: str
    boundary: list
    label: str = ""
    kind: str = "program"

    def __post_init__(self):
        self.boundary = _polygon(self.boundary)
        if len(self.boundary) < 3:
            raise ModelError("zone {} needs a boundary polygon".format(self.name))
        if self.kind not in ZONE_KINDS:
            raise ModelError("zone kind must be one of {}, got {}".format(
                ", ".join(ZONE_KINDS), self.kind))
        if not self.label:
            self.label = self.name

    def to_dict(self):
        return {"id": self.id, "name": self.name, "boundary": self.boundary,
                "label": self.label, "kind": self.kind}

    @classmethod
    def from_dict(cls, d):
        return cls(id=d["id"], name=d["name"], boundary=d["boundary"],
                   label=d.get("label", ""), kind=d.get("kind", "program"))


@dataclass
class Grid:
    enabled: bool = False
    spacing: list = field(default_factory=lambda: [24.0, 24.0])
    rotation_deg: float = 0.0
    origin: list = field(default_factory=lambda: [0.0, 0.0])

    def __post_init__(self):
        if len(self.spacing) != 2 or min(self.spacing) <= 0:
            raise ModelError("grid spacing must be two positive numbers")
        self.spacing = [float(self.spacing[0]), float(self.spacing[1])]
        self.origin = _pt(self.origin)
        self.rotation_deg = float(self.rotation_deg)

    def to_dict(self):
        return {"enabled": self.enabled, "spacing": self.spacing,
                "rotation_deg": self.rotation_deg, "origin": self.origin}

    @classmethod
    def from_dict(cls, d):
        d = d or {}
        return cls(enabled=d.get("enabled", False),
                   spacing=d.get("spacing", [24.0, 24.0]),
                   rotation_deg=d.get("rotation_deg", 0.0),
                   origin=d.get("origin", [0.0, 0.0]))


@dataclass
class Walls:
    enabled: bool = False
    thickness: float = 0.5

    def __post_init__(self):
        self.thickness = float(self.thickness)
        if self.thickness <= 0:
            raise ModelError("wall thickness must be positive, got {}".format(self.thickness))

    def to_dict(self):
        return {"enabled": self.enabled, "thickness": self.thickness}

    @classmethod
    def from_dict(cls, d):
        d = d or {}
        return cls(enabled=d.get("enabled", False), thickness=d.get("thickness", 0.5))


@dataclass
class Corridor:
    axis: str = "x"
    line: int = 1
    width: float = 8.0

    def __post_init__(self):
        if self.axis not in AXES:
            raise ModelError("corridor axis must be x or y, got {}".format(self.axis))
        self.line = int(self.line)
        self.width = float(self.width)
        if self.width <= 0:
            raise ModelError("corridor width must be positive, got {}".format(self.width))

    def to_dict(self):
        return {"axis": self.axis, "line": self.line, "width": self.width}

    @classmethod
    def from_dict(cls, d):
        if d is None:
            return None
        return cls(axis=d.get("axis", "x"), line=d.get("line", 1),
                   width=d.get("width", 8.0))


@dataclass
class Aperture:
    id: str
    kind: str
    axis: str
    line: int
    offset: float
    width: float
    hinge: str = "start"
    swing: str = "in"

    def __post_init__(self):
        if self.kind not in APERTURE_KINDS:
            raise ModelError("aperture kind must be one of {}, got {}".format(
                ", ".join(APERTURE_KINDS), self.kind))
        if self.axis not in AXES:
            raise ModelError("aperture axis must be x or y, got {}".format(self.axis))
        if self.hinge not in HINGES:
            raise ModelError("hinge must be start or end, got {}".format(self.hinge))
        if self.swing not in SWINGS:
            raise ModelError("swing must be in or out, got {}".format(self.swing))
        self.line = int(self.line)
        self.offset = float(self.offset)
        self.width = float(self.width)
        if self.width <= 0:
            raise ModelError("aperture width must be positive, got {}".format(self.width))
        if self.offset < 0:
            raise ModelError("aperture offset must not be negative, got {}".format(self.offset))

    def to_dict(self):
        return {"id": self.id, "kind": self.kind, "axis": self.axis,
                "line": self.line, "offset": self.offset, "width": self.width,
                "hinge": self.hinge, "swing": self.swing}

    @classmethod
    def from_dict(cls, d):
        return cls(id=d["id"], kind=d["kind"], axis=d["axis"], line=d["line"],
                   offset=d["offset"], width=d["width"],
                   hinge=d.get("hinge", "start"), swing=d.get("swing", "in"))


@dataclass
class Cell:
    id: str
    at: list  # [i, j] cell indices
    name: str
    label: str = ""

    def __post_init__(self):
        if len(self.at) != 2:
            raise ModelError("cell position must be two indices, got {!r}".format(self.at))
        self.at = [int(self.at[0]), int(self.at[1])]
        if not self.label:
            self.label = self.name

    def to_dict(self):
        return {"id": self.id, "at": self.at, "name": self.name, "label": self.label}

    @classmethod
    def from_dict(cls, d):
        return cls(id=d["id"], at=d["at"], name=d["name"], label=d.get("label", ""))


@dataclass
class Void:
    id: str
    shape: str = "rect"  # rect | circle
    center: list = field(default_factory=lambda: [0.0, 0.0])
    size: list = field(default_factory=lambda: [10.0, 10.0])  # [w, d] or [diameter, diameter]

    def __post_init__(self):
        if self.shape not in ("rect", "circle"):
            raise ModelError("void shape must be rect or circle, got {}".format(self.shape))
        self.center = _pt(self.center)
        self.size = [float(self.size[0]), float(self.size[1])]

    def to_dict(self):
        return {"id": self.id, "shape": self.shape, "center": self.center, "size": self.size}

    @classmethod
    def from_dict(cls, d):
        return cls(id=d["id"], shape=d.get("shape", "rect"),
                   center=d.get("center", [0.0, 0.0]), size=d.get("size", [10.0, 10.0]))


@dataclass
class Bay:
    id: str
    name: str
    origin: list = field(default_factory=lambda: [0.0, 0.0])
    rotation_deg: float = 0.0
    counts: list = field(default_factory=lambda: [1, 1])
    spacing_x: list = field(default_factory=lambda: [24.0])
    spacing_y: list = field(default_factory=lambda: [24.0])
    walls: Walls = field(default_factory=Walls)
    corridor: Corridor = None
    apertures: list = field(default_factory=list)
    cells: list = field(default_factory=list)
    voids: list = field(default_factory=list)

    def __post_init__(self):
        self.origin = _pt(self.origin)
        self.rotation_deg = float(self.rotation_deg)
        self.counts = [int(self.counts[0]), int(self.counts[1])]
        if min(self.counts) < 1:
            raise ModelError("bay counts must be at least 1x1, got {}x{}".format(*self.counts))
        self.spacing_x = [float(s) for s in self.spacing_x]
        self.spacing_y = [float(s) for s in self.spacing_y]
        if len(self.spacing_x) != self.counts[0]:
            raise ModelError("bay {}: spacing_x needs {} entries, got {}".format(
                self.name, self.counts[0], len(self.spacing_x)))
        if len(self.spacing_y) != self.counts[1]:
            raise ModelError("bay {}: spacing_y needs {} entries, got {}".format(
                self.name, self.counts[1], len(self.spacing_y)))
        if any(s <= 0 for s in self.spacing_x + self.spacing_y):
            raise ModelError("bay {}: all spacing values must be positive".format(self.name))

    @property
    def width(self):
        return sum(self.spacing_x)

    @property
    def depth(self):
        return sum(self.spacing_y)

    def find_aperture(self, ap_id):
        for ap in self.apertures:
            if ap.id == ap_id:
                return ap
        return None

    def find_cell(self, i, j):
        for c in self.cells:
            if c.at == [i, j]:
                return c
        return None

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "origin": self.origin,
            "rotation_deg": self.rotation_deg, "counts": self.counts,
            "spacing_x": self.spacing_x, "spacing_y": self.spacing_y,
            "walls": self.walls.to_dict(),
            "corridor": self.corridor.to_dict() if self.corridor else None,
            "apertures": [a.to_dict() for a in self.apertures],
            "cells": [c.to_dict() for c in self.cells],
            "voids": [v.to_dict() for v in self.voids],
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"], name=d["name"], origin=d.get("origin", [0.0, 0.0]),
            rotation_deg=d.get("rotation_deg", 0.0), counts=d.get("counts", [1, 1]),
            spacing_x=d.get("spacing_x", [24.0]), spacing_y=d.get("spacing_y", [24.0]),
            walls=Walls.from_dict(d.get("walls")),
            corridor=Corridor.from_dict(d.get("corridor")),
            apertures=[Aperture.from_dict(a) for a in d.get("apertures", [])],
            cells=[Cell.from_dict(c) for c in d.get("cells", [])],
            voids=[Void.from_dict(v) for v in d.get("voids", [])],
        )


@dataclass
class State:
    schema: str = SCHEMA_VERSION
    units: str = "feet"
    meta: Meta = field(default_factory=Meta)
    site: Site = field(default_factory=Site)
    zones: list = field(default_factory=list)
    grid: Grid = field(default_factory=Grid)
    bays: list = field(default_factory=list)

    def find_zone(self, name):
        for z in self.zones:
            if z.name == name or z.id == name:
                return z
        return None

    def find_bay(self, name):
        for b in self.bays:
            if b.name == name or b.id == name:
                return b
        return None

    def all_ids(self):
        ids = [z.id for z in self.zones] + [b.id for b in self.bays]
        for b in self.bays:
            ids += [a.id for a in b.apertures]
            ids += [c.id for c in b.cells]
            ids += [v.id for v in b.voids]
        return ids

    def to_dict(self):
        return {
            "schema": self.schema,
            "units": self.units,
            "meta": self.meta.to_dict(),
            "site": self.site.to_dict(),
            "zones": [z.to_dict() for z in self.zones],
            "grid": self.grid.to_dict(),
            "bays": [b.to_dict() for b in self.bays],
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            schema=d.get("schema", SCHEMA_VERSION),
            units=d.get("units", "feet"),
            meta=Meta.from_dict(d.get("meta")),
            site=Site.from_dict(d.get("site")),
            zones=[Zone.from_dict(z) for z in d.get("zones", [])],
            grid=Grid.from_dict(d.get("grid")),
            bays=[Bay.from_dict(b) for b in d.get("bays", [])],
        )

    @classmethod
    def new(cls):
        stamp = now_stamp()
        return cls(meta=Meta(created=stamp, modified=stamp))
