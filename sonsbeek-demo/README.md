# Sonsbeek Pavilion — 3D Viewer

Interactive Three.js viewer for Aldo van Eyck's 1966 Sonsbeek Pavilion,
modeled from the original 1:100 plan drawing (Feb 19, 1966).

## What's here

```
sonsbeek-demo/
  generate_sonsbeek.py   Python script that builds the pavilion geometry JSON
  sonsbeek.json          Pre-generated geometry (ready to load)
  viewer.html            Self-contained Three.js viewer (no server needed)
  README.md              This file
```

## Quick start

Open `viewer.html` in any modern browser. The Sonsbeek Pavilion loads
immediately in Pen mode with hidden-line rendering.

No server, no install, no build step. Just open the HTML file.

## Regenerating the geometry

```
python generate_sonsbeek.py --pretty
```

Writes `sonsbeek.json`. Uses Python stdlib only (no pip dependencies).

Options:
- `--pretty` — 2-space indented JSON (default is compact).
- `--out PATH` — write to a custom file path.

## Display modes

The viewer supports 6 display modes, selectable from the top-right buttons:

**Pen** (default) — Rhino-style pen rendering:
- White surfaces with black solid edge lines for visible edges.
- Hidden edges rendered as gray dashed lines (depth-compared).
- Graphic silhouette outline via back-face shell expansion.
- Uses a custom GLSL shader that compares each edge pixel's depth
  against a pre-rendered depth texture of the surfaces.

**Shaded** — Warm concrete-colored surfaces with directional shadows.
Uses hemisphere lighting (warm sky / cool ground) plus a shadow-casting
directional light and a fill light.

**Arctic** — Pure white surfaces with shadows for depth.

**Ghosted** — Semi-transparent surfaces with visible edge lines.
Shows the spatial relationships between overlapping elements.

**Wire** — Wireframe mesh only. No filled surfaces.

**X-Ray** — Transparent blue wireframe. All geometry visible through
all other geometry.

## Controls

**Mouse / trackpad:**
- Left-drag: orbit
- Right-drag / two-finger drag: pan
- Scroll / pinch: zoom

**Buttons (bottom right):**
- Square: fit camera to model
- Circle: toggle dark/light theme
- Arrow: load a different JSON file

## How the viewer works

### Geometry format

The JSON file uses a custom format (not RAP state.json). It defines:

- **`walls`** — Straight parallel walls. Each has an `x` position,
  `thickness`, `height`, and an array of `segments` (y_start, y_end).
  Gaps between segments are portal openings.

- **`curved_walls`** — Semicircular arc walls. Each has a `center`,
  `radius`, `start_angle_deg`, `end_angle_deg`, `height`, `thickness`.
  The arc is extruded vertically. Angles use plan convention:
  0 = east, 90 = north, 180 = west, 270 = south.

- **`discs`** — Circular concrete screen elements. Each has a `center`,
  `radius`, and `height`. Rendered as vertical cylinders.

- **`low_walls`** — Short walls (0.90 m). Same format as walls.

- **`site`** — Circle radius and platform dimensions.

### Coordinate mapping

The JSON uses plan coordinates (X = east-west, Y = north-south).
The viewer maps to Three.js coordinates:
- Plan X → Three.js X (same)
- Plan Y → Three.js -Z (north goes into the screen)
- Height → Three.js Y (up)

### Curved wall geometry

Curved walls are built as custom `BufferGeometry` with inner/outer
radius arcs extruded vertically. For each of 32 arc samples, 4
vertices are created (inner-bottom, inner-top, outer-bottom, outer-top),
then connected with indexed triangles for inner face, outer face, top,
bottom, and end caps. Normals are auto-computed.

### Hidden-line rendering (Pen mode)

The Pen mode uses a 4-pass rendering pipeline:

1. **Depth pass** — Surfaces are rendered to an offscreen
   `WebGLRenderTarget` with a `DepthTexture`. Only the depth buffer
   is needed.

2. **Outline pass** — Silhouette outlines (back-face shell meshes)
   are rendered to the screen. These are copies of each mesh with
   vertices expanded along normals by 0.02-0.025 m, rendered with
   `THREE.BackSide`. They appear only where they extend beyond the
   original mesh edges.

3. **Surface pass** — White surfaces are rendered on top, covering
   the outlines except at silhouette edges.

4. **Edge pass** — All edge lines are rendered with a custom GLSL
   `ShaderMaterial` that reads the depth texture from pass 1.
   For each fragment:
   - If the edge's depth < scene depth: **solid black** (visible edge)
   - If the edge's depth > scene depth: **dashed gray** (hidden edge)

   The dashing uses the `lineDistance` attribute from
   `computeLineDistances()` for consistent dash spacing along each
   edge segment.

### Rendering layers

Three.js layers separate object types for multi-pass rendering:
- Layer 0: surface meshes
- Layer 1: edge line segments
- Layer 2: silhouette outline meshes

The camera's layer mask is changed between passes to render only
the appropriate objects.

## About the pavilion

The Sonsbeek Pavilion (1966) was a temporary exhibition structure by
Aldo van Eyck in Sonsbeek Park, Arnhem, Netherlands. The design is a
field of 8 parallel north-south masonry walls (B5 concrete blocks,
0.20 m thick, ~2.87 m tall) within a circular ground plane (~9 m
radius). Between the inner wall pairs, semicircular curved wall
segments create intimate pocket spaces, forming a labyrinthine spatial
sequence. Five freestanding circular concrete disc screens
("schijven") punctuate the composition.

The spatial concept embodies Van Eyck's principle of "labyrinthine
clarity" — a complex yet navigable arrangement of walls that creates
a rich sequence of in-between spaces without ever fully enclosing
them.
