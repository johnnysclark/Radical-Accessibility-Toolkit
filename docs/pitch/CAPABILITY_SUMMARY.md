# Radical Accessibility Project — Capability Summary

A technical brief framed for Anthropic. Why RAP is a meaningful deployment of Claude's product stack, and what funding would unlock.

---

## TL;DR for the Anthropic reader

- **MCP, in production, for accessibility.** Two MCP servers exposing 65 functions across the entire architectural design pipeline — design intent, state mutation, geometry queries, spatial audits, macro replay, tactile rendering, image-to-tactile conversion.
- **Skills, in production.** Top-level `skills/` directory with SKILL.md-packaged Claude capabilities (`laser-export`, `update`), following the Anthropic agent-skills convention.
- **Claude Code, made accessible.** An accessible web client (`tools/webui/`) bypasses the Ink TUI, which is not screen-reader compatible. Lifecycle hooks announce events through the JAWS TTS API via a WSL2-to-PowerShell bridge. This work directly addresses a known Claude Code product gap.
- **Daily use by a blind architect.** Daniel Bein, a blind UIUC architecture graduate student, designs, audits, fabricates, and presents using only this system.

The point is not that we've used Claude. The point is that we have re-architected an entire visual discipline around Claude as the integration substrate, and it works.

---

## The system at a glance

```
Terminal (controller/controller_cli.py)    Claude Code (mcp/mcp_server.py)
        |                                          |
        | writes                                   | calls controller + direct JSON
        v                                          v
              state.json  (canonical model artifact)
                      |
                      | watches (file mtime)
                      v
              Rhino 8 (tools/rhino/rhino_watcher.py)
                      |
                      v
              2D plan drawing | PIAF swell paper | 3D tactile model
```

Three interaction modes layer on top:

1. **Claude Code + MCP** — natural language → MCP function calls → state mutation → confirmation read by a screen reader.
2. **Interactive CLI** — typed or spoken commands, direct control, no AI in the loop. Works with JAWS, NVDA, and refreshable braille displays out of the box.
3. **Rhino Python** — Claude generates editable, annotated IronPython 2.7 scripts. Daniel opens, studies, modifies, and runs them. The AI teaches; it does not replace authorship.

---

## Claude product surfaces we exercise

### MCP

Two independent MCP servers:

- **`layout-jig`** (`mcp/mcp_server.py`, ~2,600 lines) — 58 functions across nine layers:
  - Core pipeline (21) — semantic wrappers around CLI commands
  - Zone, grid, export (9) — site-scale planning + multi-format export
  - Auditor (5) — spatial validation, ADA checks, circulation analysis
  - Macro manager (4) — save, list, show, replay
  - Rhino client (4) — TCP queries to the watcher + auto-launch
  - Controller extension (2) — runtime command-handler registration
  - State introspection (7) — read/write JSON fields, bay CRUD, handler source view
  - State comparison (3) — diff against snapshots, validate JSON
  - Script generation (3) — create / list / view editable IronPython scripts

- **`tactile`** (`tools/tact/mcp_entry.py`) — 7 functions:
  - `state_to_piaf`, `image_to_piaf`, `list_presets`
  - `analyze_image`, `describe_image`, `extract_text_with_vision`, `assess_tactile_quality`

### Skills

Top-level `skills/` directory follows the Anthropic agent-skills convention:

- **`laser-export`** — drives the Siebel Center 24×40″ laser cutter from a state.json
- **`update`** — one-command teammate sync from upstream

Skills are first-class in the taxonomy (`CLAUDE.md`): SKILL.md-packaged Claude capabilities, distinct from Macros (JSON command sequences) and from MCP functions.

### Claude Code

`tools/webui/` is an accessible web UI for Claude Code, built because the Ink TUI strips poorly through JAWS/NVDA. It uses an MCP channel server to relay Claude Code I/O to a browser pane that's read cleanly by screen readers. All markdown, ANSI, and emoji are stripped before output.

`tools/webui/hooks/` adds Claude Code lifecycle hooks that announce events via the JAWS TTS API (`JFWSayString`) through a WSL2-to-PowerShell bridge.

This work is, in effect, a downstream patch for Claude Code's accessibility story. It would benefit Anthropic to take it upstream.

### Claude API

`tools/image-describer/` uses Claude vision to convert architectural images (plans, sections, photos, diagrams) to structured text at three scales — Macro, Meso, Micro. Replaces "looking at a drawing" with text a screen reader can parse. Daniel uses this to study precedent buildings (e.g., the Farnsworth House workflow in the README).

---

## The user, in one paragraph

Daniel Bein is a blind graduate student at the UIUC School of Architecture. His workflow is the test case for every tool. He types or speaks design commands. He hears confirmations through NVDA. He runs `audit` to check his design against ADA. He runs `render` to produce a PIAF swell-paper print, which he laser-prints on microcapsule paper and heats through a PIAF machine — black lines rise as tactile ridges. He reads his floor plan with his fingers. He runs `tactile3d export` to send a 1:200 STL to a Bambu Lab P1S. He presents at studio review holding the physical model, narrating from the structured text description he rehearsed with his screen reader. No sighted intermediary participates in any of this. He retains authorship at every step.

---

## What we have shipped (selected proof points)

- 3,135-line Python 3 controller CLI, stdlib-only, with undo stack, snapshots, macro system, atomic file writes, schema migration
- 2,590-line MCP server, 58 functions, 5 resources, 4 prompts
- TACT pip-installable package: 10 image-to-tactile presets, EasyOCR text detection, Grade 2 Braille via liblouis, density management (25–40% black-pixel target), BANA-compliant braille labels (30pt → 10mm spacing)
- 149-test end-to-end suite (`tests/run_tests.py`)
- TASC: Python DSL for programmatic Rhino design, with live MCP socket connection
- Web client + JAWS/NVDA hooks (Node.js + Python bridge)
- ACADIA paper draft v6 (~4,600 words): *The Full Stack of Inclusion*
- Repository: github.com/johnnysclark/Radical-Accessibility-Toolkit (MIT)

---

## What we're asking for

Three direct options. Any combination. Equipment, fabrication, and lab costs are covered through UIUC — this ask is about people and access.

1. **Money** — student stipends for Ethan, Isaac, Laura, plus a co-designer stipend for Daniel. ~$60K–$80K/year covers the four of them plus modest travel for paper presentation. See `BUDGET.md`.
2. **Credits** — Claude API + Claude Code credits to uncap student and primary-user usage during batch image description, OCR, and day-to-day design-conversation work.
3. **Expertise** — time from the people at Anthropic who own Claude Code accessibility, MCP, and Skills. Code review on our webui + screen-reader hooks. A design partner who can tell us whether what we built should be upstreamed, mirrored, or scrapped. Possibly the most valuable of the three; the cheapest for Anthropic to provide.

---

## Future directions (already mapped in the README)

- Audio simulation of designs — binaural rendering of architectural space
- Vibrotactile interfaces and models
- Haptic gloves for digital model navigation
- High-resolution interactive tactile displays (pin arrays)
- Live AI scene description via META Ray-Ban glasses during studio, pin-ups, site visits
- New tools (structural analysis, environmental simulation, fabrication-machine control) plugged into the same shell

The system is designed to extend. Funding does not buy speculative R&D; it buys the next year of shipping into an architecture already proven.

---

## Why Anthropic specifically

The toolkit is Claude-native. MCP is the only protocol designed for the kind of semantic, auditable, multi-tool integration accessibility requires. Claude Code is the only agentic interface a screen-reader user can reasonably extend. Skills give us a unit of capability that lives alongside our existing macros without confusing the taxonomy.

Switching providers would require rebuilding the integration substrate. We do not want to. Funding RAP gives Anthropic a use case competitors cannot credibly claim: AI as infrastructure for human authorship by people their discipline locked out.
