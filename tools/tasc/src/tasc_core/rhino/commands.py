"""High-level Rhino drawing operations for TASC model elements.

Uses the RhinoMCP protocol from https://github.com/jingcheng-chen/rhinomcp
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from tasc_core.rhino.protocol import (
    create_circle_cmd,
    create_layer_cmd,
    create_line_cmd,
    create_polyline_cmd,
    create_text_cmd,
    delete_all_cmd,
    execute_script_cmd,
)

if TYPE_CHECKING:
    from tasc_core.core.model import Bay, Grid, Site, TASCModel, Zone
    from tasc_core.rhino.connector import RhinoConnector

# Layer names
LAYER_SITE = "TASC_Site"
LAYER_GRID = "TASC_Grid"
LAYER_ZONES = "TASC_Zones"
LAYER_LABELS = "TASC_Labels"
LAYER_BAYS = "TASC_Bays"
LAYER_COLUMNS = "TASC_Columns"
LAYER_CORRIDORS = "TASC_Corridors"
LAYER_VOIDS = "TASC_Voids"

# Colors (RGB)
COLOR_SITE = (0, 0, 0)       # Black
COLOR_GRID = (180, 180, 180)  # Light gray
COLOR_ZONE = (60, 60, 60)    # Dark gray
COLOR_LABEL = (0, 0, 0)      # Black
COLOR_BAY = (120, 120, 120)   # Gray
COLOR_COLUMN = (0, 0, 0)      # Black
COLOR_CORRIDOR = (100, 100, 100)
COLOR_VOID = (160, 160, 160)


def _send_cmds(connector: "RhinoConnector", cmds: list[dict] | dict) -> None:
    """Send one or more protocol commands via the connector."""
    if isinstance(cmds, dict):
        cmds = [cmds]
    for cmd in cmds:
        connector.send(cmd["type"], cmd["params"])


DEFAULT_DISPLAY_MODE = "LightPen"
TACT_CAPTURE_MODE = "Pen"  # White background, black lines — required for TACT/PIAF


class RhinoDrawer:
    """Draws TASC model elements in Rhino via the connector."""

    def __init__(self, connector: "RhinoConnector"):
        self.connector = connector

    def setup_layers(self) -> None:
        """Create TASC layers in Rhino and set display mode."""
        if not self.connector.is_live:
            return
        for name, color in [
            (LAYER_SITE, COLOR_SITE),
            (LAYER_GRID, COLOR_GRID),
            (LAYER_ZONES, COLOR_ZONE),
            (LAYER_LABELS, COLOR_LABEL),
            (LAYER_BAYS, COLOR_BAY),
            (LAYER_COLUMNS, COLOR_COLUMN),
            (LAYER_CORRIDORS, COLOR_CORRIDOR),
            (LAYER_VOIDS, COLOR_VOID),
        ]:
            _send_cmds(self.connector, create_layer_cmd(name, color))
        self.set_display_mode(DEFAULT_DISPLAY_MODE)

    def set_display_mode(self, mode: str) -> str | None:
        """Set all viewports to a named display mode. Returns previous mode or None."""
        if not self.connector.is_live:
            return None
        script = (
            "import rhinoscriptsyntax as rs\n"
            f"mode = '{mode}'\n"
            "modes = rs.ViewDisplayModes(True)\n"
            "if mode in modes:\n"
            "    prev = None\n"
            "    for v in rs.ViewNames():\n"
            "        prev = rs.ViewDisplayMode(v, mode)\n"
            "    print('Switched to ' + mode)\n"
            "else:\n"
            "    print('Mode not found: ' + mode)\n"
            "    print('Available: ' + ', '.join(modes))\n"
        )
        try:
            result = self.connector.send("execute_rhinoscript_python_code", {"code": script})
            return result.get("output", "")
        except Exception:
            return None

    def capture_for_tact(self, output_path: str, viewport: str = "Top",
                         width: int = 2550, height: int = 3300) -> str | None:
        """Capture viewport image suitable for TACT/PIAF conversion.

        Temporarily switches to Pen mode (white bg, black lines), captures,
        then restores the working display mode. Returns output path or None.
        """
        if not self.connector.is_live:
            return None
        script = (
            "import rhinoscriptsyntax as rs\n"
            "import System.Drawing as sd\n"
            f"view = '{viewport}'\n"
            f"out = r'{output_path}'\n"
            f"w, h = {width}, {height}\n"
            "# Switch to Pen mode for capture\n"
            "prev = rs.ViewDisplayMode(view, 'Pen')\n"
            "rs.Command('_-ViewCaptureToFile ' + out + ' _Width=' + str(w) + ' _Height=' + str(h) + ' _Enter', False)\n"
            "# Restore previous mode\n"
            "rs.ViewDisplayMode(view, prev)\n"
            f"print('Captured to ' + out)\n"
        )
        try:
            result = self.connector.send("execute_rhinoscript_python_code", {"code": script})
            output = result.get("output", "")
            if "Captured" in output:
                return output_path
            return None
        except Exception:
            # Try to restore display mode even on failure
            self.set_display_mode(DEFAULT_DISPLAY_MODE)
            return None

    def draw_site(self, site: "Site") -> None:
        """Draw site boundary as closed polyline."""
        if not self.connector.is_live:
            return
        cmds = create_polyline_cmd(
            points=site.corners,
            name="site_boundary",
            layer=LAYER_SITE,
            color=COLOR_SITE,
            closed=True,
        )
        _send_cmds(self.connector, cmds)

    def draw_grid(self, grid: "Grid", site: "Site") -> None:
        """Draw grid lines clipped to site bounds."""
        if not self.connector.is_live:
            return
        min_x, min_y, max_x, max_y = site.bounds

        if grid.rotation == 0:
            # Vertical lines
            x = min_x + grid.origin[0] % grid.spacing
            while x <= max_x:
                _send_cmds(self.connector,
                    create_line_cmd((x, min_y), (x, max_y), LAYER_GRID, COLOR_GRID))
                x += grid.spacing
            # Horizontal lines
            y = min_y + grid.origin[1] % grid.spacing
            while y <= max_y:
                _send_cmds(self.connector,
                    create_line_cmd((min_x, y), (max_x, y), LAYER_GRID, COLOR_GRID))
                y += grid.spacing
        else:
            rad = math.radians(grid.rotation)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            diag = math.sqrt((max_x - min_x) ** 2 + (max_y - min_y) ** 2)
            cx = (min_x + max_x) / 2
            cy = (min_y + max_y) / 2

            n_lines = int(diag / grid.spacing) + 1
            for i in range(-n_lines, n_lines + 1):
                offset = i * grid.spacing
                p1 = (cx + offset * (-sin_a) - diag * cos_a, cy + offset * cos_a - diag * sin_a)
                p2 = (cx + offset * (-sin_a) + diag * cos_a, cy + offset * cos_a + diag * sin_a)
                _send_cmds(self.connector,
                    create_line_cmd(p1, p2, LAYER_GRID, COLOR_GRID))
                p3 = (cx + offset * cos_a - diag * (-sin_a), cy + offset * sin_a - diag * cos_a)
                p4 = (cx + offset * cos_a + diag * (-sin_a), cy + offset * sin_a + diag * cos_a)
                _send_cmds(self.connector,
                    create_line_cmd(p3, p4, LAYER_GRID, COLOR_GRID))

    def draw_zone(self, zone: "Zone") -> None:
        """Draw zone as closed polyline + label."""
        if not self.connector.is_live:
            return
        _send_cmds(self.connector, create_polyline_cmd(
            points=zone.corners,
            name=zone.name,
            layer=LAYER_ZONES,
            color=COLOR_ZONE,
            closed=True,
        ))
        _send_cmds(self.connector, create_text_cmd(
            text=zone.name,
            position=zone.centroid,
            layer=LAYER_LABELS,
        ))

    def draw_bay(self, bay: "Bay") -> None:
        """Draw bay grid lines between column positions."""
        if not self.connector.is_live:
            return
        gx = bay.gridlines_x
        gy = bay.gridlines_y
        rad = math.radians(bay.rotation)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        ox, oy = bay.origin

        def to_world(lx: float, ly: float) -> tuple[float, float]:
            return (ox + lx * cos_a - ly * sin_a, oy + lx * sin_a + ly * cos_a)

        # Horizontal grid lines
        for y in gy:
            p1 = to_world(gx[0], y)
            p2 = to_world(gx[-1], y)
            _send_cmds(self.connector,
                create_line_cmd(p1, p2, LAYER_BAYS, COLOR_BAY))
        # Vertical grid lines
        for x in gx:
            p1 = to_world(x, gy[0])
            p2 = to_world(x, gy[-1])
            _send_cmds(self.connector,
                create_line_cmd(p1, p2, LAYER_BAYS, COLOR_BAY))

    def draw_columns(self, bay: "Bay") -> None:
        """Draw column squares at each grid intersection."""
        if not self.connector.is_live:
            return
        gx = bay.gridlines_x
        gy = bay.gridlines_y
        rad = math.radians(bay.rotation)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        ox, oy = bay.origin
        half = bay.column_size / 2

        def to_world(lx: float, ly: float) -> tuple[float, float]:
            return (ox + lx * cos_a - ly * sin_a, oy + lx * sin_a + ly * cos_a)

        for x in gx:
            for y in gy:
                corners = [
                    to_world(x - half, y - half),
                    to_world(x + half, y - half),
                    to_world(x + half, y + half),
                    to_world(x - half, y + half),
                ]
                _send_cmds(self.connector, create_polyline_cmd(
                    points=corners,
                    name=f"col_{bay.name}",
                    layer=LAYER_COLUMNS,
                    color=COLOR_COLUMN,
                    closed=True,
                ))

    def draw_corridor(self, bay: "Bay") -> None:
        """Draw corridor rectangle spanning bay width/depth at gridline position."""
        if not self.connector.is_live or not bay.corridor or not bay.corridor.enabled:
            return
        gx = bay.gridlines_x
        gy = bay.gridlines_y
        rad = math.radians(bay.rotation)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        ox, oy = bay.origin
        half_w = bay.corridor.width / 2

        def to_world(lx: float, ly: float) -> tuple[float, float]:
            return (ox + lx * cos_a - ly * sin_a, oy + lx * sin_a + ly * cos_a)

        if bay.corridor.axis == "x":
            # East-west corridor along a y gridline
            pos_idx = min(bay.corridor.position, len(gy) - 1)
            cy = gy[pos_idx]
            corners = [
                to_world(gx[0], cy - half_w),
                to_world(gx[-1], cy - half_w),
                to_world(gx[-1], cy + half_w),
                to_world(gx[0], cy + half_w),
            ]
        else:
            # North-south corridor along an x gridline
            pos_idx = min(bay.corridor.position, len(gx) - 1)
            cx = gx[pos_idx]
            corners = [
                to_world(cx - half_w, gy[0]),
                to_world(cx + half_w, gy[0]),
                to_world(cx + half_w, gy[-1]),
                to_world(cx - half_w, gy[-1]),
            ]

        _send_cmds(self.connector, create_polyline_cmd(
            points=corners,
            name=f"corridor_{bay.name}",
            layer=LAYER_CORRIDORS,
            color=COLOR_CORRIDOR,
            closed=True,
        ))

    def draw_void(self, bay: "Bay") -> None:
        """Draw void rectangle or circle at void center."""
        if not self.connector.is_live or not bay.void:
            return
        rad = math.radians(bay.rotation)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        ox, oy = bay.origin
        vcx, vcy = bay.void.center
        # Transform void center to world coords
        wcx = ox + vcx * cos_a - vcy * sin_a
        wcy = oy + vcx * sin_a + vcy * cos_a

        if bay.void.shape == "circle":
            radius = bay.void.size[0] / 2
            _send_cmds(self.connector, create_circle_cmd(
                center=(wcx, wcy),
                radius=radius,
                layer=LAYER_VOIDS,
                color=COLOR_VOID,
            ))
        else:
            vw, vh = bay.void.size
            half_w, half_h = vw / 2, vh / 2

            def to_world(lx: float, ly: float) -> tuple[float, float]:
                return (ox + lx * cos_a - ly * sin_a, oy + lx * sin_a + ly * cos_a)

            corners = [
                to_world(vcx - half_w, vcy - half_h),
                to_world(vcx + half_w, vcy - half_h),
                to_world(vcx + half_w, vcy + half_h),
                to_world(vcx - half_w, vcy + half_h),
            ]
            _send_cmds(self.connector, create_polyline_cmd(
                points=corners,
                name=f"void_{bay.name}",
                layer=LAYER_VOIDS,
                color=COLOR_VOID,
                closed=True,
            ))

    def clear_all(self) -> None:
        """Remove all TASC objects from Rhino via script.

        Uses execute_rhinoscript to delete objects on TASC layers specifically,
        since RhinoMCP's delete_object only supports id/name/all.
        """
        if not self.connector.is_live:
            return
        script = (
            "import rhinoscriptsyntax as rs\n"
            "for layer in ['TASC_Labels', 'TASC_Zones', 'TASC_Grid', 'TASC_Site', "
            "'TASC_Bays', 'TASC_Columns', 'TASC_Corridors', 'TASC_Voids']:\n"
            "    objs = rs.ObjectsByLayer(layer)\n"
            "    if objs:\n"
            "        rs.DeleteObjects(objs)\n"
        )
        _send_cmds(self.connector, execute_script_cmd(script))

    def redraw(self, model: "TASCModel") -> None:
        """Clear and redraw entire model."""
        self.clear_all()
        self.setup_layers()
        if model.site:
            self.draw_site(model.site)
        if model.grid and model.site:
            self.draw_grid(model.grid, model.site)
        for bay in model.bays:
            self.draw_bay(bay)
            self.draw_columns(bay)
            self.draw_corridor(bay)
            self.draw_void(bay)
        for zone in model.zones:
            self.draw_zone(zone)
