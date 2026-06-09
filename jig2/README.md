# jig — accessibility-first layout controller for Rhino 8 on macOS

A from-scratch rewrite of the Layout Jig. You type (or speak, or let
Claude type) semantic commands; jig keeps the model in a plain JSON state
file; Rhino renders it live and can crash at any time without losing
anything; the same state exports to .3dm with Rhino closed.

Core ideas:

- The state file is the model. Rhino is a viewer, never the source of truth.
- Geometry math is computed once, in pure Python (`jig.geometry`), and drawn
  by two thin backends: rhinoscriptsyntax inside Rhino, rhino3dm offline.
- One command grammar serves the CLI, the REPL, and the MCP server, so a
  human and Claude drive the model the same way.
- Every response starts with OK: or ERROR: and ends with READY:. No
  spinners, no tables, no decorative characters. VoiceOver reads it cleanly.

## Install (macOS)

Requires Python 3.9+ and Rhino 8 for Mac.

    cd jig2
    python3 -m venv .venv
    .venv/bin/pip install -e .

The `jig` command is now at `.venv/bin/jig` (or activate the venv).

## Ten-minute checklist

1. `cd` to a project folder. State lives in `./state.json` by default
   (`--state PATH` to change it).
2. `jig rhino start` — launches Rhino 8 and injects the watcher via the
   `rhinocode` CLI. If injection fails, jig prints the fallback: open
   Rhino's ScriptEditor and run the `jig_watcher.py` it installed under
   `~/Library/Application Support/jig/watcher/`.
3. `jig site set 180 260` — a site rectangle appears in Rhino.
4. `jig bay add a 4x3 --spacing 24 --at 18,8` — columns and gridlines appear.
5. `jig wall a on` then
   `jig aperture add a door --axis x --line 0 --offset 10 --width 3` —
   walls with a door gap and swing arc.
6. `jig corridor a on --axis x --line 1 --width 8` — corridor carved through.
7. Force-quit Rhino. Restart it, run the watcher again: the whole scene
   rebuilds from `state.json`. Nothing is lost. That is the design.
8. `jig export 3dm out.3dm` — same geometry, written without Rhino.
9. `jig describe` — the full model in prose. `jig undo`, `jig snapshot save
   NAME`, `jig validate` do what they say.
10. `jig repl` for an interactive session; add `--say` to speak responses.

## Claude Code wiring

Add to your project's `.mcp.json`:

    {
      "mcpServers": {
        "jig": {
          "command": "/path/to/jig2/.venv/bin/python",
          "args": ["-m", "jig.mcp_server"],
          "env": { "JIG_STATE": "/path/to/your/project/state.json" }
        }
      }
    }

The server exposes 12 MCP functions. `run_command` and `run_script` take
the same grammar you type; `describe_model`, `get_state`, `validate_model`,
`measure` read; `snapshot`, `undo`, `export_model`, `rhino_status`,
`rhino_start`, `list_commands` round it out. Resources: `jig://state`,
`jig://describe`, `jig://grammar`. Prompts: `design_review`, `start_layout`.

Ask Claude: "lay out a small school on a 180 by 260 site" and watch Rhino
follow along.

## Command grammar

`jig help` lists all commands; `jig help bay add` shows one. The grammar is
speakable: real words, `--flag value` options, the only punctuation is
`NxM` for bay counts and `X,Y` for points.

    site set W D | site polygon X,Y X,Y X,Y ... | site clear
    zone add NAME W D --at X,Y [--kind program|circulation|service|open]
    zone polygon NAME X,Y X,Y X,Y ... | zone remove NAME | zone list
    grid set SX [SY] [--rotation DEG] [--origin X,Y] | grid off
    bay add NAME NxM [--spacing S] [--spacing-x A,B,C] [--at X,Y] [--rotation DEG]
    bay set NAME rotation|origin|counts|spacing VALUE | bay remove | bay list
    wall BAY on|off [--thickness T]
    aperture add BAY door|window|portal --axis x|y --line N --offset F --width W
        [--hinge start|end] [--swing in|out]
    aperture remove BAY ID | aperture list BAY
    corridor BAY on|off [--axis x|y] [--line N] [--width W]
    cell set BAY I J NAME [--label TEXT] | cell clear | cell list
    void add BAY rect|circle --at X,Y --size W[,D] | void remove BAY ID
    describe [SECTION] | status | validate | measure NAME NAME | help
    undo [N] | snapshot save|load|list|diff NAME
    export 3dm PATH | export text PATH
    rhino install | rhino start | rhino status

## Layout of the model

`state.json` (schema `jig_v4`) holds site, zones, grid, and bays. A bay is
a rectangular structural grid: `counts` bays across x and y, per-interval
spacing arrays, walls along every gridline, apertures on a wall addressed
by axis + line + offset, an optional corridor along an interior line, named
cells, and voids. Old `plan_layout_jig_v3` files migrate automatically on
load. Presentation (line weights, label sizes) lives in code defaults, not
in the geometry state.

## How the Rhino bridge works

`jig rhino install` copies a self-contained bundle (the watcher script plus
`jig.model` and `jig.geometry`, which have zero dependencies) to
`~/Library/Application Support/jig/watcher/`. Inside Rhino, the watcher
hooks the Idle event, polls the state file's mtime twice a second, and on
change clears the `JIG::` layers and redraws everything from disk. After
each rebuild it writes `scene_report.json` next to the state file —
`jig rhino status` reads that, so the CLI can tell you what Rhino drew
without a socket. Set `JIG_AUDIO=chime|speak|both` for sound feedback on
rebuilds.

## Development

    .venv/bin/pip install -e ".[dev]"
    .venv/bin/python -m pytest

The whole suite runs headless: geometry is asserted coordinate-by-
coordinate, the .3dm export is round-tripped through rhino3dm, and the
watcher's drawing dispatch runs against a fake rhinoscriptsyntax. Only the
last mile — pixels in a Rhino viewport — needs the Mac.
