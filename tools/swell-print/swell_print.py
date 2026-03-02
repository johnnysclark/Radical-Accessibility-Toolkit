#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swell-Print CLI — PIAF Tactile Graphics Pipeline  v1.0
=======================================================
Converts architectural designs to tactile swell-paper graphics.

Two modes:
  1. Render state.json → PIAF-ready B&W image (no Rhino needed)
  2. Convert any image → PIAF-ready B&W output

Follows the OK:/ERROR: protocol for screen-reader compatibility.

Part of the Radical Accessibility Project — UIUC School of Architecture.

Dependencies:  Pillow (PIL), reportlab
Optional:      opencv-python, numpy, liblouis

Usage:
  python swell_print.py                        # interactive mode
  python swell_print.py render state.json      # render from state
  python swell_print.py convert image.jpg      # convert image
"""

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(os.path.dirname(_here))
_controller = os.path.join(_root, "controller")

if _here not in sys.path:
    sys.path.insert(0, _here)
if _controller not in sys.path:
    sys.path.insert(0, _controller)

# ---------------------------------------------------------------------------
# Lazy imports (checked at runtime for better error messages)
# ---------------------------------------------------------------------------

def _check_deps():
    """Check that required dependencies are installed."""
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("ERROR: Pillow is required. Install: pip install Pillow")
        sys.exit(1)


def _import_renderer():
    import state_renderer
    return state_renderer


def _import_converter():
    import image_converter
    return image_converter


def _import_pdf():
    try:
        import pdf_generator
        return pdf_generator
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_render(args):
    """Render state.json to PIAF-ready output."""
    renderer = _import_renderer()
    pdf_gen = _import_pdf()

    state_path = args.state or os.path.join(_controller, "state.json")
    if not os.path.isfile(state_path):
        print("ERROR: State file not found: {}".format(state_path))
        return

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    paper = args.paper or "letter"
    dpi = args.dpi or 300
    output = args.output

    # Determine output format
    if output and output.lower().endswith(".pdf"):
        fmt = "pdf"
    elif output and output.lower().endswith(".png"):
        fmt = "png"
    else:
        fmt = args.format or "pdf"

    if output is None:
        base = os.path.splitext(os.path.basename(state_path))[0]
        output = base + "_tactile." + fmt

    print("Rendering: {} → {}".format(os.path.basename(state_path), output))

    try:
        img = renderer.render(state, dpi=dpi, paper_size=paper)

        if fmt == "pdf" and pdf_gen:
            pdf_gen.generate_pdf(img, output, paper_size=paper,
                                 metadata={"source": os.path.basename(state_path)})
        else:
            if fmt == "pdf" and not pdf_gen:
                print("WARNING: reportlab not installed. Saving as PNG instead.")
                output = os.path.splitext(output)[0] + ".png"
            img.save(output, dpi=(dpi, dpi))

        # Density check
        d = renderer.density(img)
        print("OK: Rendered {} ({} paper, {} DPI, density {:.1f}%)".format(
            output, paper.title(), dpi, d))
        print("READY:")

    except Exception as e:
        print("ERROR: Render failed: {}".format(e))


def cmd_convert(args):
    """Convert an image to PIAF-ready B&W."""
    converter = _import_converter()
    pdf_gen = _import_pdf()

    if not args.image:
        print("ERROR: Provide an image path. Example: convert photo.jpg")
        return

    image_path = args.image
    if not os.path.isfile(image_path):
        print("ERROR: Image not found: {}".format(image_path))
        return

    preset = args.preset or "floor_plan"
    paper = args.paper or "letter"
    dpi = args.dpi or 300
    threshold = args.threshold

    print("Converting: {} (preset: {})".format(
        os.path.basename(image_path), preset))

    try:
        result = converter.convert(
            image_path,
            output_path=args.output,
            preset=preset,
            threshold=threshold,
            paper_size=paper,
            dpi=dpi,
        )

        png_path = result["output_path"]

        # Optionally wrap in PDF
        if args.output and args.output.lower().endswith(".pdf") and pdf_gen:
            from PIL import Image
            img = Image.open(png_path)
            pdf_path = args.output
            pdf_gen.generate_pdf(img, pdf_path, paper_size=paper,
                                 metadata={"source": os.path.basename(image_path)})
            os.remove(png_path)
            print("OK: Converted {} → {} (density {:.1f}%, {})".format(
                os.path.basename(image_path), pdf_path,
                result["density"], result["message"]))
        else:
            print("OK: Converted {} → {} (density {:.1f}%, {})".format(
                os.path.basename(image_path), png_path,
                result["density"], result["message"]))

        print("READY:")

    except (FileNotFoundError, ValueError) as e:
        print("ERROR: {}".format(e))
    except Exception as e:
        print("ERROR: Conversion failed: {}".format(e))


def cmd_presets(args):
    """List available conversion presets."""
    converter = _import_converter()
    presets = converter.list_presets()
    print("OK: {} presets available:".format(len(presets)))
    for i, (name, desc) in enumerate(presets, 1):
        p = converter.PRESETS[name]
        print("  {}. {} — {} (threshold {}, max density {}%)".format(
            i, name, desc, p["threshold"], p["max_density"]))
    print("READY:")


def cmd_density(args):
    """Check density of an image."""
    converter = _import_converter()

    if not args.image:
        print("ERROR: Provide an image path.")
        return

    if not os.path.isfile(args.image):
        print("ERROR: Image not found: {}".format(args.image))
        return

    try:
        from PIL import Image
        img = Image.open(args.image)
        if img.mode != '1':
            img = img.convert('1')
        d = converter.calculate_density(img)
        ok, _, msg = converter.check_density(img)
        status = "OK" if ok else "WARNING"
        print("{}: {}".format(status, msg))
        print("READY:")
    except Exception as e:
        print("ERROR: {}".format(e))


# ---------------------------------------------------------------------------
# Interactive REPL
# ---------------------------------------------------------------------------

HELP_TEXT = """
Swell-Print v1.0 — PIAF Tactile Graphics Pipeline
====================================================
Converts designs to swell-paper tactile graphics.

COMMANDS:
  render [state.json]           Render model to PIAF output
  convert <image>               Convert image to PIAF-ready B&W
  presets                       List available conversion presets
  density <image>               Check image black pixel density
  help                          This message
  quit                          Exit

OPTIONS (for render and convert):
  --paper <letter|tabloid>      Paper size (default: letter)
  --preset <name>               Conversion preset (default: floor_plan)
  --threshold <0-255>           B&W threshold (overrides preset)
  --output <path>               Output file path
  --dpi <number>                Resolution (default: 300)
  --format <png|pdf>            Output format (default: pdf)

EXAMPLES:
  render                        Render current state.json as PDF
  render --paper tabloid        Render at tabloid size
  convert photo.jpg             Convert with floor_plan preset
  convert sketch.png --preset sketch
  density output.png            Check density of output
"""


def _interactive():
    """Interactive REPL mode."""
    print("Swell-Print v1.0 — PIAF Tactile Graphics Pipeline")
    print("Type 'help' for commands.\n")

    while True:
        try:
            raw = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0].lower()

        if cmd in ("quit", "q", "exit"):
            print("Exiting.")
            break

        if cmd in ("help", "h", "?"):
            print(HELP_TEXT)
            continue

        if cmd == "presets":
            cmd_presets(argparse.Namespace())
            continue

        if cmd == "render":
            # Parse inline args
            ns = argparse.Namespace(
                state=None, paper="letter", dpi=300, output=None,
                format="pdf", threshold=None)
            i = 1
            while i < len(parts):
                if parts[i] == "--paper" and i + 1 < len(parts):
                    ns.paper = parts[i + 1]; i += 2
                elif parts[i] == "--output" and i + 1 < len(parts):
                    ns.output = parts[i + 1]; i += 2
                elif parts[i] == "--dpi" and i + 1 < len(parts):
                    ns.dpi = int(parts[i + 1]); i += 2
                elif parts[i] == "--format" and i + 1 < len(parts):
                    ns.format = parts[i + 1]; i += 2
                elif not parts[i].startswith("--"):
                    ns.state = parts[i]; i += 1
                else:
                    i += 1
            cmd_render(ns)
            continue

        if cmd == "convert":
            ns = argparse.Namespace(
                image=None, preset="floor_plan", paper="letter",
                dpi=300, output=None, threshold=None)
            i = 1
            while i < len(parts):
                if parts[i] == "--preset" and i + 1 < len(parts):
                    ns.preset = parts[i + 1]; i += 2
                elif parts[i] == "--paper" and i + 1 < len(parts):
                    ns.paper = parts[i + 1]; i += 2
                elif parts[i] == "--output" and i + 1 < len(parts):
                    ns.output = parts[i + 1]; i += 2
                elif parts[i] == "--threshold" and i + 1 < len(parts):
                    ns.threshold = int(parts[i + 1]); i += 2
                elif parts[i] == "--dpi" and i + 1 < len(parts):
                    ns.dpi = int(parts[i + 1]); i += 2
                elif not parts[i].startswith("--"):
                    ns.image = parts[i]; i += 1
                else:
                    i += 1
            cmd_convert(ns)
            continue

        if cmd == "density":
            ns = argparse.Namespace(image=parts[1] if len(parts) > 1 else None)
            cmd_density(ns)
            continue

        print("ERROR: Unknown command '{}'. Type 'help' for commands.".format(cmd))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    _check_deps()

    ap = argparse.ArgumentParser(
        description="Swell-Print — PIAF Tactile Graphics Pipeline")
    sub = ap.add_subparsers(dest="command")

    # render subcommand
    render_p = sub.add_parser("render", help="Render state.json to tactile output")
    render_p.add_argument("state", nargs="?", default=None, help="state.json path")
    render_p.add_argument("--paper", default="letter", help="Paper size")
    render_p.add_argument("--dpi", type=int, default=300, help="DPI")
    render_p.add_argument("--output", "-o", default=None, help="Output path")
    render_p.add_argument("--format", default="pdf", help="Output format (png/pdf)")
    render_p.add_argument("--threshold", type=int, default=None)

    # convert subcommand
    convert_p = sub.add_parser("convert", help="Convert image to tactile output")
    convert_p.add_argument("image", help="Image file path")
    convert_p.add_argument("--preset", default="floor_plan", help="Preset name")
    convert_p.add_argument("--paper", default="letter", help="Paper size")
    convert_p.add_argument("--dpi", type=int, default=300, help="DPI")
    convert_p.add_argument("--output", "-o", default=None, help="Output path")
    convert_p.add_argument("--threshold", type=int, default=None, help="Threshold 0-255")

    # presets subcommand
    sub.add_parser("presets", help="List conversion presets")

    # density subcommand
    density_p = sub.add_parser("density", help="Check image density")
    density_p.add_argument("image", help="Image file path")

    args = ap.parse_args()

    if args.command == "render":
        cmd_render(args)
    elif args.command == "convert":
        cmd_convert(args)
    elif args.command == "presets":
        cmd_presets(args)
    elif args.command == "density":
        cmd_density(args)
    else:
        # No subcommand → interactive mode
        _interactive()


if __name__ == "__main__":
    main()
