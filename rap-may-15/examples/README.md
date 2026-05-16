# Examples

## Case study house example

A simple modernist case study house, used as the canonical demo for the Radical Accessibility paper. The house sits on an 80 by 60 foot site with a 48 by 24 foot footprint centered on the site. A 4 by 3 column grid carries the roof, perimeter walls enclose the floor, and the slab is extruded in tactile3d. The example works because it maps cleanly onto the controller's existing primitives: one structural bay, one wall ring with apertures, two program zones, and the tactile3d floor option. Nothing exotic, nothing custom — just the standard Radical Accessibility Controller vocabulary applied to a small house.

## The three layers

The paper frames the demo as three layers. Each layer maps onto a controller primitive.

- Layer 1 — Structure. Bay A's column grid. Three bay spans by two bay spans gives a 4 columns by 3 columns grid on 16 by 12 foot spacing. The watcher draws each column from the bay's `column_size` style.
- Layer 2 — Panels. The perimeter walls with apertures. With walls enabled and aperture entries for the south, north, east, and west faces, the watcher cuts a door and five windows into the panels surrounding the structural bay.
- Layer 3 — Slabs. The tactile3d floor option. With `tactile3d` enabled and `floor on`, the watcher extrudes a floor slab under the footprint. This is the slab the user reads with their hands.

## Run the example (load the pre-built state)

Three commands. From the `rap-may-15` folder:

1. Copy the example state into the controller:

       cp examples/case-study-house.state.json controller/state.json

2. Start the controller. The watcher attach instructions print on boot:

       ./scripts/start-mac.sh

   Expected first lines:

       OK: Controller starting. To activate the Rhino watcher, in Rhino 8 Mac type:
           _-RunPythonScript "<abs path>/rap-may-15/rhino/startup.py"

3. In Rhino 8 Mac, type the watcher command shown above. Replace `<abs path>` with the absolute path to your clone:

       _-RunPythonScript "<abs path>/rap-may-15/rhino/startup.py"

   Expected Rhino command line output:

       [STARTUP] Watcher active. Units=Feet. Ready.

   The geometry rebuilds in the viewport: site rectangle, 12 column dots, perimeter walls with the six apertures cut out, two zones, and the tactile3d slab.

## Run the example (rebuild from the macro)

Alternative path. Reach the same end state by replaying the construction commands on a default start.

1. Copy the macro into the controller's macros folder:

       cp examples/case-study-house.macro.json controller/macros/

2. Start the controller from a default state, then from the controller prompt:

       macro run case-study-house

   The macro prints one OK line per command. After the 27 commands execute, the state matches `case-study-house.state.json`.

## Capture the paper figures

Three commands, one per output format.

1. PIAF JPG:    output-cli render controller/state.json --format jpg
   Expected: OK: Rendered state_tactile.jpg (Letter, 300 DPI JPG, density N.N%)

2. SVG:         output-cli render controller/state.json --format svg
   Expected: OK: Rendered state_tactile.svg (SVG vector plan)

3. STL (from inside the controller): tactile3d export case-study-model.stl
   Expected: OK: STL written to case-study-model.stl (N triangles)

The `render` command has no `--out` flag. The output filename is auto-derived from the input as `<input-stem>_tactile.<ext>` and written next to the state file (here, `controller/state_tactile.jpg` / `controller/state_tactile.svg`). The STL exports the extruded walls and slab in one mesh, ready for the Bambu printer. `tactile3d export` takes an optional positional path; with no argument it writes to the configured `export_path` (default `./tactile3d_export.stl`).

## Inspect the source

Both example files are plain text and readable end-to-end.

- `case-study-house.state.json` is the canonical state. Top-level keys: `schema`, `meta`, `site`, `zones`, `grid`, `style`, `bays`, `blocks`, `rooms`, `legend`, `tactile3d`, `tts`, `section`, `hatch_library_path`, `print`. The bay A apertures list shows where each window and the door land on each face.
- `case-study-house.macro.json` is a 27-command macro that produces the same state from the controller's default start. Each command prints an `OK:` line, so the full run produces a screen-reader-friendly log of the construction sequence.

The `expected/` folder describes what the three captured outputs should look like, so reviewers can verify their own runs without an authoritative binary to diff against.

## Notes for the paper

The house is intentionally simple so the three layers — structure, panels, slabs — read clearly under a swell-paper print and are not confused with one another by a finger reading the page. The demo is one-directional (CLI to `state.json` to watcher to Rhino to screenshots); Rhino is a passive consumer here, never the source of truth. This file-watcher pattern is the proprietary integration that replaces jingchen-chen's rhinomcp in our pipeline, and it is what keeps the controller authoritative and Rhino crash-only.
