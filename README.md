# Layout Jig

A terminal-driven architectural plan generator built for blind and low-vision architecture students. Part of the [Radical Accessibility Project](https://github.com/johnnysclark/radical-accessibility) at UIUC School of Architecture.

The tool treats non-visual interaction as the primary design case. All design intent is expressed through typed commands and confirmed through text output compatible with screen readers (JAWS, NVDA) and braille displays.

## How It Works

```
Terminal (controller_cli.py)
        |
        | writes
        v
    state.json  (canonical model artifact)
        |
        | watches (file mtime)
        v
Rhino 8 (rhino_watcher.py)
        |
        v
    2D plan drawing + optional 3D tactile model
```

The controller and Rhino never communicate directly. The JSON file is the only coupling. If Rhino crashes, nothing is lost — restart Rhino, run the watcher, everything rebuilds from state.json.

## Requirements

- **Python 3.8+** (stdlib only, no pip installs)
- **Rhino 8** (for the watcher; the controller runs independently)
- **Windows** (Rhino requirement; controller works cross-platform)

## Quick Start

**1. Run the controller:**
```
python controller_cli.py
```

**2. In Rhino 8, open EditPythonScript and run:**
```python
exec(open("C:/path/to/rhino_watcher.py").read())
```

The watcher polls state.json every 0.5 seconds and rebuilds geometry on every change.

**3. Type commands in the terminal:**
```
>> set bay A origin 20 10
OK: Bay A origin = (20.0, 10.0). Was (18.0, 8.0).

>> wall A on
OK: Bay A walls ON, 6-inch thick.

>> aperture A add d1 door x 0 10 3 7
OK: Bay A aperture 'd1' added: door, x-gridline 0, 3.0 x 7.0 ft.

>> describe
(full model description, screen-reader-friendly)
```

## Files

| File | Runtime | Purpose |
|------|---------|---------|
| `controller_cli.py` | Python 3 | Terminal interface. Validates input, manages undo, writes state.json. |
| `rhino_watcher.py` | IronPython 2.7 (inside Rhino) | Watches state.json, rebuilds geometry on change. Read-only on state. |
| `state.json` | — | The canonical model artifact. Complete design state in human-readable JSON. |
| `tactile_print.py` | Python 3 | Generates watertight STL meshes for 3D printing. Bambu Lab printer integration. |
| `MANUAL.docx` | — | User documentation. |

## Features

**Structural grids:** Rectangular and radial grids with configurable bay counts, spacing (regular or irregular), rotation, and z-ordering for overlapping grids.

**Walls and apertures:** Walls on gridlines with doors (arc swing symbol), windows (glass line), and portals (bracket marks). Full control over placement, dimensions, hinge side, and swing direction.

**Corridors:** Single or double-loaded corridors along any gridline with configurable width, dashed centerline, and hatch fill.

**Cell rooms:** Subdivide bays into named rooms with area calculations, hatch patterns, and braille labels.

**Legend:** Auto-generated braille + English legend with hatch swatches and aperture symbols.

**Tactile output:** PIAF-optimized line weights for swell paper. Four weight tiers: heavy (columns), medium (corridors/walls), light (gridlines), fine (hatches).

**3D printing:** Extrude walls to a configurable cut height, generate watertight STL, slice with OrcaSlicer, and send directly to a Bambu Lab printer — all from the terminal.

## Command Reference

```
describe ............... Full model description
list bays .............. Compact bay table
undo ................... Revert last change
help ................... All commands

set bay A origin 20 10         set bay A bays 6 3
set bay A spacing 24 24        set bay A rotation 30
set bay A grid_type radial     set bay A z_order 2

wall A on                      wall A thickness 0.5
corridor A on                  corridor A width 8
corridor A axis x              corridor A position 1

aperture A add d1 door x 0 10 3 7
aperture A set d1 swing negative
aperture A list                aperture A remove d1

cell A 0,0 name "Office"       cell A 0,0-2,1 name "Open Plan"
cell A rooms                   cell A auto_corridor

room list                      legend on
tactile3d on                   tactile3d cut_height 4

bambu config ip 192.168.1.100
bambu preview                  bambu print
```

## Architecture Principles

- **Text is the universal interface.** Every command is typed. Every response is printed. Everything works with screen readers.
- **The JSON is the design.** state.json captures complete design intent. The Rhino viewport is a rendering, not the source of truth.
- **Crash-only viewer.** Rhino can crash anytime. The design lives in state.json, not in Rhino's memory.
- **Zero dependencies.** The controller uses Python stdlib only. No pip, no conda, no venv.
- **Atomic writes.** State is written via tmp file + os.replace. The watcher never reads a half-written file.

## Project Context

This tool is part of a research project exploring what happens when architectural design tools are built for blindness first. The thesis: accessibility constraints produce genuinely better workflows — crash resilience, semantic clarity, auditable state, and full keyboard operability emerge naturally when visual interaction is removed as a dependency.

The primary user is Daniel, a blind graduate architecture student at UIUC who co-designs all tools and uses JAWS/NVDA with a braille display.

## License

MIT
