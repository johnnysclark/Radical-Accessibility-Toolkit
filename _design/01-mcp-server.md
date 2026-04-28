---
# 01 — MCP Server subsystem

## Purpose
`mcp/mcp_server.py` wraps the Layout Jig controller and related engines as a FastMCP server, exposing them to Claude Code via MCP. The controller is a Python CLI the agent cannot call directly; MCP functions are the typed, documented bridge.

## Public API / entry points
71 `@mcp.tool()` functions, 6 `@mcp.resource()` endpoints, 4 `@mcp.prompt()` generators.

- Escape hatch: `run_command`
- State read: `describe`, `list_bays`, `get_state`, `get_help`, `list_apertures`, `list_cells`, `list_rooms`, `list_snapshots`, `list_commands`, `show_command_source`
- Bay mutations: `set_bay`, `set_walls`, `set_corridor`, `set_cell`, `auto_corridor_cells`, `add_bay`, `remove_bay`, `clone_bay`
- Apertures: `add_aperture`, `remove_aperture`, `modify_aperture`
- Site/grid/zones: `set_site`, `set_style`, `set_grid`, `clear_grid`, `set_site_polygon`, `add_zone`, `add_zone_polygon`, `remove_zone`, `list_zones`, `set_zone_label`
- Snapshots: `save_snapshot`, `load_snapshot`, `diff_snapshot`, `validate_state`
- Audit: `audit_model`, `audit_bay`, `describe_bay`, `describe_circulation`, `measure`
- Macros/templates: `macro_list`, `macro_show`, `macro_run`, `macro_save`, `template_list`, `template_show`, `template_load`
- Rhino bridge: `rhino_status`, `rhino_query`, `rhino_run_script`, `setup_rhino`
- Extension/introspection: `extend_controller`, `list_extensions`, `get_field`, `set_field`, `list_fields`
- Scripts/export: `generate_script`, `list_scripts`, `show_script`, `export_model`
- Style/views: `style_use`, `style_show`, `style_set`, `style_save`, `style_list`, `style_test`, `view_plan`, `view_section`, `view_axon`, `view_elevation`

## Dependencies
- External: `mcp>=1.26.0` (FastMCP); optional `style_manager`, `pdf_generator`, `state_renderer`
- Internal RAP modules: `controller_cli`, `auditor`, `macro_manager`, `template_manager`, `rhino_client`, `braille`

## What's essential
- `_run()` as the single dispatch path: load state, call `cli.apply_command`, save atomically.
- Stdout globally redirected to stderr so JSON-RPC is never corrupted.
- All responses return plain strings with `OK:` / `ERROR:` / `READY:` prefixes for screen-reader compatibility.
- Optional subsystems fail gracefully with `ImportError` guards, never crashing the server.

## What's accidental
- `tactile3d._export_once` flag cleared inside `_run()` — side-effect logic that belongs in the controller.
- `extend_controller` writes Python source to `controller_cli.py` at runtime — unsafe and file-layout-coupled.
- View tools embed rendering logic directly instead of delegating to a renderer module.
- `_swell_available` is a vestigial alias of `_style_available` from a prior architecture split.
- Version changelogs (v2.0–v4.0) belong in git history, not the module docstring.
- 2590-line single file; tool groups share only `_run()` and `STATE_PATH` and are separable.
---
