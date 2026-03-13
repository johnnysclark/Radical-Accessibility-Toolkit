"""CLI entry point for webcam-dither."""

import click

from webcam_dither.webcam import run_webcam, DitherParams


def _parse_resolution(value):
    """Parse 'WxH' string into (width, height) tuple."""
    try:
        parts = value.lower().split("x")
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        raise click.BadParameter(
            "Resolution must be WxH, e.g. 640x480"
        )


@click.command()
@click.option("--camera", "-c", default=0, type=int,
              help="Camera device index (default: 0).")
@click.option("--spacing", "-s", default=8, type=int,
              help="Initial dot spacing in pixels (default: 8).")
@click.option("--dot-scale", "-d", default=0.8, type=float,
              help="Initial dot scale factor (default: 0.8).")
@click.option("--algorithm", "-a", default="halftone",
              type=click.Choice(["halftone", "ordered", "floyd_steinberg"]),
              help="Initial dithering algorithm (default: halftone).")
@click.option("--output-dir", "-o", default="./captures",
              help="Screenshot output directory (default: ./captures).")
@click.option("--paper-size", "-p", default="letter",
              type=click.Choice(["letter", "tabloid"]),
              help="PIAF paper size for PDF export (default: letter).")
@click.option("--no-pdf", is_flag=True, default=False,
              help="Skip PDF generation on screenshot.")
@click.option("--invert", is_flag=True, default=False,
              help="Start with inverted output.")
@click.option("--resolution", "-r", default="640x480",
              help="Webcam resolution as WxH (default: 640x480).")
@click.option("--brightness", default=0, type=int,
              help="Initial brightness offset (default: 0).")
@click.option("--contrast", default=1.0, type=float,
              help="Initial contrast multiplier (default: 1.0).")
@click.option("--verbose", "-v", is_flag=True, default=False,
              help="Verbose output.")
def main(camera, spacing, dot_scale, algorithm, output_dir, paper_size,
         no_pdf, invert, resolution, brightness, contrast, verbose):
    """Live webcam dithering converter for PIAF tactile output.

    Opens a webcam feed with real-time dithertone rendering. Use keyboard
    controls to tune parameters and take screenshots for PIAF swell paper.
    """
    res = _parse_resolution(resolution)

    params = DitherParams(
        spacing=spacing,
        dot_scale=dot_scale,
        algorithm=algorithm,
        brightness=brightness,
        contrast=contrast,
        invert=invert,
    )

    run_webcam(
        camera_index=camera,
        resolution=res,
        params=params,
        output_dir=output_dir,
        paper_size=paper_size,
        generate_pdf=not no_pdf,
        verbose=verbose,
    )


if __name__ == "__main__":
    main()
