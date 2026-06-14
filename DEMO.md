# Accessible Rhino Demo — 10-Minute Runbook

A blind student drives Rhino with Claude through the web UI: draw a plan,
raise it into 3D walls, give each room a tactile floor texture, and keep
everything in one JSON file. No screen required on the student's side.

The whole demo runs from one template plus a few spoken commands. Read this
once, do the pre-flight, then follow the script.

---

## What the audience will see

1. The student talks to Claude in the browser.
2. Claude writes `controller/state.json`.
3. Rhino redraws automatically: grid, walls, rooms, then a 3D tactile model
   with raised floor textures.

The student never touches Rhino. Rhino is a viewer; the JSON is the truth.

---

## Pre-flight (do this BEFORE the meeting)

Three things must be running. Confirm each, then leave them up.

1. **First-time setup (once).** From the repo root, in cmd.exe:

   ```
   python setup.py
   ```

   This installs `mcp`, writes `.mcp.json`, and creates `controller/state.json`.

2. **Rhino + watcher.** Open Rhino, open the Python editor (F2 /
   EditPythonScript), paste these two lines, edit the path, press F5:

   ```
   __file__ = r"C:\path\to\Radical-Accessibility-Toolkit\tools\rhino\rhino_watcher.py"
   exec(open(__file__).read())
   ```

   You should see `[PLJ] Ready.` on the Rhino command line. The watcher reads
   `controller/state.json` automatically.

3. **Web UI.** Start it and open the browser tab:

   ```
   tools/webui/start-webui.sh        (WSL)   — or   start-webui.bat (Windows)
   ```

   Then open `http://localhost:8788`. This is the accessible chat the student
   drives. It talks to Claude, which calls the Layout Jig MCP functions.

**Smoke test (30 seconds, before the audience arrives):** in the web UI, say
"Load the simple building template." Rhino should show a 3-by-2 grid with
walls, three rooms, and a 3D model with raised floor textures. Then say
"Undo that" or reload, so you start clean.

---

## The 10-minute script

Spoken lines are what the **student says** to Claude. Each maps to a Layout
Jig command behind the scenes (named in parentheses).

### 1. Draw a plan — 2 min

> "Load the simple building template."
*(template_load simple-building)*

Rhino draws a 36 ft by 24 ft building: a 3-bay-by-2-bay grid, a wall around
the outside, a front door, and three rooms — Studio, Gallery, Office. Claude
reads back a short text description so the student hears the result.

Optional, to show it is live and parametric:

> "Make each structural bay 14 feet instead of 12."
*(template load simple-building bay_width=14)* — or — "Add a window on the east wall."
*(add_aperture)*

### 2. Make 3D walls — 2 min

The template already turns the 3D tactile model on, so the walls are already
extruded. Show that it is adjustable:

> "Raise the walls to 10 feet."  *(tactile3d wall_height 10)*

> "Cut the model at 6 feet so we can see into the rooms."  *(tactile3d cut_height 6)*

Rhino re-extrudes the walls and the clipping plane drops in. Point out: the
walls open exactly where the door is — apertures are real gaps, not drawn-on.

### 3. Hatch the floor with tactile patterns — 2 min

Each room already has a different raised floor texture you can feel apart:
Studio = ridges, Gallery = waffle, Office = bumps. Demonstrate changing one:

> "Give the Office floor ridges instead of bumps."
*(cell A 2,0 hatch diagonal; cell A 2,1 hatch diagonal)*

> "Actually, turn the floor textures off for a second... now back on."
*(tactile3d floor_hatch off / on)*

This is the accessibility point: a blind reader runs a finger across the floor
and knows which room they are in by texture alone.

### 4. Save the state in JSON — 1 min

> "Save a snapshot called demo."  *(snapshot save demo)*

> "Describe the whole model."  *(describe)*

Explain: everything — plan, walls, rooms, textures — lives in one
`controller/state.json`. If Rhino crashes mid-demo, restart it, run the
watcher, and the model rebuilds from the file. Nothing is lost.

### 5. Hand it to the printer — 1 min

> "Export the 3D model to STL."  *(tactile3d export)*

The same JSON also drives a 2D PIAF tactile plan (via TACT) and a Bambu 3D
print. One model, three physical outputs.

### 6. Questions — 2 min buffer.

---

## If something misbehaves

- **Rhino did not update.** The watcher rebuilds on file change. Re-save by
  re-running the last command, or in Rhino press F5 to re-run the watcher.
- **Rhino crashed.** Restart Rhino, re-run the watcher (pre-flight step 2).
  The model rebuilds from `controller/state.json`.
- **Web UI stalls.** Fall back to the typed CLI in cmd.exe — same commands,
  same JSON, same live Rhino:

  ```
  python controller/controller_cli.py
  >> template load simple-building
  >> tactile3d cut_height 6
  >> cell A 2,0 hatch diagonal
  >> snapshot save demo
  >> describe
  ```

Both paths write the same `controller/state.json`, so you can switch between
the web UI and the terminal at any time without losing the model.

---

## Cheat sheet — what each room feels like

- Studio (west) — parallel ridges.
- Gallery (center) — a waffle grid.
- Office (east) — a field of bumps.

Texture names you can assign to any room: `diagonal` (ridges),
`crosshatch` (waffle), `dots` (bumps).
