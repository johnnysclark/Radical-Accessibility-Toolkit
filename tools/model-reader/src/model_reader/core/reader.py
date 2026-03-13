"""Load .3dm files and extract structured model information."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class BBox:
    """Axis-aligned bounding box."""

    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float

    @property
    def width(self):
        return self.max_x - self.min_x

    @property
    def depth(self):
        return self.max_y - self.min_y

    @property
    def height(self):
        return self.max_z - self.min_z

    @property
    def center(self):
        return (
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2,
            (self.min_z + self.max_z) / 2,
        )

    @property
    def is_flat(self):
        """True if the bounding box has zero height (2D geometry)."""
        return abs(self.height) < 1e-6


@dataclass
class LayerInfo:
    """Summary of a single layer."""

    index: int
    name: str
    color: tuple
    object_count: int
    visible: bool
    locked: bool


@dataclass
class ObjectInfo:
    """Summary of a single geometry object."""

    id: str
    name: str
    layer_name: str
    geometry_type: str
    bbox: BBox | None


@dataclass
class ModelInfo:
    """Structured summary of a .3dm file."""

    file_path: str
    file_name: str
    units: str
    layers: list[LayerInfo] = field(default_factory=list)
    objects: list[ObjectInfo] = field(default_factory=list)
    bounding_box: BBox | None = None
    file3dm: object = None  # raw rhino3dm.File3dm for slicer access


# Map rhino3dm UnitSystem enum values to readable strings
_UNIT_NAMES = {
    0: "none",
    1: "microns",
    2: "millimeters",
    3: "centimeters",
    4: "meters",
    5: "kilometers",
    6: "microinches",
    7: "mils",
    8: "inches",
    9: "feet",
    10: "miles",
}


def _geometry_type_name(geometry) -> str:
    """Extract a readable type name from a rhino3dm geometry object."""
    type_name = type(geometry).__name__
    # Strip common suffixes for cleaner display
    for suffix in ("Geometry",):
        if type_name.endswith(suffix) and len(type_name) > len(suffix):
            type_name = type_name[: -len(suffix)]
    return type_name


def _extract_bbox(geometry) -> BBox | None:
    """Extract bounding box from a rhino3dm geometry object."""
    try:
        bb = geometry.GetBoundingBox()
        return BBox(
            min_x=bb.Min.X,
            min_y=bb.Min.Y,
            min_z=bb.Min.Z,
            max_x=bb.Max.X,
            max_y=bb.Max.Y,
            max_z=bb.Max.Z,
        )
    except Exception:
        return None


def _layer_name_by_index(file3dm, index: int) -> str:
    """Look up layer name by index, return 'unknown' if not found."""
    try:
        return file3dm.Layers[index].Name
    except (IndexError, Exception):
        return "unknown"


def load_3dm(path: str) -> ModelInfo:
    """Load a .3dm file and return structured model information.

    Args:
        path: Path to the .3dm file.

    Returns:
        ModelInfo with layers, objects, bounding box, and raw file3dm.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file cannot be read as a .3dm file.
    """
    import rhino3dm

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    file3dm = rhino3dm.File3dm.Read(path)
    if file3dm is None:
        raise ValueError(f"Cannot read as .3dm file: {path}")

    # Units
    unit_val = int(file3dm.Settings.ModelUnitSystem)
    units = _UNIT_NAMES.get(unit_val, f"unit-{unit_val}")

    # Layers — count objects per layer
    layer_counts = {}
    for obj in file3dm.Objects:
        li = obj.Attributes.LayerIndex
        layer_counts[li] = layer_counts.get(li, 0) + 1

    layers = []
    for i, layer in enumerate(file3dm.Layers):
        layers.append(
            LayerInfo(
                index=i,
                name=layer.Name,
                color=tuple(layer.Color[:3]) if hasattr(layer.Color, '__iter__') else (0, 0, 0),
                object_count=layer_counts.get(i, 0),
                visible=layer.Visible,
                locked=layer.Locked,
            )
        )

    # Objects
    objects = []
    all_min_x = all_min_y = all_min_z = float("inf")
    all_max_x = all_max_y = all_max_z = float("-inf")

    for obj in file3dm.Objects:
        geo = obj.Geometry
        if geo is None:
            continue

        obj_bbox = _extract_bbox(geo)
        if obj_bbox is not None:
            all_min_x = min(all_min_x, obj_bbox.min_x)
            all_min_y = min(all_min_y, obj_bbox.min_y)
            all_min_z = min(all_min_z, obj_bbox.min_z)
            all_max_x = max(all_max_x, obj_bbox.max_x)
            all_max_y = max(all_max_y, obj_bbox.max_y)
            all_max_z = max(all_max_z, obj_bbox.max_z)

        objects.append(
            ObjectInfo(
                id=str(obj.Attributes.Id),
                name=obj.Attributes.Name or "",
                layer_name=_layer_name_by_index(file3dm, obj.Attributes.LayerIndex),
                geometry_type=_geometry_type_name(geo),
                bbox=obj_bbox,
            )
        )

    # Overall bounding box
    overall_bbox = None
    if all_min_x != float("inf"):
        overall_bbox = BBox(
            min_x=all_min_x,
            min_y=all_min_y,
            min_z=all_min_z,
            max_x=all_max_x,
            max_y=all_max_y,
            max_z=all_max_z,
        )

    return ModelInfo(
        file_path=os.path.abspath(path),
        file_name=os.path.basename(path),
        units=units,
        layers=layers,
        objects=objects,
        bounding_box=overall_bbox,
        file3dm=file3dm,
    )
