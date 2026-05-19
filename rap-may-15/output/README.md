# output

## What this is

The OUTPUT component of the Radical Accessibility Controller (the
rap-may-15 toolkit). It converts a controller `state.json` or a source
image into tactile-ready output formats: PIAF JPG for swell-paper
printing, plan-view SVG for vector workflows, and (via the controller's
export pipeline) STL for 3D-printed tactile models.

OUTPUT is read-only with respect to controller state. It consumes the
state file and produces print-ready artifacts; it never writes back to
state.

## Install

From inside `output/`:

    pip install -e .

Or, from `rap-may-15/`:

    pip install -e ./output

## CLI

Render a controller `state.json` to a PIAF JPG:

    output-cli render <state.json> --format jpg

Render a controller `state.json` to a plan-view SVG:

    output-cli render <state.json> --format svg

A PDF format is also available via `--format pdf` for swell-paper PIAF
output.

## MCP server

`output/mcp_entry.py` exposes the output package as an MCP server so
Claude Code can call render functions directly.

## See also

The full demo lives in the parent `rap-may-15/` folder; see its README
for the end-to-end controller-watcher-output flow.
