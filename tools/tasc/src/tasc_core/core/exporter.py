"""Export TASC models to PIAF PDF, .3dm, and text formats."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tasc_core.core.model import TASCModel


def _render_model_image(model: "TASCModel", width_px: int = 2400, height_px: int = 3000):
    """Render model to a high-contrast B&W PIL Image for PIAF.

    Site = thick black outline
    Zones = filled dark gray with black outline
    Grid = thin gray lines
    Labels = text at zone centroids
    """
    from PIL import Image, ImageDraw, ImageFont

    if not model.site:
        raise ValueError("Cannot render: no site boundary defined")

    # Calculate scale to fit image
    s_min_x, s_min_y, s_max_x, s_max_y = model.site.bounds
    site_w = s_max_x - s_min_x
    site_h = s_max_y - s_min_y
    if site_w == 0 or site_h == 0:
        raise ValueError("Site has zero dimension")

    # Leave margin
    margin = 100
    usable_w = width_px - 2 * margin
    usable_h = height_px - 2 * margin
    scale = min(usable_w / site_w, usable_h / site_h)

    def to_px(x: float, y: float) -> tuple[int, int]:
        """Convert model coords to pixel coords (y-flipped for image)."""
        px = int((x - s_min_x) * scale + margin)
        py = int((s_max_y - y) * scale + margin)  # Flip Y
        return (px, py)

    img = Image.new("L", (width_px, height_px), 255)  # White background
    draw = ImageDraw.Draw(img)

    # Draw grid (thin gray lines)
    if model.grid and model.grid.spacing > 0:
        x = s_min_x
        while x <= s_max_x:
            p1 = to_px(x, s_min_y)
            p2 = to_px(x, s_max_y)
            draw.line([p1, p2], fill=180, width=1)
            x += model.grid.spacing
        y = s_min_y
        while y <= s_max_y:
            p1 = to_px(s_min_x, y)
            p2 = to_px(s_max_x, y)
            draw.line([p1, p2], fill=180, width=1)
            y += model.grid.spacing

    # Draw zones (filled)
    for zone in model.zones:
        poly_px = [to_px(c[0], c[1]) for c in zone.corners]
        if len(poly_px) >= 3:
            draw.polygon(poly_px, fill=200, outline=0)
            # Label
            cx, cy = zone.centroid
            label_pos = to_px(cx, cy)
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 24)
            except (IOError, OSError):
                font = ImageFont.load_default()
            bbox = draw.textbbox(label_pos, zone.name, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text((label_pos[0] - tw // 2, label_pos[1] - th // 2), zone.name, fill=0, font=font)

    # Draw site boundary (thick black outline)
    site_px = [to_px(c[0], c[1]) for c in model.site.corners]
    if len(site_px) >= 3:
        site_px.append(site_px[0])  # Close polygon
        draw.line(site_px, fill=0, width=4)

    return img


def export_piaf(model: "TASCModel", output_path: Path) -> str:
    """Generate PIAF tactile PDF via TACT pipeline.

    Returns the output file path as string.
    """
    from tactile_core.core.pdf_generator import PIAFPDFGenerator
    from tactile_core.core.processor import ImageProcessor

    img = _render_model_image(model)

    # Process through TACT pipeline
    processor = ImageProcessor()
    # Convert PIL Image to format processor expects
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img.save(tmp.name)
        processed_img, metadata = processor.process(tmp.name, threshold=128)

    # Generate PDF
    generator = PIAFPDFGenerator()
    output_str = str(output_path)
    generator.generate(processed_img, output_str, paper_size="letter")

    # Clean up temp file
    Path(tmp.name).unlink(missing_ok=True)

    return output_str


def export_3dm(model: "TASCModel", output_path: Path) -> str:
    """Generate .3dm file via rhino3dm (works offline)."""
    import rhino3dm

    file3dm = rhino3dm.File3dm()

    # Set units
    if model.site and model.site.units == "feet":
        file3dm.Settings.ModelUnitSystem = rhino3dm.UnitSystem.Feet
    else:
        file3dm.Settings.ModelUnitSystem = rhino3dm.UnitSystem.Meters

    # Add site boundary
    if model.site:
        pts = [rhino3dm.Point3d(c[0], c[1], 0) for c in model.site.corners]
        pts.append(pts[0])  # Close
        polyline = rhino3dm.Polyline(len(pts))
        for p in pts:
            polyline.Add(p.X, p.Y, p.Z)
        curve = polyline.ToPolylineCurve()
        attrs = rhino3dm.ObjectAttributes()
        attrs.Name = "site_boundary"
        file3dm.Objects.AddCurve(curve, attrs)

    # Add zones
    for zone in model.zones:
        pts = [rhino3dm.Point3d(c[0], c[1], 0) for c in zone.corners]
        pts.append(pts[0])  # Close
        polyline = rhino3dm.Polyline(len(pts))
        for p in pts:
            polyline.Add(p.X, p.Y, p.Z)
        curve = polyline.ToPolylineCurve()
        attrs = rhino3dm.ObjectAttributes()
        attrs.Name = zone.name
        file3dm.Objects.AddCurve(curve, attrs)

    # Add grid lines
    if model.grid and model.site and model.grid.spacing > 0:
        min_x, min_y, max_x, max_y = model.site.bounds
        x = min_x
        while x <= max_x:
            line = rhino3dm.LineCurve(
                rhino3dm.Point3d(x, min_y, 0), rhino3dm.Point3d(x, max_y, 0)
            )
            file3dm.Objects.AddCurve(line)
            x += model.grid.spacing
        y = min_y
        while y <= max_y:
            line = rhino3dm.LineCurve(
                rhino3dm.Point3d(min_x, y, 0), rhino3dm.Point3d(max_x, y, 0)
            )
            file3dm.Objects.AddCurve(line)
            y += model.grid.spacing

    file3dm.Write(str(output_path), version=7)
    return str(output_path)


def export_text(model: "TASCModel", output_path: Path) -> str:
    """Generate text description file."""
    from tasc_core.core.feedback import describe_model

    text = describe_model(model)
    output_path.write_text(text)
    return str(output_path)
