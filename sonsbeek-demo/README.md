# Sonsbeek Pavilion — 3D Viewer Demo

Interactive Three.js viewer for Aldo van Eyck's 1966 Sonsbeek Pavilion,
generated from a RAP Layout Jig state file.

## What's here

```
sonsbeek-demo/
  generate_state.py      Python script that builds the pavilion state JSON
  sonsbeek_state.json    Pre-generated state (ready to load)
  viewer.html            Self-contained Three.js viewer (no server needed)
  README.md              This file
```

## Quick start

1. Open `viewer.html` in any browser. A demo model loads automatically.
2. To load the Sonsbeek Pavilion instead:
   - Click **Load** (bottom bar).
   - Either click **Choose File** and select `sonsbeek_state.json`,
     or paste the JSON contents into the text area.
   - Click **Render**.

No server, no install, no dependencies. Just open the HTML file.

## Regenerating the state

```
python generate_state.py --pretty
```

Writes `sonsbeek_state.json` in the same folder. Uses Python stdlib only.

Options:
- `--pretty` — 2-space indented JSON (default is compact).
- `--out PATH` — write to a custom file path.

## Viewer controls

**Display modes** (tab bar at top):
Pen, Arctic, Shaded, Ghosted, Wireframe, Technical, X-Ray.

**Mouse / touch:**
- Left-drag: orbit.
- Right-drag / two-finger: pan.
- Scroll / pinch: zoom.

**Bottom bar:**
- **Load** — open the JSON input panel.
- **Fit** — reset camera to fit the model.
- **Theme** — toggle light / dark mode.
- **Photo** — download a screenshot (PNG).

## About the model

The Sonsbeek Pavilion (1966) was a temporary exhibition structure by
Aldo van Eyck in Arnhem, Netherlands. The design is a field of 7
parallel north-south masonry walls of varying lengths with portal
openings, plus 3 column clusters — all within a 100 x 100 ft site.

Walls are 46 ft (14 m) tall and 2 ft (0.6 m) thick. The state file
models each wall as a single-bay rectangular grid element with wall
flags and portal apertures.

## How the viewer works

`viewer.html` is a single self-contained HTML file (~60 KB). It loads
Three.js r128 from a CDN and contains all rendering logic inline.

**Data flow:**

1. The viewer reads a Layout Jig `state.json` (schema v2.3).
2. It iterates over `state.bays`, reading each bay's origin, spacing,
   rotation, wall flags, apertures, and corridor settings.
3. For each bay it builds Three.js `BoxGeometry` for walls (with gaps
   cut for apertures) and `CylinderGeometry` for columns at grid
   intersections.
4. Display modes swap materials — e.g. Pen mode uses `MeshBasicMaterial`
   with `wireframe: false` and edge lines; Ghosted uses transparency;
   X-Ray uses wireframe with depth-write off.

**No backend.** Everything runs client-side. The JSON is parsed in the
browser and geometry is built on the fly.
