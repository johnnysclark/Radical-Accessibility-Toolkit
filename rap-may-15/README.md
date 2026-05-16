# rap-may-15

## Overview

macOS demo for the Radical Accessibility Toolkit. Four components: CONTROLLER (the authoritative CLI in `controller/`), STATE (the canonical JSON model at `controller/state.json`), WATCHER (the Rhino-side rebuilder in `rhino/`), and MCP (the proprietary Model Context Protocol bridge in `mcp/`, no rhinomcp). Produces three tactile-ready outputs: PIAF JPG (swell-paper raster), SVG (vector for screen review or further processing), and STL (3D-printable relief). No WebUI, no third-party Rhino plugins.

## Install

    cd rap-may-15
    python3 setup.py

Pass `--allow-non-mac` to override the platform check on Linux or Windows.

## Run the demo

Step 1. Launch the controller:

    ./scripts/start-mac.sh

Expected output:

    OK: Controller starting. To activate the Rhino watcher, in Rhino 8 Mac type:
        _-RunPythonScript "/path/to/rap-may-15/rhino/startup.py"

Step 2. In Rhino 8 Mac, type at the command line:

    _-RunPythonScript "/path/to/rap-may-15/rhino/startup.py"

Step 3. Drive the controller from the prompt:

    site corners 0 0 100 0 100 80 0 80
    zone add lobby corners 10 10 40 10 40 40 10 40
    tactile3d export demo.stl

Each command prints `OK: ...` on success or `ERROR: ...` on failure, followed by `READY:` when the state has settled.

## Capture screenshots

Render the current state to a PIAF JPG:

    output-cli render controller/state.json --format jpg --out fig1.jpg

Expected: `OK: Wrote fig1.jpg`.

Render to SVG:

    output-cli render controller/state.json --format svg --out fig1.svg

Expected: `OK: Wrote fig1.svg`.

Export an STL from the controller:

    tactile3d export demo.stl

Expected: `OK: Wrote demo.stl`.

Rhino viewport screenshots can be captured with macOS Shift-Cmd-4 once the watcher has rebuilt the model.

## Layout

- `controller/` — the authoritative CLI and state engine.
- `rhino/` — the watcher script that runs inside Rhino 8 Mac (`startup.py`).
- `output/` — the renderer package (PIAF JPG, SVG, STL) and its MCP entry point.
- `mcp/` — the proprietary controller MCP server.
- `scripts/` — macOS launcher helpers.

## What's not here

- WebUI — the accessible web front-end is omitted for this lean macOS demo.
- Image describer — vision-to-text tooling is not bundled.
- Web viewer — no browser-based geometry viewer.
- TASC parallel CLI — only the main controller CLI is included.
- Laser-cut export — SVG is produced but no cutter-specific job files.
- Bambu printer integration — STL is produced but printer drivers are not bundled.

## Troubleshooting

Q: rhino not found.
A: Confirm Rhino 8 is installed at `/Applications/Rhino 8.app`. The watcher requires Rhino 8 for Mac. Output: `ERROR: Rhino 8 not found at /Applications/Rhino 8.app`.

Q: watcher not running.
A: In Rhino 8 Mac, run the `_-RunPythonScript "..../rhino/startup.py"` line shown by `start-mac.sh`, then type `setup status` in the controller. Expected: `OK: Watcher attached.` If you see `ERROR: Watcher not detected.`, retry the script.

Q: output package not found.
A: Re-run `python3 setup.py` from the `rap-may-15/` folder. Expected: `OK: Installing output package...` followed by `OK: Setup complete.`
