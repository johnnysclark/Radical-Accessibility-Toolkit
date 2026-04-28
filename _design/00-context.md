# 00 — Context (Phase 0 orientation)

## Directory shape

Top-level subsystems:
- `controller/` — CLI shell, command dispatch, undo stack, state.json writes, macro runner, style manager, auditor, exporter, braille output
- `mcp/` — single MCP server bridging Claude Code to the controller and Rhino
- `tools/rhino/` — Rhino watcher (IronPython 2.7), tactile print script, Rhino client
- `tools/tact/` — TACT CLI and MCP server: image-to-PIAF tactile conversion, PDF generation, Braille conversion, state renderer
- `tools/tasc/` — TASC CLI: accessible programmatic Rhino design via text commands
- `tools/image-describer/` — architectural alt-text generation
- `tools/webui/` — accessible web client for JAWS/NVDA; channel server; screen reader hooks
- `tools/web-viewer/` — simple HTML viewer
- `skills/` — SKILL.md-packaged Claude capabilities (laser-export, update)
- `docs/` — ACADIA papers, manual, MCP guide, working documents
- `patterns/` — architectural tactile guidelines, image description machine
- `tests/` — integration test runner

## Top files by LOC (source only)

1. controller/controller_cli.py — 3135
2. mcp/mcp_server.py — 2590
3. tools/tact/src/tact/mcp_server/tools.py — 2110
4. tools/rhino/rhino_watcher.py — 1835
5. tools/tact/src/tact/core/pdf_generator.py — 1667
6. tools/tact/src/tact/core/state_renderer.py — 1633
7. tools/tact/src/tact/cli.py — 1453
8. tools/tact/src/tact/core/converter.py — 1159
9. tools/rhino/tactile_print.py — 1032
10. tools/tact/src/tact/core/processor.py — 961

## Major subsystems (by name)

1. CLI / agent loop (controller/)
2. MCP bridge (mcp/)
3. Rhino watcher + JSON contract (tools/rhino/)
4. Tactile output pipeline: TACT + TASC (tools/tact/, tools/tasc/)
5. Accessibility layer: web UI + hooks (tools/webui/)
6. Image description channel (tools/image-describer/)

## Conceptual ambition (bay/zone language stripped)

RAP is a non-visual, agentic design pipeline. A human or language agent issues semantic design commands through a text shell. Those commands update a plain-text JSON state file that is the sole source of truth for the design. Downstream renderers — a geometry engine, a tactile PDF generator, a 3D print pipeline — are read-only consumers of that file. The pipeline is designed so that every step can be driven by keyboard, voice, or braille input, and every output can be received by speech synthesis, braille display, or physical fabrication. Vision is never required.
