"""TASC data model: Site, Grid, Zone, Bay, Corridor, BayVoid, and TASCModel."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Site:
    """Site boundary defined as a 2D polygon."""

    corners: list[tuple[float, float]]
    units: str = "feet"

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        """Returns (min_x, min_y, max_x, max_y)."""
        xs = [c[0] for c in self.corners]
        ys = [c[1] for c in self.corners]
        return (min(xs), min(ys), max(xs), max(ys))

    @property
    def width(self) -> float:
        min_x, _, max_x, _ = self.bounds
        return max_x - min_x

    @property
    def depth(self) -> float:
        _, min_y, _, max_y = self.bounds
        return max_y - min_y

    @property
    def area(self) -> float:
        """Shoelace formula for polygon area."""
        n = len(self.corners)
        if n < 3:
            return 0.0
        a = 0.0
        for i in range(n):
            j = (i + 1) % n
            a += self.corners[i][0] * self.corners[j][1]
            a -= self.corners[j][0] * self.corners[i][1]
        return abs(a) / 2.0

    def to_dict(self) -> dict:
        return {"corners": self.corners, "units": self.units}

    @classmethod
    def from_dict(cls, data: dict) -> Site:
        return cls(
            corners=[tuple(c) for c in data["corners"]],
            units=data.get("units", "feet"),
        )

    @classmethod
    def rectangle(cls, width: float, depth: float, units: str = "feet") -> Site:
        """Create a rectangular site at origin."""
        return cls(
            corners=[(0, 0), (width, 0), (width, depth), (0, depth)],
            units=units,
        )


@dataclass
class Grid:
    """Structural grid overlay."""

    spacing: float
    rotation: float = 0.0
    origin: tuple[float, float] = (0, 0)

    def to_dict(self) -> dict:
        return {
            "spacing": self.spacing,
            "rotation": self.rotation,
            "origin": list(self.origin),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Grid:
        return cls(
            spacing=data["spacing"],
            rotation=data.get("rotation", 0.0),
            origin=tuple(data.get("origin", (0, 0))),
        )


@dataclass
class Zone:
    """A programmatic zone within the site."""

    name: str
    corners: list[tuple[float, float]]
    program_type: str = ""
    label: str = ""
    braille: str = ""

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        xs = [c[0] for c in self.corners]
        ys = [c[1] for c in self.corners]
        return (min(xs), min(ys), max(xs), max(ys))

    @property
    def width(self) -> float:
        min_x, _, max_x, _ = self.bounds
        return max_x - min_x

    @property
    def depth(self) -> float:
        _, min_y, _, max_y = self.bounds
        return max_y - min_y

    @property
    def area(self) -> float:
        """Shoelace formula for polygon area."""
        n = len(self.corners)
        if n < 3:
            return 0.0
        a = 0.0
        for i in range(n):
            j = (i + 1) % n
            a += self.corners[i][0] * self.corners[j][1]
            a -= self.corners[j][0] * self.corners[i][1]
        return abs(a) / 2.0

    @property
    def centroid(self) -> tuple[float, float]:
        n = len(self.corners)
        if n == 0:
            return (0, 0)
        cx = sum(c[0] for c in self.corners) / n
        cy = sum(c[1] for c in self.corners) / n
        return (cx, cy)

    @classmethod
    def rectangle(
        cls, name: str, width: float, depth: float, at: tuple[float, float] = (0, 0), program_type: str = ""
    ) -> Zone:
        """Create a rectangular zone at a given position."""
        x, y = at
        return cls(
            name=name,
            corners=[(x, y), (x + width, y), (x + width, y + depth), (x, y + depth)],
            program_type=program_type,
        )

    def to_dict(self) -> dict:
        d = {
            "name": self.name,
            "corners": self.corners,
            "program_type": self.program_type,
        }
        if self.label:
            d["label"] = self.label
        if self.braille:
            d["braille"] = self.braille
        return d

    @classmethod
    def from_dict(cls, data: dict) -> Zone:
        return cls(
            name=data["name"],
            corners=[tuple(c) for c in data["corners"]],
            program_type=data.get("program_type", ""),
            label=data.get("label", ""),
            braille=data.get("braille", ""),
        )


@dataclass
class Corridor:
    """Corridor within a structural bay."""

    enabled: bool = False
    axis: str = "x"  # "x" (east-west) or "y" (north-south)
    position: int = 1  # gridline index
    width: float = 8.0  # feet
    loading: str = "double"  # "single" or "double"

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "axis": self.axis,
            "position": self.position,
            "width": self.width,
            "loading": self.loading,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Corridor:
        return cls(
            enabled=data.get("enabled", False),
            axis=data.get("axis", "x"),
            position=data.get("position", 1),
            width=data.get("width", 8.0),
            loading=data.get("loading", "double"),
        )


@dataclass
class BayVoid:
    """Void (opening) within a structural bay."""

    center: tuple[float, float] = (0, 0)
    size: tuple[float, float] = (20, 20)
    shape: str = "rectangle"  # "rectangle" or "circle"

    def to_dict(self) -> dict:
        return {
            "center": list(self.center),
            "size": list(self.size),
            "shape": self.shape,
        }

    @classmethod
    def from_dict(cls, data: dict) -> BayVoid:
        return cls(
            center=tuple(data.get("center", (0, 0))),
            size=tuple(data.get("size", (20, 20))),
            shape=data.get("shape", "rectangle"),
        )


@dataclass
class Bay:
    """Structural bay with column grid."""

    name: str
    origin: tuple[float, float] = (0, 0)
    rotation: float = 0.0
    grid: tuple[int, int] = (1, 1)  # (nx, ny) number of bays
    spacing: tuple[float, float] = (24, 24)
    spacing_x: list[float] | None = None  # irregular x spacing
    spacing_y: list[float] | None = None  # irregular y spacing
    column_size: float = 1.5
    corridor: Corridor | None = None
    void: BayVoid | None = None
    label: str = ""
    braille: str = ""

    @property
    def column_count(self) -> int:
        """Total number of columns: (nx+1) * (ny+1)."""
        nx, ny = self.grid
        return (nx + 1) * (ny + 1)

    @property
    def gridlines_x(self) -> list[float]:
        """Cumulative x positions of gridlines from origin."""
        nx, _ = self.grid
        if self.spacing_x:
            lines = [0.0]
            for s in self.spacing_x[:nx]:
                lines.append(lines[-1] + s)
            return lines
        sx, _ = self.spacing
        return [i * sx for i in range(nx + 1)]

    @property
    def gridlines_y(self) -> list[float]:
        """Cumulative y positions of gridlines from origin."""
        _, ny = self.grid
        if self.spacing_y:
            lines = [0.0]
            for s in self.spacing_y[:ny]:
                lines.append(lines[-1] + s)
            return lines
        _, sy = self.spacing
        return [i * sy for i in range(ny + 1)]

    @property
    def footprint(self) -> tuple[float, float]:
        """Bay footprint size (total_x, total_y) in local coords."""
        return (self.gridlines_x[-1], self.gridlines_y[-1])

    @property
    def extents(self) -> tuple[float, float, float, float]:
        """World-coords bounding box (min_x, min_y, max_x, max_y) with rotation."""
        gx = self.gridlines_x
        gy = self.gridlines_y
        corners_local = [
            (gx[0], gy[0]),
            (gx[-1], gy[0]),
            (gx[-1], gy[-1]),
            (gx[0], gy[-1]),
        ]
        rad = math.radians(self.rotation)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        ox, oy = self.origin
        world_pts = []
        for lx, ly in corners_local:
            wx = ox + lx * cos_a - ly * sin_a
            wy = oy + lx * sin_a + ly * cos_a
            world_pts.append((wx, wy))
        xs = [p[0] for p in world_pts]
        ys = [p[1] for p in world_pts]
        return (min(xs), min(ys), max(xs), max(ys))

    def to_dict(self) -> dict:
        d: dict = {
            "name": self.name,
            "origin": list(self.origin),
            "rotation": self.rotation,
            "grid": list(self.grid),
            "spacing": list(self.spacing),
            "column_size": self.column_size,
        }
        if self.spacing_x is not None:
            d["spacing_x"] = self.spacing_x
        if self.spacing_y is not None:
            d["spacing_y"] = self.spacing_y
        if self.corridor is not None:
            d["corridor"] = self.corridor.to_dict()
        if self.void is not None:
            d["void"] = self.void.to_dict()
        if self.label:
            d["label"] = self.label
        if self.braille:
            d["braille"] = self.braille
        return d

    @classmethod
    def from_dict(cls, data: dict) -> Bay:
        corridor = None
        if data.get("corridor"):
            corridor = Corridor.from_dict(data["corridor"])
        void = None
        if data.get("void"):
            void = BayVoid.from_dict(data["void"])
        return cls(
            name=data["name"],
            origin=tuple(data.get("origin", (0, 0))),
            rotation=data.get("rotation", 0.0),
            grid=tuple(data.get("grid", (1, 1))),
            spacing=tuple(data.get("spacing", (24, 24))),
            spacing_x=data.get("spacing_x"),
            spacing_y=data.get("spacing_y"),
            column_size=data.get("column_size", 1.5),
            corridor=corridor,
            void=void,
            label=data.get("label", ""),
            braille=data.get("braille", ""),
        )


@dataclass
class TASCModel:
    """Root container for the entire design state."""

    site: Site | None = None
    grid: Grid | None = None
    zones: list[Zone] = field(default_factory=list)
    bays: list[Bay] = field(default_factory=list)

    def add_bay(self, bay: Bay) -> None:
        """Add or replace a bay by name."""
        for i, b in enumerate(self.bays):
            if b.name.lower() == bay.name.lower():
                self.bays[i] = bay
                return
        self.bays.append(bay)

    def remove_bay(self, name: str) -> bool:
        """Remove a bay by name. Returns True if found and removed."""
        for i, b in enumerate(self.bays):
            if b.name.lower() == name.lower():
                self.bays.pop(i)
                return True
        return False

    def get_bay(self, name: str) -> Bay | None:
        for b in self.bays:
            if b.name.lower() == name.lower():
                return b
        return None

    def add_zone(self, zone: Zone) -> list[str]:
        """Add zone, return list of warnings."""
        from tasc_core.core.validation import check_zone_in_boundary, check_zone_overlaps

        warnings = []
        if self.site:
            warnings.extend(check_zone_in_boundary(zone, self.site))
        warnings.extend(check_zone_overlaps(zone, self.zones))
        self.zones.append(zone)
        return warnings

    def remove_zone(self, name: str) -> bool:
        """Remove a zone by name. Returns True if found and removed."""
        for i, z in enumerate(self.zones):
            if z.name.lower() == name.lower():
                self.zones.pop(i)
                return True
        return False

    def get_zone(self, name: str) -> Zone | None:
        for z in self.zones:
            if z.name.lower() == name.lower():
                return z
        return None

    @property
    def total_zone_area(self) -> float:
        return sum(z.area for z in self.zones)

    def to_dict(self) -> dict:
        return {
            "site": self.site.to_dict() if self.site else None,
            "grid": self.grid.to_dict() if self.grid else None,
            "zones": [z.to_dict() for z in self.zones],
            "bays": [b.to_dict() for b in self.bays],
        }

    @classmethod
    def from_dict(cls, data: dict) -> TASCModel:
        model = cls()
        if data.get("site"):
            model.site = Site.from_dict(data["site"])
        if data.get("grid"):
            model.grid = Grid.from_dict(data["grid"])
        for z in data.get("zones", []):
            model.zones.append(Zone.from_dict(z))
        for b in data.get("bays", []):
            model.bays.append(Bay.from_dict(b))
        return model

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: Path) -> TASCModel:
        data = json.loads(path.read_text())
        return cls.from_dict(data)


# --- Undo system (disk-persisted) ---

UNDO_FILE = ".tasc_undo.json"
MAX_UNDO = 10


def push_undo(model: TASCModel, state_path: Path) -> None:
    """Save current state to undo stack before modification."""
    undo_path = state_path.parent / UNDO_FILE
    stack: list = []
    if undo_path.exists():
        try:
            stack = json.loads(undo_path.read_text())
        except (json.JSONDecodeError, ValueError):
            stack = []
    stack.append(model.to_dict())
    if len(stack) > MAX_UNDO:
        stack = stack[-MAX_UNDO:]
    undo_path.write_text(json.dumps(stack, indent=2))


def pop_undo(state_path: Path) -> TASCModel | None:
    """Pop and return last state from undo stack."""
    undo_path = state_path.parent / UNDO_FILE
    if not undo_path.exists():
        return None
    try:
        stack = json.loads(undo_path.read_text())
    except (json.JSONDecodeError, ValueError):
        return None
    if not stack:
        return None
    state = stack.pop()
    undo_path.write_text(json.dumps(stack, indent=2))
    return TASCModel.from_dict(state)


def clear_undo(state_path: Path) -> None:
    """Clear the undo stack."""
    undo_path = state_path.parent / UNDO_FILE
    if undo_path.exists():
        undo_path.unlink()
