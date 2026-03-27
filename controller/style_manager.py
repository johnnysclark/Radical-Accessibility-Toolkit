# -*- coding: utf-8 -*-
"""
Style Manager — PIAF Style Profiles for Tactile Rendering  v1.0
=================================================================
Manages named style profiles that control every rendering property
of the PIAF tactile output pipeline: lineweights, hatch patterns,
label sizes, page layout, and density management.

A style profile is a JSON file in controller/styles/.  The "working"
profile ships as the default.  All hardcoded rendering values in the
renderer are replaced with style.get() lookups.

Part of the Radical Accessibility Project — UIUC School of Architecture.
"""

import copy
import json
import os


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STYLES_DIR = os.path.join(_HERE, "styles")

# Built-in hatch names that cannot be removed
BUILTIN_HATCHES = frozenset([
    "diagonal", "crosshatch", "horizontal", "vertical",
    "dots", "dense_diagonal", "sparse_diagonal",
])

# Required top-level keys in a style profile
REQUIRED_SECTIONS = ("name", "description", "lineweights", "hatches",
                     "labels", "layout", "density", "drawing_overrides")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _atomic_write(path, text):
    """Write text to path via tmp + replace for crash safety."""
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _deep_get(d, key_path):
    """Retrieve a nested value using dot notation.

    >>> _deep_get({"a": {"b": 3}}, "a.b")
    3
    """
    keys = key_path.split(".")
    current = d
    for k in keys:
        if isinstance(current, dict):
            if k not in current:
                raise KeyError("Key not found: '{}'".format(key_path))
            current = current[k]
        elif isinstance(current, list):
            try:
                current = current[int(k)]
            except (ValueError, IndexError):
                raise KeyError("Key not found: '{}'".format(key_path))
        else:
            raise KeyError("Key not found: '{}'".format(key_path))
    return current


def _deep_set(d, key_path, value):
    """Set a nested value using dot notation.  Returns old value."""
    keys = key_path.split(".")
    current = d
    for k in keys[:-1]:
        if isinstance(current, dict):
            if k not in current:
                current[k] = {}
            current = current[k]
        elif isinstance(current, list):
            current = current[int(k)]
        else:
            raise KeyError("Cannot traverse into: '{}'".format(k))
    last = keys[-1]
    old = current.get(last) if isinstance(current, dict) else None
    current[last] = value
    return old


def _coerce_value(raw):
    """Attempt to parse a string as a JSON value, fall back to string."""
    if isinstance(raw, (int, float, bool, list, dict)):
        return raw
    raw_s = str(raw).strip()
    # Try JSON parse
    try:
        return json.loads(raw_s)
    except (json.JSONDecodeError, ValueError):
        pass
    # Try float
    try:
        v = float(raw_s)
        return int(v) if v == int(v) else v
    except ValueError:
        pass
    # Return as string
    return raw_s


# ---------------------------------------------------------------------------
# StyleManager
# ---------------------------------------------------------------------------

class StyleManager:
    """Manages PIAF style profiles for tactile rendering."""

    def __init__(self, styles_dir=None):
        self._styles_dir = styles_dir or DEFAULT_STYLES_DIR
        self._profiles = {}        # name -> dict
        self._saved = {}           # name -> dict (last-saved copy)
        self._active_name = None
        self._load_all()
        if not self._profiles:
            self._generate_defaults()
            self._load_all()
        if "working" in self._profiles:
            self._active_name = "working"
        elif self._profiles:
            self._active_name = sorted(self._profiles.keys())[0]

    # ── Loading ──

    def _load_all(self):
        """Load all .json files from the styles directory."""
        if not os.path.isdir(self._styles_dir):
            os.makedirs(self._styles_dir, exist_ok=True)
            return
        for fname in sorted(os.listdir(self._styles_dir)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(self._styles_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                name = data.get("name", os.path.splitext(fname)[0])
                self._profiles[name] = data
                self._saved[name] = copy.deepcopy(data)
            except (json.JSONDecodeError, IOError):
                continue

    def _generate_defaults(self):
        """Generate default style files if none exist.

        This is a safety net — normally the JSON files ship with the repo.
        """
        # Minimal working style inline
        working = {
            "name": "working",
            "description": "Everyday design iteration. Medium weights, compact layout.",
            "lineweights": {
                "column": 3.0, "wall_exterior": 2.5, "wall_interior": 1.5,
                "corridor_edge": 1.0, "corridor_dash": 0.8,
                "door_swing": 0.6, "door_frame": 0.8,
                "window_line": 0.6, "portal_line": 0.6,
                "grid_line": 0.3, "section_cut": 3.5, "section_beyond": 0.8,
                "hatch_line": 0.4, "dimension_line": 0.3, "leader_line": 0.3,
                "site_boundary": 2.0, "north_arrow": 1.5,
            },
            "hatches": {
                "diagonal": {"spacing_mm": 8.0, "angle_deg": 45, "weight_pt": 0.4},
                "crosshatch": {"spacing_mm": 8.0, "angle_deg": [45, 135], "weight_pt": 0.4},
                "horizontal": {"spacing_mm": 6.0, "angle_deg": 0, "weight_pt": 0.4},
                "vertical": {"spacing_mm": 6.0, "angle_deg": 90, "weight_pt": 0.4},
                "dots": {"spacing_mm": 5.0, "radius_mm": 1.0, "filled": True},
                "dense_diagonal": {"spacing_mm": 5.0, "angle_deg": 45, "weight_pt": 0.5},
                "sparse_diagonal": {"spacing_mm": 12.0, "angle_deg": 45, "weight_pt": 0.3},
            },
            "labels": {
                "braille_pt": 30, "room_name_pt": 12, "dimension_pt": 8,
                "legend_title_pt": 14, "legend_entry_pt": 10,
                "bay_label_pt": 14, "grid_label_pt": 10,
            },
            "layout": {
                "paper": "letter", "orientation": "landscape",
                "margin_inches": 0.5, "scale": "auto",
                "title_block": True, "legend": True, "north_arrow": True,
                "grid_labels": True, "braille_labels": True,
                "english_labels": True, "dimensions": False,
                "section_marks": True,
            },
            "density": {
                "target_percent": 30, "warning_percent": 40,
                "reject_percent": 45, "auto_adjust": True,
                "priority": ["column", "wall_exterior", "wall_interior",
                             "corridor_edge", "section_cut", "door_frame",
                             "labels", "hatches", "grid_line"],
            },
            "drawing_overrides": {
                "plan": {},
                "section": {"poche_fill": True, "beyond_weight_factor": 0.5,
                            "hatches_beyond_cut": False},
                "axon": {"hatches": False, "depth_fade": True,
                         "depth_fade_min_factor": 0.3, "hidden_line": True,
                         "projection_angle": [30, 60]},
                "elevation": {"hatches": True, "depth_fade": False},
            },
        }
        fpath = os.path.join(self._styles_dir, "working.json")
        _atomic_write(fpath, json.dumps(working, indent=2, sort_keys=False))

    # ── Active style access ──

    @property
    def active(self):
        """Return the active style profile dict."""
        if self._active_name and self._active_name in self._profiles:
            return self._profiles[self._active_name]
        return {}

    @property
    def active_name(self):
        return self._active_name

    def get(self, key_path, default=None):
        """Get a value from the active style using dot notation.

        style.get("lineweights.column") -> 3.0
        style.get("hatches.diagonal.spacing_mm") -> 8.0
        style.get("layout.paper") -> "letter"
        """
        try:
            return _deep_get(self.active, key_path)
        except (KeyError, IndexError):
            return default

    def set(self, key_path, value):
        """Set a value in the active style.  Does NOT auto-save.

        Returns (new_value, old_value) for confirmation message.
        """
        value = _coerce_value(value)
        old = _deep_set(self.active, key_path, value)
        return (value, old)

    # ── Profile management ──

    def use(self, name):
        """Switch active style.  Returns (name, description)."""
        if name not in self._profiles:
            available = ", ".join(sorted(self._profiles.keys()))
            raise ValueError(
                "Style '{}' not found. Available: {}".format(name, available))
        self._active_name = name
        desc = self._profiles[name].get("description", "")
        return (name, desc)

    def save(self, name=None):
        """Save active style to disk.  If name given, save-as to new file.

        Returns the file path written.
        """
        if name:
            # Save-as: copy active profile with new name
            data = copy.deepcopy(self.active)
            data["name"] = name
            self._profiles[name] = data
            self._active_name = name
        else:
            name = self._active_name

        fpath = os.path.join(self._styles_dir, "{}.json".format(name))
        text = json.dumps(self._profiles[name], indent=2, sort_keys=False)
        _atomic_write(fpath, text)
        self._saved[name] = copy.deepcopy(self._profiles[name])
        return fpath

    def reset(self):
        """Reset active style to its last-saved state.

        Returns the style name.
        """
        name = self._active_name
        if name in self._saved:
            self._profiles[name] = copy.deepcopy(self._saved[name])
        return name

    def list_styles(self):
        """Return list of (name, description, is_active) tuples."""
        result = []
        for name in sorted(self._profiles.keys()):
            desc = self._profiles[name].get("description", "")
            active = (name == self._active_name)
            result.append((name, desc, active))
        return result

    def show(self, category=None):
        """Return formatted string showing style values.

        If category given (lineweights, hatches, labels, layout, density),
        show only that category.  Otherwise show summary.
        """
        profile = self.active
        name = self._active_name
        lines = []

        if category:
            cat = category.lower()
            if cat not in profile:
                return "ERROR: Unknown category '{}'. Options: lineweights, hatches, labels, layout, density.".format(cat)
            data = profile[cat]
            lines.append("{} (active style: {}):".format(cat.title(), name))
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, dict):
                        sub_parts = []
                        for sk, sv in v.items():
                            sub_parts.append("{} {}".format(sk, sv))
                        lines.append("  {} : {}".format(k, ", ".join(sub_parts)))
                    else:
                        unit = ""
                        if cat == "lineweights":
                            unit = " pt"
                        elif cat == "labels" and str(k).endswith("_pt"):
                            unit = " pt"
                        lines.append("  {} = {}{}".format(k, v, unit))
            else:
                lines.append("  {}".format(data))
        else:
            lines.append("Active style: {}".format(name))
            lines.append("  {}".format(profile.get("description", "")))
            # Summary of each section
            lw = profile.get("lineweights", {})
            lines.append("  Lineweights: {} entries, column={} pt, wall_exterior={} pt".format(
                len(lw), lw.get("column", "?"), lw.get("wall_exterior", "?")))
            ht = profile.get("hatches", {})
            lines.append("  Hatches: {} patterns".format(len(ht)))
            lb = profile.get("labels", {})
            lines.append("  Labels: braille={} pt, room_name={} pt".format(
                lb.get("braille_pt", "?"), lb.get("room_name_pt", "?")))
            lo = profile.get("layout", {})
            lines.append("  Layout: {} {}, margin {} in".format(
                lo.get("paper", "?"), lo.get("orientation", "?"),
                lo.get("margin_inches", "?")))
            dn = profile.get("density", {})
            lines.append("  Density: target {}%, warning {}%, reject {}%".format(
                dn.get("target_percent", "?"), dn.get("warning_percent", "?"),
                dn.get("reject_percent", "?")))

        return "\n".join(lines)

    # ── Hatch management ──

    def add_hatch(self, name, spacing_mm, angle_deg, weight_pt=0.4,
                  radius_mm=None, filled=False):
        """Add a custom hatch pattern to the active style."""
        hatches = self.active.get("hatches", {})
        entry = {
            "spacing_mm": float(spacing_mm),
            "angle_deg": angle_deg,
            "weight_pt": float(weight_pt),
        }
        if radius_mm is not None:
            entry["radius_mm"] = float(radius_mm)
            entry["filled"] = filled
        hatches[name] = entry
        self.active["hatches"] = hatches
        return entry

    def remove_hatch(self, name):
        """Remove a custom hatch pattern.  Cannot remove built-ins."""
        if name in BUILTIN_HATCHES:
            raise ValueError(
                "Cannot remove built-in hatch '{}'. "
                "Built-in hatches: {}".format(name, ", ".join(sorted(BUILTIN_HATCHES))))
        hatches = self.active.get("hatches", {})
        if name not in hatches:
            raise ValueError("Hatch '{}' not found.".format(name))
        del hatches[name]
        return name

    # ── Conversion helpers (paper-absolute math) ──

    @staticmethod
    def pt_to_px(pt, dpi=300):
        """Convert typographic points to pixels.  1 pt = 1/72 inch."""
        return max(1, int(round(pt * dpi / 72.0)))

    @staticmethod
    def mm_to_px(mm, dpi=300):
        """Convert millimeters to pixels at given DPI."""
        return max(1, int(round(mm * dpi / 25.4)))

    def get_lineweight_px(self, element, dpi=300):
        """Get a lineweight in pixels for a named element.

        element: key in lineweights dict (e.g. "column", "wall_exterior")
        """
        pt = self.get("lineweights.{}".format(element), 1.0)
        return self.pt_to_px(pt, dpi)

    def get_hatch_spacing_px(self, hatch_name, dpi=300):
        """Get hatch spacing in pixels (paper-absolute conversion).

        spacing_px = spacing_mm * (dpi / 25.4)
        """
        mm = self.get("hatches.{}.spacing_mm".format(hatch_name), 8.0)
        return self.mm_to_px(mm, dpi)

    def get_hatch_weight_px(self, hatch_name, dpi=300):
        """Get hatch line weight in pixels."""
        pt = self.get("hatches.{}.weight_pt".format(hatch_name), 0.4)
        return self.pt_to_px(pt, dpi)

    def get_hatch_info(self, hatch_name):
        """Get full hatch dict for a named pattern, or None."""
        return self.get("hatches.{}".format(hatch_name))

    def get_label_px(self, label_key, dpi=300):
        """Get a label size in pixels.  label_key: e.g. 'braille_pt'."""
        pt = self.get("labels.{}".format(label_key), 12)
        return self.pt_to_px(pt, dpi)

    # ── Test swatch ──

    def generate_test_swatch(self, output_path, dpi=300):
        """Render a calibration sheet showing all lineweights and hatches.

        The test swatch contains:
        - Horizontal bars at every lineweight from 0.3pt to 4.0pt, labeled
        - A sample square of every hatch pattern, labeled
        - A density gradient strip from 10% to 50% black
        - The active style name and date

        Output is a black-and-white image ready for PIAF printing.
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            raise ImportError("Pillow is required for test swatch generation.")

        from datetime import datetime

        paper = self.get("layout.paper", "letter")
        paper_sizes = {"letter": (8.5, 11.0), "tabloid": (11.0, 17.0)}
        pw, ph = paper_sizes.get(paper, paper_sizes["letter"])
        w_px = int(pw * dpi)
        h_px = int(ph * dpi)
        margin = int(0.5 * dpi)

        img = Image.new('1', (w_px, h_px), 1)
        draw = ImageDraw.Draw(img)

        # Font
        try:
            font = ImageFont.truetype("arial.ttf", self.pt_to_px(10, dpi))
            font_sm = ImageFont.truetype("arial.ttf", self.pt_to_px(8, dpi))
            font_lg = ImageFont.truetype("arial.ttf", self.pt_to_px(14, dpi))
        except (IOError, OSError):
            font = ImageFont.load_default()
            font_sm = font
            font_lg = font

        x = margin
        y = margin

        # Title
        title = "Style Test: {} ({})".format(
            self._active_name, datetime.now().strftime("%Y-%m-%d"))
        draw.text((x, y), title, fill=0, font=font_lg)
        y += self.pt_to_px(20, dpi)

        # Section: Lineweights
        draw.text((x, y), "LINEWEIGHTS", fill=0, font=font)
        y += self.pt_to_px(14, dpi)

        lw = self.active.get("lineweights", {})
        bar_len = int((pw - 1.5) * dpi)  # drawing width minus margins
        for name, pt_val in sorted(lw.items()):
            px_w = self.pt_to_px(pt_val, dpi)
            label = "{} ({} pt)".format(name, pt_val)
            draw.text((x, y), label, fill=0, font=font_sm)
            bar_y = y + self.pt_to_px(10, dpi)
            draw.line([(x, bar_y), (x + bar_len, bar_y)], fill=0, width=px_w)
            y = bar_y + max(px_w, self.pt_to_px(4, dpi)) + self.pt_to_px(4, dpi)
            if y > h_px - margin * 2:
                break

        y += self.pt_to_px(12, dpi)

        # Section: Hatches
        if y < h_px - margin * 3:
            draw.text((x, y), "HATCH PATTERNS", fill=0, font=font)
            y += self.pt_to_px(14, dpi)

            swatch_size = int(0.8 * dpi)  # 0.8 inch squares
            gap = int(0.2 * dpi)
            col_x = x

            for hname, hdata in sorted(self.active.get("hatches", {}).items()):
                if col_x + swatch_size > w_px - margin:
                    col_x = x
                    y += swatch_size + self.pt_to_px(16, dpi) + gap

                if y + swatch_size > h_px - margin:
                    break

                # Draw swatch box
                draw.rectangle(
                    [col_x, y, col_x + swatch_size, y + swatch_size],
                    fill=None, outline=0, width=1)

                # Draw hatch pattern inside
                sp_mm = hdata.get("spacing_mm", 8.0)
                sp_px = max(4, self.mm_to_px(sp_mm, dpi))
                wt_pt = hdata.get("weight_pt", 0.4)
                wt_px = max(1, self.pt_to_px(wt_pt, dpi))

                if "radius_mm" in hdata:
                    # Dots pattern
                    r_px = max(1, self.mm_to_px(hdata["radius_mm"], dpi))
                    for dx in range(col_x + sp_px, col_x + swatch_size, sp_px):
                        for dy in range(y + sp_px, y + swatch_size, sp_px):
                            if hdata.get("filled", True):
                                draw.ellipse([dx - r_px, dy - r_px,
                                              dx + r_px, dy + r_px], fill=0)
                            else:
                                draw.ellipse([dx - r_px, dy - r_px,
                                              dx + r_px, dy + r_px],
                                             outline=0, width=1)
                else:
                    angle = hdata.get("angle_deg", 45)
                    angles = angle if isinstance(angle, list) else [angle]
                    for a in angles:
                        if a == 0:
                            for ly in range(y, y + swatch_size, sp_px):
                                draw.line([(col_x, ly),
                                           (col_x + swatch_size, ly)],
                                          fill=0, width=wt_px)
                        elif a == 90:
                            for lx in range(col_x, col_x + swatch_size, sp_px):
                                draw.line([(lx, y), (lx, y + swatch_size)],
                                          fill=0, width=wt_px)
                        else:
                            # Diagonal lines
                            span = swatch_size * 2
                            for off in range(-span, span, sp_px):
                                if a == 45 or a == 135:
                                    if a == 45:
                                        x0 = col_x + off
                                        y0 = y
                                        x1 = col_x + off + swatch_size
                                        y1 = y + swatch_size
                                    else:
                                        x0 = col_x + off + swatch_size
                                        y0 = y
                                        x1 = col_x + off
                                        y1 = y + swatch_size
                                    draw.line([(x0, y0), (x1, y1)],
                                              fill=0, width=wt_px)

                # Label below swatch
                draw.text((col_x, y + swatch_size + 2),
                          "{} ({}mm)".format(hname, sp_mm),
                          fill=0, font=font_sm)
                col_x += swatch_size + gap

        # Save
        img.save(output_path, dpi=(dpi, dpi))
        return output_path
