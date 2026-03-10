# -*- coding: utf-8 -*-
"""
State Renderer — Render state.json to PIAF-ready B&W image  v2.0
=================================================================
Reads the Layout Jig Canonical Model Artifact (state.json) and
draws a high-contrast black-and-white plan at 300 DPI, suitable
for PIAF swell-paper printing.

No Rhino dependency.  Uses Pillow for rasterization.

v2.0: Style profile support via StyleManager.  All hardcoded rendering
values replaced with style.get() lookups.  Paper-absolute measurements
for hatches and labels.  New view types: section, axon, elevation.

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
# Fallback text sizing (used when no StyleManager is provided)
# These match the v1.0 defaults so existing behavior is preserved.
# ---------------------------------------------------------------------------
BRAILLE_FONT_PT = 30    # ~10 mm line height (BANA standard)
TEXT_FONT_PT = 12        # 12 pt English text (~4.2 mm)
LEGEND_TITLE_FONT_PT = 16  # 16 pt legend title (~5.6 mm)
LEGEND_TEXT_FONT_PT = 12   # 12 pt legend labels
LEGEND_BRAILLE_FONT_PT = 30  # BANA standard for legend braille


def _pt_to_px(pt, dpi=300):
    """Convert typographic points to pixels.  1 pt = 1/72 inch."""
    return max(1, int(round(pt * dpi / 72.0)))


def _mm_to_px(mm, dpi=DEFAULT_DPI):
    """Convert millimeters to pixels at given DPI."""
    return max(1, int(round(mm * dpi / 25.4)))


# ---------------------------------------------------------------------------
# Coordinate helpers
# ---------------------------------------------------------------------------

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
                 margin_in=DEFAULT_MARGIN_IN, style_manager=None):
        self.state = state
        self.dpi = dpi
        self.margin_in = margin_in
        self.sm = style_manager

        pw, ph = PAPER_SIZES.get(paper_size, PAPER_SIZES["letter"])
        self.paper_w_px = int(pw * dpi)
        self.paper_h_px = int(ph * dpi)
        self.margin_px = int(margin_in * dpi)

        draw_w = self.paper_w_px - 2 * self.margin_px
        draw_h = self.paper_h_px - 2 * self.margin_px

        site_w = state.get("site", {}).get("width", 200)
        site_h = state.get("site", {}).get("height", 200)

        self.scale = min(draw_w / site_w, draw_h / site_h)

        # Resolve lineweights — from style profile or state.style fallback
        if self.sm:
            # Style profile provides lineweights in points
            # Convert pt -> px:  px = pt * dpi / 72
            self.heavy_px = max(MIN_LINE_PX, _pt_to_px(self.sm.get("lineweights.column", 3.0), dpi))
            self.wall_px = max(MIN_LINE_PX, _pt_to_px(self.sm.get("lineweights.wall_exterior", 2.5), dpi))
            self.wall_int_px = max(1, _pt_to_px(self.sm.get("lineweights.wall_interior", 1.5), dpi))
            self.corr_px = max(1, _pt_to_px(self.sm.get("lineweights.corridor_edge", 1.0), dpi))
            self.corr_dash_px = max(1, _pt_to_px(self.sm.get("lineweights.corridor_dash", 0.8), dpi))
            self.door_swing_px = max(1, _pt_to_px(self.sm.get("lineweights.door_swing", 0.6), dpi))
            self.door_frame_px = max(1, _pt_to_px(self.sm.get("lineweights.door_frame", 0.8), dpi))
            self.window_px = max(1, _pt_to_px(self.sm.get("lineweights.window_line", 0.6), dpi))
            self.portal_px = max(1, _pt_to_px(self.sm.get("lineweights.portal_line", 0.6), dpi))
            self.light_px = max(1, _pt_to_px(self.sm.get("lineweights.grid_line", 0.3), dpi))
            self.section_px = max(MIN_LINE_PX, _pt_to_px(self.sm.get("lineweights.section_cut", 3.5), dpi))
            self.site_px = max(1, _pt_to_px(self.sm.get("lineweights.site_boundary", 2.0), dpi))
            self.hatch_px = max(1, _pt_to_px(self.sm.get("lineweights.hatch_line", 0.4), dpi))
        else:
            # Fallback: read from state.style (v1.0 compat, values in mm)
            style = state.get("style", {})
            self.heavy_px = _mm_to_px(style.get("heavy_lineweight_mm", 1.4), dpi)
            self.wall_px = _mm_to_px(style.get("wall_lineweight_mm", 0.25), dpi)
            self.wall_int_px = self.wall_px
            self.corr_px = _mm_to_px(style.get("corridor_lineweight_mm", 0.35), dpi)
            self.corr_dash_px = self.corr_px
            self.door_swing_px = self.wall_px
            self.door_frame_px = self.wall_px
            self.window_px = self.wall_px
            self.portal_px = self.wall_px
            self.light_px = max(1, round(style.get("light_lineweight_mm", 0.08) * dpi / 25.4))
            self.section_px = self.corr_px
            self.site_px = self.light_px
            self.hatch_px = 1

        self.col_size = state.get("style", {}).get("column_size", 1.5)

        self.img = None
        self.draw = None

    def _w2p(self, wx, wy):
        """World coords (feet) -> pixel coords on the image."""
        px = self.margin_px + wx * self.scale
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
        self._rect_outline((0, 0), (sw, sh), width=self.site_px)

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

            # Determine wall weight: exterior walls use wall_px,
            # interior walls use wall_int_px
            nx, ny = bay["bays"]

            # Horizontal walls (x-axis gridlines)
            for j, y_val in enumerate(cy_arr):
                is_exterior = (j == 0 or j == len(cy_arr) - 1)
                w_px = self.wall_px if is_exterior else self.wall_int_px
                wall_aps = sorted(
                    [a for a in aps if a.get("axis") == "x" and a.get("gridline") == j],
                    key=lambda a: a.get("corner", 0))
                for s, e in _calc_wall_segments(cx_arr[-1], wall_aps):
                    p1 = _local_to_world(s, y_val - half_t, (ox, oy), rot)
                    p2 = _local_to_world(e, y_val - half_t, (ox, oy), rot)
                    self._line(p1, p2, w_px)
                    p1 = _local_to_world(s, y_val + half_t, (ox, oy), rot)
                    p2 = _local_to_world(e, y_val + half_t, (ox, oy), rot)
                    self._line(p1, p2, w_px)
                for ap in wall_aps:
                    cn = ap.get("corner", 0)
                    wd = ap.get("width", 3)
                    for x_pos in [cn, cn + wd]:
                        p1 = _local_to_world(x_pos, y_val - half_t, (ox, oy), rot)
                        p2 = _local_to_world(x_pos, y_val + half_t, (ox, oy), rot)
                        self._line(p1, p2, w_px)

            # Vertical walls (y-axis gridlines)
            for i, x_val in enumerate(cx_arr):
                is_exterior = (i == 0 or i == len(cx_arr) - 1)
                w_px = self.wall_px if is_exterior else self.wall_int_px
                wall_aps = sorted(
                    [a for a in aps if a.get("axis") == "y" and a.get("gridline") == i],
                    key=lambda a: a.get("corner", 0))
                for s, e in _calc_wall_segments(cy_arr[-1], wall_aps):
                    p1 = _local_to_world(x_val - half_t, s, (ox, oy), rot)
                    p2 = _local_to_world(x_val - half_t, e, (ox, oy), rot)
                    self._line(p1, p2, w_px)
                    p1 = _local_to_world(x_val + half_t, s, (ox, oy), rot)
                    p2 = _local_to_world(x_val + half_t, e, (ox, oy), rot)
                    self._line(p1, p2, w_px)
                for ap in wall_aps:
                    cn = ap.get("corner", 0)
                    wd = ap.get("width", 3)
                    for y_pos in [cn, cn + wd]:
                        p1 = _local_to_world(x_val - half_t, y_pos, (ox, oy), rot)
                        p2 = _local_to_world(x_val + half_t, y_pos, (ox, oy), rot)
                        self._line(p1, p2, w_px)

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
            center_w = _local_to_world(hx, y_val, (ox, oy), rot)
            r_px = self._ft_to_px(wd)
            cx_px, cy_px = self._w2p(center_w[0], center_w[1])
            start_angle = 0 if swing_sign > 0 else 270
            end_angle = start_angle + 90
            bbox = [cx_px - r_px, cy_px - r_px, cx_px + r_px, cy_px + r_px]
            self.draw.arc(bbox, start_angle, end_angle, fill=0, width=self.door_swing_px)
        else:
            x_val = cx_arr[gl] if gl < len(cx_arr) else cx_arr[-1]
            hy = cn if hinge == "start" else cn + wd
            center_w = _local_to_world(x_val, hy, (ox, oy), rot)
            r_px = self._ft_to_px(wd)
            cx_px, cy_px = self._w2p(center_w[0], center_w[1])
            start_angle = 180 if swing_sign > 0 else 90
            end_angle = start_angle + 90
            bbox = [cx_px - r_px, cy_px - r_px, cx_px + r_px, cy_px + r_px]
            self.draw.arc(bbox, start_angle, end_angle, fill=0, width=self.door_swing_px)

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
        offset = t * 0.3

        if axis == "x":
            y_val = cy_arr[gl] if gl < len(cy_arr) else cy_arr[-1]
            for off in [-offset, offset]:
                p1 = _local_to_world(cn, y_val + off, (ox, oy), rot)
                p2 = _local_to_world(cn + wd, y_val + off, (ox, oy), rot)
                self._line(p1, p2, self.window_px)
        else:
            x_val = cx_arr[gl] if gl < len(cx_arr) else cx_arr[-1]
            for off in [-offset, offset]:
                p1 = _local_to_world(x_val + off, cn, (ox, oy), rot)
                p2 = _local_to_world(x_val + off, cn + wd, (ox, oy), rot)
                self._line(p1, p2, self.window_px)

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
                    self._line(p1, p2, self.portal_px)
        else:
            x_val = cx_arr[gl] if gl < len(cx_arr) else cx_arr[-1]
            for y_off in [cn, cn + wd]:
                for sign in [-1, 1]:
                    p1 = _local_to_world(x_val + sign * bracket, y_off, (ox, oy), rot)
                    p2 = _local_to_world(x_val, y_off, (ox, oy), rot)
                    self._line(p1, p2, self.portal_px)

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
                p1 = _local_to_world(0, y_val, (ox, oy), rot)
                p2 = _local_to_world(span, y_val, (ox, oy), rot)
                self._dashed_line(p1, p2, self.corr_dash_px, dash_ft, gap_ft)
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
                self._dashed_line(p1, p2, self.corr_dash_px, dash_ft, gap_ft)
                p1 = _local_to_world(x_val - half_w, 0, (ox, oy), rot)
                p2 = _local_to_world(x_val - half_w, span, (ox, oy), rot)
                self._dashed_line(p1, p2, max(1, self.corr_px // 2), dash_ft, gap_ft)
                p1 = _local_to_world(x_val + half_w, 0, (ox, oy), rot)
                p2 = _local_to_world(x_val + half_w, span, (ox, oy), rot)
                self._dashed_line(p1, p2, max(1, self.corr_px // 2), dash_ft, gap_ft)

    def _draw_hatch_region(self, corners_world, pattern, spacing_ft=2.0,
                           hatch_name=None):
        """Fill a polygon region with a hatch pattern.

        If style_manager is available and hatch_name is given, spacing and
        weight are read from the style profile in PAPER-ABSOLUTE units
        (mm on paper, independent of model scale).
        """
        if pattern in ("none", None, ""):
            return
        pts = [self._w2p(c[0], c[1]) for c in corners_world]
        if len(pts) < 3:
            return

        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)

        # Determine spacing and weight from style (paper-absolute) or fallback
        if self.sm and hatch_name:
            hinfo = self.sm.get_hatch_info(hatch_name)
            if hinfo:
                spacing_px = max(4, self.sm.get_hatch_spacing_px(hatch_name, self.dpi))
                line_w = max(1, self.sm.get_hatch_weight_px(hatch_name, self.dpi))
            else:
                spacing_px = max(4, self._ft_to_px(spacing_ft))
                line_w = self.hatch_px
        elif self.sm:
            # Style available but no specific hatch name — use generic pattern
            # Try to find the pattern by name in the style
            hinfo = self.sm.get_hatch_info(pattern)
            if hinfo:
                spacing_px = max(4, self.sm.get_hatch_spacing_px(pattern, self.dpi))
                line_w = max(1, self.sm.get_hatch_weight_px(pattern, self.dpi))
            else:
                spacing_px = max(4, self._ft_to_px(spacing_ft))
                line_w = self.hatch_px
        else:
            spacing_px = max(4, self._ft_to_px(spacing_ft))
            line_w = 1

        # Create polygon mask
        mask = Image.new('1', self.img.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.polygon(pts, fill=1)

        temp = Image.new('1', self.img.size, 1)
        temp_draw = ImageDraw.Draw(temp)

        if pattern == "diagonal":
            for offset in range(-max(x1 - x0, y1 - y0), max(x1 - x0, y1 - y0), spacing_px):
                temp_draw.line([(x0 + offset, y0), (x1 + offset, y1)], fill=0, width=line_w)
        elif pattern == "crosshatch":
            for offset in range(-max(x1 - x0, y1 - y0), max(x1 - x0, y1 - y0), spacing_px):
                temp_draw.line([(x0 + offset, y0), (x1 + offset, y1)], fill=0, width=line_w)
                temp_draw.line([(x0 + offset, y1), (x1 + offset, y0)], fill=0, width=line_w)
        elif pattern == "dots":
            dot_r = 1
            if self.sm:
                hinfo = self.sm.get_hatch_info("dots")
                if hinfo and "radius_mm" in hinfo:
                    dot_r = max(1, _mm_to_px(hinfo["radius_mm"], self.dpi))
            for x in range(x0, x1, spacing_px):
                for y in range(y0, y1, spacing_px):
                    temp_draw.ellipse([x - dot_r, y - dot_r, x + dot_r, y + dot_r], fill=0)
        elif pattern == "horizontal":
            for y in range(y0, y1, spacing_px):
                temp_draw.line([(x0, y), (x1, y)], fill=0, width=line_w)
        elif pattern == "vertical":
            for x in range(x0, x1, spacing_px):
                temp_draw.line([(x, y0), (x, y1)], fill=0, width=line_w)
        elif pattern == "solid":
            temp_draw.polygon(pts, fill=0)
        elif pattern in ("dense_diagonal", "sparse_diagonal"):
            # Treat as diagonal variant
            for offset in range(-max(x1 - x0, y1 - y0), max(x1 - x0, y1 - y0), spacing_px):
                temp_draw.line([(x0 + offset, y0), (x1 + offset, y1)], fill=0, width=line_w)

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
                try:
                    parts = key.split(",")
                    col, row = int(parts[0]), int(parts[1])
                except (ValueError, IndexError):
                    continue
                if col >= len(cx_arr) - 1 or row >= len(cy_arr) - 1:
                    continue
                x0, x1 = cx_arr[col], cx_arr[col + 1]
                y0, y1 = cy_arr[row], cy_arr[row + 1]
                corners = [
                    _local_to_world(x0, y0, (ox, oy), rot),
                    _local_to_world(x1, y0, (ox, oy), rot),
                    _local_to_world(x1, y1, (ox, oy), rot),
                    _local_to_world(x0, y1, (ox, oy), rot),
                ]
                scale_factor = cell.get("hatch_scale", 1.0)
                self._draw_hatch_region(corners, hatch,
                                        spacing_ft=2.0 * scale_factor,
                                        hatch_name=hatch)

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

        # Resolve font sizes from style profile or fallback
        if self.sm:
            text_pt = self.sm.get("labels.bay_label_pt", TEXT_FONT_PT)
            braille_pt = self.sm.get("labels.braille_pt", BRAILLE_FONT_PT)
        else:
            text_pt = TEXT_FONT_PT
            braille_pt = BRAILLE_FONT_PT

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
                font_h = _pt_to_px(text_pt, self.dpi)
                try:
                    font = ImageFont.truetype("arial.ttf", font_h)
                except (IOError, OSError):
                    font = ImageFont.load_default()
                self.draw.text((px, py), label, fill=0, font=font, anchor="mt")

            if braille_text:
                if not braille_text.strip() and label:
                    braille_text = _braille.to_braille(label)
                brl_offset_px = _pt_to_px(braille_pt, self.dpi)
                brl_off_ft = brl_offset_px / self.scale if self.scale > 0 else 1.0
                brl_world = _local_to_world(
                    mid_x if gt == "rectangular" else 0,
                    (top_y + brl_off_ft) if gt == "rectangular" else (oy + outer + label_off + brl_off_ft) - oy,
                    (ox, oy), rot)
                px, py = self._w2p(brl_world[0], brl_world[1])
                brl_h = _pt_to_px(braille_pt, self.dpi)
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
            self._dashed_line((0, offset), (sw, offset), self.section_px, 4.0, 2.0)
        else:
            self._dashed_line((offset, 0), (offset, sh), self.section_px, 4.0, 2.0)

    def _draw_legend(self):
        """Draw legend box with hatch swatches and labels."""
        legend = self.state.get("legend", {})
        if not legend.get("enabled"):
            return

        position = legend.get("position", "bottom-right")
        width_ft = legend.get("width", 40.0)
        padding = legend.get("padding", 3.0)
        row_h = legend.get("row_height", 7.0)
        swatch = legend.get("swatch_size", 5.0)

        # Resolve font sizes
        if self.sm:
            title_pt = self.sm.get("labels.legend_title_pt", LEGEND_TITLE_FONT_PT)
            label_pt = self.sm.get("labels.legend_entry_pt", LEGEND_TEXT_FONT_PT)
        else:
            title_pt = LEGEND_TITLE_FONT_PT
            label_pt = LEGEND_TEXT_FONT_PT

        rooms = self.state.get("rooms", {})
        hatched = [(k, v) for k, v in sorted(rooms.items())
                   if v.get("hatch_image", "none") != "none"]
        if not hatched:
            return

        sw = self.state["site"]["width"]
        sh = self.state["site"]["height"]
        legend_h = padding * 2 + row_h * (len(hatched) + 1)

        if "right" in position:
            lx = sw - width_ft - padding
        else:
            lx = padding
        if "bottom" in position:
            ly = padding
        else:
            ly = sh - legend_h - padding

        self._rect_outline((lx, ly), (lx + width_ft, ly + legend_h),
                           _mm_to_px(legend.get("border_weight_mm", 0.5), self.dpi))

        title = legend.get("title", "Legend")
        px, py = self._w2p(lx + padding, ly + legend_h - padding)
        try:
            title_font = ImageFont.truetype("arial.ttf",
                                            _pt_to_px(title_pt, self.dpi))
        except (IOError, OSError):
            title_font = ImageFont.load_default()
        self.draw.text((px, py), title, fill=0, font=title_font)

        try:
            label_font = ImageFont.truetype("arial.ttf",
                                            _pt_to_px(label_pt, self.dpi))
        except (IOError, OSError):
            label_font = ImageFont.load_default()

        for idx, (rname, rdata) in enumerate(hatched):
            ry = ly + legend_h - padding - row_h * (idx + 2)
            corners = [
                (lx + padding, ry),
                (lx + padding + swatch, ry),
                (lx + padding + swatch, ry + swatch),
                (lx + padding, ry + swatch),
            ]
            hatch_pat = rdata.get("hatch_image", "none")
            if hatch_pat != "none":
                self._draw_hatch_region(corners, hatch_pat, spacing_ft=1.0,
                                        hatch_name=hatch_pat)
            self._rect_outline(corners[0], corners[2], 1)
            label_text = rdata.get("label", rname)
            lbl_px, lbl_py = self._w2p(lx + padding + swatch + padding, ry + swatch / 2)
            self.draw.text((lbl_px, lbl_py), label_text, fill=0, font=label_font)

    # -- Main render --

    def render(self):
        """Render the full plan and return a B&W PIL Image."""
        self.img = Image.new('1', (self.paper_w_px, self.paper_h_px), 1)
        self.draw = ImageDraw.Draw(self.img)

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
# Section Renderer
# ---------------------------------------------------------------------------

class SectionRenderer:
    """Renders a building section cut from state.json."""

    def __init__(self, state, axis, gridline, dpi=DEFAULT_DPI,
                 paper_size="letter", style_manager=None,
                 poche_fill=True, beyond_weight_factor=0.5):
        self.state = state
        self.axis = axis
        self.gridline = gridline
        self.dpi = dpi
        self.sm = style_manager
        self.poche = poche_fill
        self.beyond_factor = beyond_weight_factor

        pw, ph = PAPER_SIZES.get(paper_size, PAPER_SIZES["letter"])
        self.paper_w_px = int(pw * dpi)
        self.paper_h_px = int(ph * dpi)
        self.margin_px = int(0.5 * dpi)

    def render(self):
        """Render section and return B&W PIL Image."""
        img = Image.new('1', (self.paper_w_px, self.paper_h_px), 1)
        draw = ImageDraw.Draw(img)

        draw_w = self.paper_w_px - 2 * self.margin_px
        draw_h = self.paper_h_px - 2 * self.margin_px

        # Collect all bays and compute section geometry
        bays = self.state.get("bays", {})
        site_w = self.state.get("site", {}).get("width", 200)
        site_h = self.state.get("site", {}).get("height", 200)

        # For section: horizontal span = site width (or height),
        # vertical span = max wall height
        max_height = 0
        for name, bay in bays.items():
            h = bay.get("wall_height", 10.0)
            if h > max_height:
                max_height = h

        if max_height == 0:
            max_height = 10.0

        # Determine span along the section
        if self.axis == "x":
            span = site_w
        else:
            span = site_h

        # Scale to fit drawing area
        scale_x = draw_w / span if span > 0 else 1
        scale_y = draw_h / (max_height * 1.2) if max_height > 0 else 1
        scale = min(scale_x, scale_y)

        def to_px(x_world, y_world):
            px = self.margin_px + x_world * scale
            py = self.margin_px + draw_h - y_world * scale
            return (int(round(px)), int(round(py)))

        # Resolve lineweights
        if self.sm:
            cut_w = max(2, _pt_to_px(self.sm.get("lineweights.section_cut", 3.5), self.dpi))
            wall_w = max(1, _pt_to_px(self.sm.get("lineweights.wall_exterior", 2.5), self.dpi))
            beyond_w = max(1, int(wall_w * self.beyond_factor))
            floor_w = max(1, _pt_to_px(self.sm.get("lineweights.wall_interior", 1.5), self.dpi))
        else:
            cut_w = max(2, _mm_to_px(1.4, self.dpi))
            wall_w = max(1, _mm_to_px(0.25, self.dpi))
            beyond_w = max(1, wall_w // 2)
            floor_w = wall_w

        # Draw ground line
        p1 = to_px(0, 0)
        p2 = to_px(span, 0)
        draw.line([p1, p2], fill=0, width=cut_w)

        # For each bay, determine if it is cut by the section plane
        for name, bay in sorted(bays.items()):
            if bay.get("grid_type", "rectangular") != "rectangular":
                continue
            ox, oy = bay["origin"]
            rot = bay.get("rotation_deg", 0)
            cx_arr, cy_arr = _get_spacing_arrays(bay)
            wall_h = bay.get("wall_height", 10.0)
            walls = bay.get("walls", {})
            if not walls.get("enabled"):
                continue

            # Check if the section plane intersects this bay
            # For axis="x", section is at y = cy_arr[gridline] in bay local coords
            # For axis="y", section is at x = cx_arr[gridline]
            if self.axis == "x":
                if self.gridline >= len(cy_arr):
                    continue
                cut_pos = cy_arr[self.gridline]
                # Draw walls perpendicular to cut
                for i, x_val in enumerate(cx_arr):
                    # Transform to world
                    wp = _local_to_world(x_val, cut_pos, (ox, oy), rot)
                    base_x = wp[0] if self.axis == "x" else wp[1]

                    # Wall profile at cut
                    t = walls.get("thickness", 0.5)
                    x_left = base_x - t / 2.0
                    x_right = base_x + t / 2.0

                    # Draw cut wall rectangle (poche)
                    p_bl = to_px(x_left, 0)
                    p_tr = to_px(x_right, wall_h)
                    rect = [min(p_bl[0], p_tr[0]), min(p_bl[1], p_tr[1]),
                            max(p_bl[0], p_tr[0]), max(p_bl[1], p_tr[1])]
                    if self.poche:
                        draw.rectangle(rect, fill=0)
                    else:
                        draw.rectangle(rect, outline=0, width=cut_w)

                # Draw floor and ceiling lines
                bay_start = _local_to_world(cx_arr[0], cut_pos, (ox, oy), rot)
                bay_end = _local_to_world(cx_arr[-1], cut_pos, (ox, oy), rot)
                x_start = bay_start[0]
                x_end = bay_end[0]

                # Floor line
                draw.line([to_px(x_start, 0), to_px(x_end, 0)], fill=0, width=floor_w)
                # Ceiling line
                draw.line([to_px(x_start, wall_h), to_px(x_end, wall_h)],
                          fill=0, width=beyond_w)
            else:
                # axis == "y"
                if self.gridline >= len(cx_arr):
                    continue
                cut_pos = cx_arr[self.gridline]
                for j, y_val in enumerate(cy_arr):
                    wp = _local_to_world(cut_pos, y_val, (ox, oy), rot)
                    base_y = wp[1]

                    t = walls.get("thickness", 0.5)
                    y_left = base_y - t / 2.0
                    y_right = base_y + t / 2.0

                    p_bl = to_px(y_left, 0)
                    p_tr = to_px(y_right, wall_h)
                    rect = [min(p_bl[0], p_tr[0]), min(p_bl[1], p_tr[1]),
                            max(p_bl[0], p_tr[0]), max(p_bl[1], p_tr[1])]
                    if self.poche:
                        draw.rectangle(rect, fill=0)
                    else:
                        draw.rectangle(rect, outline=0, width=cut_w)

                bay_start = _local_to_world(cut_pos, cy_arr[0], (ox, oy), rot)
                bay_end = _local_to_world(cut_pos, cy_arr[-1], (ox, oy), rot)
                y_start = bay_start[1]
                y_end = bay_end[1]

                draw.line([to_px(y_start, 0), to_px(y_end, 0)], fill=0, width=floor_w)
                draw.line([to_px(y_start, wall_h), to_px(y_end, wall_h)],
                          fill=0, width=beyond_w)

        return img


# ---------------------------------------------------------------------------
# Axonometric Renderer
# ---------------------------------------------------------------------------

class AxonRenderer:
    """Renders a parallel axonometric projection from state.json."""

    def __init__(self, state, angle1=30, angle2=60, dpi=DEFAULT_DPI,
                 paper_size="letter", style_manager=None,
                 hidden_line=False, depth_fade=True, depth_fade_min=0.3):
        self.state = state
        self.angle1 = math.radians(angle1)
        self.angle2 = math.radians(angle2)
        self.dpi = dpi
        self.sm = style_manager
        self.hidden_line = hidden_line
        self.depth_fade = depth_fade
        self.depth_fade_min = depth_fade_min

        pw, ph = PAPER_SIZES.get(paper_size, PAPER_SIZES["letter"])
        self.paper_w_px = int(pw * dpi)
        self.paper_h_px = int(ph * dpi)
        self.margin_px = int(0.5 * dpi)

    def _project(self, x, y, z):
        """Apply parallel axonometric projection."""
        a = self.angle1
        b = self.angle2
        px = x * math.cos(a) + y * math.sin(a)
        py = -x * math.sin(a) * math.sin(b) + y * math.cos(a) * math.sin(b) + z * math.cos(b)
        return (px, py)

    def _collect_edges(self):
        """Build 3D wireframe edges from state.json."""
        edges = []  # list of ((x1,y1,z1), (x2,y2,z2), weight_name)
        bays = self.state.get("bays", {})

        for name, bay in sorted(bays.items()):
            if bay.get("grid_type", "rectangular") != "rectangular":
                continue
            ox, oy = bay["origin"]
            rot = bay.get("rotation_deg", 0)
            cx_arr, cy_arr = _get_spacing_arrays(bay)
            wall_h = bay.get("wall_height", 10.0)
            walls = bay.get("walls", {})

            # Column verticals
            for x in cx_arr:
                for y in cy_arr:
                    wp = _local_to_world(x, y, (ox, oy), rot)
                    edges.append(((wp[0], wp[1], 0), (wp[0], wp[1], wall_h), "column"))

            # Floor grid lines
            for x in cx_arr:
                p1 = _local_to_world(x, cy_arr[0], (ox, oy), rot)
                p2 = _local_to_world(x, cy_arr[-1], (ox, oy), rot)
                edges.append(((p1[0], p1[1], 0), (p2[0], p2[1], 0), "grid_line"))
            for y in cy_arr:
                p1 = _local_to_world(cx_arr[0], y, (ox, oy), rot)
                p2 = _local_to_world(cx_arr[-1], y, (ox, oy), rot)
                edges.append(((p1[0], p1[1], 0), (p2[0], p2[1], 0), "grid_line"))

            # Wall edges (if enabled)
            if walls.get("enabled"):
                t = walls.get("thickness", 0.5)
                ht = t / 2.0
                # Bottom and top perimeter
                for z in [0, wall_h]:
                    # Horizontal walls
                    for j in [0, len(cy_arr) - 1]:
                        y_val = cy_arr[j]
                        for off in [-ht, ht]:
                            p1 = _local_to_world(cx_arr[0], y_val + off, (ox, oy), rot)
                            p2 = _local_to_world(cx_arr[-1], y_val + off, (ox, oy), rot)
                            edges.append(((p1[0], p1[1], z), (p2[0], p2[1], z), "wall_exterior"))
                    # Vertical walls
                    for i in [0, len(cx_arr) - 1]:
                        x_val = cx_arr[i]
                        for off in [-ht, ht]:
                            p1 = _local_to_world(x_val + off, cy_arr[0], (ox, oy), rot)
                            p2 = _local_to_world(x_val + off, cy_arr[-1], (ox, oy), rot)
                            edges.append(((p1[0], p1[1], z), (p2[0], p2[1], z), "wall_exterior"))
                # Wall verticals at corners
                for x_val in [cx_arr[0], cx_arr[-1]]:
                    for y_val in [cy_arr[0], cy_arr[-1]]:
                        for off_x in [-ht, ht]:
                            for off_y in [-ht, ht]:
                                wp = _local_to_world(x_val + off_x, y_val + off_y, (ox, oy), rot)
                                edges.append(((wp[0], wp[1], 0), (wp[0], wp[1], wall_h), "wall_exterior"))

        return edges

    def render(self):
        """Render axonometric view and return B&W PIL Image."""
        img = Image.new('1', (self.paper_w_px, self.paper_h_px), 1)
        draw = ImageDraw.Draw(img)

        edges = self._collect_edges()
        if not edges:
            return img

        # Project all edges to 2D
        projected = []
        for (x1, y1, z1), (x2, y2, z2), wname in edges:
            p1 = self._project(x1, y1, z1)
            p2 = self._project(x2, y2, z2)
            depth = (z1 + z2) / 2.0  # average depth for sorting
            projected.append((p1, p2, wname, depth))

        # Find bounds for scaling
        all_x = []
        all_y = []
        for p1, p2, _, _ in projected:
            all_x.extend([p1[0], p2[0]])
            all_y.extend([p1[1], p2[1]])

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        span_x = max_x - min_x or 1
        span_y = max_y - min_y or 1

        draw_w = self.paper_w_px - 2 * self.margin_px
        draw_h = self.paper_h_px - 2 * self.margin_px
        scale = min(draw_w / span_x, draw_h / span_y) * 0.9

        cx = self.margin_px + draw_w / 2
        cy = self.margin_px + draw_h / 2
        mid_x = (min_x + max_x) / 2
        mid_y = (min_y + max_y) / 2

        def to_px(proj_pt):
            px = cx + (proj_pt[0] - mid_x) * scale
            py = cy - (proj_pt[1] - mid_y) * scale
            return (int(round(px)), int(round(py)))

        # Sort by depth for painter's algorithm (back to front)
        max_depth = max(d for _, _, _, d in projected) if projected else 1
        min_depth = min(d for _, _, _, d in projected) if projected else 0
        depth_range = max_depth - min_depth or 1

        projected.sort(key=lambda e: e[3])

        for p1, p2, wname, depth in projected:
            # Resolve lineweight
            if self.sm:
                base_pt = self.sm.get("lineweights.{}".format(wname), 1.0)
                w = max(1, _pt_to_px(base_pt, self.dpi))
            else:
                w = 2

            # Apply depth fading
            if self.depth_fade and depth_range > 0:
                t = (depth - min_depth) / depth_range
                factor = 1.0 - (1.0 - self.depth_fade_min) * (1.0 - t)
                w = max(1, int(w * factor))

            pp1 = to_px(p1)
            pp2 = to_px(p2)
            draw.line([pp1, pp2], fill=0, width=w)

        return img


# ---------------------------------------------------------------------------
# Elevation Renderer
# ---------------------------------------------------------------------------

class ElevationRenderer:
    """Renders an orthographic elevation from state.json."""

    def __init__(self, state, direction, dpi=DEFAULT_DPI,
                 paper_size="letter", style_manager=None):
        self.state = state
        self.direction = direction
        self.dpi = dpi
        self.sm = style_manager

        pw, ph = PAPER_SIZES.get(paper_size, PAPER_SIZES["letter"])
        self.paper_w_px = int(pw * dpi)
        self.paper_h_px = int(ph * dpi)
        self.margin_px = int(0.5 * dpi)

    def render(self):
        """Render elevation and return B&W PIL Image."""
        img = Image.new('1', (self.paper_w_px, self.paper_h_px), 1)
        draw = ImageDraw.Draw(img)

        draw_w = self.paper_w_px - 2 * self.margin_px
        draw_h = self.paper_h_px - 2 * self.margin_px

        bays = self.state.get("bays", {})
        site_w = self.state.get("site", {}).get("width", 200)
        site_h = self.state.get("site", {}).get("height", 200)

        # Determine viewing span based on direction
        if self.direction in ("south", "north"):
            span_h = site_w  # horizontal span is site width (east-west)
        else:
            span_h = site_h  # horizontal span is site height (north-south)

        # Find max wall height
        max_height = 0
        for name, bay in bays.items():
            h = bay.get("wall_height", 10.0)
            if h > max_height:
                max_height = h
        if max_height == 0:
            max_height = 10.0

        scale_x = draw_w / span_h if span_h > 0 else 1
        scale_y = draw_h / (max_height * 1.3) if max_height > 0 else 1
        scale = min(scale_x, scale_y)

        def to_px(horiz, vert):
            px = self.margin_px + horiz * scale
            py = self.margin_px + draw_h - vert * scale
            return (int(round(px)), int(round(py)))

        # Resolve lineweights
        if self.sm:
            wall_w = max(1, _pt_to_px(self.sm.get("lineweights.wall_exterior", 2.5), self.dpi))
            col_w = max(1, _pt_to_px(self.sm.get("lineweights.column", 3.0), self.dpi))
            ground_w = max(2, _pt_to_px(self.sm.get("lineweights.site_boundary", 2.0), self.dpi))
        else:
            wall_w = max(1, _mm_to_px(0.25, self.dpi))
            col_w = max(1, _mm_to_px(1.4, self.dpi))
            ground_w = 2

        # Ground line
        draw.line([to_px(0, 0), to_px(span_h, 0)], fill=0, width=ground_w)

        # Draw each bay as a rectangle on the elevation
        for name, bay in sorted(bays.items()):
            if bay.get("grid_type", "rectangular") != "rectangular":
                continue
            ox, oy = bay["origin"]
            cx_arr, cy_arr = _get_spacing_arrays(bay)
            wall_h = bay.get("wall_height", 10.0)
            walls = bay.get("walls", {})

            if self.direction == "south":
                h_start = ox + cx_arr[0]
                h_end = ox + cx_arr[-1]
            elif self.direction == "north":
                h_start = ox + cx_arr[0]
                h_end = ox + cx_arr[-1]
            elif self.direction == "east":
                h_start = oy + cy_arr[0]
                h_end = oy + cy_arr[-1]
            else:  # west
                h_start = oy + cy_arr[0]
                h_end = oy + cy_arr[-1]

            if walls.get("enabled"):
                # Draw wall outline
                p_bl = to_px(h_start, 0)
                p_br = to_px(h_end, 0)
                p_tl = to_px(h_start, wall_h)
                p_tr = to_px(h_end, wall_h)
                draw.line([p_bl, p_br], fill=0, width=wall_w)
                draw.line([p_br, p_tr], fill=0, width=wall_w)
                draw.line([p_tr, p_tl], fill=0, width=wall_w)
                draw.line([p_tl, p_bl], fill=0, width=wall_w)

            # Draw column verticals
            positions = cx_arr if self.direction in ("south", "north") else cy_arr
            origin_offset = ox if self.direction in ("south", "north") else oy
            for pos in positions:
                h_pos = origin_offset + pos
                draw.line([to_px(h_pos, 0), to_px(h_pos, wall_h)],
                          fill=0, width=max(1, col_w // 2))

        return img


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render(state, dpi=DEFAULT_DPI, paper_size="letter",
           margin_in=DEFAULT_MARGIN_IN, style_manager=None):
    """Render state.json dict to a B&W PIL Image for PIAF printing.

    Args:
        state:         Parsed state.json dict.
        dpi:           Output resolution (default 300).
        paper_size:    "letter" or "tabloid".
        margin_in:     Margin in inches.
        style_manager: Optional StyleManager instance for style profiles.

    Returns:
        PIL.Image in mode '1' (1-bit B&W).
    """
    renderer = StateRenderer(state, dpi=dpi, paper_size=paper_size,
                             margin_in=margin_in, style_manager=style_manager)
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


def render_section(state, axis, gridline, dpi=DEFAULT_DPI,
                   paper_size="letter", style_manager=None,
                   poche_fill=True, beyond_weight_factor=0.5):
    """Render a section cut through the model.

    Returns:
        PIL.Image in mode '1' (1-bit B&W).
    """
    renderer = SectionRenderer(state, axis, gridline, dpi=dpi,
                               paper_size=paper_size,
                               style_manager=style_manager,
                               poche_fill=poche_fill,
                               beyond_weight_factor=beyond_weight_factor)
    return renderer.render()


def render_axon(state, angle1=30, angle2=60, dpi=DEFAULT_DPI,
                paper_size="letter", style_manager=None,
                hidden_line=False, depth_fade=True, depth_fade_min=0.3):
    """Render an axonometric projection.

    Returns:
        PIL.Image in mode '1' (1-bit B&W).
    """
    renderer = AxonRenderer(state, angle1, angle2, dpi=dpi,
                            paper_size=paper_size,
                            style_manager=style_manager,
                            hidden_line=hidden_line,
                            depth_fade=depth_fade,
                            depth_fade_min=depth_fade_min)
    return renderer.render()


def render_elevation(state, direction, dpi=DEFAULT_DPI,
                     paper_size="letter", style_manager=None):
    """Render a building elevation.

    Returns:
        PIL.Image in mode '1' (1-bit B&W).
    """
    renderer = ElevationRenderer(state, direction, dpi=dpi,
                                 paper_size=paper_size,
                                 style_manager=style_manager)
    return renderer.render()


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
    black = sum(1 for px in image.getdata() if px == 0)
    return (black / total) * 100.0
