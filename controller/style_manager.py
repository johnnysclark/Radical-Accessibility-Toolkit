# -*- coding: utf-8 -*-
"""
Style Manager — PIAF Style Profiles for Tactile Rendering
==========================================================
Manages named JSON style profiles that control every rendering
property of the PIAF tactile output pipeline.

Part of the Radical Accessibility Project — UIUC School of Architecture.

Zero external dependencies (stdlib only).
"""

import copy
import json
import os


# ---------------------------------------------------------------------------
# Required schema keys — used for validation
# ---------------------------------------------------------------------------

REQUIRED_TOP_KEYS = {"name", "description", "lineweights", "hatches",
                     "labels", "layout", "density", "drawing_overrides"}

REQUIRED_LINEWEIGHT_KEYS = {
    "column", "wall_exterior", "wall_interior", "corridor_edge",
    "corridor_dash", "door_swing", "door_frame", "window_line",
    "portal_line", "grid_line", "section_cut", "section_beyond",
    "hatch_line", "dimension_line", "leader_line", "site_boundary",
    "north_arrow",
}

REQUIRED_LABEL_KEYS = {
    "braille_pt", "room_name_pt", "dimension_pt", "legend_title_pt",
    "legend_entry_pt", "bay_label_pt", "grid_label_pt",
}

REQUIRED_LAYOUT_KEYS = {
    "paper", "orientation", "margin_inches", "scale", "title_block",
    "legend", "north_arrow", "grid_labels", "braille_labels",
    "english_labels", "dimensions", "section_marks",
}

REQUIRED_DENSITY_KEYS = {
    "target_percent", "warning_percent", "reject_percent",
    "auto_adjust", "priority",
}

VALID_PAPERS = {"letter", "tabloid"}
VALID_ORIENTATIONS = {"landscape", "portrait"}


# ---------------------------------------------------------------------------
# Paper sizes in inches (width, height) — landscape orientation
# ---------------------------------------------------------------------------

PAPER_SIZES = {
    "letter":  (11.0, 8.5),
    "tabloid": (17.0, 11.0),
}

PAPER_SIZES_PORTRAIT = {
    "letter":  (8.5, 11.0),
    "tabloid": (11.0, 17.0),
}

# Built-in hatch names that cannot be removed
BUILTIN_HATCHES = {
    "diagonal", "crosshatch", "horizontal", "vertical", "dots",
    "dense_diagonal", "sparse_diagonal",
}


def _resolve_styles_dir(styles_dir):
    """Resolve styles_dir relative to this module's location."""
    if os.path.isabs(styles_dir):
        return styles_dir
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, styles_dir)


class StyleManager:
    """Manages PIAF style profiles for tactile rendering."""

    def __init__(self, styles_dir="styles"):
        self._styles_dir = _resolve_styles_dir(styles_dir)
        self._styles = {}          # name -> style dict
        self._saved = {}           # name -> last-saved copy (for reset)
        self._active_name = None
        self._load_all()
        if not self._styles:
            self._generate_defaults()
            self._load_all()
        if "working" in self._styles:
            self._active_name = "working"
        elif self._styles:
            self._active_name = sorted(self._styles.keys())[0]

    # -- Loading --------------------------------------------------------

    def _load_all(self):
        """Load all .json files from the styles directory."""
        if not os.path.isdir(self._styles_dir):
            return
        for fname in sorted(os.listdir(self._styles_dir)):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(self._styles_dir, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                name = data.get("name", os.path.splitext(fname)[0])
                self._styles[name] = data
                self._saved[name] = copy.deepcopy(data)
            except (json.JSONDecodeError, IOError):
                continue

    def _generate_defaults(self):
        """Copy bundled default styles into the styles directory."""
        # The defaults ship alongside this module in controller/styles/
        # If they don't exist, we have a problem — but the files are
        # created by the build process. This is a fallback.
        os.makedirs(self._styles_dir, exist_ok=True)

    # -- Active style ---------------------------------------------------

    @property
    def active(self):
        """Return the active style dict."""
        if self._active_name and self._active_name in self._styles:
            return self._styles[self._active_name]
        return {}

    @property
    def active_name(self):
        return self._active_name

    # -- Get / Set ------------------------------------------------------

    def get(self, key_path, default=None):
        """Get a value from the active style using dot notation.

        style.get("lineweights.column") -> 3.0
        style.get("hatches.diagonal.spacing_mm") -> 8.0
        style.get("layout.paper") -> "letter"
        """
        parts = key_path.split(".")
        node = self.active
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                return default
        return node

    def set(self, key_path, value):
        """Set a value in the active style. Does NOT auto-save.

        Returns (new_value, old_value) for confirmation message.
        """
        parts = key_path.split(".")
        node = self.active
        for p in parts[:-1]:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                raise ValueError("Key path not found: {}".format(key_path))
        last = parts[-1]
        if not isinstance(node, dict) or last not in node:
            raise ValueError("Key not found: {}".format(key_path))
        old_value = node[last]
        # Type coercion: match the type of the existing value
        value = self._coerce(value, old_value)
        node[last] = value
        return (value, old_value)

    def _coerce(self, value, reference):
        """Coerce value to match reference type."""
        if isinstance(reference, bool):
            if isinstance(value, str):
                return value.lower() in ("true", "1", "on", "yes")
            return bool(value)
        if isinstance(reference, float):
            return float(value)
        if isinstance(reference, int):
            return int(float(value))
        if isinstance(reference, list):
            if isinstance(value, str):
                # Try JSON parse
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, ValueError):
                    pass
            return value
        return value

    # -- Style switching ------------------------------------------------

    def use(self, name):
        """Switch active style. Returns (style_name, description)."""
        if name not in self._styles:
            available = ", ".join(sorted(self._styles.keys()))
            raise ValueError("Style '{}' not found. Available: {}".format(
                name, available))
        self._active_name = name
        s = self._styles[name]
        return (s.get("name", name), s.get("description", ""))

    # -- Save / Reset ---------------------------------------------------

    def save(self, name=None):
        """Save active style. If name given, save-as to new file."""
        if name:
            # Save-as: copy active style with new name
            data = copy.deepcopy(self.active)
            data["name"] = name
            self._styles[name] = data
            self._active_name = name
        else:
            name = self._active_name

        data = self._styles[name]
        os.makedirs(self._styles_dir, exist_ok=True)
        path = os.path.join(self._styles_dir, "{}.json".format(name))
        text = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
        self._saved[name] = copy.deepcopy(data)
        return path

    def reset(self):
        """Reset active style to its saved state (discard unsaved changes)."""
        name = self._active_name
        if name in self._saved:
            self._styles[name] = copy.deepcopy(self._saved[name])
            return name
        raise ValueError("No saved state for style '{}'.".format(name))

    # -- Listing --------------------------------------------------------

    def list_styles(self):
        """Return list of (name, description, is_active) tuples."""
        result = []
        for name in sorted(self._styles.keys()):
            s = self._styles[name]
            result.append((
                s.get("name", name),
                s.get("description", ""),
                name == self._active_name,
            ))
        return result

    # -- Show -----------------------------------------------------------

    def show(self, category=None):
        """Return formatted string showing style values.

        If category given (lineweights, hatches, labels, layout, density),
        show only that category. Otherwise show summary.
        """
        s = self.active
        name = s.get("name", self._active_name)
        lines = []

        if category is None:
            # Summary
            lw = s.get("lineweights", {})
            h = s.get("hatches", {})
            lb = s.get("labels", {})
            la = s.get("layout", {})
            d = s.get("density", {})
            lines.append("Style: {} — {}".format(name, s.get("description", "")))
            lines.append("  lineweights: {} entries, range {:.1f}-{:.1f} pt".format(
                len(lw),
                min(lw.values()) if lw else 0,
                max(lw.values()) if lw else 0))
            lines.append("  hatches: {} patterns".format(len(h)))
            lines.append("  labels: braille {}pt, room {}pt, legend title {}pt".format(
                lb.get("braille_pt", "?"),
                lb.get("room_name_pt", "?"),
                lb.get("legend_title_pt", "?")))
            lines.append("  layout: {} {}, margin {:.2f} in".format(
                la.get("paper", "?"),
                la.get("orientation", "?"),
                la.get("margin_inches", 0)))
            lines.append("  density: target {}%, warning {}%, reject {}%".format(
                d.get("target_percent", "?"),
                d.get("warning_percent", "?"),
                d.get("reject_percent", "?")))
            return "\n".join(lines)

        cat = category.lower()
        if cat == "lineweights":
            lw = s.get("lineweights", {})
            lines.append("Lineweights (active style: {}):".format(name))
            max_key_len = max((len(k) for k in lw), default=0)
            for k in sorted(lw.keys()):
                dots = "." * (max_key_len - len(k) + 3)
                lines.append("  {} {} {:.1f} pt".format(k, dots, lw[k]))
        elif cat == "hatches":
            h = s.get("hatches", {})
            lines.append("Hatches (active style: {}):".format(name))
            for k in sorted(h.keys()):
                v = h[k]
                if "radius_mm" in v:
                    lines.append("  {}: spacing {:.1f} mm, radius {:.1f} mm".format(
                        k, v.get("spacing_mm", 0), v.get("radius_mm", 0)))
                else:
                    angle = v.get("angle_deg", 0)
                    if isinstance(angle, list):
                        angle_s = "/".join(str(a) for a in angle)
                    else:
                        angle_s = str(angle)
                    lines.append("  {}: spacing {:.1f} mm, angle {} deg, weight {:.1f} pt".format(
                        k, v.get("spacing_mm", 0), angle_s, v.get("weight_pt", 0)))
        elif cat == "labels":
            lb = s.get("labels", {})
            lines.append("Labels (active style: {}):".format(name))
            for k in sorted(lb.keys()):
                lines.append("  {}: {} pt".format(k, lb[k]))
        elif cat == "layout":
            la = s.get("layout", {})
            lines.append("Layout (active style: {}):".format(name))
            for k in sorted(la.keys()):
                lines.append("  {}: {}".format(k, la[k]))
        elif cat == "density":
            d = s.get("density", {})
            lines.append("Density (active style: {}):".format(name))
            for k in sorted(d.keys()):
                v = d[k]
                if isinstance(v, list):
                    lines.append("  {}: {}".format(k, ", ".join(str(x) for x in v)))
                else:
                    lines.append("  {}: {}".format(k, v))
        else:
            return "Unknown category: {}. Options: lineweights, hatches, labels, layout, density".format(
                category)

        return "\n".join(lines)

    # -- Hatch management -----------------------------------------------

    def add_hatch(self, name, spacing_mm, angle_deg, weight_pt=0.4,
                  radius_mm=None, filled=False):
        """Add a custom hatch pattern to the active style."""
        hatches = self.active.get("hatches", {})
        if radius_mm is not None:
            hatches[name] = {
                "spacing_mm": float(spacing_mm),
                "radius_mm": float(radius_mm),
                "filled": bool(filled),
            }
        else:
            hatches[name] = {
                "spacing_mm": float(spacing_mm),
                "angle_deg": angle_deg,
                "weight_pt": float(weight_pt),
            }
        self.active["hatches"] = hatches
        return name

    def remove_hatch(self, name):
        """Remove a custom hatch pattern. Cannot remove built-in hatches."""
        if name in BUILTIN_HATCHES:
            raise ValueError("Cannot remove built-in hatch '{}'.".format(name))
        hatches = self.active.get("hatches", {})
        if name not in hatches:
            raise ValueError("Hatch '{}' not found.".format(name))
        del hatches[name]
        return name

    # -- Test swatch ----------------------------------------------------

    def generate_test_swatch(self, output_path, dpi=300):
        """Render a calibration sheet showing all lineweights and hatches.

        Output is a black-and-white image ready for PIAF printing.
        Returns the output path.
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            raise ImportError("Pillow is required for test swatch generation.")

        s = self.active
        paper = s.get("layout", {}).get("paper", "letter")
        orient = s.get("layout", {}).get("orientation", "landscape")

        if orient == "landscape":
            pw, ph = PAPER_SIZES.get(paper, (11.0, 8.5))
        else:
            pw, ph = PAPER_SIZES_PORTRAIT.get(paper, (8.5, 11.0))

        w_px = int(pw * dpi)
        h_px = int(ph * dpi)
        margin_px = int(s.get("layout", {}).get("margin_inches", 0.5) * dpi)

        img = Image.new('1', (w_px, h_px), 1)
        draw = ImageDraw.Draw(img)

        # Load font
        try:
            font = ImageFont.truetype("arial.ttf", int(10 * dpi / 72))
        except (IOError, OSError):
            font = ImageFont.load_default()

        try:
            title_font = ImageFont.truetype("arial.ttf", int(14 * dpi / 72))
        except (IOError, OSError):
            title_font = font

        def pt_to_px(pt):
            return max(1, int(round(pt * dpi / 72.0)))

        def mm_to_px(mm):
            return max(1, int(round(mm * dpi / 25.4)))

        x = margin_px
        y = margin_px

        # Title
        name = s.get("name", self._active_name or "unknown")
        draw.text((x, y), "Style Test Swatch: {}".format(name), fill=0, font=title_font)
        y += int(20 * dpi / 72)

        # Lineweight samples
        draw.text((x, y), "LINEWEIGHTS", fill=0, font=title_font)
        y += int(16 * dpi / 72)

        lw = s.get("lineweights", {})
        bar_length = int((pw - 2 * pw * 0.1) * dpi * 0.5)
        for k in sorted(lw.keys()):
            weight_px = pt_to_px(lw[k])
            label = "{} ({:.1f} pt)".format(k, lw[k])
            draw.text((x, y), label, fill=0, font=font)
            bar_y = y + int(6 * dpi / 72)
            bar_x = x + int(2.5 * dpi)
            draw.line([(bar_x, bar_y), (bar_x + bar_length, bar_y)],
                      fill=0, width=weight_px)
            y += int(14 * dpi / 72)
            if y > h_px - margin_px - int(dpi * 2):
                break

        # Hatch pattern samples
        y += int(10 * dpi / 72)
        if y < h_px - margin_px - int(dpi * 2):
            draw.text((x, y), "HATCH PATTERNS", fill=0, font=title_font)
            y += int(16 * dpi / 72)

            hatches = s.get("hatches", {})
            swatch_size = int(0.8 * dpi)  # ~0.8 inch squares
            gap = int(0.3 * dpi)

            sx = x
            for hname in sorted(hatches.keys()):
                hatch = hatches[hname]
                if sx + swatch_size + gap > w_px - margin_px:
                    sx = x
                    y += swatch_size + gap + int(14 * dpi / 72)
                if y + swatch_size > h_px - margin_px:
                    break

                # Draw swatch border
                draw.rectangle([sx, y, sx + swatch_size, y + swatch_size],
                               fill=None, outline=0, width=1)

                # Draw hatch pattern inside
                spacing_px = mm_to_px(hatch.get("spacing_mm", 8.0))
                if "radius_mm" in hatch:
                    # Dots pattern
                    r_px = mm_to_px(hatch.get("radius_mm", 1.0))
                    for dx in range(0, swatch_size, spacing_px):
                        for dy in range(0, swatch_size, spacing_px):
                            cx = sx + dx + spacing_px // 2
                            cy = y + dy + spacing_px // 2
                            if cx < sx + swatch_size and cy < y + swatch_size:
                                draw.ellipse([cx - r_px, cy - r_px,
                                              cx + r_px, cy + r_px], fill=0)
                else:
                    angles = hatch.get("angle_deg", 45)
                    if not isinstance(angles, list):
                        angles = [angles]
                    weight_px = pt_to_px(hatch.get("weight_pt", 0.4))
                    for angle in angles:
                        rad = angle * 3.14159265 / 180.0
                        import math
                        cos_a = math.cos(rad)
                        sin_a = math.sin(rad)
                        # Draw parallel lines at the given angle
                        diag = int(math.hypot(swatch_size, swatch_size))
                        for offset in range(-diag, diag, spacing_px):
                            if abs(sin_a) > abs(cos_a):
                                # More vertical: sweep x
                                for px_i in range(swatch_size):
                                    py_i = int((offset - px_i * cos_a) / sin_a) if sin_a != 0 else 0
                                    if 0 <= py_i < swatch_size:
                                        ax = sx + px_i
                                        ay = y + py_i
                                        draw.line([(ax, ay), (ax, ay)], fill=0, width=weight_px)
                            else:
                                # More horizontal: sweep y
                                for py_i in range(swatch_size):
                                    px_i = int((offset - py_i * sin_a) / cos_a) if cos_a != 0 else 0
                                    if 0 <= px_i < swatch_size:
                                        ax = sx + px_i
                                        ay = y + py_i
                                        draw.line([(ax, ay), (ax, ay)], fill=0, width=weight_px)

                # Label below swatch
                draw.text((sx, y + swatch_size + 2), hname, fill=0, font=font)
                sx += swatch_size + gap

        # Density gradient strip
        y += swatch_size + gap + int(20 * dpi / 72) if y < h_px - margin_px - dpi else 0
        if y < h_px - margin_px - int(dpi * 0.5):
            draw.text((x, y), "DENSITY GRADIENT (10%-50%)", fill=0, font=title_font)
            y += int(16 * dpi / 72)
            strip_w = w_px - 2 * margin_px
            strip_h = int(0.4 * dpi)
            for col in range(strip_w):
                pct = 10 + 40 * col / strip_w
                # Dither: fill pixel if random-ish threshold < pct
                for row in range(strip_h):
                    # Simple ordered dither
                    threshold = ((col * 7 + row * 13) % 100)
                    if threshold < pct:
                        draw.point((x + col, y + row), fill=0)

        # Save
        if output_path.lower().endswith(".pdf"):
            # Save as PNG first, then convert
            png_path = output_path.rsplit(".", 1)[0] + ".png"
            img.save(png_path, dpi=(dpi, dpi))
            try:
                from reportlab.pdfgen import canvas as _canvas
                from reportlab.lib.utils import ImageReader
                import io
                buf = io.BytesIO()
                img.convert('L').save(buf, format='PNG', dpi=(dpi, dpi))
                buf.seek(0)
                page_w = pw * 72
                page_h = ph * 72
                c = _canvas.Canvas(output_path, pagesize=(page_w, page_h))
                c.drawImage(ImageReader(buf), 0, 0, page_w, page_h)
                c.save()
                os.remove(png_path)
            except ImportError:
                output_path = png_path
        else:
            img.save(output_path, dpi=(dpi, dpi))

        return output_path

    # -- Validation -----------------------------------------------------

    def validate(self, style=None):
        """Validate a style dict. Returns list of error strings (empty = valid)."""
        if style is None:
            style = self.active
        errors = []

        # Top-level keys
        for k in REQUIRED_TOP_KEYS:
            if k not in style:
                errors.append("Missing top-level key: {}".format(k))

        # Lineweights
        lw = style.get("lineweights", {})
        for k in REQUIRED_LINEWEIGHT_KEYS:
            if k not in lw:
                errors.append("Missing lineweight: {}".format(k))
            elif not isinstance(lw[k], (int, float)) or lw[k] <= 0:
                errors.append("Lineweight {} must be > 0, got {}".format(k, lw[k]))

        # Labels
        lb = style.get("labels", {})
        for k in REQUIRED_LABEL_KEYS:
            if k not in lb:
                errors.append("Missing label: {}".format(k))
            elif not isinstance(lb[k], (int, float)) or lb[k] <= 0:
                errors.append("Label {} must be > 0, got {}".format(k, lb[k]))

        # Layout
        la = style.get("layout", {})
        for k in REQUIRED_LAYOUT_KEYS:
            if k not in la:
                errors.append("Missing layout key: {}".format(k))
        if la.get("paper") not in VALID_PAPERS:
            errors.append("Invalid paper: {}. Options: {}".format(
                la.get("paper"), ", ".join(sorted(VALID_PAPERS))))
        if la.get("orientation") not in VALID_ORIENTATIONS:
            errors.append("Invalid orientation: {}".format(la.get("orientation")))

        # Density
        d = style.get("density", {})
        for k in REQUIRED_DENSITY_KEYS:
            if k not in d:
                errors.append("Missing density key: {}".format(k))
        for k in ("target_percent", "warning_percent", "reject_percent"):
            v = d.get(k, -1)
            if isinstance(v, (int, float)) and not (0 <= v <= 100):
                errors.append("Density {} must be 0-100, got {}".format(k, v))

        return errors
