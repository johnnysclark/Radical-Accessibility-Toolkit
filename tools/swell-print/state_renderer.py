# -*- coding: utf-8 -*-
"""
State Renderer — Render state.json to PIAF-ready B&W image  v1.0
=================================================================
Reads the Layout Jig Canonical Model Artifact (state.json) and
draws a high-contrast black-and-white plan at 300 DPI, suitable
for PIAF swell-paper printing.

No Rhino dependency.  Uses Pillow for rasterization.

Draws:  site boundary, column grid, walls (with aperture gaps),
        corridors (dashed), door/window/portal symbols, room hatches,
        void outlines, text labels, braille labels, legend, section cut.

Part of the Radical Accessibility Project — UIUC School of Architecture.

Dependencies:  Pillow (PIL)
"""

import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# Import braille from controller (stdlib)
_here = os.path.dirname(os.path.abspath(__file__))
_controller = os.path.join(os.path.dirname(os.path.dirname(_here)), "controller")
if _controller not in sys.path:
    sys.path.insert(0, _controller)
import braille as _braille

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PAPER_SIZES = {
    "letter":  (8.5, 11.0),
    "tabloid": (11.0, 17.0),
}

DEFAULT_DPI = 300
DEFAULT_MARGIN_IN = 0.5
MIN_LINE_PX = 2  # minimum line width for PIAF readability


# ---------------------------------------------------------------------------
# Coordinate helpers
# ---------------------------------------------------------------------------

def _mm_to_px(mm, dpi=DEFAULT_DPI):
    """Convert millimeters to pixels at given DPI, with minimum floor."""
    return max(MIN_LINE_PX, round(mm * dpi / 25.4))


def _get_spacing_arrays(bay):
    """Compute cumulative gridline positions (local coords, feet)."""
    nx, ny = bay["bays"]
    sx_a = bay.get("spacing_x")
    sy_a = bay.get("spacing_y")
    if sx_a and len(sx_a) == nx:
        cx = [0.0]
        for s in sx_a:
            cx.append(cx[-1] + s)
    else:
        s = bay["spacing"][0]
        cx = [i * s for i in range(nx + 1)]
    if sy_a and len(sy_a) == ny:
        cy = [0.0]
        for s in sy_a:
            cy.append(cy[-1] + s)
    else:
        s = bay["spacing"][1]
        cy = [j * s for j in range(ny + 1)]
    return cx, cy


def _local_to_world(lx, ly, origin, rot_deg):
    """Transform local bay coords to world coords."""
    r = math.radians(rot_deg)
    wx = origin[0] + lx * math.cos(r) - ly * math.sin(r)
    wy = origin[1] + lx * math.sin(r) + ly * math.cos(r)
    return (wx, wy)


def _calc_wall_segments(wall_len, apertures):
    """Return solid wall segments as (start, end) pairs, skipping apertures."""
    if not apertures:
        return [(0.0, wall_len)]
    segments = []
    pos = 0.0
    for ap in apertures:
        cn = ap.get("corner", 0)
        wd = ap.get("width", 3)
        if cn > pos:
            segments.append((pos, cn))
        pos = cn + wd
    if pos < wall_len:
        segments.append((pos, wall_len))
    return segments


# ---------------------------------------------------------------------------
# Renderer class
# ---------------------------------------------------------------------------

class StateRenderer:
    """Renders state.json to a B&W PIL Image for PIAF printing."""

    def __init__(self, state, dpi=DEFAULT_DPI, paper_size="letter",
                 margin_in=DEFAULT_MARGIN_IN):
        self.state = state
        self.dpi = dpi
        self.margin_in = margin_in

        pw, ph = PAPER_SIZES.get(paper_size, PAPER_SIZES["letter"])
        self.paper_w_px = int(pw * dpi)
        self.paper_h_px = int(ph * dpi)
        self.margin_px = int(margin_in * dpi)

        draw_w = self.paper_w_px - 2 * self.margin_px
        draw_h = self.paper_h_px - 2 * self.margin_px

        site_w = state.get("site", {}).get("width", 200)
        site_h = state.get("site", {}).get("height", 200)

        self.scale = min(draw_w / site_w, draw_h / site_h)

        # Style settings
        style = state.get("style", {})
        self.heavy_px = _mm_to_px(style.get("heavy_lineweight_mm", 1.4), dpi)
        self.wall_px = _mm_to_px(style.get("wall_lineweight_mm", 0.25), dpi)
        self.corr_px = _mm_to_px(style.get("corridor_lineweight_mm", 0.35), dpi)
        self.light_px = max(1, round(style.get("light_lineweight_mm", 0.08) * dpi / 25.4))
        self.col_size = style.get("column_size", 1.5)

        self.img = None
        self.draw = None

    def _w2p(self, wx, wy):
        """World coords (feet) → pixel coords on the image."""
        px = self.margin_px + wx * self.scale
        # Flip Y axis (image Y goes down, world Y goes up)
        site_h = self.state.get("site", {}).get("height", 200)
        py = self.margin_px + (site_h - wy) * self.scale
        return (int(round(px)), int(round(py)))

    def _w2p_pair(self, p1, p2):
        """Convert two world points to pixel pairs."""
        return [self._w2p(p1[0], p1[1]), self._w2p(p2[0], p2[1])]

    def _ft_to_px(self, feet):
        """Convert a distance in feet to pixels."""
        return max(1, int(round(feet * self.scale)))

    # -- Drawing primitives --

    def _line(self, p1, p2, width=2):
        """Draw a line between two world points."""
        pp1 = self._w2p(p1[0], p1[1])
        pp2 = self._w2p(p2[0], p2[1])
        self.draw.line([pp1, pp2], fill=0, width=width)

    def _dashed_line(self, p1, p2, width=2, dash_ft=3.0, gap_ft=2.0):
        """Draw a dashed line between two world points."""
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length < 0.01:
            return
        ux, uy = dx / length, dy / length
        dash_len = dash_ft
        gap_len = gap_ft
        pos = 0.0
        drawing = True
        while pos < length:
            seg = dash_len if drawing else gap_len
            end_pos = min(pos + seg, length)
            if drawing:
                s = (p1[0] + ux * pos, p1[1] + uy * pos)
                e = (p1[0] + ux * end_pos, p1[1] + uy * end_pos)
                self._line(s, e, width)
            pos = end_pos
            drawing = not drawing

    def _filled_circle(self, center, radius_ft, fill=0):
        """Draw a filled circle at world coords."""
        r_px = self._ft_to_px(radius_ft)
        cx, cy = self._w2p(center[0], center[1])
        bbox = [cx - r_px, cy - r_px, cx + r_px, cy + r_px]
        self.draw.ellipse(bbox, fill=fill, outline=0)

    def _circle_outline(self, center, radius_ft, width=2):
        """Draw a circle outline at world coords."""
        r_px = self._ft_to_px(radius_ft)
        cx, cy = self._w2p(center[0], center[1])
        bbox = [cx - r_px, cy - r_px, cx + r_px, cy + r_px]
        self.draw.ellipse(bbox, fill=None, outline=0, width=width)

    def _rect_outline(self, p1, p2, width=2):
        """Draw a rectangle outline from two corner world points."""
        pp1 = self._w2p(p1[0], p1[1])
        pp2 = self._w2p(p2[0], p2[1])
        x0 = min(pp1[0], pp2[0])
        y0 = min(pp1[1], pp2[1])
        x1 = max(pp1[0], pp2[0])
        y1 = max(pp1[1], pp2[1])
        self.draw.rectangle([x0, y0, x1, y1], fill=None, outline=0, width=width)

    # -- Layer drawers --

    def _draw_site(self):
        """Draw site boundary rectangle."""
        sw = self.state["site"]["width"]
        sh = self.state["site"]["height"]
        self._rect_outline((0, 0), (sw, sh), width=self.light_px)

    def _draw_columns(self):
        """Draw filled circles at each column position."""
        radius = self.col_size / 2.0
        for name, bay in sorted(self.state.get("bays", {}).items()):
            gt = bay.get("grid_type", "rectangular")
            ox, oy = bay["origin"]
            rot = bay.get("rotation_deg", 0)

            if gt == "rectangular":
                cx_arr, cy_arr = _get_spacing_arrays(bay)
                for x in cx_arr:
                    for y in cy_arr:
                        wp = _local_to_world(x, y, (ox, oy), rot)
                        self._filled_circle(wp, radius)
            else:  # radial
                nr = bay.get("rings", 4)
                rs = bay.get("ring_spacing", 20)
                na = bay.get("arms", 8)
                arc = bay.get("arc_deg", 360)
                arc_start = bay.get("arc_start_deg", 0)
                for ring in range(nr + 1):
                    r = ring * rs
                    if r == 0:
                        self._filled_circle((ox, oy), radius)
                        continue
                    for arm in range(na):
                        angle = arc_start + arc * arm / na
                        a = math.radians(angle)
                        cx = ox + r * math.cos(a)
                        cy_pt = oy + r * math.sin(a)
                        self._filled_circle((cx, cy_pt), radius)

    def _draw_walls(self):
        """Draw wall lines with aperture gaps."""
        for name, bay in sorted(self.state.get("bays", {}).items()):
            if bay.get("grid_type", "rectangular") != "rectangular":
                continue
            w = bay.get("walls", {})
            if not w.get("enabled"):
                continue
            t = w.get("thickness", 0.5)
            half_t = t / 2.0
            ox, oy = bay["origin"]
            rot = bay.get("rotation_deg", 0)
            cx_arr, cy_arr = _get_spacing_arrays(bay)
            aps = bay.get("apertures", [])

            # Horizontal walls (x-axis gridlines)
            for j, y_val in enumerate(cy_arr):
                wall_aps = sorted(
                    [a for a in aps if a.get("axis") == "x" and a.get("gridline") == j],
                    key=lambda a: a.get("corner", 0))
                for s, e in _calc_wall_segments(cx_arr[-1], wall_aps):
                    # Top edge
                    p1 = _local_to_world(s, y_val - half_t, (ox, oy), rot)
                    p2 = _local_to_world(e, y_val - half_t, (ox, oy), rot)
                    self._line(p1, p2, self.wall_px)
                    # Bottom edge
                    p1 = _local_to_world(s, y_val + half_t, (ox, oy), rot)
                    p2 = _local_to_world(e, y_val + half_t, (ox, oy), rot)
                    self._line(p1, p2, self.wall_px)
                # End caps at aperture edges
                for ap in wall_aps:
                    cn = ap.get("corner", 0)
                    wd = ap.get("width", 3)
                    for x_pos in [cn, cn + wd]:
                        p1 = _local_to_world(x_pos, y_val - half_t, (ox, oy), rot)
                        p2 = _local_to_world(x_pos, y_val + half_t, (ox, oy), rot)
                        self._line(p1, p2, self.wall_px)

            # Vertical walls (y-axis gridlines)
            for i, x_val in enumerate(cx_arr):
                wall_aps = sorted(
                    [a for a in aps if a.get("axis") == "y" and a.get("gridline") == i],
                    key=lambda a: a.get("corner", 0))
                for s, e in _calc_wall_segments(cy_arr[-1], wall_aps):
                    p1 = _local_to_world(x_val - half_t, s, (ox, oy), rot)
                    p2 = _local_to_world(x_val - half_t, e, (ox, oy), rot)
                    self._line(p1, p2, self.wall_px)
                    p1 = _local_to_world(x_val + half_t, s, (ox, oy), rot)
                    p2 = _local_to_world(x_val + half_t, e, (ox, oy), rot)
                    self._line(p1, p2, self.wall_px)
                for ap in wall_aps:
                    cn = ap.get("corner", 0)
                    wd = ap.get("width", 3)
                    for y_pos in [cn, cn + wd]:
                        p1 = _local_to_world(x_val - half_t, y_pos, (ox, oy), rot)
                        p2 = _local_to_world(x_val + half_t, y_pos, (ox, oy), rot)
                        self._line(p1, p2, self.wall_px)

    def _draw_door_arc(self, ap, bay):
        """Draw a door arc swing symbol."""
        ox, oy = bay["origin"]
        rot = bay.get("rotation_deg", 0)
        cx_arr, cy_arr = _get_spacing_arrays(bay)
        axis = ap.get("axis", "x")
        gl = ap.get("gridline", 0)
        cn = ap.get("corner", 0)
        wd = ap.get("width", 3)
        hinge = ap.get("hinge", "start")
        swing = ap.get("swing", "positive")
        swing_sign = 1 if swing == "positive" else -1

        if axis == "x":
            y_val = cy_arr[gl] if gl < len(cy_arr) else cy_arr[-1]
            hx = cn if hinge == "start" else cn + wd
            # Arc from open end
            center_w = _local_to_world(hx, y_val, (ox, oy), rot)
            r_px = self._ft_to_px(wd)
            cx_px, cy_px = self._w2p(center_w[0], center_w[1])

            # Draw arc (quarter circle)
            start_angle = 0 if swing_sign > 0 else 270
            end_angle = start_angle + 90
            bbox = [cx_px - r_px, cy_px - r_px, cx_px + r_px, cy_px + r_px]
            self.draw.arc(bbox, start_angle, end_angle, fill=0, width=self.wall_px)
        else:
            x_val = cx_arr[gl] if gl < len(cx_arr) else cx_arr[-1]
            hy = cn if hinge == "start" else cn + wd
            center_w = _local_to_world(x_val, hy, (ox, oy), rot)
            r_px = self._ft_to_px(wd)
            cx_px, cy_px = self._w2p(center_w[0], center_w[1])
            start_angle = 180 if swing_sign > 0 else 90
            end_angle = start_angle + 90
            bbox = [cx_px - r_px, cy_px - r_px, cx_px + r_px, cy_px + r_px]
            self.draw.arc(bbox, start_angle, end_angle, fill=0, width=self.wall_px)

    def _draw_apertures(self):
        """Draw aperture symbols (doors, windows, portals)."""
        for name, bay in sorted(self.state.get("bays", {}).items()):
            if bay.get("grid_type", "rectangular") != "rectangular":
                continue
            if not bay.get("walls", {}).get("enabled"):
                continue
            ox, oy = bay["origin"]
            rot = bay.get("rotation_deg", 0)
            cx_arr, cy_arr = _get_spacing_arrays(bay)

            for ap in bay.get("apertures", []):
                ap_type = ap.get("type", "door")
                if ap_type == "door":
                    self._draw_door_arc(ap, bay)
                elif ap_type == "window":
                    self._draw_window_symbol(ap, bay, cx_arr, cy_arr, ox, oy, rot)
                elif ap_type == "portal":
                    self._draw_portal_symbol(ap, bay, cx_arr, cy_arr, ox, oy, rot)

    def _draw_window_symbol(self, ap, bay, cx_arr, cy_arr, ox, oy, rot):
        """Draw parallel lines for window."""
        axis = ap.get("axis", "x")
        gl = ap.get("gridline", 0)
        cn = ap.get("corner", 0)
        wd = ap.get("width", 3)
        t = bay.get("walls", {}).get("thickness", 0.5)
        ht = t / 2.0
        offset = t * 0.3  # glass line inset

        if axis == "x":
            y_val = cy_arr[gl] if gl < len(cy_arr) else cy_arr[-1]
            # Two parallel glass lines
            for off in [-offset, offset]:
                p1 = _local_to_world(cn, y_val + off, (ox, oy), rot)
                p2 = _local_to_world(cn + wd, y_val + off, (ox, oy), rot)
                self._line(p1, p2, self.wall_px)
        else:
            x_val = cx_arr[gl] if gl < len(cx_arr) else cx_arr[-1]
            for off in [-offset, offset]:
                p1 = _local_to_world(x_val + off, cn, (ox, oy), rot)
                p2 = _local_to_world(x_val + off, cn + wd, (ox, oy), rot)
                self._line(p1, p2, self.wall_px)

    def _draw_portal_symbol(self, ap, bay, cx_arr, cy_arr, ox, oy, rot):
        """Draw bracket marks for portal opening."""
        axis = ap.get("axis", "x")
        gl = ap.get("gridline", 0)
        cn = ap.get("corner", 0)
        wd = ap.get("width", 3)
        t = bay.get("walls", {}).get("thickness", 0.5)
        bracket = t * 1.5

        if axis == "x":
            y_val = cy_arr[gl] if gl < len(cy_arr) else cy_arr[-1]
            for x_off in [cn, cn + wd]:
                for sign in [-1, 1]:
                    p1 = _local_to_world(x_off, y_val + sign * bracket, (ox, oy), rot)
                    p2 = _local_to_world(x_off, y_val, (ox, oy), rot)
                    self._line(p1, p2, self.wall_px)
        else:
            x_val = cx_arr[gl] if gl < len(cx_arr) else cx_arr[-1]
            for y_off in [cn, cn + wd]:
                for sign in [-1, 1]:
                    p1 = _local_to_world(x_val + sign * bracket, y_off, (ox, oy), rot)
                    p2 = _local_to_world(x_val, y_off, (ox, oy), rot)
                    self._line(p1, p2, self.wall_px)

    def _draw_corridors(self):
        """Draw corridor dashed centerlines and boundaries."""
        style = self.state.get("style", {})
        dash_ft = style.get("corridor_dash_len", 3.0)
        gap_ft = style.get("corridor_gap_len", 2.0)

        for name, bay in sorted(self.state.get("bays", {}).items()):
            if bay.get("grid_type", "rectangular") != "rectangular":
                continue
            corr = bay.get("corridor", {})
            if not corr.get("enabled"):
                continue

            ox, oy = bay["origin"]
            rot = bay.get("rotation_deg", 0)
            cx_arr, cy_arr = _get_spacing_arrays(bay)
            axis = corr.get("axis", "x")
            pos = corr.get("position", 1)
            width = corr.get("width", 8.0)
            half_w = width / 2.0

            if axis == "x":
                y_val = cy_arr[pos] if pos < len(cy_arr) else cy_arr[-1]
                span = cx_arr[-1]
                # Centerline (dashed)
                p1 = _local_to_world(0, y_val, (ox, oy), rot)
                p2 = _local_to_world(span, y_val, (ox, oy), rot)
                self._dashed_line(p1, p2, self.corr_px, dash_ft, gap_ft)
                # Boundary lines
                p1 = _local_to_world(0, y_val - half_w, (ox, oy), rot)
                p2 = _local_to_world(span, y_val - half_w, (ox, oy), rot)
                self._dashed_line(p1, p2, max(1, self.corr_px // 2), dash_ft, gap_ft)
                p1 = _local_to_world(0, y_val + half_w, (ox, oy), rot)
                p2 = _local_to_world(span, y_val + half_w, (ox, oy), rot)
                self._dashed_line(p1, p2, max(1, self.corr_px // 2), dash_ft, gap_ft)
            else:
                x_val = cx_arr[pos] if pos < len(cx_arr) else cx_arr[-1]
                span = cy_arr[-1]
                p1 = _local_to_world(x_val, 0, (ox, oy), rot)
                p2 = _local_to_world(x_val, span, (ox, oy), rot)
                self._dashed_line(p1, p2, self.corr_px, dash_ft, gap_ft)
                p1 = _local_to_world(x_val - half_w, 0, (ox, oy), rot)
                p2 = _local_to_world(x_val - half_w, span, (ox, oy), rot)
                self._dashed_line(p1, p2, max(1, self.corr_px // 2), dash_ft, gap_ft)
                p1 = _local_to_world(x_val + half_w, 0, (ox, oy), rot)
                p2 = _local_to_world(x_val + half_w, span, (ox, oy), rot)
                self._dashed_line(p1, p2, max(1, self.corr_px // 2), dash_ft, gap_ft)

    def _draw_hatch_region(self, corners_world, pattern, spacing_ft=2.0):
        """Fill a polygon region with a hatch pattern."""
        if pattern in ("none", None, ""):
            return
        # Convert world corners to pixel coords
        pts = [self._w2p(c[0], c[1]) for c in corners_world]
        if len(pts) < 3:
            return

        # Bounding box in pixels
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)

        spacing_px = max(4, self._ft_to_px(spacing_ft))

        # Create a mask for the polygon
        mask = Image.new('1', self.img.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.polygon(pts, fill=1)

        # Draw pattern lines on a temp image, then composite with mask
        temp = Image.new('1', self.img.size, 1)  # white
        temp_draw = ImageDraw.Draw(temp)

        if pattern == "diagonal":
            for offset in range(-max(x1 - x0, y1 - y0), max(x1 - x0, y1 - y0), spacing_px):
                temp_draw.line([(x0 + offset, y0), (x1 + offset, y1)], fill=0, width=1)
        elif pattern == "crosshatch":
            for offset in range(-max(x1 - x0, y1 - y0), max(x1 - x0, y1 - y0), spacing_px):
                temp_draw.line([(x0 + offset, y0), (x1 + offset, y1)], fill=0, width=1)
                temp_draw.line([(x0 + offset, y1), (x1 + offset, y0)], fill=0, width=1)
        elif pattern == "dots":
            for x in range(x0, x1, spacing_px):
                for y in range(y0, y1, spacing_px):
                    temp_draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=0)
        elif pattern == "horizontal":
            for y in range(y0, y1, spacing_px):
                temp_draw.line([(x0, y), (x1, y)], fill=0, width=1)
        elif pattern == "vertical":
            for x in range(x0, x1, spacing_px):
                temp_draw.line([(x, y0), (x, y1)], fill=0, width=1)
        elif pattern == "solid":
            temp_draw.polygon(pts, fill=0)

        # Apply mask: where mask is 1, use temp (hatched); where 0, keep self.img
        self.img = Image.composite(temp, self.img, mask)
        self.draw = ImageDraw.Draw(self.img)

    def _draw_cell_hatches(self):
        """Draw hatch patterns in named cells."""
        for name, bay in sorted(self.state.get("bays", {}).items()):
            if bay.get("grid_type", "rectangular") != "rectangular":
                continue
            cells = bay.get("cells", {})
            if not cells:
                continue
            ox, oy = bay["origin"]
            rot = bay.get("rotation_deg", 0)
            cx_arr, cy_arr = _get_spacing_arrays(bay)

            for key, cell in cells.items():
                hatch = cell.get("hatch", "none")
                if hatch in ("none", None, ""):
                    continue
                # Parse cell key "col,row"
                try:
                    parts = key.split(",")
                    col, row = int(parts[0]), int(parts[1])
                except (ValueError, IndexError):
                    continue
                if col >= len(cx_arr) - 1 or row >= len(cy_arr) - 1:
                    continue
                # Cell corners in local coords
                x0, x1 = cx_arr[col], cx_arr[col + 1]
                y0, y1 = cy_arr[row], cy_arr[row + 1]
                corners = [
                    _local_to_world(x0, y0, (ox, oy), rot),
                    _local_to_world(x1, y0, (ox, oy), rot),
                    _local_to_world(x1, y1, (ox, oy), rot),
                    _local_to_world(x0, y1, (ox, oy), rot),
                ]
                scale_factor = cell.get("hatch_scale", 1.0)
                self._draw_hatch_region(corners, hatch, spacing_ft=2.0 * scale_factor)

    def _draw_voids(self):
        """Draw void outlines (rectangle or circle)."""
        for name, bay in sorted(self.state.get("bays", {}).items()):
            vc = bay.get("void_center")
            vs = bay.get("void_size", [0, 0])
            if not vc or (vs[0] == 0 and vs[1] == 0):
                continue
            shape = bay.get("void_shape", "rectangle")
            if shape == "circle":
                radius = vs[0] / 2.0
                self._circle_outline(vc, radius, self.light_px)
            else:
                half_w = vs[0] / 2.0
                half_h = vs[1] / 2.0
                p1 = (vc[0] - half_w, vc[1] - half_h)
                p2 = (vc[0] + half_w, vc[1] + half_h)
                self._rect_outline(p1, p2, self.light_px)

    def _draw_labels(self):
        """Draw English and braille labels for each bay."""
        style = self.state.get("style", {})
        label_off = style.get("label_offset", 3.0)

        for name, bay in sorted(self.state.get("bays", {}).items()):
            gt = bay.get("grid_type", "rectangular")
            ox, oy = bay["origin"]
            rot = bay.get("rotation_deg", 0)
            label = bay.get("label", "Bay {}".format(name))
            braille_text = bay.get("braille", "")

            if gt == "rectangular":
                cx_arr, cy_arr = _get_spacing_arrays(bay)
                mid_x = cx_arr[-1] / 2.0
                top_y = cy_arr[-1] + label_off
                label_world = _local_to_world(mid_x, top_y, (ox, oy), rot)
            else:
                outer = bay.get("rings", 4) * bay.get("ring_spacing", 20)
                label_world = (ox, oy + outer + label_off)

            if label:
                px, py = self._w2p(label_world[0], label_world[1])
                # Use default font at appropriate size
                font_h = max(8, self._ft_to_px(style.get("label_text_height", 0.3)))
                try:
                    font = ImageFont.truetype("arial.ttf", font_h)
                except (IOError, OSError):
                    font = ImageFont.load_default()
                self.draw.text((px, py), label, fill=0, font=font, anchor="mt")

            if braille_text:
                # If braille is empty, auto-generate from label
                if not braille_text.strip() and label:
                    braille_text = _braille.to_braille(label)
                brl_off = style.get("braille_text_height", 0.5) * 1.5
                brl_world = _local_to_world(
                    mid_x if gt == "rectangular" else 0,
                    (top_y + brl_off) if gt == "rectangular" else (oy + outer + label_off + brl_off) - oy,
                    (ox, oy), rot)
                px, py = self._w2p(brl_world[0], brl_world[1])
                brl_h = max(10, self._ft_to_px(style.get("braille_text_height", 0.5)))
                try:
                    font = ImageFont.truetype("DejaVuSans.ttf", brl_h)
                except (IOError, OSError):
                    try:
                        font = ImageFont.truetype("arial.ttf", brl_h)
                    except (IOError, OSError):
                        font = ImageFont.load_default()
                self.draw.text((px, py), braille_text, fill=0, font=font, anchor="mt")

    def _draw_section_cut(self):
        """Draw section cut line if defined."""
        sec = self.state.get("section", {})
        axis = sec.get("axis")
        offset = sec.get("offset")
        if not axis or offset is None:
            return
        sw = self.state["site"]["width"]
        sh = self.state["site"]["height"]
        if axis == "x":
            self._dashed_line((0, offset), (sw, offset), self.corr_px, 4.0, 2.0)
        else:
            self._dashed_line((offset, 0), (offset, sh), self.corr_px, 4.0, 2.0)

    def _draw_legend(self):
        """Draw legend box with hatch swatches and labels."""
        legend = self.state.get("legend", {})
        if not legend.get("enabled"):
            return
        # Simplified legend: box in corner with room list
        position = legend.get("position", "bottom-right")
        width_ft = legend.get("width", 40.0)
        padding = legend.get("padding", 3.0)
        row_h = legend.get("row_height", 7.0)
        swatch = legend.get("swatch_size", 5.0)

        # Collect hatched rooms
        rooms = self.state.get("rooms", {})
        hatched = [(k, v) for k, v in sorted(rooms.items())
                   if v.get("hatch_image", "none") != "none"]
        if not hatched:
            return

        sw = self.state["site"]["width"]
        sh = self.state["site"]["height"]
        legend_h = padding * 2 + row_h * (len(hatched) + 1)  # +1 for title

        if "right" in position:
            lx = sw - width_ft - padding
        else:
            lx = padding
        if "bottom" in position:
            ly = padding
        else:
            ly = sh - legend_h - padding

        # Draw legend border
        self._rect_outline((lx, ly), (lx + width_ft, ly + legend_h),
                           _mm_to_px(legend.get("border_weight_mm", 0.5), self.dpi))

        # Title
        title = legend.get("title", "Legend")
        px, py = self._w2p(lx + padding, ly + legend_h - padding)
        try:
            font = ImageFont.truetype("arial.ttf",
                                      max(8, self._ft_to_px(legend.get("text_height", 2.0))))
        except (IOError, OSError):
            font = ImageFont.load_default()
        self.draw.text((px, py), title, fill=0, font=font)

        # Room rows with hatch swatches
        for idx, (rname, rdata) in enumerate(hatched):
            ry = ly + legend_h - padding - row_h * (idx + 2)
            # Hatch swatch
            corners = [
                (lx + padding, ry),
                (lx + padding + swatch, ry),
                (lx + padding + swatch, ry + swatch),
                (lx + padding, ry + swatch),
            ]
            hatch_pat = rdata.get("hatch_image", "none")
            if hatch_pat != "none":
                self._draw_hatch_region(corners, hatch_pat, spacing_ft=1.0)
            self._rect_outline(corners[0], corners[2], 1)
            # Label
            label_text = rdata.get("label", rname)
            lbl_px, lbl_py = self._w2p(lx + padding + swatch + padding, ry + swatch / 2)
            self.draw.text((lbl_px, lbl_py), label_text, fill=0, font=font)

    # -- Main render --

    def render(self):
        """Render the full plan and return a B&W PIL Image."""
        # White background
        self.img = Image.new('1', (self.paper_w_px, self.paper_h_px), 1)
        self.draw = ImageDraw.Draw(self.img)

        # Draw layers in order (back to front)
        self._draw_site()
        self._draw_cell_hatches()
        self._draw_voids()
        self._draw_corridors()
        self._draw_columns()
        self._draw_walls()
        self._draw_apertures()
        self._draw_labels()
        self._draw_section_cut()
        self._draw_legend()

        return self.img


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render(state, dpi=DEFAULT_DPI, paper_size="letter", margin_in=DEFAULT_MARGIN_IN):
    """Render state.json dict to a B&W PIL Image for PIAF printing.

    Args:
        state:     Parsed state.json dict.
        dpi:       Output resolution (default 300).
        paper_size: "letter" or "tabloid".
        margin_in:  Margin in inches.

    Returns:
        PIL.Image in mode '1' (1-bit B&W).
    """
    renderer = StateRenderer(state, dpi=dpi, paper_size=paper_size,
                             margin_in=margin_in)
    return renderer.render()


def render_to_file(state, output_path, **kwargs):
    """Render state to a PNG file.

    Returns:
        Output file path.
    """
    img = render(state, **kwargs)
    img.save(output_path, dpi=(kwargs.get("dpi", DEFAULT_DPI),
                                kwargs.get("dpi", DEFAULT_DPI)))
    return output_path


def density(image):
    """Calculate black pixel density of a 1-bit image.

    Args:
        image: PIL.Image in mode '1'.

    Returns:
        Percentage of black pixels (0-100).
    """
    if image.mode != '1':
        image = image.convert('1')
    total = image.size[0] * image.size[1]
    # In mode '1', 0 is black, 255 is white
    black = sum(1 for px in image.getdata() if px == 0)
    return (black / total) * 100.0
