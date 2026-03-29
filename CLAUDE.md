# CLAUDE.md — Rhino Automation Harness

## What This Is

A Claude Code harness for driving Rhino 3D. Claude connects to a watcher process inside Rhino via TCP, executes IronPython scripts, queries model state, and manages reusable scripts and session logs.

The harness is the MCP server at `harness/mcp_server.py`. It is self-contained — no other MCP servers or project-specific tools are required.

---

## Setup

1. Install the MCP dependency: `pip install mcp`
2. Add to `.mcp.json`:
```json
{
  "mcpServers": {
    "rhino-harness": {
      "command": "python3",
      "args": ["harness/mcp_server.py"]
    }
  }
}
```
3. In Rhino, run the watcher: `tools/rhino/rhino_watcher.py`
4. Verify: call `rhino_status` — should report ONLINE.

---

## MCP Tools

### Connection
- `rhino_status` — Check if Rhino is reachable, get object/layer counts.
- `rhino_connect(host, port)` — Change connection target (default 127.0.0.1:1998).

### Query
- `rhino_layers` — List layers and object counts.
- `rhino_objects(layer)` — Object count, optionally by layer.
- `rhino_bounds` — Bounding box of all geometry.

### Execute
- `rhino_run(code)` — Run IronPython code in Rhino, return printed output.
- `rhino_command(command)` — Run a Rhino command-line string.

### Scripts
- `script_save(name, code, description)` — Save a reusable IronPython script.
- `script_list` — List saved scripts.
- `script_show(name)` — Show script contents.
- `script_run(name)` — Execute a saved script in Rhino.
- `script_delete(name)` — Delete a script.

### Session
- `session_log(entry, tag)` — Log a note or milestone.
- `session_read(last)` — Read recent log entries.
- `session_clear` — Start a fresh session log.
- `session_export` — Dump the full session log.

---

## IronPython 2.7 Rules

All code that runs inside Rhino uses IronPython 2.7. Follow these rules:

- **No f-strings** — use `.format()` or `%` formatting.
- **No pathlib** — use `os.path`.
- `import rhinoscriptsyntax as rs` at the top of every script.
- All coordinates are `[x, y, z]` lists.
- All angles in degrees.
- `rs.EnableRedraw(False)` before bulk operations, `rs.EnableRedraw(True)` after.

---

## RhinoScript Quick Reference

### Object Creation
- `rs.AddPoint(x, y, z)` — point
- `rs.AddLine([x1,y1,z1], [x2,y2,z2])` — line
- `rs.AddPolyline([[x1,y1,z1], ...])` — polyline (close by repeating first point)
- `rs.AddCircle([cx,cy,cz], radius)` — circle
- `rs.AddRectangle(rs.WorldXYPlane(), width, height)` — rectangle
- `rs.AddSphere([cx,cy,cz], radius)` — sphere
- `rs.AddBox([corners_8_points])` — box
- `rs.AddCylinder([base], height, radius)` — cylinder
- `rs.AddSrfPt([[p1],[p2],[p3],[p4]])` — surface from points
- `rs.AddPlanarSrf([curve_id])` — planar surface from closed curve
- `rs.AddLoftSrf([curve1, curve2, ...])` — loft
- `rs.ExtrudeCurveStraight(curve, [start], [end])` — extrusion
- `rs.AddText("text", [x,y,z], height)` — text
- `rs.AddHatch(curve_id, "Solid")` — hatch

### Query
- `rs.ObjectName(guid)` / `rs.ObjectName(guid, "name")` — get/set name
- `rs.ObjectLayer(guid)` / `rs.ObjectLayer(guid, "layer")` — get/set layer
- `rs.ObjectType(guid)` — type code (1=point, 4=curve, 8=surface, 16=polysurface, 32=mesh)
- `rs.ObjectsByLayer("layer")` — all objects on a layer
- `rs.BoundingBox(guid)` — 8-point bounding box
- `rs.CurveLength(id)` — curve length
- `rs.SurfaceArea(id)` — (area, error)
- `rs.IsObject(guid)` / `rs.IsCurve(guid)` / `rs.IsSurface(guid)` — type checks

### Transform
- `rs.MoveObject(guid, [dx,dy,dz])` — move
- `rs.RotateObject(guid, [cx,cy,cz], angle)` — rotate in XY
- `rs.ScaleObject(guid, [cx,cy,cz], [sx,sy,sz])` — scale
- `rs.CopyObject(guid, [dx,dy,dz])` — copy
- `rs.MirrorObject(guid, [start], [end])` — mirror
- `rs.DeleteObject(guid)` / `rs.DeleteObjects([guids])` — delete

### Layers
- `rs.AddLayer("name")` — create layer
- `rs.DeleteLayer("name")` — delete layer
- `rs.CurrentLayer()` / `rs.CurrentLayer("name")` — get/set current
- `rs.LayerVisible("name", True/False)` — visibility

### Metadata
- `rs.SetUserText(guid, "key", "value")` — set metadata
- `rs.GetUserText(guid, "key")` — get metadata
- `rs.GetUserText(guid)` — list all keys

### View
- `rs.ZoomExtents()` — fit all
- `rs.Redraw()` — force refresh
- `rs.EnableRedraw(True/False)` — batch mode

### Booleans
- `rs.BooleanUnion([guid1, guid2])` — union
- `rs.BooleanDifference([a], [b])` — difference
- `rs.BooleanIntersection([a], [b])` — intersection
- `rs.OffsetCurve(curve, [direction], distance)` — offset

---

## Harness Protocol

### Plan-Execute-Verify

Every non-trivial Rhino operation follows three phases:

1. **Plan** — State what you intend to do and why.
2. **Execute** — Run the script or commands. One step at a time.
3. **Verify** — Query Rhino to confirm the change took effect.

### Session Discipline

- Log milestones with `session_log("completed X", tag="milestone")`.
- Before destructive operations, state what will change.
- Save reusable operations as scripts with `script_save`.
- At session end, `session_log` a summary.

### Script Conventions

- Name scripts with lowercase-hyphen: `draw-grid`, `place-columns`, `export-view`.
- Include a description when saving.
- Scripts should be self-contained (import rhinoscriptsyntax at the top).
- Use `rs.EnableRedraw(False/True)` to wrap bulk geometry creation.

---

## Code Conventions

- Python files: PEP 8, snake_case.
- IronPython scripts: `.format()` strings, `os.path`, no f-strings.
- JSON: 2-space indent, snake_case keys.
- Git branches: `author/action-topic` (e.g. `claude/add-grid-script`).
