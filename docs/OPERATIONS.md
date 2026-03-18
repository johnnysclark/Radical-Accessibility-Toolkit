# Operations Guide

How to launch, monitor, validate, and recover the Radical Accessibility Toolkit.

## Runtime Launcher

The runtime launcher validates the environment and starts the system.

### Commands

```
python runtime/launcher.py start    — validate environment, start controller CLI
python runtime/launcher.py status   — show all subsystem health
python runtime/launcher.py doctor   — detailed health checks with diagnostics
python runtime/launcher.py stop     — release stale locks, write shutdown status
```

### What "start" checks

1. Python version (3.8+ required)
2. Project directory structure (controller/, mcp/, tools/)
3. Controller CLI importability
4. State file existence and validity
5. MCP package availability
6. MCP server file presence
7. Rhino watcher script presence
8. Swell-print dependencies
9. Write lock status
10. Journal status

If critical checks fail (Python version, project structure, controller CLI),
the launcher will not start and will report the specific errors.

### Status file

After every command, the launcher writes machine-readable status to
`runtime/status.json`. This file can be read by monitoring scripts
or CI systems.

## State Transaction Manager

The state manager wraps state.json mutations with:

- Advisory file locking (single-writer enforcement)
- Monotonic revision numbers in state.meta.state_revision
- Transaction metadata (writer, timestamp, transaction ID)
- Append-only operation journal in controller/journal/

### Lock behavior

- Locks are advisory (.lock file next to state.json)
- Stale locks (older than 60 seconds) are automatically cleared
- Use `runtime/launcher.py stop` to manually clear a stuck lock

### Journal

Every committed state change records:

- transaction_id (e.g., txn_000128)
- revision_before and revision_after
- writer (cli, mcp, runtime, script)
- command that was executed
- status (committed or failed)
- timestamp

Journal entries are stored as individual JSON files in controller/journal/.

## Validation Framework

Five validation layers check different aspects of the model:

### Layers

1. Schema — required keys, types, enums, nested structure
2. Semantic — corridor references, aperture placement, cell bounds, labels
3. Spatial — overlapping bays, site boundary, degenerate geometry, aperture overlaps
4. Tactile — hatch differentiation, braille labels, density, legend status
5. Fabrication — wall height, floor thickness, export paths, scale factor

### CLI commands

```
validate           — run all layers
validate schema    — schema only
validate semantic  — semantic only
validate spatial   — spatial only
validate tactile   — tactile readiness
validate fab       — fabrication readiness
```

### MCP functions

- validate_schema()
- validate_semantic()
- validate_spatial()
- validate_tactile()
- validate_fabrication()
- validate_all()

## Capture Subsystem

First-class repeatable image captures from Rhino.

### Presets

Capture presets define named view, display mode, resolution, format, and output path.
Default presets: plan_technical, axon_technical, perspective_pen.

### CLI commands

```
capture list              — show all presets
capture run <preset_id>   — run one capture
capture run all           — run all enabled presets
capture status            — show last capture results
capture preset add <id>   — add a new preset with defaults
```

### MCP functions

- list_capture_presets()
- capture_view(preset_id)
- capture_all_views()
- get_capture_status()
- set_capture_preset_field(preset_id, field, value)

### Capture outputs

- Images in captures/ directory
- manifest.json — history of all capture runs (last 50)
- latest_status.json — most recent capture status

### Offline behavior

When Rhino is not running, capture commands return error status with
clear messages. The manifest still records the attempt.

## Failure and Recovery

### Rhino crash

Nothing is lost. Restart Rhino, run the watcher, everything rebuilds from state.json.

### Stale write lock

```
python runtime/launcher.py stop
```

Or manually delete the .lock file next to state.json.

### Invalid state.json

```
validate schema
```

Identifies structural problems. Use `snapshot load <name>` to restore a known good state.

### MCP server offline

The controller CLI works independently. Check with:

```
python runtime/launcher.py doctor
```

### Corrupt journal

The journal is supplementary. Delete entries in controller/journal/ if needed.
State.json remains the source of truth.

## Operational Modes

### Solo local use
Start the controller CLI directly or via the runtime launcher.
Rhino optional. MCP optional.

### Claude-assisted use
Start MCP server via .mcp.json or manually. Claude calls MCP functions.
Both CLI and MCP write to the same state.json.

### Remote review
Use capture presets to generate high-resolution images.
Share captures/ directory or latest_status.json.

### Classroom / shared lab
Use the runtime launcher for consistent startup.
Validation catches common mistakes.
Journal tracks who changed what.
