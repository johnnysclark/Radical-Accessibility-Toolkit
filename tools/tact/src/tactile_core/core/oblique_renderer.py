# -*- coding: utf-8 -*-
"""
Oblique Projection Renderer — Standalone Module
================================================
Renders a cut military oblique (plan oblique) projection from a
Layout Jig state.json dict to a B&W PIL Image for PIAF swell-paper
printing.

The plan (XY) is drawn true — no distortion. Wall heights project
at a configurable angle from the cut plane upward. Walls intersected
by the cut plane are shown as solid poche. Above-cut wall tops
project as lighter lines.

Can be run standalone:

    python oblique_renderer.py state.json [cut_height] [--angle N]
        [--scale N] [--paper letter|tabloid] [--output path.png]

Part of the Radical Accessibility Project — UIUC School of Architecture.

Dependencies:  Pillow (PIL)
"""

import math

from PIL import Image, ImageDraw

import os as _os
import sys as _sys

# Import shared helpers from state_renderer without triggering the
# tactile_core package __init__ (which has heavy optional dependencies).
_core_dir = _os.path.dirname(_os.path.abspath(__file__))
if _core_dir not in _sys.path:
    _sys.path.insert(0, _core_dir)
import state_renderer as _sr  # noqa: E402

PAPER_SIZES = _sr.PAPER_SIZES
DEFAULT_DPI = _sr.DEFAULT_DPI
MIN_LINE_PX = _sr.MIN_LINE_PX
_pt_to_px = _sr._pt_to_px
_mm_to_px = _sr._mm_to_px
_get_spacing_arrays = _sr._get_spacing_arrays
_local_to_world = _sr._local_to_world
_calc_wall_segments = _sr._calc_wall_segments


# ---------------------------------------------------------------------------
# Oblique Projection Renderer (Military / Plan Oblique)
# ---------------------------------------------------------------------------

class ObliqueRenderer:
    """Renders a cut military oblique (plan oblique) projection.

    The plan (XY) is drawn true — no distortion. Wall heights project
    at a 45-degree angle from the cut plane upward. Walls intersected
    by the cut plane are shown as solid poche. Above-cut wall tops
    project as lighter lines.
    """

    def __init__(self, state, cut_height=10.0, z_angle=45, z_scale=1.0,
                 dpi=DEFAULT_DPI, paper_size="letter", style_manager=None):
        self.state = state
        self.cut_height = cut_height
        self.z_angle = math.radians(z_angle)
        self.z_scale = z_scale
        self.dpi = dpi
        self.sm = style_manager

        pw, ph = PAPER_SIZES.get(paper_size, PAPER_SIZES["letter"])
        self.paper_w_px = int(pw * dpi)
        self.paper_h_px = int(ph * dpi)
        self.margin_px = int(0.5 * dpi)

    def _project(self, x, y, z):
        """Military oblique: plan true, Z projects at angle."""
        px = x + z * self.z_scale * math.cos(self.z_angle)
        py = y + z * self.z_scale * math.sin(self.z_angle)
        return (px, py)

    def _collect_wall_data(self):
        """Collect wall segment geometry from state.

        Returns list of dicts, each with:
            p1, p2:  world-coord endpoints of the wall centreline
            half_t:  half-thickness
            axis:    'x' or 'y'
            wall_h:  full wall height
            rot:     rotation in degrees
            origin:  bay origin
            is_ext:  True if exterior wall
        """
        walls = []
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
            wall_h = bay.get("wall_height", 10.0)

            # Horizontal walls (x-axis gridlines)
            for j, y_val in enumerate(cy_arr):
                is_ext = (j == 0 or j == len(cy_arr) - 1)
                wall_aps = sorted(
                    [a for a in aps if a.get("axis") == "x" and a.get("gridline") == j],
                    key=lambda a: a.get("corner", 0))
                for s, e in _calc_wall_segments(cx_arr[-1], wall_aps):
                    p1 = _local_to_world(s, y_val, (ox, oy), rot)
                    p2 = _local_to_world(e, y_val, (ox, oy), rot)
                    walls.append({
                        "p1": p1, "p2": p2, "half_t": half_t,
                        "axis": "x", "wall_h": wall_h, "rot": rot,
                        "origin": (ox, oy), "is_ext": is_ext,
                        "y_val": y_val, "s": s, "e": e,
                    })

            # Vertical walls (y-axis gridlines)
            for i, x_val in enumerate(cx_arr):
                is_ext = (i == 0 or i == len(cx_arr) - 1)
                wall_aps = sorted(
                    [a for a in aps if a.get("axis") == "y" and a.get("gridline") == i],
                    key=lambda a: a.get("corner", 0))
                for s, e in _calc_wall_segments(cy_arr[-1], wall_aps):
                    p1 = _local_to_world(x_val, s, (ox, oy), rot)
                    p2 = _local_to_world(x_val, e, (ox, oy), rot)
                    walls.append({
                        "p1": p1, "p2": p2, "half_t": half_t,
                        "axis": "y", "wall_h": wall_h, "rot": rot,
                        "origin": (ox, oy), "is_ext": is_ext,
                        "x_val": x_val, "s": s, "e": e,
                    })

        return walls

    def render(self):
        """Render cut oblique projection and return B&W PIL Image."""
        img = Image.new('1', (self.paper_w_px, self.paper_h_px), 1)
        draw = ImageDraw.Draw(img)

        walls = self._collect_wall_data()
        if not walls:
            return img

        # Determine bounding box including projected wall tops
        all_pts = []
        for w in walls:
            for p in [w["p1"], w["p2"]]:
                # Ground-level point
                all_pts.append(self._project(p[0], p[1], 0))
                # Projected wall top (above cut)
                above = w["wall_h"] - self.cut_height
                if above > 0:
                    all_pts.append(self._project(p[0], p[1], above))

        # Add column positions
        for name, bay in self.state.get("bays", {}).items():
            if bay.get("grid_type") != "rectangular":
                continue
            ox, oy = bay["origin"]
            rot = bay.get("rotation_deg", 0)
            cx_arr, cy_arr = _get_spacing_arrays(bay)
            for x in cx_arr:
                for y in cy_arr:
                    wp = _local_to_world(x, y, (ox, oy), rot)
                    all_pts.append((wp[0], wp[1]))

        if not all_pts:
            return img

        xs = [p[0] for p in all_pts]
        ys = [p[1] for p in all_pts]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max_x - min_x or 1
        span_y = max_y - min_y or 1

        draw_w = self.paper_w_px - 2 * self.margin_px
        draw_h = self.paper_h_px - 2 * self.margin_px
        scale = min(draw_w / span_x, draw_h / span_y) * 0.85

        cx = self.margin_px + draw_w / 2
        cy = self.margin_px + draw_h / 2
        mid_x = (min_x + max_x) / 2
        mid_y = (min_y + max_y) / 2

        def to_px(proj_pt):
            px = cx + (proj_pt[0] - mid_x) * scale
            py = cy - (proj_pt[1] - mid_y) * scale
            return (int(round(px)), int(round(py)))

        def world_to_px(wx, wy):
            proj = self._project(wx, wy, 0)
            return to_px(proj)

        def ft_to_px(feet):
            return max(1, int(round(abs(feet) * scale)))

        # Resolve lineweights
        if self.sm:
            wall_w = max(MIN_LINE_PX, _pt_to_px(self.sm.get("lineweights.wall_exterior", 2.5), self.dpi))
            wall_int_w = max(1, _pt_to_px(self.sm.get("lineweights.wall_interior", 1.5), self.dpi))
            col_w = max(MIN_LINE_PX, _pt_to_px(self.sm.get("lineweights.column", 3.0), self.dpi))
            proj_w = max(1, _pt_to_px(self.sm.get("lineweights.grid_line", 0.3), self.dpi))
        else:
            wall_w = max(MIN_LINE_PX, _mm_to_px(0.8, self.dpi))
            wall_int_w = max(1, _mm_to_px(0.5, self.dpi))
            col_w = max(MIN_LINE_PX, _mm_to_px(1.0, self.dpi))
            proj_w = max(1, _mm_to_px(0.2, self.dpi))

        # -- Layer 1: Above-cut projection (light lines) --
        for w in walls:
            above = w["wall_h"] - self.cut_height
            if above <= 0:
                continue
            ht = w["half_t"]
            ox, oy = w["origin"]
            rot = w["rot"]

            if w["axis"] == "x":
                y_val = w["y_val"]
                s, e = w["s"], w["e"]
                # Four corners of wall top, projected from cut_height
                corners_base = [
                    _local_to_world(s, y_val - ht, (ox, oy), rot),
                    _local_to_world(e, y_val - ht, (ox, oy), rot),
                    _local_to_world(e, y_val + ht, (ox, oy), rot),
                    _local_to_world(s, y_val + ht, (ox, oy), rot),
                ]
            else:
                x_val = w["x_val"]
                s, e = w["s"], w["e"]
                corners_base = [
                    _local_to_world(x_val - ht, s, (ox, oy), rot),
                    _local_to_world(x_val - ht, e, (ox, oy), rot),
                    _local_to_world(x_val + ht, e, (ox, oy), rot),
                    _local_to_world(x_val + ht, s, (ox, oy), rot),
                ]

            # Project top corners at full wall height above cut
            top_pts = [to_px(self._project(c[0], c[1], above)) for c in corners_base]
            # Draw projected top rectangle outline
            for i in range(4):
                draw.line([top_pts[i], top_pts[(i + 1) % 4]], fill=0, width=proj_w)

            # Draw vertical projection lines from cut to top at corners
            base_pts = [to_px(self._project(c[0], c[1], 0)) for c in corners_base]
            for i in range(4):
                draw.line([base_pts[i], top_pts[i]], fill=0, width=proj_w)

        # -- Layer 2: Cut plane poche (filled walls) --
        for w in walls:
            if w["wall_h"] < self.cut_height:
                continue  # wall doesn't reach cut — skip poche
            ht = w["half_t"]
            ox, oy = w["origin"]
            rot = w["rot"]
            lw = wall_w if w["is_ext"] else wall_int_w

            if w["axis"] == "x":
                y_val = w["y_val"]
                s, e = w["s"], w["e"]
                corners = [
                    _local_to_world(s, y_val - ht, (ox, oy), rot),
                    _local_to_world(e, y_val - ht, (ox, oy), rot),
                    _local_to_world(e, y_val + ht, (ox, oy), rot),
                    _local_to_world(s, y_val + ht, (ox, oy), rot),
                ]
            else:
                x_val = w["x_val"]
                s, e = w["s"], w["e"]
                corners = [
                    _local_to_world(x_val - ht, s, (ox, oy), rot),
                    _local_to_world(x_val - ht, e, (ox, oy), rot),
                    _local_to_world(x_val + ht, e, (ox, oy), rot),
                    _local_to_world(x_val + ht, s, (ox, oy), rot),
                ]

            px_corners = [world_to_px(c[0], c[1]) for c in corners]
            # Fill poche
            draw.polygon(px_corners, fill=0)

        # -- Layer 3: Below-cut elements (columns) --
        col_size = self.state.get("style", {}).get("column_size", 1.5)
        for name, bay in sorted(self.state.get("bays", {}).items()):
            if bay.get("grid_type") != "rectangular":
                continue
            ox, oy = bay["origin"]
            rot = bay.get("rotation_deg", 0)
            cx_arr, cy_arr = _get_spacing_arrays(bay)
            for x in cx_arr:
                for y in cy_arr:
                    wp = _local_to_world(x, y, (ox, oy), rot)
                    cpx, cpy = world_to_px(wp[0], wp[1])
                    r = ft_to_px(col_size / 2.0)
                    bbox = [cpx - r, cpy - r, cpx + r, cpy + r]
                    draw.ellipse(bbox, fill=0)

        return img


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_oblique(state, cut_height=10.0, z_angle=45, z_scale=1.0,
                   dpi=DEFAULT_DPI, paper_size="letter", style_manager=None):
    """Render a cut military oblique (plan oblique) projection.

    The plan (XY) is drawn true. Wall heights project at z_angle.
    Walls cut at cut_height show solid poche; above-cut tops project
    as lighter lines.

    Args:
        state:         Parsed state.json dict.
        cut_height:    Height of the section cut plane (feet).
        z_angle:       Projection angle for Z axis in degrees (default 45).
        z_scale:       Foreshortening of Z axis (1.0 = military, 0.5 = cabinet).
        dpi:           Output resolution (default 300).
        paper_size:    "letter" or "tabloid".
        style_manager: Optional StyleManager instance.

    Returns:
        PIL.Image in mode '1' (1-bit B&W).
    """
    renderer = ObliqueRenderer(state, cut_height=cut_height,
                                z_angle=z_angle, z_scale=z_scale,
                                dpi=dpi, paper_size=paper_size,
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


# ---------------------------------------------------------------------------
# Standalone CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    import os
    import sys

    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("OK: Usage: python oblique_renderer.py STATE_JSON [CUT_HEIGHT]")
        print("  Options:")
        print("    --angle N      Z projection angle in degrees (default 45)")
        print("    --scale N      Z foreshortening (1.0=military, 0.5=cabinet)")
        print("    --paper SIZE   letter or tabloid (default letter)")
        print("    --output PATH  output PNG path (default oblique.png)")
        print("    --dpi N        output resolution (default 300)")
        print("READY:")
        sys.exit(0)

    state_path = args[0]
    cut_height = None
    z_angle = 45.0
    z_scale = 1.0
    paper = "letter"
    output = None
    dpi = 300

    i = 1
    positional = []
    while i < len(args):
        if args[i] == "--angle" and i + 1 < len(args):
            z_angle = float(args[i + 1])
            i += 2
        elif args[i] == "--scale" and i + 1 < len(args):
            z_scale = float(args[i + 1])
            i += 2
        elif args[i] == "--paper" and i + 1 < len(args):
            paper = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output = args[i + 1]
            i += 2
        elif args[i] == "--dpi" and i + 1 < len(args):
            dpi = int(args[i + 1])
            i += 2
        elif not args[i].startswith("--"):
            positional.append(args[i])
            i += 1
        else:
            i += 1

    if positional:
        try:
            cut_height = float(positional[0])
        except ValueError:
            pass

    if not os.path.isfile(state_path):
        print("ERROR: File not found: {}".format(state_path))
        sys.exit(1)

    with open(state_path, "r") as f:
        state = json.load(f)

    if cut_height is None:
        cut_height = state.get("tactile3d", {}).get("cut_height", 10.0)

    if output is None:
        suffix = "_cabinet" if z_scale < 1.0 else ""
        output = "oblique{}.png".format(suffix)

    img = render_oblique(state, cut_height=cut_height, z_angle=z_angle,
                         z_scale=z_scale, dpi=dpi, paper_size=paper)
    img.save(output, dpi=(dpi, dpi))

    d = density(img)
    mode = "military" if z_scale >= 1.0 else "cabinet"
    print("OK: Rendered {} ({} oblique, cut at {:.0f} ft, density {:.1f}%)".format(
        output, mode, cut_height, d))
    print("READY:")
