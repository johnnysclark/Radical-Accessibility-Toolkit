"""CLI entry point for webcam-dither.

Provides live webcam dithering with tunable parameters and
single-shot snapshot capture.
"""

import os
import sys

import click
import cv2

from webcam_dither.core.capture import WebcamCapture, CaptureError
from webcam_dither.core.dithertone import DithertoneRenderer, DithertoneParams
from webcam_dither.core.export import save_screenshot, save_piaf_pdf, save_bracket
from webcam_dither.utils import logger


def _parse_camera_source(value):
    """Parse camera source: integer index or URL string."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return str(value)


def _add_status_overlay(image, text):
    """Add a status text bar at the bottom of the image."""
    h, w = image.shape[:2]
    # Convert to BGR for colored text overlay
    display = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    bar_height = 30
    # Dark background bar
    display[h - bar_height:h, :] = (40, 40, 40)
    cv2.putText(
        display, text,
        (10, h - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1,
        cv2.LINE_AA,
    )
    return display


HELP_TEXT = """Webcam Dither -- live dithertone converter.

Captures webcam video and applies real-time dithertone processing
(dot patterns where dot size varies with brightness). Take screenshots
and optionally export PIAF-ready PDFs for tactile printing.

Keyboard controls during live view:
  q / ESC     Quit
  SPACE       Take screenshot
  b           Bracket shot (tight/medium/loose)
  + / =       Increase spacing (fewer, bigger dots)
  -           Decrease spacing (more, smaller dots)
  [ ]         Decrease / increase gamma
  c / v       Increase / decrease contrast
  i           Toggle invert
  r           Reset parameters
  p           Toggle PIAF auto-export
"""


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Webcam Dither -- live dithertone converter for PIAF."""
    if ctx.invoked_subcommand is None:
        click.echo(HELP_TEXT)


@main.command()
@click.option("--camera", "-c", default="0",
              help="Camera index (0,1,...) or URL for IP camera / phone stream.")
@click.option("--spacing", "-s", default=8, type=int,
              help="Initial grid spacing in pixels (default: 8).")
@click.option("--min-radius", default=0.5, type=float,
              help="Minimum dot radius to draw (default: 0.5).")
@click.option("--max-radius", default=0.45, type=float,
              help="Max radius as fraction of half-spacing (default: 0.45).")
@click.option("--invert", is_flag=True, default=False,
              help="Start in inverted mode (white dots on black).")
@click.option("--width", "-w", default=640, type=int,
              help="Capture width in pixels (default: 640).")
@click.option("--height", default=480, type=int,
              help="Capture height in pixels (default: 480).")
@click.option("--output-dir", "-o", default=".",
              help="Directory for screenshots (default: current dir).")
@click.option("--piaf", is_flag=True, default=False,
              help="Auto-generate PIAF PDF with each screenshot.")
@click.option("--paper-size", "-p", default="letter",
              type=click.Choice(["letter", "tabloid"]),
              help="Paper size for PIAF output (default: letter).")
def live(camera, spacing, min_radius, max_radius, invert,
         width, height, output_dir, piaf, paper_size):
    """Start live webcam dithering with real-time preview."""
    source = _parse_camera_source(camera)
    params = DithertoneParams(
        spacing=spacing,
        min_radius=min_radius,
        max_radius_factor=max_radius,
        invert=invert,
    )
    renderer = DithertoneRenderer(params)
    piaf_enabled = piaf

    # Check PIAF availability
    piaf_available = True
    try:
        from tactile_core.core.pdf_generator import PIAFPDFGenerator  # noqa: F401
    except ImportError:
        piaf_available = False
        if piaf_enabled:
            logger.error(
                "tactile-core not installed. PIAF PDF export disabled. "
                "Install with: pip install -e tools/tact"
            )
            piaf_enabled = False

    capture = WebcamCapture(source=source, width=width, height=height)
    try:
        capture.open()
    except CaptureError as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info(f"Camera opened ({source}). Resolution: {width}x{height}.")
    logger.info("Press 'q' or ESC to quit. SPACE to screenshot.")
    logger.ready("Live dithering started.")

    window_name = "Webcam Dither"
    try:
        while True:
            try:
                frame = capture.read_frame()
            except CaptureError:
                logger.error("Lost camera connection.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            dithered = renderer.render(gray)

            # Build status line
            piaf_status = "PIAF:ON" if piaf_enabled else "PIAF:OFF"
            status = f"{renderer.get_status_text()}  {piaf_status}"
            display = _add_status_overlay(dithered, status)

            cv2.imshow(window_name, display)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q") or key == 27:  # q or ESC
                break

            elif key == ord(" "):  # SPACE - screenshot
                png_path = save_screenshot(dithered, output_dir)
                logger.info(f"Screenshot saved: {png_path}")
                if piaf_enabled:
                    pdf_path = save_piaf_pdf(dithered, output_dir, paper_size)
                    if pdf_path:
                        logger.info(f"PIAF PDF saved: {pdf_path}")
                    else:
                        logger.error("PIAF PDF generation failed.")

            elif key == ord("b"):  # bracket shot
                results = save_bracket(
                    gray, renderer, output_dir, paper_size, piaf=piaf_enabled
                )
                for label, png_p, pdf_p in results:
                    logger.info(f"Bracket {label}: {png_p}")
                    if pdf_p:
                        logger.info(f"Bracket {label} PDF: {pdf_p}")

            elif key in (ord("+"), ord("=")):
                renderer.adjust_spacing(1)

            elif key == ord("-"):
                renderer.adjust_spacing(-1)

            elif key == ord("["):
                renderer.adjust_gamma(-0.1)

            elif key == ord("]"):
                renderer.adjust_gamma(0.1)

            elif key == ord("c"):
                renderer.adjust_contrast(10)

            elif key == ord("v"):
                renderer.adjust_contrast(-10)

            elif key == ord("i"):
                renderer.toggle_invert()

            elif key == ord("r"):
                renderer.reset()
                logger.info("Parameters reset to defaults.")

            elif key == ord("p"):
                if not piaf_available:
                    logger.error(
                        "tactile-core not installed. "
                        "Install with: pip install -e tools/tact"
                    )
                else:
                    piaf_enabled = not piaf_enabled
                    state = "ON" if piaf_enabled else "OFF"
                    logger.info(f"PIAF auto-export: {state}")

    finally:
        capture.release()
        cv2.destroyAllWindows()
        logger.ready("Webcam dither stopped.")


@main.command()
@click.option("--camera", "-c", default="0",
              help="Camera index or URL for IP camera.")
@click.option("--spacing", "-s", default=8, type=int,
              help="Grid spacing in pixels.")
@click.option("--min-radius", default=0.5, type=float,
              help="Minimum dot radius.")
@click.option("--max-radius", default=0.45, type=float,
              help="Max radius factor.")
@click.option("--invert", is_flag=True, default=False,
              help="Inverted mode.")
@click.option("--gamma", "-g", default=1.0, type=float,
              help="Gamma correction (default: 1.0).")
@click.option("--contrast", default=0.0, type=float,
              help="Contrast adjustment (-100 to 100).")
@click.option("--brightness", default=0.0, type=float,
              help="Brightness adjustment (-100 to 100).")
@click.option("--output", "-o", default=None,
              help="Output file path (default: auto-named in current dir).")
@click.option("--piaf", is_flag=True, default=False,
              help="Also generate PIAF PDF.")
@click.option("--paper-size", "-p", default="letter",
              type=click.Choice(["letter", "tabloid"]),
              help="Paper size for PIAF.")
@click.option("--bracket", is_flag=True, default=False,
              help="Save tight/medium/loose spacing variants.")
def snapshot(camera, spacing, min_radius, max_radius, invert,
             gamma, contrast, brightness, output, piaf, paper_size, bracket):
    """Capture a single frame, dither it, and save."""
    source = _parse_camera_source(camera)
    params = DithertoneParams(
        spacing=spacing,
        min_radius=min_radius,
        max_radius_factor=max_radius,
        invert=invert,
        gamma=gamma,
        contrast=contrast,
        brightness=brightness,
    )
    renderer = DithertoneRenderer(params)

    capture = WebcamCapture(source=source)
    try:
        capture.open()
    except CaptureError as e:
        logger.error(str(e))
        sys.exit(1)

    try:
        frame = capture.read_frame()
    except CaptureError as e:
        logger.error(str(e))
        capture.release()
        sys.exit(1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if bracket:
        output_dir = os.path.dirname(output) if output else "."
        results = save_bracket(gray, renderer, output_dir, paper_size, piaf=piaf)
        for label, png_p, pdf_p in results:
            logger.info(f"Bracket {label}: {png_p}")
            if pdf_p:
                logger.info(f"Bracket {label} PDF: {pdf_p}")
    else:
        dithered = renderer.render(gray)
        if output:
            output_dir = os.path.dirname(output) or "."
            prefix = os.path.splitext(os.path.basename(output))[0]
        else:
            output_dir = "."
            prefix = "dither"

        png_path = save_screenshot(dithered, output_dir, prefix=prefix)
        logger.info(f"Screenshot saved: {png_path}")

        if piaf:
            pdf_path = save_piaf_pdf(dithered, output_dir, paper_size, prefix=prefix)
            if pdf_path:
                logger.info(f"PIAF PDF saved: {pdf_path}")
            else:
                logger.error(
                    "PIAF PDF failed. Is tactile-core installed? "
                    "pip install -e tools/tact"
                )

    capture.release()
    logger.ready()


if __name__ == "__main__":
    main()
