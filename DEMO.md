# Accessible Rhino Demo — Recreate-From-Scratch Script

A blind student drives Rhino with Claude through a web UI: draw a plan, see
3D walls, and feel every space by its 2D floor texture — all kept in one JSON
file. No screen required on the student's side.

This is written as a script. Follow it top to bottom and you will have the
demo running. Anything in a code block is meant to be copied verbatim. Lines
the **student says** are in quotes; the command Claude runs is named after it.

The model used here is the `simple-building` template: **two volumes that
union into one L-shaped building, set at an angle, sharing a bent hallway**,
with a distinct 2D texture on each room and on the hallway.

---

## Part 0 — What you need (once)

1. Windows PC with **Rhino** (any recent version).
2. **Python 3.10+** on PATH (check: `python --version`).
3. For the web UI: **Node 18+** and **bun**, plus the `claude` CLI.
4. This repository, on the demo branch.

You do not need any API keys — the MCP servers run through the Claude Code
subscription.

---

## Part 1 — Get the code

```
git clone <your-repo-url> Radical-Accessibility-Toolkit
cd Radical-Accessibility-Toolkit
git checkout claude/3d-walls-floor-hatching-4dqef2
```

---

## Part 2 — One-time setup

From the repo root, in **cmd.exe** (not Rhino, not Windows Terminal):

```
python setup.py
```

This installs `mcp`, writes `.mcp.json`, and creates `controller/state.json`.
When it finishes, the MCP servers are ready.

---

## Part 3 — Start the three pieces

You will have three things running at once. Start them in this order.

### 3a. Rhino + the watcher (the live 3D view)

Open Rhino. Open the Python editor (press **F2**, or run
`EditPythonScript`). Paste these two lines, fix the path to your checkout,
and press **F5**:

```
__file__ = r"C:\path\to\Radical-Accessibility-Toolkit\tools\rhino\rhino_watcher.py"
exec(open(__file__).read())
```

You should see `[PLJ] Ready.` on the Rhino command line. The watcher now
reads `controller/state.json` and rebuilds the model whenever that file
changes. Only this one script runs inside Rhino — never the controller.

### 3b. The web UI (what the student drives)

In a **WSL** shell (or use `start-webui.bat` on Windows):

```
tools/webui/start-webui.sh
```

Then open **http://localhost:8788** in a browser. This is the accessible
chat. The student talks to Claude here; Claude calls the Layout Jig MCP
functions, which write `controller/state.json`, which Rhino then redraws.

### 3c. (Optional) the typed CLI — your safety net

Keep one more cmd.exe window open with the controller running, in case the
web UI hiccups. It writes the same `controller/state.json`:

```
python controller/controller_cli.py
```

---

## Part 4 — Smoke test (do this before the audience arrives)

In the web UI, say:

> "Load the simple building template."

Within a second, Rhino should show an **L-shaped, angled** plan: two
volumes, a bent hallway, three rooms, and a 3D model with extruded walls.
Then say "Undo that" (or just reload at the start of the real demo) so you
begin clean.

If Rhino did not change, see Part 6.

---

## Part 5 — The 10-minute demo script

### 1. Draw a plan — 2 min

> "Load the simple building template."
*(template_load simple-building)*

Rhino draws the building: **two volumes that union into one L**, set at 30
degrees, with a **bent hallway** running across the lower wing and turning up
the side wing. Three rooms — **Studio, Gallery, Office** — open onto the
hallway. Claude reads back a short text description so the student hears the
result.

Talking point: the two volumes share an opened seam where the hallway crosses
between them, so they read as one connected building, not two boxes.

### 2. It is parametric and angled — 1 min

> "Reload it at 15 degrees instead."
*(template load simple-building rotation=15)*

The whole L rotates to the new angle as one piece — the seam and the bent
hallway stay aligned. (You can also pass `bay_size=14` to grow it.)

### 3. 3D walls — 2 min

The template already turns the 3D model on, so the walls are extruded. Show
that it is adjustable:

> "Raise the walls to 10 feet."  *(tactile3d wall_height 10)*

> "Cut the model at 6 feet so we can see into the rooms."
*(tactile3d cut_height 6)*

Rhino re-extrudes and the clipping plane drops in. Point out: the walls open
exactly at the doors and at the shared seam — apertures are real gaps, not
drawn-on.

### 4. Feel the spaces — textures on the 2D plan — 2 min

Every space carries a different texture on the 2D tactile plan, so a blind
reader knows where they are by touch:

- **Studio** — diagonal ridges
- **Office** — dots
- **Gallery** — crosshatch (waffle)
- **Hallway** — horizontal lines

Demonstrate changing one live:

> "Change the Office floor to crosshatch."
*(cell A 2,0 hatch crosshatch / cell A 3,0 hatch crosshatch)*

Talking point: textures live on the **2D surfaces** for now. The 3D model can
also carry raised floor textures (`tactile3d floor_hatch on`), but for this
demo we keep them on the plan.

### 5. Save the state in JSON — 1 min

> "Save a snapshot called demo."  *(snapshot save demo)*

> "Describe the whole model."  *(describe)*

Talking point: everything — the two volumes, the angle, the hallway, the
textures — lives in one `controller/state.json`. If Rhino crashes mid-demo,
restart it, run the watcher, and the model rebuilds from the file. Nothing is
lost.

### 6. Hand it to the printer — 1 min

> "Export the 3D model to STL."  *(tactile3d export)*

The same JSON also drives a 2D PIAF tactile plan (via TACT) and a Bambu 3D
print. One model, three physical outputs.

### 7. Questions — 1 min buffer.

---

## Part 6 — If something misbehaves

- **Rhino did not update.** The watcher rebuilds on file change. Re-run the
  last command, or press **F5** in Rhino to re-run the watcher.
- **Rhino crashed.** Restart Rhino and re-run the watcher (Part 3a). The model
  rebuilds from `controller/state.json` — nothing is lost.
- **Web UI stalled.** Fall back to the typed CLI (Part 3c). Same commands,
  same JSON, same live Rhino. The exact sequence:

  ```
  template load simple-building
  template load simple-building rotation=15
  tactile3d wall_height 10
  tactile3d cut_height 6
  cell A 2,0 hatch crosshatch
  cell A 3,0 hatch crosshatch
  snapshot save demo
  describe
  ```

Both paths write the same `controller/state.json`, so you can switch between
the web UI and the terminal at any time without losing the model.

---

## Appendix — quick reference

**The plan (before rotation).** Volume A is the lower wing (4 bays wide, 2
deep); Volume B is the side wing (2 wide, 3 deep). They abut and the shared
wall is opened where the hallway crosses, forming one L.

```
+--------+
| VOL B  |
| hall | Gallery |
+----+---+--------+
| hallway ....... |
| Studio | Office |
+-----------------+
```

**What each space feels like.**
- Studio — diagonal ridges
- Office — dots
- Gallery — crosshatch (waffle)
- Hallway — horizontal lines

**Texture names you can assign** to any space (room or hallway):
`diagonal`, `crosshatch`, `dots`, `horizontal`, `solid`.

**Change the angle:** `template load simple-building rotation=<degrees>`
(0 = axis-aligned).

**Grow it:** `template load simple-building bay_size=<feet>`.
