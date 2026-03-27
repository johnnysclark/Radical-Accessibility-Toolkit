# TASC - Tactile Architecture Scripting Console

Accessible programmatic Rhino design for tactile architecture. Part of the Radical Accessibility Project at UIUC.

TASC gives blind and low-vision architects direct, programmatic control of site layouts via an accessible CLI with text feedback, live Rhino viewport updates, and tactile PIAF output.

---

## Setup

TASC lives inside the Radical-Accessibility-Toolkit repo under tools/. It depends on TACT, so install both.

```bash
# From the repo root
cd path/to/Radical-Accessibility-Toolkit

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install TACT first (TASC depends on it), then TASC
pip install -e tools/tact/
pip install -e tools/tasc/

# Verify installation
tasc version
```

You should see:

```
TASC - Tactile Architecture Scripting Console v0.1.0
Part of the Radical Accessibility Project at UIUC
```

**Note:** You must activate the venv (`source venv/bin/activate`) in every new terminal session before using `tasc`.

---

## Quick Start

TASC has two modes of use:

1. **Interactive CLI** -- build up a site step by step with individual commands
2. **Script mode** -- write a `.py` file using the Python DSL and run it all at once

### Interactive CLI Example

```bash
# 1. Define a 200x150 foot site
tasc site 200 150

# 2. Add a 10-foot structural grid
tasc grid 10

# 3. Place zones
tasc zone living 50 40 --at 10,10
tasc zone kitchen 30 40 --at 70,10
tasc zone circulation 10 40 --at 100,10

# 4. See what you have
tasc describe

# 5. Export
tasc export text              # text description file
tasc export 3dm               # Rhino .3dm file (works offline)
tasc export piaf              # tactile PDF for PIAF printer

# 6. Clean up when done
tasc reset
```

### Script Mode Example

Create a file called `my_site.py`:

```python
from tasc_core.dsl.api import *

boundary(200, 150, units="feet")
grid(10)

zone("living", 50, 40, at=(10, 10))
zone("kitchen", 30, 40, at=(70, 10))
zone("circulation", corners=[(100,10), (110,10), (110,50), (100,50)])

describe()
export("text", output="my_site_description.txt")
```

Run it:

```bash
tasc my_site.py                # auto-routes to 'tasc run my_site.py'
tasc my_site.py --no-rhino     # skip Rhino connection (offline only)
```

---

## CLI Command Reference

TASC uses a DefaultGroup pattern: `tasc my_file.py` automatically routes to `tasc run my_file.py`. All other commands are explicit subcommands.

### `tasc site WIDTH DEPTH`

Define a rectangular site boundary.

```bash
tasc site 200 150                    # 200x150 feet (default)
tasc site 60 40 --units meters       # 60x40 meters
```

**Options:**
- `--units [feet|meters]` -- unit system (default: feet)

**Output:**
```
Site boundary created. 200 by 150 feet. Area: 30,000 square feet.
```

---

### `tasc grid SPACING`

Apply a structural grid to the current site.

```bash
tasc grid 10                         # 10-foot grid
tasc grid 5 --rotation 45            # 5-foot grid rotated 45 degrees
```

**Options:**
- `--rotation DEGREES` -- grid rotation (default: 0)

**Output:**
```
Grid applied. 20 by 15 cells, 10 feet spacing.
```

---

### `tasc zone NAME [WIDTH DEPTH] [--at X,Y] [--corners ...]`

Place a zone. Two forms:

**Rectangular zone:**
```bash
tasc zone living 50 40 --at 10,10
tasc zone kitchen 30 20 --at 70,10 --type service
```

**Polygon zone (arbitrary corners):**
```bash
tasc zone lobby --corners "0,0 20,0 20,15 0,15"
```

**Options:**
- `--at X,Y` -- position for rectangular zone (default: 0,0)
- `--corners "X1,Y1 X2,Y2 ..."` -- corner list for polygon zone
- `--type LABEL` -- program type label (e.g. residential, circulation, service)

**Output:**
```
living zone placed at 10, 10. 50 by 40 feet. Area: 2,000 square feet.
  Distances to boundary: north 100 feet, south 10 feet, east 140 feet, west 10 feet.
```

**Warnings** are issued automatically if a zone extends past the site boundary or overlaps with existing zones.

---

### `tasc bay NAME [DIMS] [--spacing SX SY] [--at X,Y]`

Place a structural bay with columns. Bays define a column grid; zones define program areas. Use both together.

```bash
tasc bay A 6x3 --spacing 24 24 --at 18,8
tasc bay B 3x3 --spacing 30 30 --column-size 2.0
tasc bay MAIN 5x3 --spacing-x 24,30,24,18,24
```

**Options:**
- `DIMS` -- grid dimensions as NxN (e.g. 6x3 = 6 columns by 3 rows)
- `--spacing SX SY` -- uniform spacing in feet (default: 24 24)
- `--spacing-x X1,X2,...` -- irregular x-axis spacing
- `--spacing-y Y1,Y2,...` -- irregular y-axis spacing
- `--at X,Y` -- origin position (default: 0,0)
- `--rotation DEGREES` -- rotation (default: 0)
- `--column-size FEET` -- column width (default: 1.5)

**Output:**
```
Bay A placed at 18, 8. 6 by 3 bays at 24 by 24 foot spacing. 28 columns.
```

---

### `tasc corridor BAY_NAME [on|off] [--axis x|y] [--width FEET]`

Add or remove a corridor within a bay.

```bash
tasc corridor A on --axis x --width 8
tasc corridor B on --axis y --width 10 --loading single --position 2
tasc corridor C off
```

**Options:**
- `on|off` -- enable or disable corridor (default: on)
- `--axis [x|y]` -- corridor direction: x = east-west, y = north-south
- `--width FEET` -- corridor width in feet
- `--loading [single|double]` -- single or double loaded (default: single)
- `--position INDEX` -- gridline index where corridor runs (default: 0)

**Output:**
```
Corridor enabled on Bay A. East-west, 8 feet wide, single-loaded.
```

---

### `tasc void BAY_NAME [SHAPE] [SIZE] [--at X,Y]`

Cut a void (courtyard, atrium, lightwell) within a bay.

```bash
tasc void A rectangle 30x18 --at 90,44
tasc void B circle 24
tasc void C off                          # remove void
```

**Options:**
- `SHAPE` -- rectangle, circle, or off (default: rectangle)
- `SIZE` -- WxH for rectangle or diameter for circle (default: 20x20)
- `--at X,Y` -- center position in bay-local coordinates

**Output:**
```
Void set on Bay A. Rectangle, 30 by 18 feet, center 90, 44.
```

---

### `tasc label NAME "TEXT" [--braille "BRAILLE"]`

Set a text label (and optional Braille) on a zone or bay.

```bash
tasc label A "Library" --braille "⠇⠊⠃⠗⠁⠗⠽"
tasc label living "Living Room"
```

**Output:**
```
Label set on A. Text: Library. Braille: ⠇⠊⠃⠗⠁⠗⠽.
```

---

### `tasc undo`

Revert the last command. Each command automatically saves an undo checkpoint to `.tasc_undo.json`.

```bash
tasc undo
```

**Output:**
```
Undo: restored previous state.
Site: 200 x 150 feet
Bay A: 6x3 at (18, 8)
```

If there is nothing to undo:
```
Nothing to undo.
```

---

### `tasc remove NAME`

Remove a zone or bay by name (case-insensitive).

```bash
tasc remove kitchen
tasc remove A
```

---

### `tasc list`

Short listing of current model state, including zones and bays.

```bash
tasc list
```

**Output:**
```
Site: 200 x 150 feet
Grid: 10 spacing
Zones:
  living: 50 x 40 at (10, 10)
  kitchen: 30 x 40 at (70, 10)
Bays:
  A: 6x3 at (18, 8), 24x24 spacing, 28 columns
```

---

### `tasc describe`

Full text description with dimensions, areas, coverage, and structural info.

```bash
tasc describe
```

**Output:**
```
Site: 200 by 150 feet. Area: 30,000 square feet.
Grid: 10 feet spacing. 20 by 15 cells.
Zones (2):
  1. living: 50 by 40 feet at 10, 10. Area: 2,000 sq feet.
  2. kitchen: 30 by 40 feet at 70, 10. Area: 1,200 sq feet.
Bays (1):
  1. A: 6 by 3 bays at 24 by 24 foot spacing. 28 columns. Origin: 18, 8.
Total program area: 3,200 square feet.
Site coverage: 10.7%. Remaining area: 26,800 square feet.
```

---

### `tasc export [piaf|3dm|text]`

Export the current model.

```bash
tasc export text                     # text description → tasc_output.txt
tasc export 3dm                      # Rhino file → tasc_output.3dm (works offline)
tasc export piaf                     # tactile PDF → tasc_output.pdf (via TACT)
tasc export text -o my_site.txt      # custom output path
```

**Options:**
- `-o, --output PATH` -- output file path (auto-generated if omitted)

---

### `tasc connect`

Test Rhino connection status.

```bash
tasc connect
tasc connect --host 192.168.1.10 --port 1999
```

TASC tries three connection methods in order:
1. **MCP socket** (port 1999) -- requires RhinoMCP plugin running in Rhino
2. **RhinoCode CLI** -- requires `rhinocode` binary and Rhino running
3. **Offline** -- model tracked locally, .3dm export still works

---

### `tasc reset`

Clear all model state and Rhino objects.

```bash
tasc reset
```

---

### `tasc version`

Show version information.

```bash
tasc version
```

---

### `tasc run SCRIPT.py`

Execute a TASC Python DSL script. You rarely type this directly because the DefaultGroup routes `tasc my_file.py` here automatically.

```bash
tasc run my_site.py
tasc run my_site.py --no-rhino       # skip Rhino connection
```

---

## Python DSL Reference

For script mode, import everything from the DSL:

```python
from tasc_core.dsl.api import *
```

### `boundary(width, depth, units="feet")`

Define a rectangular site boundary.

```python
boundary(200, 150)                              # 200x150 feet
boundary(60, 40, units="meters")                # 60x40 meters
boundary(corners=[(0,0), (200,0), (200,150), (0,150)])  # polygon
```

### `grid(spacing, rotation=0, origin=(0,0))`

Set up a structural grid.

```python
grid(10)                                        # 10-unit grid
grid(5, rotation=30)                            # rotated grid
```

### `zone(name, width, depth, at=(x,y))`

Place a zone.

```python
zone("living", 50, 40, at=(10, 10))             # rectangle
zone("lobby", corners=[(0,0), (20,0), (20,15), (0,15)])  # polygon
zone("kitchen", 30, 20, at=(60, 10), program_type="service")
```

### `remove(name)`

Remove a zone by name.

```python
remove("kitchen")
```

### `describe()`

Print full model description to stdout and return it as a string.

### `list_model()`

Print short model listing.

### `export(format, output=None)`

Export the model.

```python
export("text")                                  # → tasc_output.txt
export("3dm", output="my_design.3dm")           # → my_design.3dm
export("piaf", output="tactile_output.pdf")     # → tactile PDF
```

### `connect(host, port)`

Explicitly connect to Rhino (auto-connects on first operation by default).

```python
connect("127.0.0.1", 1999)
```

### `reset()`

Clear the model and Rhino objects.

### `get_model()`

Get the underlying `TASCModel` object for advanced use.

---

## State Persistence

Interactive CLI commands (`tasc site`, `tasc zone`, etc.) save state to `.tasc_state.json` in the current working directory. This means commands accumulate across invocations:

```bash
tasc site 200 150      # creates .tasc_state.json
tasc zone living 50 40 --at 10,10   # adds to existing state
tasc describe          # shows both site and zone
tasc reset             # clears .tasc_state.json
```

Each command also saves an undo checkpoint to `.tasc_undo.json`. Run `tasc undo` to revert the last change. Both files are gitignored.

Script mode (`tasc run`) executes from scratch and does not use the state file.

---

## Rhino Connection

### Option A: Open .3dm files (no setup needed)

```bash
tasc site 200 150
tasc zone living 50 40 --at 10,10
tasc export 3dm
```

Open `tasc_output.3dm` in Rhino. This works completely offline.

### Option B: Live viewport (requires RhinoMCP)

For real-time geometry updates as you type commands, install the [RhinoMCP plugin](https://github.com/jingcheng-chen/rhinomcp):

1. In Rhino, go to **Tools > Package Manager**
2. Search for `rhinomcp` and click **Install**
3. Restart Rhino
4. In Rhino's command line, type `MCPStart`
5. From your terminal:

```bash
tasc connect    # should say "Connected to Rhino via MCP socket"
tasc site 200 150    # geometry appears live in viewport
```

TASC creates these layers in Rhino:

- **TASC_Site** -- site boundary (black)
- **TASC_Grid** -- grid lines (light gray)
- **TASC_Zones** -- zone outlines (dark gray)
- **TASC_Labels** -- text labels (black)
- **TASC_Bays** -- bay grid lines (gray)
- **TASC_Columns** -- column squares (black)
- **TASC_Corridors** -- corridor rectangles (medium gray)
- **TASC_Voids** -- void shapes (light gray)

Without Rhino, everything still works -- the model is tracked locally, text feedback is identical, and `.3dm` / text exports work offline. Only live viewport updates require a Rhino connection.

### Option C: Live viewport from WSL2 (Rhino on Windows)

When Rhino runs on Windows but TASC runs inside WSL2, TASC **automatically detects WSL2** and routes the MCP connection through the Windows gateway IP. No manual host configuration needed.

**One-time setup:** RhinoMCP binds to `127.0.0.1` on Windows, which isn't directly reachable from WSL2. You need a Windows port proxy:

1. Open an **admin PowerShell** on Windows and run:

```powershell
netsh interface portproxy add v4tov4 listenport=1999 listenaddress=0.0.0.0 connectport=1999 connectaddress=127.0.0.1
netsh advfirewall firewall add rule name="RhinoMCP" dir=in action=allow protocol=TCP localport=1999
```

2. Start RhinoMCP in Rhino (`MCPStart`), then from WSL2:

```bash
tasc connect    # auto-detects WSL2 gateway, connects to Rhino on Windows
```

To remove the proxy later:

```powershell
netsh interface portproxy delete v4tov4 listenport=1999 listenaddress=0.0.0.0
netsh advfirewall firewall delete rule name="RhinoMCP"
```
