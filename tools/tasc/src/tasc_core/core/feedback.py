"""Text descriptions with dimensions for screen-reader-friendly feedback."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tasc_core.core.model import Bay, BayVoid, Corridor, Grid, Site, TASCModel, Zone


def _fmt(value: float) -> str:
    """Format a number: show as integer if whole, otherwise 1 decimal."""
    if value == int(value):
        return f"{int(value):,}"
    return f"{value:,.1f}"


def site_created(site: "Site") -> str:
    return (
        f"Site boundary created. {_fmt(site.width)} by {_fmt(site.depth)} {site.units}. "
        f"Area: {_fmt(site.area)} square {site.units}."
    )


def grid_applied(grid: "Grid", site: "Site") -> str:
    cols = int(site.width / grid.spacing) if grid.spacing > 0 else 0
    rows = int(site.depth / grid.spacing) if grid.spacing > 0 else 0
    msg = (
        f"Grid applied. {cols} by {rows} cells, {_fmt(grid.spacing)} {site.units} spacing"
    )
    if grid.rotation != 0:
        msg += f", {_fmt(grid.rotation)} degree rotation"
    msg += "."
    return msg


def zone_placed(zone: "Zone", site: "Site | None") -> str:
    cx, cy = zone.centroid
    min_x, min_y, _, _ = zone.bounds
    msg = (
        f"{zone.name} zone placed at {_fmt(min_x)}, {_fmt(min_y)}. "
        f"{_fmt(zone.width)} by {_fmt(zone.depth)}"
    )
    if site:
        msg += f" {site.units}"
    msg += f". Area: {_fmt(zone.area)} square"
    if site:
        msg += f" {site.units}"
    msg += "."

    # Distances to boundary
    if site:
        s_min_x, s_min_y, s_max_x, s_max_y = site.bounds
        z_min_x, z_min_y, z_max_x, z_max_y = zone.bounds
        north = s_max_y - z_max_y
        south = z_min_y - s_min_y
        east = s_max_x - z_max_x
        west = z_min_x - s_min_x
        msg += (
            f" Distances to boundary:"
            f" north {_fmt(north)} {site.units},"
            f" south {_fmt(south)} {site.units},"
            f" east {_fmt(east)} {site.units},"
            f" west {_fmt(west)} {site.units}."
        )

    return msg


def zone_removed(name: str) -> str:
    return f"Zone {name} removed."


def zone_not_found(name: str) -> str:
    return f"Zone {name} not found."


def warning_message(warning: str) -> str:
    return f"Warning: {warning}."


def bay_placed(bay: "Bay", site: "Site | None") -> str:
    nx, ny = bay.grid
    sx, sy = bay.spacing
    ox, oy = bay.origin
    msg = (
        f"Bay {bay.name} placed at {_fmt(ox)}, {_fmt(oy)}. "
        f"{nx} by {ny} bays at {_fmt(sx)} by {_fmt(sy)} foot spacing. "
        f"{bay.column_count} columns."
    )
    if bay.rotation != 0:
        msg += f" Rotated {_fmt(bay.rotation)} degrees."
    return msg


def bay_updated(bay: "Bay", field_name: str, old_val, new_val) -> str:
    return f"Bay {bay.name} {field_name} = {new_val}. Was {old_val}."


def corridor_updated(bay_name: str, corridor: "Corridor") -> str:
    if not corridor.enabled:
        return f"Corridor disabled on Bay {bay_name}."
    axis_label = "East-west" if corridor.axis == "x" else "North-south"
    return (
        f"Corridor enabled on Bay {bay_name}. "
        f"{axis_label}, {_fmt(corridor.width)} feet wide, {corridor.loading}-loaded."
    )


def void_updated(bay_name: str, void: "BayVoid | None") -> str:
    if void is None:
        return f"Void removed from Bay {bay_name}."
    w, h = void.size
    cx, cy = void.center
    if void.shape == "circle":
        return (
            f"Void set on Bay {bay_name}. "
            f"Circle, {_fmt(w)} feet diameter, center {_fmt(cx)}, {_fmt(cy)}."
        )
    return (
        f"Void set on Bay {bay_name}. "
        f"Rectangle, {_fmt(w)} by {_fmt(h)} feet, center {_fmt(cx)}, {_fmt(cy)}."
    )


def label_set(name: str, label: str, braille: str) -> str:
    msg = f"Label set on {name}. Text: {label}."
    if braille:
        msg += f" Braille: {braille}."
    return msg


def describe_model(model: "TASCModel") -> str:
    """Produce a full text description of the model."""
    lines = []

    if model.site:
        lines.append(
            f"Site: {_fmt(model.site.width)} by {_fmt(model.site.depth)} {model.site.units}. "
            f"Area: {_fmt(model.site.area)} square {model.site.units}."
        )
    else:
        lines.append("No site boundary defined.")

    if model.grid and model.site:
        cols = int(model.site.width / model.grid.spacing) if model.grid.spacing > 0 else 0
        rows = int(model.site.depth / model.grid.spacing) if model.grid.spacing > 0 else 0
        grid_line = f"Grid: {_fmt(model.grid.spacing)} {model.site.units} spacing"
        if model.grid.rotation != 0:
            grid_line += f", {_fmt(model.grid.rotation)} degree rotation"
        grid_line += f". {cols} by {rows} cells."
        lines.append(grid_line)

    if model.bays:
        lines.append(f"Bays ({len(model.bays)}):")
        for i, b in enumerate(model.bays, 1):
            nx, ny = b.grid
            sx, sy = b.spacing
            ox, oy = b.origin
            entry = (
                f"  {i}. {b.name}: {nx} by {ny} bays at "
                f"{_fmt(sx)} by {_fmt(sy)} foot spacing. "
                f"{b.column_count} columns. Anchor: {_fmt(ox)}, {_fmt(oy)}."
            )
            if b.rotation != 0:
                entry += f" Rotated {_fmt(b.rotation)} degrees."
            lines.append(entry)
            if b.corridor and b.corridor.enabled:
                axis_label = "east-west" if b.corridor.axis == "x" else "north-south"
                lines.append(
                    f"     Corridor: {axis_label}, {_fmt(b.corridor.width)} feet wide, "
                    f"{b.corridor.loading}-loaded."
                )
            if b.void:
                vw, vh = b.void.size
                if b.void.shape == "circle":
                    lines.append(f"     Void: circle, {_fmt(vw)} feet diameter.")
                else:
                    lines.append(f"     Void: rectangle, {_fmt(vw)} by {_fmt(vh)} feet.")
            if b.label:
                entry_label = f"     Label: {b.label}."
                if b.braille:
                    entry_label += f" Braille: {b.braille}."
                lines.append(entry_label)

    if model.zones:
        lines.append(f"Zones ({len(model.zones)}):")
        for i, z in enumerate(model.zones, 1):
            z_min_x, z_min_y, _, _ = z.bounds
            entry = f"  {i}. {z.name}: {_fmt(z.width)} by {_fmt(z.depth)}"
            if model.site:
                entry += f" {model.site.units}"
            entry += f" at {_fmt(z_min_x)}, {_fmt(z_min_y)}"
            entry += f". Area: {_fmt(z.area)} sq"
            if model.site:
                entry += f" {model.site.units}"
            entry += "."
            if z.program_type:
                entry += f" Type: {z.program_type}."
            if z.label:
                entry += f" Label: {z.label}."
            lines.append(entry)

        total = model.total_zone_area
        lines.append(f"Total program area: {_fmt(total)} square"
                      + (f" {model.site.units}" if model.site else "")
                      + ".")
        if model.site and model.site.area > 0:
            pct = (total / model.site.area) * 100
            remaining = model.site.area - total
            lines.append(
                f"Site coverage: {pct:.1f}%. "
                f"Remaining area: {_fmt(remaining)} square {model.site.units}."
            )
    else:
        if not model.bays:
            lines.append("No zones defined.")

    return "\n".join(lines)


def list_zones(model: "TASCModel") -> str:
    """Short listing of current model state."""
    lines = []
    if model.site:
        lines.append(f"Site: {_fmt(model.site.width)} x {_fmt(model.site.depth)} {model.site.units}")
    if model.grid:
        lines.append(f"Grid: {_fmt(model.grid.spacing)} spacing")
    if model.bays:
        for b in model.bays:
            nx, ny = b.grid
            ox, oy = b.origin
            line = f"  Bay {b.name}: {nx}x{ny} at ({_fmt(ox)}, {_fmt(oy)})"
            if b.label:
                line += f" [{b.label}]"
            lines.append(line)
    if model.zones:
        for z in model.zones:
            z_min_x, z_min_y, _, _ = z.bounds
            line = f"  {z.name}: {_fmt(z.width)} x {_fmt(z.depth)} at ({_fmt(z_min_x)}, {_fmt(z_min_y)})"
            if z.label:
                line += f" [{z.label}]"
            lines.append(line)
    if not model.bays and not model.zones:
        lines.append("No zones.")
    return "\n".join(lines)
