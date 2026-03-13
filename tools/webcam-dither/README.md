# Webcam Dither

Live webcam dithertone converter for PIAF tactile printing.

Captures webcam video and applies real-time dithertone processing where dot size varies with brightness. Darker areas produce bigger dots, lighter areas produce smaller or no dots. Take screenshots and export PIAF-ready PDFs.

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
