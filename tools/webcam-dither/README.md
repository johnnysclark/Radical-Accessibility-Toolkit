# Webcam Dither

Live webcam dithertone converter for PIAF tactile printing.

Captures webcam video and applies real-time dithertone processing where dot size varies with brightness. Darker areas produce bigger dots, lighter areas produce smaller or no dots. Take screenshots and export PIAF-ready PDFs.

## Browser App

Open `browser/photo.html` directly on any device. Supports photo capture, library import, and live camera mode. All processing happens client-side.

## What is Dithering?

Dithering converts a photograph with continuous shades of gray into a pattern of pure black and white marks. This is essential for PIAF tactile printing, which can only raise or not raise the paper. Different algorithms create different visual and tactile textures while preserving the impression of the original image.

## Algorithms

- **Dots** — Variable-size shapes (circle, cross, dash, diamond) on a regular grid. Darker areas get bigger shapes. Predictable spacing makes it a good default for tactile printing.
- **Floyd** — Floyd-Steinberg error diffusion. Rounds each pixel to black or white and spreads the rounding error to neighbors. Produces detailed, organic results.
- **Atkinson** — Bill Atkinson's error diffusion from the original Macintosh. Lighter and more open than Floyd because it intentionally discards some error. Less cluttered for tactile use.
- **Bayer** — Ordered dithering with a 4x4 threshold matrix. Creates a regular grid-like pattern with a retro/digital look. Highly structured and easy to read by touch.
- **Halftone** — Diamond-shaped dots on a 45-degree rotated grid. Dots grow and merge into a connected diamond mesh at mid-tones. Classic amplitude-modulated print screen.
- **Lines** — Horizontal bars with variable thickness. Simple and effective for architectural drawings.
- **Hatch** — Cross-hatching that layers lines at different angles based on darkness level (1 to 4 directions). Mimics pen-and-ink illustration.
- **Engrave** — Continuous diagonal lines with variable thickness. Produces the look of engraved banknotes or etched illustrations.
- **Stipple** — Randomly placed dots with density proportional to darkness. Hand-drawn pointillist effect. Deterministic (same image always produces same output).
- **OX** — Two mark shapes: O (circle outlines) for light areas, X (diagonal crosses) for dark. You can feel the difference by mark shape, not just density.

## Install

```bash
pip install -e tools/webcam-dither
```

For PIAF PDF export, also install tactile-core:

```bash
pip install -e tools/tact
```

## Usage

Start live dithering:

```bash
webcam-dither live
```

With an iPhone or IP camera:

```bash
webcam-dither live --camera http://192.168.1.5:4747/video
```

Single-shot capture:

```bash
webcam-dither snapshot -o output.png
```

Bracket capture (tight, medium, loose spacing):

```bash
webcam-dither snapshot --bracket
```

## Keyboard Controls (live mode)

- q / ESC: Quit
- SPACE: Take screenshot
- b: Bracket shot (3 spacing variants)
- +/=: Increase spacing (fewer, bigger dots)
- -: Decrease spacing (more, smaller dots)
- [/]: Decrease/increase gamma
- c/v: Increase/decrease contrast
- i: Toggle invert
- r: Reset parameters
- p: Toggle PIAF auto-export
