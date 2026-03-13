"""Accessible text descriptions of 3dm model contents.

All output follows CLAUDE.md screen reader rules:
- Short labeled lines
- Numbered lists for enumeration
- No tables, no multi-column layouts
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model_reader.core.reader import ModelInfo


def _fmt(value: float) -> str:
    """Format a number: drop trailing zeros, cap at 2 decimal places."""
    if abs(value) < 0.005:
        return "0"
    formatted = f"{value:.2f}"
    return formatted.rstrip("0").rstrip(".")


def describe_model(info: "ModelInfo") -> str:
    """One-paragraph summary of the model."""
    lines = [f"OK: Model loaded. {info.file_name}"]
    lines.append(f"Units: {info.units}.")

    if info.bounding_box:
        bb = info.bounding_box
        lines.append(
            f"Bounding box: {_fmt(bb.width)} by {_fmt(bb.depth)} by {_fmt(bb.height)} {info.units}."
        )

    lines.append(f"Layers: {len(info.layers)}.")
    lines.append(f"Objects: {len(info.objects)} total.")

    # Summarize geometry types
    type_counts = {}
    for obj in info.objects:
        t = obj.geometry_type
        type_counts[t] = type_counts.get(t, 0) + 1
    if type_counts:
        parts = [f"{count} {name}" for name, count in sorted(type_counts.items())]
        lines.append(f"Types: {', '.join(parts)}.")

    return "\n".join(lines)


def describe_layers(info: "ModelInfo") -> str:
    """Numbered list of layers with object counts."""
    if not info.layers:
        return "OK: No layers found."

    lines = [f"OK: {len(info.layers)} layers."]
    for i, layer in enumerate(info.layers, 1):
        status = ""
        if not layer.visible:
            status = " (hidden)"
        elif layer.locked:
            status = " (locked)"
        lines.append(f"{i}. {layer.name}: {layer.object_count} objects{status}.")
    return "\n".join(lines)


def describe_objects(
    info: "ModelInfo",
    layer: str | None = None,
    geo_type: str | None = None,
) -> str:
    """Filtered listing of objects with dimensions."""
    filtered = info.objects

    if layer:
        layer_lower = layer.lower()
        filtered = [o for o in filtered if o.layer_name.lower() == layer_lower]

    if geo_type:
        type_lower = geo_type.lower()
        filtered = [o for o in filtered if o.geometry_type.lower() == type_lower]

    if not filtered:
        msg = "No objects found"
        if layer:
            msg += f" on layer '{layer}'"
        if geo_type:
            msg += f" of type '{geo_type}'"
        return f"OK: {msg}."

    lines = [f"OK: {len(filtered)} objects."]

    # Limit to first 50 for screen reader friendliness
    show = filtered[:50]
    for i, obj in enumerate(show, 1):
        name_part = obj.name if obj.name else "(unnamed)"
        dims = ""
        if obj.bbox:
            dims = f" {_fmt(obj.bbox.width)}x{_fmt(obj.bbox.depth)}x{_fmt(obj.bbox.height)}"
        lines.append(
            f"{i}. {name_part}: {obj.geometry_type} on {obj.layer_name}{dims}."
        )

    if len(filtered) > 50:
        lines.append(f"... and {len(filtered) - 50} more.")

    return "\n".join(lines)


def describe_object_detail(info: "ModelInfo", name_or_id: str) -> str:
    """Detailed description of a single object by name or ID."""
    target = name_or_id.lower()
    match = None
    for obj in info.objects:
        if obj.name.lower() == target or obj.id.lower() == target:
            match = obj
            break

    if match is None:
        return f"ERROR: Object '{name_or_id}' not found."

    lines = [f"OK: Object detail."]
    lines.append(f"Name: {match.name or '(unnamed)'}.")
    lines.append(f"ID: {match.id}.")
    lines.append(f"Type: {match.geometry_type}.")
    lines.append(f"Layer: {match.layer_name}.")

    if match.bbox:
        bb = match.bbox
        lines.append(
            f"Dimensions: {_fmt(bb.width)} by {_fmt(bb.depth)} by {_fmt(bb.height)} {info.units}."
        )
        cx, cy, cz = bb.center
        lines.append(f"Center: ({_fmt(cx)}, {_fmt(cy)}, {_fmt(cz)}).")
        if bb.is_flat:
            lines.append("Flat (2D geometry).")

    return "\n".join(lines)
