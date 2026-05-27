# Summer 2026 Planning Dossier — Radical Accessibility Toolkit

A wide-aperture survey to pick from. Compiled 2026-05-27 by seven parallel research agents covering: repo audit, summer demos, Claude Code feature track, Superfund AI workflows, accessible-studio pedagogy with Daniel, tactile+AI capabilities and hardware, and the broader AI ecosystem beyond Claude.

Don't try to do it all. Choose what excites you, move fast on those. The synthesis in §8 is the only place this document makes choices for you.

## Map of this dossier

1. Where the toolkit actually stands today — honest inventory.
2. Summer demos to vibe-code — 60 concrete projects.
3. Claude Code learning track — features to master and teach.
4. Second-year studio: Superfund sites + AI — 53 workflows by phase.
5. Third-year studio: radically accessible (with Daniel) — 60+ pedagogical tactics.
6. Tactile + AI capabilities + hardware — what AI brings to tactile workflows.
7. AI tools beyond Claude — opinionated landscape.
8. Highest-leverage picks — cross-cutting synthesis if you want a starting line.

---

# 1. Repo audit (current state)

**Branch:** `claude/practical-johnson-TMH6o`. Working tree clean.

## 1.1 Tools (major capability modules)

| Tool | Location | State | Description |
|------|----------|-------|-------------|
| **Layout Jig** | `controller/` | Working | Semantic architectural modeling: bays, zones, corridors, apertures, grids, site boundaries. 90+ CLI command handlers, 60+ MCP functions. `controller/state.json` is the source of truth. |
| **TACT** | `tools/tact/` | Working | Tactile conversion: images to PIAF-ready PDF, state.json to tactile PDFs, EasyOCR text detection, 10 presets, Grade 2 Braille. 7 MCP functions. |
| **TASC** | `tools/tasc/` | Working | Accessible site-planning DSL for Rhino: zones, bays, corridors via text commands. Live MCP socket to Rhino. |
| **Rhino Watcher** | `tools/rhino/rhino_watcher.py` | Working | IronPython 2.7 in Rhino; reads state.json, rebuilds geometry on file change (full rebuild, crash-safe, read-only on state.json). |
| **Laser Export** | `tools/rhino/laser-export/` | Working | Stages geometry onto Cut/Engrave layers, exports to Illustrator at correct scale for Siebel Center 24″×40″ laser. 6 IronPython modules. |
| **Image Describer** | `tools/image-describer/` | **Stub** | `arch_alt_text.py` (726 lines) exists; CLI not wired; no MCP functions. |
| **Web UI** | `tools/webui/` | Partial | TypeScript web client + MCP channel server for JAWS/NVDA. Hooks (image-detector, conversion-tracker, feedback-capture) written but not auto-loaded. |
| **Web Viewer** | `tools/web-viewer/` | **Stub** | `viewer.html` (1297 lines) standalone. Not integrated. |
| **Tactile Printer** | `tools/rhino/tactile_print.py` | Working | STL/3D output for Bambu printers, integrated into controller export pipeline. |

## 1.2 MCP servers (configured in `.mcp.json.example`)

- **layout-jig** — `mcp/mcp_server.py`. 60+ tools, 4 resources, 2 prompts (`accessibility_audit`, `macro_builder`).
- **tactile** — `tools/tact/mcp_entry.py`. 7 functions: `image_to_piaf`, `list_presets`, `analyze_image`, `describe_image`, `extract_text_with_vision`, `assess_tactile_quality`, `state_to_piaf`.
- **rhinomcp** (optional) — external Rhino MCP adapter on port 1999.

## 1.3 Skills (`skills/*/SKILL.md`)

- **laser-export** — wraps the Siebel laser workflow (stage → make2d/unroll → export to Illustrator).
- **update** — runs `scripts/update.sh`: fetch upstream, fast-forward, report post-pull actions.

## 1.4 Templates and macros

Two of each as starter examples:

- `controller/templates/add-double-loaded-corridor.json`, `enclose-bay-with-door.json`
- `controller/macros/` — two examples

## 1.5 CLI command surface (90 handlers across these groups)

Bay (12) • Aperture (4) • Cell (3) • Corridor (1) • Walls (1) • Zone (5) • Grid (3) • Site (2) • Style (7) • View (4) • Export (3) • Print (2) • Snapshot (3) • History (2) • Macro (4) • Template (3) • Rhino (4) • Audit (5) • Section (4) • Tactile3D (7) • Bambu (7) • Hatch (3) • TTS (2) • Undo/Redo (2) • Help (2)

## 1.6 State schema (controller/state.json)

Top-level: `schema`, `meta`, `site` (with `polygon_corners`), `zones`, `grid`, `style`, `bays` (with `rooms` and `apertures`), `blocks`, `rooms`, `legend`, `tactile3d`, `hatch_library_path`, `print`, `bambu`. Every addressable object has a stable ID + human name. Schema migration runs on load.

## 1.7 Watcher (Rhino integration)

`tools/rhino/rhino_watcher.py` (1835 lines, IronPython 2.7). Hooks `Rhino.RhinoApp.Idle`, polls state.json mtime every 500ms. Full rebuild on change; clears `JIG_` layers; tags objects with `JIG_OWNER`, `JIG_ID`, `JIG_SCHEMA` UserText. No exception handling — crashes on malformed state.json; user restarts Rhino. File-based recovery means nothing is lost.

## 1.8 Claude Code hooks

In `tools/webui/hooks/`: `image-detector.ts` (UserPromptSubmit), `conversion-tracker.ts` (PostToolUse), `feedback-capture.ts` (UserPromptSubmit). **All written, none auto-loaded.** A `screen-reader/` directory holds WSL2-to-PowerShell bridge for JAWS via JFWSayString API; infrastructure in place, not wired. No `.claude/settings.json` in repo.

## 1.9 Docs

- `docs/` — ACADIA paper drafts (6 versions), brainstorms, MANUAL.md, MCP_GUIDE.md, TEST_MANUAL.md, WORKING_DOCUMENT_Summer2025.md
- `docs/references/` — citations
- `docs/archive/` — older docs
- `docs/vault/` — OneDrive-symlinked Obsidian vault, gitignored, contains work sessions, tool docs, timesheet, people

Root: CLAUDE.md (301 lines), DESIGN_SESSION.md, STARTUP.md, README.md (500+ lines), `setup.py`.

## 1.10 Notable gaps

| Item | Status | Impact |
|------|--------|--------|
| Image Describer MCP | Stub; no CLI or MCP entry | Not callable |
| Web Viewer entry | Standalone HTML, no integration | Manual file-open only |
| `WORKFLOW.md` / `quick-start.md` in laser-export | Referenced in SKILL.md but missing | Skill wired, walkthrough missing |
| `.claude/settings.json` | Not in repo | User must set up manually |
| TASC MCP server | CLI only; no MCP entry | TASC commands can't go via MCP |
| Hooks auto-loading | None of the three is wired into a settings file | Manual install required |
| Rhino auto-launch on watcher start | Partial | User restarts manually after Rhino crash |

**Summary:** Toolkit is structurally complete at the semantic/CLI layer. Layout Jig, TACT, TASC, Rhino watcher, and laser-export all work. Hooks, Image Describer, and Web Viewer are the main loose ends. No uncommitted work; last major feature landed four days ago.

---

# 2. Summer demos to vibe-code

Sixty concrete projects, grouped by category. Each has a scope tag (S = a session, M = a few days, L = a week+) and topic tags. Lead with what excites you; nothing in here depends on the others.

## 2.1 Tactile output experiments

**1. Swell-paper diff viewer.** Render two state.json snapshots as overlaid tactile pages: solid lines for current model, dashed/stippled for what was removed, hatched for what was added. Side-by-side panels with a Braille legend.
_Demos round-trip auditability — you can feel what changed since last critique._
M • [tactile, semantic, accessibility]

**2. Tactile section cutter.** `tact section state.json --axis x --at 12.0` slices the model and emits a tactile elevation/section PDF, with column cuts as filled circles, wall cuts as thick lines, and a tiny key plan in the corner.
_Sections are the architectural drawing most often skipped in tactile pipelines._
M • [tactile, semantic, rhino]

**3. Multi-page tactile booklet.** `tact booklet state.json --pages plan,section,axon,zones` produces a stapled-PDF tactile booklet with consistent scale bars, Braille TOC, and cross-references ("see page 3 for section A-A"). One command, one studio-ready desk crit packet.
_Replaces the 4-hour manual prep for blind students at every review._
M • [tactile, classroom, accessibility]

**4. Tactile texture library.** A `patterns/` browser that prints a single PIAF "swatch card" of all 30+ RainbowTact patterns, each labeled in Braille. Includes a "twin test" page pairing visually-distinct patterns to check they're also tactilely distinct.
_Closes the long-standing gap: how do you pick patterns without seeing them?_
S • [tactile, accessibility]

**5. Tactile contour map from heightfield.** Ingest a GeoTIFF or a state.json `terrain` field; emit a contour-line PIAF with major contours thicker, plus Braille spot elevations at peaks.
_Reaches beyond building scale into geography teaching._
M • [tactile, semantic]

**6. Braille dimension annotator.** Post-process any TACT PDF: detect long edges and auto-place Braille dimension callouts at midpoints with leader lines. Suppresses dimensions shorter than a configurable tactile-resolution threshold.
_Solves the "I can feel the shape but how big is it" problem._
S • [tactile, accessibility]

**7. Reverse-OCR tactile labels.** When EasyOCR finds text, render the label _position_ tactilely (small triangle or asterisk) and emit a separate keyed-Braille legend page.
_Acknowledges tactile text rules differ from print text rules._
S • [tactile, ai, accessibility]

## 2.2 Voice-first design

**8. Voice-driven Layout Jig.** Local Whisper + a tiny grammar layer maps "set bay A rotation thirty" → CLI command. Push-to-talk hotkey, immediate audio echo of the resulting state diff.
_Proves the CLI grammar is already a voice grammar._
M • [voice, accessibility, semantic]

**9. Design dictation mode.** Long-form "narrate your studio crit" capture: Claude transcribes, tags speaker turns, produces a structured critique JSON (one entry per design move) you can later replay as comments anchored to specific bays.
_Turns ephemeral conversation into addressable record._
M • [voice, ai, classroom]

**10. Spoken model summary.** `controller_cli speak` reads the model out loud at three detail levels (one sentence, one paragraph, full walkthrough). Local TTS by default.
_The audio equivalent of `axon.png` — a thumbnail you can listen to._
S • [voice, accessibility, semantic]

**11. Verbal undo with reasoning.** Instead of `undo`, you say "undo the rotation but keep the wall I just added." Claude resolves intent against the undo stack and replays only matching mutations.
_Demonstrates semantic undo — a thing CAD has never had._
M • [voice, ai, semantic]

**12. Talkback dimensioning.** Point at a bay in the tactile printout, press a Bluetooth foot pedal, the system speaks "Bay B, six by six meters, rotated 12 degrees, four columns." Uses a USB camera + ArUco fiducials on the printout.
_The killer demo for "tactile is not a one-way export."_
L • [voice, tactile, hardware, accessibility]

## 2.3 Semantic-over-geometric modeling

**13. Adjacency-graph editor.** View of state.json as a graph: zones are nodes, shared walls/doors are edges. `connect kitchen to dining via door` mutates the graph; watcher resolves geometry.
_The clearest demonstration of "semantic is authoritative."_
L • [semantic, rhino]

**14. Constraint solver for bay grids.** Declare "bays A through D are colinear" or "corridor width constant" as JSON facts; a small solver enforces them on every mutation. Failures print as plain-English explanations.
_Constraint-based design without the AutoCAD constraint UI._
L • [semantic, infra]

**15. Program-brief importer.** Paste a written program brief ("3 classrooms 50sqm each, one corridor, two stairs"); Claude emits a starter state.json that satisfies it.
_Brief-to-massing in 10 seconds, fully editable from the CLI afterward._
M • [ai, semantic, classroom]

**16. Named-view bookmarks.** `view save "entry-from-north"` stores a semantic view (target zone, direction, distance) — not camera coordinates. Resolves freshly each load so views survive geometry edits.
_Crash-only viewer principle extended to viewports._
S • [semantic, rhino]

**17. Egress checker.** Walk the adjacency graph from every room to the nearest exit; print "longest egress path is 47m from studio C" with a tactile overlay highlighting it.
_Code compliance as graph traversal, fully accessible._
M • [semantic, accessibility]

**18. Schema diff & migrate tool.** `state migrate --to schema_3` reads any old state.json, prints every field added/renamed/dropped in screen-reader format, and writes the new file atomically. Bundle with `state explain schema`.
_Pure infra polish that pays back every time the project evolves._
S • [infra, semantic]

## 2.4 Critique & review tooling

**19. Pin-up board generator.** `controller_cli pinup --crit fall-final` collects every student's latest state.json from a shared folder, renders plan + axon + tactile booklet, emits one indexed PDF + a printable Braille program.
_Whole-studio choreography from a single CLI call._
M • [classroom, tactile, infra]

**20. Voice-anchored markup.** During a crit, the instructor speaks comments while pointing at the tactile printout (fiducial-tracked). Each comment stored against the bay/zone ID, not pixel coordinates — survives geometry edits and reprints.
_Critique persists across iterations._
L • [voice, tactile, classroom, hardware]

**21. AI design critique.** Claude reads state.json + brief, writes a paragraph critique referencing specific bays by name ("the rotation of bay B breaks the daylight axis you described"). Two modes: gentle and brutal.
_Asynchronous studio feedback for blind students who can't lurk at the pinup._
S • [ai, classroom]

**22. Iteration history reel.** `state history --since 2026-05-01 --tactile` prints one tactile mini-plan per saved version, captioned with the commit message and diff stats. A flipbook of design moves.
_Process portfolio for free, generated from git log._
M • [tactile, classroom, infra]

**23. Annotated walkthrough export.** Combine TASC `describe` with a voice recording: student speaks the design narrative; Claude aligns timestamps to the zones being discussed. Ship an audio+state.json bundle a remote reviewer can scrub.
_A new accessible deliverable format for studio._
M • [voice, classroom, ai]

## 2.5 Site analysis & urban scale

**24. Tactile site context builder.** Pull OSM data for a lat/lon + radius, simplify buildings to footprints, emit a tactile site map with the parcel highlighted and street names in Braille along the edges.
_Site analysis pipeline a blind student can drive end-to-end._
M • [tactile, semantic, accessibility]

**25. Sun-path describer.** Compute solar position across a year, print a Braille-readable summary: "South facade receives 6.2 hours summer, 2.4 hours winter; bay D is shaded by neighbor 3 from 2pm onward." No psychrometric chart.
_Climate analysis as prose, not graphs._
M • [semantic, accessibility, ai]

**26. Tactile wind rose.** Pull NOAA hourly wind data, bin by direction and season; emit a tactile rose with raised-dot magnitudes per octant. Annotated in Braille with prevailing direction.
_The wind-rose chart, finally accessible._
S • [tactile, accessibility]

**27. Walkable-area analyzer.** From a state.json with zones and doors, compute the largest contiguous walkable region from any entry point (BFS on adjacency). Tactile shading: walkable = smooth, isolated = stippled.
_Wayfinding/accessibility audit baked into the model._
M • [semantic, accessibility, tactile]

## 2.6 Hardware bridges

**28. Pegboard digitizer.** USB webcam over a physical pegboard detects peg positions via ArUco-on-peg fiducials and writes them as bay coordinates into state.json. Foot pedal commits each scan. Screen reader announces each new bay.
_The cleanest possible physical-to-digital round-trip demo._
L • [hardware, tactile, accessibility]

**29. Braille label printer driver.** Python wrapper around an Index Everest (or similar embosser) that takes a state.json zone list and emits stick-on Braille labels sized to fit a tactile printout. Zero manual cutting.
_Tactile maps with proper Braille keys, in one shot._
M • [hardware, tactile, accessibility]

**30. Stream Deck command palette.** Each Stream Deck button maps to a named CLI command or macro, with the LCD showing the command in large text. Tactile bumps on key keys make it usable eyes-free.
_A physical CLI launcher for studio workshops._
S • [hardware, accessibility, voice]

**31. 3D-print queue manager.** `print queue add state.json --part zones` slices and queues a tactile relief print for the studio's Bambu/Prusa; supports "edge label" mode printing raised Braille IDs along the model's edge.
_Physical model production as a one-command pipeline._
M • [hardware, tactile]

**32. Haptic feedback wand.** Handheld Bluetooth wand with a vibration motor: held over an ArUco-marked tactile print, it buzzes when you cross a wall, pulses on a door, hums in a zone. Camera + state.json adjacency.
_Adds a third sensory channel to a tactile printout._
L • [hardware, tactile, accessibility]

## 2.7 Bridges to existing CAD

**33. Revit IFC ingest.** Drop an IFC export from Revit into a watch folder; a converter pulls spaces, walls, and grids into a state.json. Lossy but explicit — every dropped attribute logged in plain English.
_Lets a sighted collaborator work in Revit while you work in CLI._
L • [rhino, semantic, infra]

**34. SketchUp round-trip.** `.skp` import via the headless SketchUp SDK, re-export after CLI edits. Names round-trip through component definitions.
_Meets students where they actually are — most arrive knowing SketchUp._
L • [rhino, semantic]

**35. AutoCAD DWG-to-state importer.** Parse a 2D DWG of an existing-building survey via `ezdxf`: layers become zones, polylines become walls. Hand-curate the mapping in a JSON file per project.
_Most architecture practice still lives in DWG._
M • [semantic, infra]

**36. Grasshopper companion node.** A Grasshopper component "Read RAT State" exposes state.json as a parametric input; sighted collaborators iterate in Grasshopper while CLI remains source-of-truth. No writes back.
_Reinforces controller-is-authoritative across collaborators._
M • [rhino, infra]

**37. Speckle stream publisher.** Push state.json + watcher-built geometry to a Speckle stream on every save. Remote reviewers scrub version history in their browser.
_Async studio review for distributed teams._
M • [rhino, web, infra]

## 2.8 AI / Claude integration

**38. Skill: `describe-my-model`.** SKILL.md that runs `controller_cli describe`, pipes to Claude, writes a markdown narrative to the vault under `Work-Sessions/`. Auto-fills the work-session template with what changed since last session.
_Closes the loop between model, Claude, and the Obsidian vault._
S • [ai, mcp, semantic]

**39. Skill: `tactile-this`.** Given any file (image, PDF, state.json), pick the right TACT pipeline automatically and produce a tactile output with sensible defaults. Hides the preset-picking step.
_"One button" tactile for guest users in workshops._
S • [ai, tactile, mcp]

**40. Reference-image stylist.** Given a target reference (Aalto plan, say) and your state.json, Claude proposes 3-5 concrete CLI commands that would nudge your layout toward the reference's qualities, each with a one-line rationale.
_Precedent-driven design as an editable command list, not a magic transformation._
M • [ai, semantic, classroom]

**41. MCP function: `floor-plan-to-state`.** Vision-model MCP function ingests a scanned hand-drawn plan and proposes a starter state.json (zones, doors). The student accepts/rejects each guess on the CLI.
_The "I sketched on tracing paper, now what?" pipeline._
M • [ai, mcp, semantic]

**42. Critique-bot persona library.** `personas/` YAML files (Hejduk, Lina Bo Bardi, building-code-officer, accessibility consultant). `critique --as hejduk` runs state.json through that lens.
_Pedagogical fun, forces students to articulate critique frames._
S • [ai, classroom]

**43. Macro-from-history compiler.** Watch the undo stack; after a useful run, `macro save deepen-corridor` packages the last N mutations as a parametric macro, with Claude inferring sensible parameter names from the diff.
_Macros without writing JSON._
M • [ai, semantic, infra]

## 2.9 Classroom-ready demos

**44. 90-minute workshop kit.** A scripted classroom session: pre-built starter state.json, three guided exercises, a worksheet PDF, a teacher script. Drop into any school visit without bespoke prep.
M • [classroom, tactile]

**45. Studio rubric scorer.** YAML rubric ("clear circulation," "zone hierarchy," "egress") gets scored by Claude against state.json with rationale per item. Students self-check before pinup; you spot-audit.
_Formative assessment a blind student can actually engage with._
S • [ai, classroom, semantic]

**46. Replay-the-master demo.** Library of macros that reconstruct famous small plans (Schroeder House, Maison Domino, a Voisin bay) step-by-step. Students step through and feel the tactile output at each step.
_History-of-architecture as procedural reconstruction._
M • [classroom, tactile, semantic]

**47. Beginner web playground.** No-install web page (built on `web-viewer/viewer.html`) where visitors type CLI commands into a textbox and see/hear the state evolve. Backed by a sandboxed controller via the channel-server.
_A public-facing front door to the project._
M • [web, classroom, accessibility]

**48. Open-house demo loop.** Self-running kiosk that cycles every 30 seconds through "voice command → state diff → tactile print preview," with captions and audio. Set on a table at recruiting events.
S • [accessibility, classroom, web]

## 2.10 Infrastructure / developer experience

**49. State.json fuzzer.** Generate thousands of random-but-schema-valid state.json files; run through controller + watcher; report any that crash or produce non-deterministic geometry. CI integration.
_Crash-only viewer claims need crash-only testing._
M • [infra]

**50. Headless Rhino smoke test.** Bash harness boots Rhino headless on every PR, runs the watcher against three reference fixtures, exports 3dm, diffs vertex counts against golden files.
_Catches watcher regressions that today only surface on the studio machine._
M • [rhino, infra]

**51. Atomic-write audit tool.** Grep-plus-lint scans the repo for any `open(... "w")` not routed through `_atomic_write`. Enforces the principle mechanically.
S • [infra]

**52. CLI command dictionary export.** `controller_cli help --export json` emits a machine-readable list of every command, parameter, and one-line description. Feeds voice grammars, web playground, docs site, and Claude's system prompt.
_One source of truth for what the CLI can do._
S • [infra, voice, mcp]

**53. Screen-reader output linter.** Static analysis on `print()` calls: flag lines over 80 chars, missing OK/ERROR prefix, embedded box-drawing characters, or missing READY: at end of handlers.
_Encodes the screen-reader rules from CLAUDE.md as a test._
S • [accessibility, infra]

**54. Daily vault sync skill.** SKILL.md that, at end of session, summarizes git activity + state.json diffs into a new vault `Work-Sessions/YYYY-MM-DD.md`, ready for human editing. Fills the timesheet stub too.
_The work-session log writes itself._
S • [ai, infra]

## 2.11 Public demos & outreach

**55. Tactile-of-the-week generator.** Weekly cron picks a famous building, builds its state.json from a stored template, posts the tactile PDF to a public page with a written + audio description.
_Continuous demo without continuous effort._
M • [tactile, web, classroom]

**56. "Try-this-plan" QR cards.** Print business-card-sized swell-paper plans with a QR linking to a hosted voice-driven demo of editing that plan. Hand them out at conferences.
S • [tactile, web, accessibility]

**57. Public CLI replay site.** Embed asciinema-style recordings of CLI sessions with synchronized tactile-preview thumbnails. Each session a 90-second story: brief, commands, result.
_Documentation as theater._
M • [web, classroom]

**58. NVDA add-on for studio.** Small NVDA add-on that recognizes the toolkit's `OK:` / `ERROR:` / `READY:` prefixes and gives each a distinct earcon. Bundle with install instructions for the Console Toolkit setup.
_Makes the screen-reader rules pay off with an audible signature._
M • [accessibility, voice, infra]

**59. Accessible portfolio site generator.** `portfolio build` takes a folder of state.json projects and generates a static site: per-project narrative, tactile PDF download, audio description MP3, embedded web viewer. WCAG AA validated in CI.
_Graduating students get an accessible portfolio for free._
L • [web, accessibility, classroom]

**60. Conference-talk autopilot.** Scripted demo runner: `talk run aag-2026 --section opening` advances through a slide+CLI+tactile-print choreography on stage, with cue cards announced through a Bluetooth earpiece.
_The toolkit demoing the toolkit, hands-free._
M • [voice, classroom, infra]

---

# 3. Claude Code learning track

A comprehensive Claude Code feature inventory mapped to accessibility-first architecture pedagogy. For each feature: what it is, why it matters for this project, where to learn it, and a concrete classroom use case.

## 3.1 Hooks — event-triggered automation

Shell commands that execute at lifecycle points (file edits, task completion, input requests). Deterministic — they always fire, unlike instructions Claude might ignore.

**Why it matters here:** Essential for accessibility-first workflows. Enforce auto-formatting on every edit, announce tool completion to screen readers, filter logs to remove visual dependencies before Claude processes them.

**Docs:** https://code.claude.com/docs/en/hooks-guide.md and https://code.claude.com/docs/en/hooks.md

**Key hooks:**
- `SessionStart` — runs at session start; verify dependencies, set environment.
- `UserPromptSubmit` — fires before Claude processes a prompt; filter/enrich input.
- `PreToolUse` — before each tool call; validate or rewrite commands (e.g., block dangerous `rm`).
- `PostToolUse` — after tool execution; process output (filter test logs to failures only).
- `Stop` — when user stops Claude; clean up, git checks, notifications.
- `Notification` — desktop/terminal alerts when Claude needs input.
- `SubagentStop`, `PreCompact` — lifecycle moments around delegation and compaction.

**Classroom use case:** Before a student runs tactile export, a hook validates `state.json` for completeness, auto-formats it, and announces "state ready for export" via the JAWS bridge already scaffolded in `tools/webui/hooks/screen-reader/`.

## 3.2 MCP servers — connecting external tools

Model Context Protocol standardizes Claude's connection to external data and tools. Servers run locally (stdio) or remotely (HTTP).

**Why it matters here:** You already publish two (layout-jig, tactile). Building a `superfund` MCP (EPA APIs) and a TASC MCP would be the highest-leverage moves for the second-year studio.

**Docs:** https://code.claude.com/docs/en/mcp.md

**Key concepts:**
- Stdio (local processes) vs HTTP (remote, OAuth2-capable).
- Tools (functions Claude calls), Resources (data referenced via `@server:protocol://path`), Prompts (exposed as `/mcp__servername__promptname`).
- Tool search: defers loading definitions until needed to save context.
- Scope hierarchy: Local (private) → Project (`.mcp.json`, shared) → User (global).

**Classroom use case:** Wrap `controller_cli.py` even more fully via MCP so Claude orchestrates entire tactile workflows as MCP tool calls — `bay add`, `zone list`, `macro run` — with all communication text-based and screen-reader-friendly.

## 3.3 Skills — reusable workflow packages

Markdown files (`skills/<skill-name>/SKILL.md`) bundling instructions, workflows, and code pointers. Claude loads them on-demand when relevant or when invoked.

**Why it matters here:** Your taxonomy already calls these "skills" (renaming the prior "skill" concept to "macro"). You're ahead of the curve. Skills package repeatable procedures so students don't re-explain them.

**Docs:** https://code.claude.com/docs/en/skills.md

**Difference from CLAUDE.md:** CLAUDE.md loads every session (base context, costs tokens always). Skills load on-demand only.

**Classroom use case:** Create `/tactile-export`, `/validate-state`, `/accessibility-audit` skills. Students invoke with `/skillname` and the workflow runs; no re-explanation needed. You already have `laser-export` and `update`; aim for 8–12 by fall.

## 3.4 Subagents — parallel task isolation

Specialized AI instances spawned for specific tasks, each with its own context, system prompt, tools, and permissions. Main Claude orchestrates; subagents run independently and return summaries.

**Why it matters here:** Subagents preserve context by isolating verbose work. A "rhino-viewer" subagent can explore a 3D model while the main agent focuses on command generation. Use Haiku for cheap subagents, Sonnet/Opus for main reasoning.

**Docs:** https://code.claude.com/docs/en/sub-agents.md

**Patterns:**
- Custom subagent types in `.claude/agents/`: name, description, system prompt, allowed tools, model.
- Parallel execution: spawn multiple to work on different parts simultaneously.
- Resource constraints: limit subagent tool access.

**Classroom use case:** When a student asks "what does the layout jig controller do?" spawn a "codebase-explorer" subagent (Haiku) to read source files and summarize, letting the student stay focused on their design.

## 3.5 Settings.json — configuration & permissions

JSON files at three scopes: user (`~/.claude/settings.json`), project (`.claude/settings.json`), local (`.claude/settings.local.json`, gitignored). Configure permissions, env vars, hooks, model defaults.

**Why it matters here:** You can enforce project-wide rules — "never edit state.json without approval," accessibility hooks wired by default — and pre-approve safe commands so students aren't fighting permission prompts.

**Docs:** https://code.claude.com/docs/en/settings.md

**Permission rules:**
- Deny / Ask / Allow lists. Deny first, then ask, then allow.
- Rule syntax: `Bash(git commit *)`, `Read(./src/**)`, `Edit(*.md)`.

**Classroom use case:** Project `.claude/settings.json` denies `.env` access, pre-approves `tact render`, `tasc *`, common git reads. A Notification hook announces "command complete" via speaker when tools finish.

## 3.6 Headless mode — scripting & automation

Non-interactive CLI invocation: `claude -p "prompt"`. Run from scripts, CI/CD, or pipes.

**Why it matters here:** **Headless is the right entry point for week-1 students under a screen reader.** The TUI streams output (bad for screen readers). Headless is request/response. See §5.2.5 for the studio policy.

**Docs:** https://code.claude.com/docs/en/headless.md

**Flags:**
- `-p "prompt"` — non-interactive.
- `--output-format text|json|stream-json` — for scripting.
- `--allowedTools "Read,Edit,Bash"` — pre-approve tools.
- `--continue` — continue the last conversation.
- `--bare` — skip auto-discovery (hooks, skills, CLAUDE.md); ideal for CI reproducibility.

**Classroom use case:** `claude -p "validate this state.json for accessibility compliance" --output-format json` in a pre-commit hook that blocks bad states.

## 3.7 Memory & CLAUDE.md hierarchy

Two systems: (1) CLAUDE.md files you write that persist instructions, and (2) auto-memory Claude writes itself.

**Docs:** https://code.claude.com/docs/en/memory.md

**CLAUDE.md scopes:**
- Managed policy (org-wide).
- User (`~/.claude/CLAUDE.md`) — personal preferences.
- Project (`./CLAUDE.md`) — team-shared, in git.
- Local (`./CLAUDE.local.md`) — personal overrides, gitignored.

**Path-scoped rules** (`.claude/rules/`): conditional instructions loading only when Claude edits matching files (e.g., `tools/rhino/**/*.py` triggers IronPython 2.7 rules).

Auto-memory: stores under `~/.claude/projects/<project>/memory/MEMORY.md`. First 200 lines / 25KB load at startup; topic files load on-demand.

**Classroom use case:** Project CLAUDE.md (you have one) documents tactile workflows, accessibility standards, and TACT/TASC syntax. Local CLAUDE.md per student stores their sandbox URLs and test data.

## 3.8 GitHub Actions integration

Automated workflows triggered by GitHub events. Claude can review code, implement features, fix bugs in CI.

**Docs:** https://code.claude.com/docs/en/github-actions.md

**Setup:** Install Claude GitHub App (https://github.com/apps/claude); add `ANTHROPIC_API_KEY` secret; create a workflow file.

**Patterns:**
- `@claude implement this feature` on an issue → PR with code.
- Automatic PR review on every push (no trigger needed).
- Daily report on open issues and PRs.

**Classroom use case:** Workflow that runs when students push: Claude validates state.json, runs style checks, comments on the PR with suggestions. No manual review of mechanical issues.

## 3.9 Web & Mobile (Claude Code on the Web)

Run Claude Code in your browser at claude.ai/code or in the iOS app. No local setup. Ideal for long-running tasks, parallel sessions, or remote work.

**Docs:** https://code.claude.com/docs/en/claude-code-on-the-web

**Limits:** Some local tools (Rhino watcher) require a terminal session; sandboxing applies. Environment policies determine outbound network access.

**Classroom use case:** Students submit tactile images via web Claude Code, which runs TACT conversion and stores PDFs in shared storage. Done in background while they're in lecture.

## 3.10 Fast mode (`/fast`)

Configuration flag making Claude Opus ~2.5× faster at higher per-token cost. Toggle with `/fast`. Same quality, much lower latency.

**Docs:** https://code.claude.com/docs/en/fast-mode.md

**When to use:** Live demos, real-time critique with students, rapid iteration. Avoid for batch/CI/long autonomous runs.

## 3.11 Slash commands (built-in + custom)

Built-in: `/help`, `/clear`, `/compact`, `/cost`, `/fast`, `/config`, `/agents`, etc. Custom commands live in `.claude/commands/<name>.md` and run as slash commands.

**Classroom use case:** Custom `/critique` command that runs your design-critique skill against the current state.json. Students type `/critique` instead of remembering the full skill invocation.

## 3.12 Cost management

Token pricing varies by model (Opus > Sonnet > Haiku). Track with `/usage` or the Console.

**Docs:** https://code.claude.com/docs/en/costs.md

**Optimization:**
- Sonnet 4.6 for general coding, Opus 4.7 for complex reasoning, Haiku 4.5 for subagents.
- `/clear` between unrelated tasks; `/compact` with focus instructions.
- Hooks to filter logs/grep errors before Claude sees them.
- MCP tool search defers tool definitions until needed.
- Prompt caching (implicit, free): repeated CLAUDE.md and large attachments cost ~10% on cache hits.

## 3.13 Agent SDK (programmatic custom agents)

Python and TypeScript libraries for building custom agents using Claude's tools and agent loop. Not Claude Code itself.

**Docs:** https://code.claude.com/docs/en/agent-sdk/overview.md

**When to use Agent SDK vs Claude Code:**
- Building a custom web UI for students (not the web Claude Code).
- Running Claude in a serverless environment.
- Structured outputs or custom tool approval callbacks.
- Full programmatic control over session state.

You probably don't need this for the toolkit itself, but it's worth knowing about — `tools/webui/` could grow into a custom Agent-SDK-powered UI if the Ink TUI bypass needs to go deeper.

## 3.14 Claude API directly (drop down from CC)

Sometimes you'll want the raw API: prompt caching, batch (50% off, 24h turnaround), tool use, vision, citations, files, computer use, code execution.

**Vision:** TACT already uses this.
**Batch API:** `tact convert --batch *.png` for course-sized jobs.
**Prompt caching:** Cache the architectural-vocabulary system prompt for cheap multi-image runs.
**Citations:** Claude returns source spans for documents — great for "build a reading list with page numbers."
**Files API:** Upload large drawing sets once, reference by ID.
**Computer use:** Drive Rhino's GUI for the rare commands TASC can't reach.

## 3.15 IDE extensions

VS Code and JetBrains extensions surface Claude Code inside the editor. Inline diffs, @-mentions, plan review, conversation history.

Same settings, CLAUDE.md, and MCP servers apply across all surfaces (terminal, web, mobile, IDE).

## 3.16 Sub-agents vs. Skills vs. Slash commands vs. Hooks — when to use which

| Feature | Use when | Load timing | Context cost |
|---------|----------|-------------|--------------|
| CLAUDE.md | Base rules, always-needed context | Session start | High (always loaded) |
| Skills | Repeatable workflows | On-demand | Low |
| Subagents | Parallel isolated tasks | When spawned | Per-subagent |
| Slash commands | Quick aliases, toggles | Built-in or on-demand | Minimal |
| Hooks | Deterministic enforcement | Specific lifecycle event | None (shell scripts) |

**Decision tree for the studio:**
- "How should students format state.json?" → CLAUDE.md.
- "How do I automate the tactile export workflow?" → Skill (`/tactile-export`).
- "How do I reduce tokens when Claude explores the codebase?" → Subagent.
- "How do I prevent direct edits to state.json?" → Hook (PreToolUse) or permission deny rule.
- "How do I speed up responses?" → `/fast`.

## 3.17 If you only learn 5 things

Ranked for this specific project:

1. **CLAUDE.md + Memory.** Document conventions, tactile workflows, accessibility standards, TACT/TASC syntax once. Every session inherits.
2. **Hooks + settings.json.** Enforce accessibility rules at the lifecycle level. Hooks fire deterministically — no LLM decides whether to follow them. Wire the three hooks already written in `tools/webui/hooks/`.
3. **MCP servers.** You already write them; the higher-leverage version is building one wrapping `controller_cli.py` so Claude orchestrates the toolkit as MCP tool calls instead of CLI invocations.
4. **Skills.** Package `/tactile-export`, `/validate-state`, `/accessibility-audit`, `/ej-audit`, `/rod-parser`. Students invoke; the workflow runs.
5. **Headless mode + GitHub Actions.** Automate validation, linting, and export on every commit or PR. Students push, CI runs accessibility checks, Claude comments with feedback. Use `--bare` for reproducibility.

---

# 4. Second-year studio — Superfund sites + AI workflows

Fifty-three workflows by phase. Concrete enough to assign. Items marked **Ties to RAT** plug directly into existing Layout Jig / TACT / TASC primitives.

## 4.1 Site research & contamination understanding

**1. CERCLIS/SEMS pull-and-parse agent.** Students give Claude a Superfund site name. Claude WebFetches the SEMS record, NPL listing narrative, and Five-Year Review PDFs, then returns a structured brief: operable units (OUs), responsible parties, listing date, current ROD status. _Easy. Datasets: SEMS, NPL, cumulis.epa.gov._

**2. ECHO enforcement history timeline.** Students query EPA's ECHO API for a facility's violation history; Claude builds a chronological narrative of who polluted, when, and what penalties were assessed. Output is a screen-reader-friendly timeline written to `controller/state.json` as semantic events. _Easy. ECHO REST API, FRS facility registry._

**3. TRI contaminant decoder.** Students paste a TRI row (TCE, hexavalent chromium, PFOA); Claude produces a one-page fact sheet covering chemical behavior, half-life in soil vs. groundwater, primary exposure routes, regulatory limits (MCL, RfD, IRIS), and known epidemiological links. _Easy. Pulls EPA IRIS, ATSDR ToxProfiles, PubChem._

**4. Envirofacts multi-database mashup skill.** Custom SKILL.md at `skills/envirofacts-pull/` that, given a lat/lon or zip, queries Envirofacts across FRS, TRI, SDWIS, AIRS/AFS, RCRAInfo and returns a unified contamination profile. Stored as JSON for downstream use. _Moderate (API quirks, rate limits)._

**5. Historical aerial photo analyzer.** Students upload USGS EarthExplorer aerials from 1930s/50s/70s/90s/present; Claude vision annotates land-use change: smokestacks 1952, lagoons 1968, capped 1991. Cross-referenced against Library of Congress Sanborn maps. _Moderate (manual aerial download)._

**6. Deed chain & redlining overlay.** Deed records from the county recorder + HOLC redlining maps from the Mapping Inequality project (dsl.richmond.edu/panorama). Claude correlates which properties were Black/immigrant-coded and which became industrial dumping grounds — the canonical pattern in Sugrue's _Origins of the Urban Crisis_. _Moderate._

**7. ProQuest / Newspapers.com narrative miner.** Students export historical clippings (1978 Love Canal, 1980s Times Beach dioxin); Claude extracts who-said-what, identifies community leaders by name, surfaces the moment regulatory action shifted. Builds a citable narrative bibliography. _Easy (requires database access)._

**8. Oral history cross-reference engine.** Students collect 5-10 community oral histories; Claude clusters them by theme (smell, illness, employment, displacement) and matches claims against the regulatory record from #1-2 to surface "things residents knew before EPA confirmed." _Moderate._

## 4.2 Site analysis & visualization

**9. QGIS / PyQGIS scripting assistant.** Students describe what they want ("buffer the plume 500m, intersect with parcels zoned residential, output a list"); Claude writes the PyQGIS script. The student runs it. _Easy._

**10. Contamination plume state.json layer. (Ties to RAT.)** Extend the Layout Jig schema with a `contamination` block: polygon coordinates, contaminant ID, concentration field, depth band, confidence. TACT then renders tactile site models where the plume is a distinct hatch pattern — students literally feel where the pollution is. _Moderate._

**11. Tactile contamination section renderer. (Ties to RAT.)** New `tact section` command takes a state.json with subsurface layers (fill, native soil, water table, bedrock) + a plume volume and renders a vertical cross-section PIAF. Plumes use a different tactile texture than aquifers. _Moderate._

**12. Sensitive receptor MCP function. (Ties to RAT.)** A `receptors_within` MCP function that, given a site centroid, queries: NCES schools API, HIFLD hospitals, USGS NWIS wells, ACS census blocks for under-5 and over-65 populations. Returns a receptor inventory pinned into state.json as zone metadata. _Moderate._

**13. Soil/groundwater statistical summary.** Students dump CSV of monitoring well data; Claude computes 95% UCL, compares against PRGs and MCLs, flags exceedances. Outputs screen-reader-friendly with `OK:`/`ERROR:` prefixes. _Easy._

**14. Wind rose + air dispersion plot.** Students pull NOAA ISD wind data for the nearest met station; Claude builds an annual wind rose, then runs a simplified AERMOD-style Gaussian dispersion for fugitive dust. _Hard for full AERMOD; moderate for simplified._

**15. Site walk audio annotator. (Ties to RAT.)** Students record an audio walking tour; Claude transcribes (Whisper), geotags utterances against the GPS track, writes a spatial narrative back into state.json as "observation" zones. _Moderate._

**16. Layout Jig contamination zones. (Ties to RAT.)** Use existing `zone add` but extend the type vocabulary: `zone add plume-tce`, `zone add cap-multilayer`, `zone add hot-spot-pcb`. Students model contamination alongside the architectural program — impossible to design around without acknowledging. _Easy._

## 4.3 Community engagement & ethics

**17. EJScreen equity briefing generator.** Students hand Claude an address; Claude calls EJScreen REST API and returns the 12 EJ indicators (PM2.5, ozone, diesel PM, lead paint, Superfund proximity, RMP proximity, hazardous waste, wastewater, demographic index) with percentile rankings. _Easy. ejscreen.epa.gov/mapper/ejscreenapi.html._

**18. Interview transcription + thematic coding.** Students record community interviews; Claude transcribes, then performs inductive thematic analysis (Braun & Clarke) generating a codebook, frequency table, and supporting quotes. Maintains anonymity by default. _Easy._

**19. Community asset map MCP. (Ties to RAT.)** A `community_assets_add` MCP function: students walk a neighborhood with their phone, dictating "barbershop at 412 Main, community fridge on Elm" — each becomes a zone in state.json, TACT renders them as tactile dots alongside the contamination. _Moderate._

**20. Accessible feedback form generator. (Ties to RAT.)** Claude generates the same comment-collection instrument in five forms: large-print PDF, screen-reader-optimized HTML, plain-Spanish, tactile braille (via TACT), audio (TTS). Unified dataset regardless of input modality. _Moderate._

**21. EJ court case precedent search.** Students query "what happened in cases like ours?" — Claude retrieves _Bean v. Southwestern Waste Management_ (1979, Houston), _R.I.S.E. v. Kay_ (1991), _South Camden Citizens in Action v. NJDEP_ (2001), the _Warren County PCB protests_. Summarizes legal outcome, advocacy lessons, design implications. _Moderate._

**22. Plain-language ROD translator.** Students paste a section of the Record of Decision; Claude rewrites it at 8th-grade reading level, preserving technical accuracy. Includes a "what this means for residents" sidebar. _Easy._

## 4.4 Design ideation & precedent

**23. Phytoremediation species selector.** Students input contaminant + climate zone (USDA hardiness + Köppen); Claude returns ranked species with documented uptake performance: _Helianthus annuus_ and _Brassica juncea_ for lead/cadmium, _Pteris vittata_ for arsenic (Ma et al. 2001, _Nature_), _Populus deltoides_ for TCE, _Salix_ spp. for petroleum hydrocarbons, _Festuca arundinacea_ and _Panicum virgatum_ for PAHs. Cites EPA Phytotechnologies Action Team documents. _Easy._

**24. Mycoremediation strain matcher.** Fungal version: _Pleurotus ostreatus_ for petroleum and PAHs (Stamets/Battelle work at Fort Bragg), _Trametes versicolor_ for pentachlorophenol, _Phanerochaete chrysosporium_ for chlorinated solvents. Honest about lab-vs-field performance gap. _Moderate._

**25. Remedy selection trade-off matrix.** Claude builds a matrix across cap-and-cover, ISCO (in-situ chemical oxidation), soil washing, thermal desorption, bioventing, MNA (monitored natural attenuation), excavation-and-haul. Columns: cost/yd³, timeline, residual risk, community-disruption score, carbon footprint. Pulls EPA's Remediation Technologies Roadmap (FRTR matrix). _Moderate._

**26. Brownfield precedent pattern-matcher.** Students upload site analysis drawings; Claude (vision) compares against a curated precedent library: Landschaftspark Duisburg-Nord (Latz, 1991), Fresh Kills Lifescape (Field Operations, 2001-), Gas Works Park (Haag, 1975), Westergasfabriek (Gustafson Porter), Zollverein (OMA), Parc des Buttes-Chaumont as proto-precedent, the High Line, Renaissance Park (Hargreaves), Vintondale Reclamation Park (Stacy Levy). Returns "your site resembles X because Y." _Moderate._

**27. Precedent skill pack. (Ties to RAT.)** Build `skills/brownfield-precedents/` SKILL.md with 40 precedents in structured metadata (site type, contaminant, remedy, designer, year, scale, primary moves) so Claude can answer "show me precedents that use phytoremediation + public access + AMD treatment" without web-searching every time. _Moderate._

**28. AI-as-design-partner generative sessions.** Students keep a Markdown design journal in the vault; Claude reads the running journal each session and asks pointed questions: "You moved the school to the south edge — did you check whether that's downwind of the cap?" _Easy._

**29. Counter-precedent search.** For every precedent the student loves, Claude finds a counter-precedent that critiques it. Love Duisburg-Nord? Read Brian Davis on the politics of post-industrial aesthetics. Love Fresh Kills? Read Sze's _Noxious New York_ on Staten Island environmental justice. _Moderate._

## 4.5 Simulation & modeling

**30. Plume migration estimator.** Students input hydraulic conductivity, gradient, porosity, source concentration; Claude generates a Python script using a simplified advection-dispersion model (or MT3DMS via FloPy if MODFLOW is available) and projects plume extent at 10/30/100 years. _Hard (MODFLOW install + validated inputs)._

**31. Remediation timeline simulator.** Given remedy + contaminant + concentration, Claude estimates years-to-cleanup using first-order biodegradation, EPA-published phyto uptake rates, or engineered system throughputs. Honest uncertainty bands. _Moderate._

**32. Sea-level rise + plume stress test.** For coastal Superfund sites (Gowanus, Newtown Creek, San Jacinto Waste Pits), Claude overlays NOAA SLR scenarios on the cap design and flags inundation/erosion risk to the remedy. Honest about the _Hurricane Harvey unearthed the San Jacinto cap_ precedent. _Moderate. NOAA Digital Coast, Climate.gov._

**33. Tactile time-lapse render. (Ties to RAT.)** Students pick 5 timesteps (year 0, 5, 15, 30, 100); TACT renders 5 PIAF pages where the plume shrinks and the cap "weathers." Blind/low-vision crit panel can feel the temporal logic of the design. _Moderate._

**34. Hydrology + cap performance diagram.** Students input rainfall (PRISM data), cap geometry, vegetation cover; Claude estimates runoff, infiltration, leachate via simplified HELP (Hydrologic Evaluation of Landfill Performance). _Hard for full HELP; moderate for hand-spreadsheet equivalent._

**35. Simulation-output narrator.** After any simulation, Claude reads the output files and produces a screen-reader-friendly summary: "At year 30, the plume centerline has migrated 142 meters northeast. Concentration at well MW-12 drops below MCL at year 47." No tables, no plots — just sentences. _Easy._

## 4.6 Drawing & representation

**36. Subsurface section AI overlay. (Ties to RAT.)** Students draw a base section in Rhino; Claude generates a contamination overlay layer with plumes, monitoring wells, water table, and cap layers — written to state.json and rendered by the watcher. _Moderate._

**37. Time-lapse remediation diagram series. (Ties to RAT.)** A `controller/macros/remediation_timelapse.json` macro snapshots state.json at user-defined intervals during simulated remediation and exports each as 3dm + PIAF. Outputs a flip-book. _Moderate._

**38. Tactile + visual hybrid plates. (Ties to RAT.)** Every final plate is produced in two registered versions: visual PDF and tactile PIAF, with identical layout/scale. Tactile uses TACT's hatch palette to encode visual color-coding. _Moderate._

**39. AI-drafted diagram captions. (Ties to RAT.)** Every diagram exported from state.json gets an alt-text caption auto-drafted by Claude reading the underlying JSON — not pixel-recognition guesses. The student edits, the system saves. Thesis book is fully screen-reader navigable. _Easy._

**40. Stable Diffusion / ControlNet atmosphere studies.** Students use ControlNet (depth + canny from Rhino exports) to generate atmospheric renderings of _the same site at year 5, 30, 100_. Forces students to design what the site feels like, not just what it does. _Moderate (local SD setup or paid API)._

**41. Contamination-as-figure drawing convention.** Studio-wide drawing convention where the plume is rendered as figure (solid, dark) and the architecture is ground — inverting the standard. Claude generates the SVG symbol library and sets up the Rhino template. _Easy._

## 4.7 Writing, regulatory navigation, presentation

**42. ROD parser skill. (Ties to RAT.)** A `skills/rod-parser/` SKILL.md that takes any EPA Record of Decision (often 200+ pages) and extracts: selected remedy, cleanup levels for each COC, ARARs invoked, cost estimate, public comment summary, alternatives considered and why rejected. _Easy._

**43. CERCLA/RCRA navigator.** Students ask plain questions ("Can our community garden go on a site still on the NPL?") and Claude returns the regulatory pathway with specific section citations — CERCLA §121, RCRA Subtitle C, AAI under 40 CFR Part 312, BFPP protections, EPA Comfort/Status letters. _Moderate (cite-with-date discipline required)._

**44. Two-audience presentation generator.** From a single source-of-truth design document, Claude produces two parallel slide decks: a technical version with COCs, MCLs, design ARARs (for the EPA RPM and consulting engineer crit), and a community version in plain language with no acronyms (for the CAG — Community Advisory Group — crit). _Easy._

**45. Brownfield grant writing assistant.** Students draft applications for EPA Brownfields Assessment/Cleanup/Multipurpose grants ($500K-$1M typical), HUD Choice Neighborhoods, state revolving funds. Claude knows scoring rubrics, populates boilerplate, flags most-frequently-missing sections (CBO partnership letters, leveraging documentation). _Moderate._

**46. Public comment drafting studio.** The next ROD comment period for the studio's site is identified; students draft formal public comments. Claude knows what makes a comment legally substantive (specific objection to specific ARAR application, alternative remedy proposal with citation) vs. dismissible. _Easy._

**47. Five-Year Review critical read.** EPA conducts Five-Year Reviews on every Superfund site. Claude pulls the most recent FYR, summarizes protectiveness determinations, flags inconsistencies between EPA's claims and the underlying monitoring data tables. _Moderate._

## 4.8 Critique, review, peer feedback

**48. Devil's-advocate crit bot.** Before pin-up, students run their design through Claude with: "be the most hostile reviewer this work could face — the consulting engineer who thinks landscape architecture is decorative, the community member who's been promised parks before and got nothing, the EPA RPM worried about long-term stewardship liability." Returns three distinct critiques. _Easy._

**49. EJ/equity checklist auditor. (Ties to RAT.)** Custom skill `skills/ej-audit/` runs a 25-point checklist against the proposal: Who maintains this in year 30? Who pays property tax once it's clean? Is there a community benefits agreement? Is there a deed restriction surviving redevelopment? Is the community's existing use displaced? _Moderate._

**50. Precedent-distance score.** Claude compares the student's proposal against the curated precedent library (#26-27) and reports a similarity score per precedent — useful for catching unintentional plagiarism _and_ for asking "you're 80% Duisburg-Nord; what's the 20% that's yours?" _Hard (careful embedding setup)._

**51. Pre-pin-up self-critique macro. (Ties to RAT.)** A `controller/macros/precrit.json` that triggers in sequence: ROD-compliance check, EJ audit, screen-reader walkthrough of alt-text, precedent distance check, "name the three weakest moves in your project" question. _Moderate._

**52. Cross-studio peer match.** Claude reads all student work in the studio (with consent) and proposes peer review pairs based on _complementary_ strengths/weaknesses — students whose projects share a contaminant but differ in remedy strategy, or share a site condition but differ in community engagement. _Moderate._

**53. Final review transcription + action items. (Ties to RAT.)** During final reviews, audio is captured; Claude transcribes per-student, extracts the substantive critique (separating it from social chatter), and emails each student a screen-reader-friendly summary with action items by Monday morning. _Moderate._

## 4.9 Cross-cutting infrastructure

**One state.json per student site.** Each project is a versioned `controller/state.json` in their own git branch (per the `author/action-topic` naming — e.g., `maya/add-gowanus-site`). The watcher renders to Rhino; TACT renders the same state to tactile PDFs for the studio's blind crit member. Same source of truth, multiple modalities — which is the whole point of doing this inside the Radical Accessibility Toolkit rather than vanilla Rhino. The studio becomes a living test of the "Semantic Over Geometric" principle: students describe _what contamination is_, not just where it is, and the system gives them visual, tactile, and verbal outputs from one description.

---

# 5. Third-year studio — radically accessible (with Daniel)

Sixty-plus tactics for a tactile-first, mixed-ability studio where blind, low-vision, and sighted students work the same way through the same toolkit. Tactics over principles; each is a move you can deploy in class.

## 5.1 Studio structure & calendar

**1.1 Week-zero tactile bootcamp (4 sessions before design starts).** Before the brief drops, every student spends a full week doing only tactile reading and CLI scaffolding — no Rhino, no design. Sessions: (a) reading swell-paper plans by hand, (b) NVDA + Console Toolkit in cmd.exe, (c) running `template load` and `tact convert` on canned exercises, (d) recording a 60-second audio description of an existing plan.

**1.2 Calibration kit on day one.** Hand every student an identical box: pegboard, a stack of PIAF sheets of known plans (a Mies house, a Kahn plan, an Alvar Aalto plan), a USB stick with `controller/state.json` files matching those plans, and a printed Braille/large-print command card. They are told: these are the same plan in three media.

**1.3 Five-phase semester arc.** (1) Read (weeks 1-2, tactile precedents only), (2) Site (weeks 3-4, voice-narrated site walks + tactile site model), (3) Concept (weeks 5-7, TASC sketching, no Rhino yet), (4) Schematic (weeks 8-10, full Layout Jig + tactile prints), (5) DD & Final (weeks 11-15). Each phase ends with a tactile pin-up, never a screen review.

**1.4 Skill ladders, not skill dumps.** Each week introduces exactly one new command family and one new tactile output. Week 3: `tasc site`/`tasc zone`. Week 4: `tasc bay`. Week 5: `tact convert --preset`. Week 6: `tact convert --detect-text --braille-grade 2`. Week 7: state.json hand-editing. A student who misses a week has one specific catch-up target.

**1.5 Friday "macro hour."** Last hour of every Friday, students write one macro from their week's repeated commands and commit it to `controller/macros/`. By week 8 the class has a shared library of 30-40 macros.

**1.6 Milestone tactile portfolios.** At weeks 4, 7, 10, 13, students assemble a small tactile binder: 4-6 PIAF sheets, one 3D-printed massing, one `state.json` printed to Braille. The binder, not a slide deck, is the milestone.

## 5.2 Tool onboarding

**2.1 Minimum viable week-1 toolset.** By Friday of week 1 every student can: launch NVDA + Console Toolkit in cmd.exe, run `python controller/controller_cli.py` and execute five commands, run `tact convert sample.png --preset plan-bw`, run `template load classroom-3x3`, and read a fresh PIAF print with their hands. That's the floor.

**2.2 Pair-installed environments.** Students install in pairs using `python setup.py` while one reads the screen reader output aloud. No solo installs. Surfaces every install bug as a shared learning moment.

**2.3 NVDA Console Toolkit as the default terminal.** Studio policy: cmd.exe + NVDA + Console Toolkit, never Windows Terminal, never PowerShell ISE. Demonstrate the difference live.

**2.4 Voice input drills, ten minutes a day.** Each studio session opens with a ten-minute dictation drill: students dictate a known command sequence ("tasc bay A three by three spacing twenty twenty at zero zero") into Claude Code headless. Mistakes graded by whether the final state.json is correct.

**2.5 Claude Code in headless mode only for weeks 1-2.** Students use `claude -p "..." --output-format text`, never the TUI. Removes the Ink streaming UI and forces a request/response rhythm compatible with screen readers. TUI is unlocked after they've demonstrated headless fluency.

**2.6 Web UI as the second interface, not the first.** Students learn `start-webui.bat` / `start-webui.sh` in week 3. Frame it as "the same Claude, in a JAWS-friendly window," not as a friendlier alternative.

**2.7 Tactile-output certification.** Before a student is allowed to submit a tactile deliverable, they must independently produce a PIAF print, hand it to a partner blindfolded or eyes-closed, and have the partner correctly identify the building type, orientation, and a named element. Pass/fail, repeat until passed.

**2.8 Two-hour "tour of the toolkit" lab.** Scripted lab in week 1: every Tool in the taxonomy — Layout Jig, Image Describer, Tactile Printer, TACT, TASC, Rhino Viewer — 15 minutes each, one command, one output. Lab handout is Braille-printed.

## 5.3 Collaboration patterns

**3.1 Three-mode pair rotation.** Every pair works in three modes across the week: (a) driver/navigator on one keyboard, (b) parallel — both editing the same `state.json` on different branches with `git`, (c) tactile exchange — one prints a PIAF, hands it over, partner re-enters it as state.json. Rotate roles every session.

**3.2 Blind-lead defaults.** When a pair contains a blind and a sighted student, the blind student drives the keyboard and the sighted student is forbidden from touching the mouse or pointing at the screen. The sighted student narrates only in semantic terms ("bay A is rotated thirty degrees" — never "the box on the left").

**3.3 The state.json handoff ritual.** Collaboration always ends with `git commit` of `state.json` and a 30-second audio note. The next session opens with the receiving student listening to the note, running `git pull`, and reading state aloud via `cmd_tts` before any new work.

**3.4 Tactile-first peer critique.** When A reviews B's work, A receives only the PIAF print and the audio walkthrough — not the screen, not the state.json. A writes critique by hand or dictates it. Only afterward does A see the state.json.

**3.5 Group projects with role specialization.** Four-person teams divide into: site lead (TASC), program lead (Layout Jig zones), tactile lead (TACT presets and PIAF output), audio lead (audio walkthroughs and state.json narration). Roles rotate at each milestone.

**3.6 No-screen pairing days.** One day per week, all monitors are off (or covered). Pairs work entirely through audio output, PIAF prints, and pegboards. Most productive day of the week, per past students.

**3.7 Shared macros as collaboration currency.** Pairs write macros for each other. "Write me a macro that adds a 3x3 bay rotated 30 degrees with a corridor on the south side." The macro becomes a gift, signed in the JSON `meta` block.

## 5.4 Critique format

**4.1 The three-channel desk crit.** Every desk crit consumes three artifacts in order: (1) tactile print(s) on the table, (2) audio walkthrough played aloud, (3) state.json read via `cmd_tts` or screen reader. Faculty and student keep hands on the print throughout. No screen during desk crit.

**4.2 The "no deixis" rule.** During any crit, words like "here," "this," "that corner," "over there" are flagged and the speaker must restate using semantic IDs: "bay A," "the north corridor," "the entry column at grid B-3." Faculty buzz a small bell or say "restate" — a ritualized correction, not shaming.

**4.3 Pin-up as tactile table.** Pin-ups happen on tables, not walls. Each student has a 60cm x 90cm tactile zone: PIAF prints, 3D-printed massing, a printed Braille legend, a Bluetooth speaker playing the audio walkthrough on loop.

**4.4 Structured verbal feedback template.** Critics give feedback in a fixed format: (1) "What I felt in the tactile," (2) "What I heard in the audio," (3) "What the state.json told me," (4) "What's missing across the three."

**4.5 Crit recording as default.** Every crit recorded (audio only, with consent), dropped into the project folder named `crit-YYYY-MM-DD.m4a`. Students re-listen before the next session. No note-taking required during crit — frees both hands for the print.

**4.6 Jury pre-briefing the morning of.** Jurors get a 45-minute briefing: the "no deixis" rule, how to read a PIAF print, how to operate `cmd_tts`, the project's semantic vocabulary. Tactile cheat sheet at every seat.

## 5.5 Deliverables per phase

**5.1 The standard triple deliverable.** Every phase produces: (a) a tactile artifact (PIAF for plans/sections, 3D print for massing), (b) a `state.json` committed to git, (c) an audio walkthrough (3-5 min mp3). No phase accepts a deliverable missing any leg of the triple.

**5.2 Concept phase: pegboard + 200-word narrative.** Concept delivered as a pegboard arrangement (photographed for the archive), a 200-word audio narrative, and a minimal `state.json` containing only zones — no walls, no bays. Forces concept to live at the program/relationship level.

**5.3 Schematic phase: TASC site + bays + corridors.** State.json with `tasc site`, three to six zones, structural bays, corridors. Exported via `tasc export piaf` and `tasc export 3dm`. Audio walkthrough generated semi-automatically from `tasc describe`.

**5.4 Design development: walls, apertures, materials.** DD phase adds wall thicknesses, apertures (`cmd_aperture`), material/hatch assignments (`cmd_hatch`). Tactile output uses two presets: `plan-detail` for the plan, separate elevation PIAF.

**5.5 Final: full triple plus 3D print.** Full triple plus a Bambu-printed massing (`cmd_bambu`) at a fixed scale specified in the brief. Plus a Braille legend printed via `controller/braille.py`. Plus the section cut (`cmd_section`).

**5.6 No renderings, ever.** Renderings are banned as deliverables for the entire semester. Stated in the syllabus.

**5.7 Format specs are in the syllabus, not the brief.** PIAF page size, print resolution, 3D print scale, audio file length/format (mp3, mono, 96kbps), state.json schema version — all fixed. Students never debate format; they debate content.

## 5.6 Site visits & site documentation

**6.1 Pre-visit accessibility audit.** Before any site visit, one student team produces an access audit: tactile pavement, audible signals, surface changes, gradients above 1:20, obstacles. Delivered as audio + state.json zone overlay. Determines the visit route.

**6.2 Ambient sound recording protocol.** Every student carries a small recorder (Zoom H1 or phone with windscreen). At each stop, 60 seconds of ambient sound. Files named `<site>-<stop>-<HHMM>.wav` go into the project archive.

**6.3 Tactile site model from contour data.** Within a week of the site visit, the team produces a tactile site model: a low-relief 3D print from contours (Bambu) or a stacked-foam tactile section. The model lives on the studio table for the rest of the semester.

**6.4 Voice-narrated site walk.** During the visit, one student narrates a 10-15 minute walk continuously into a recorder. "I'm now at the south corner. The pavement transitions from concrete to brick. There's a slope rising about three degrees." This recording becomes canonical site documentation.

**6.5 Texture and material samples.** Students collect physical samples (with permission) into labeled bags. Each is photographed, described in 30 words, entered into a shared material library.

**6.6 Site state.json template.** A `template load site-<name>` produces a state.json with the site boundary, contours, neighboring buildings, an empty zone block. Every student starts from this template.

## 5.7 Drawing alternatives

**7.1 state.json as the drawing of record.** The syllabus states explicitly: the canonical representation of the project is `state.json`. PIAF, 3D prints, audio, and Rhino exports are all derived. If they disagree, state.json wins.

**7.2 Audio walkthrough script template.** Students write audio walkthroughs against a fixed structure: (1) approach, (2) entry, (3) primary spaces in circulation order, (4) materials and light, (5) one moment of architectural interest. 3-5 minutes total.

**7.3 Sound-mapped plans.** For a major space, students produce a sound map: imagined or measured acoustic character at five points, recorded as 30-second clips, each tagged to a state.json point ID. Played back in sequence, it's a sonic plan.

**7.4 Tactile sections with material legend.** Sections produced as PIAF prints with hatched material zones (`cmd_hatch`) and a Braille legend printed separately. The hand reads section + legend simultaneously.

**7.5 Time-based audio elevations.** For an elevation, students produce a 90-second audio "scan" — left to right, narrating heights, openings, materials, rhythms. Paired with a PIAF print of the same elevation.

**7.6 The describe-it-from-memory exercise.** Once per phase, students produce a fresh audio walkthrough of their own project from memory, no notes, recorded in one take. Reveals what's actually designed vs. what's been "drawn."

## 5.8 Voice-first design loops

**8.1 The dictation-to-macro loop.** Students dictate TASC commands into Claude Code headless, debug them aloud, then save a working sequence as a macro. By week 6 every student has 5-10 personal macros.

**8.2 Conversational design sessions.** Office hours conducted as conversational design: student speaks intent, Claude Code edits state.json, faculty listens to `cmd_tts` readout, suggests next move. No screen consulted.

**8.3 Voice macros for common moves.** Pre-built voice-triggerable macros: "add a 3x3 bay rotated 30 degrees," "enclose this bay with a door on the south," "add a double-loaded corridor." Two already exist (`enclose-bay-with-door.json`, `add-double-loaded-corridor.json`). Each student contributes at least two.

**8.4 The two-minute speech sketch.** Studio warm-up: in two minutes, students dictate a complete schematic ("site forty by sixty, zone classroom thirty by twenty at ten ten, bay structural three by three at zero zero...") into TASC and produce a PIAF print.

**8.5 Talk-aloud debugging.** When a command fails (ERROR: line), students must talk through the error aloud before retrying. Faculty enforce this — silent typing-and-retry is not allowed.

**8.6 The "no mouse" pledge.** Students sign a week-by-week pledge to use no mouse during studio hours. Faculty model it. After three weeks most students don't notice the mouse is gone.

## 5.9 Mixed-ability pairing

**9.1 Role cards on the table.** Every pair session begins with two physical cards drawn from a deck: DRIVER and NARRATOR (or PRINTER and READER, or PROGRAMMER and CRITIC). Cards rotate every 25 minutes via timer.

**9.2 The "describe before doing" rule.** When the driver is about to issue a command, they say it aloud first, the narrator confirms, then it gets typed. This works for both blind and sighted drivers and equalizes tempo.

**9.3 Blind-student-as-teacher rotations.** Once per phase, a blind student leads a 20-minute tutorial for the cohort on a tool or technique. Faculty schedule this from the start.

**9.4 The "five-minute audit" intervention.** When faculty sense a sighted student dominating, they intervene with a five-minute audit: pair pauses, faculty asks the non-driver to describe the current state of the project from memory. If they can't, the pair has been working visually-only. Recalibrate.

**9.5 Tactile-only review checkpoints.** Twice per phase, pairs must produce a tactile output and review each other's work using only the tactile + audio. No screen. Reveals which pairs have built genuine shared understanding vs. one student "showing" the other.

**9.6 Etiquette short list.** Posted on the studio wall (also in Braille, also in the audio orientation): (1) Use IDs and names, never deictics. (2) Don't grab the keyboard. (3) Don't read the screen out of turn. (4) If you point, you've failed. (5) State your action before doing it.

**9.7 Sighted-only check.** Twice a semester, the sighted students do a session blindfolded. Not as empathy theater — as a fluency test. If they can't operate the toolkit blind, they've been free-riding on sight.

## 5.10 Critique culture

**10.1 The "restate" intervention.** Any deictic gets a "restate." Apply consistently from day one to faculty, jurors, and students alike. Within three weeks it's automatic.

**10.2 Feedback in numbered points.** "One: the entry sequence reads clearly in tactile. Two: the section is missing material differentiation. Three: the audio walkthrough skips the courtyard." Easy to capture, easy to act on.

**10.3 The "what I learned" closing.** Every crit ends with the student giving one sentence on what they learned, recorded into the crit audio. Forces synthesis; gives the archive a usable index.

**10.4 Crit audio review homework.** Between crits, students are assigned to re-listen to two peers' crits (not their own). Reduces the "performance" feel of crit because the audience extends in time.

**10.5 No screens in jury room.** Final jury room: no projector, no laptops on the table. PIAF prints, 3D prints, Braille legends, Bluetooth speakers. Faculty enforce — visiting critics who pull out a laptop are gently asked to close it.

**10.6 Verbal-only feedback discipline drill.** Once per week, faculty give a 10-minute crit on a published precedent (not student work) using only verbal description. Students hear what good tactile-compatible critique sounds like, modeled.

## 5.11 Reading & precedent

**11.1 Precedent library as PIAF binder.** Studio maintains a binder of 50 canonical plans pre-converted via `tact convert` with consistent presets. Each plan has a Braille legend and a 2-minute audio description. Students check out the binder like a library book.

**11.2 Audio descriptions of canonical buildings.** Studio commissions or curates 20-30 high-quality audio descriptions of canonical buildings (Mies Barcelona, Kahn Salk, Aalto Saynatsalo, etc.) at 5-8 minutes each. Students listen during commutes; cited in crit.

**11.3 Plain-text reading list.** Reading list is plain-text or EPUB only — no scanned PDFs, no image-heavy textbooks. Where a key text only exists as scanned PDF, the studio pays to have it OCR'd properly.

**11.4 Precedent reproduction exercise.** Each student reproduces one canonical plan as a `state.json` via TASC/controller, then `tact render`s it back to PIAF and compares to the original PIAF in the binder. Reveals what the semantic schema captures and what it omits.

**11.5 Weekly precedent-recall warm-up.** Each Monday opens with: "From memory, describe the entry sequence of [precedent]." Five students give 30-second answers, faculty don't comment.

## 5.12 Documentation & archive

**12.1 Git-as-archive.** Every student project is a git repo. `state.json` commits are the canonical archive. Tactile masters (PDFs ready for PIAF), audio files, and crit recordings sit alongside in the repo.

**12.2 Snapshot at every milestone.** `cmd_snapshot` invoked at every milestone deliverable, producing a tagged, immutable state.json copy.

**12.3 Transcript every crit.** Audio crits transcribed (Whisper or similar) within 48 hours. Transcripts live next to the audio in the project repo.

**12.4 Tactile master library.** Every PIAF master that prints cleanly goes into a shared tactile master library — `tact convert` outputs with the parameters and source state.json archived together.

**12.5 The reproducibility test.** Periodically, faculty pull an old `state.json` from a past student and run the watcher + `tact render` + `cmd_tactile3d`. Output must match the archived tactile masters. If not, schema drift has happened — fix it.

**12.6 Audio walkthrough as project trailer.** Each project archives one definitive 3-minute audio walkthrough. This is the "thumbnail" the archive presents — not a hero render.

## 5.13 Final review & jury

**13.1 Jury accessibility briefing, mandatory.** Forty-five minutes the morning of, with coffee. Cover: "no deixis," tactile reading basics, how to use `cmd_tts`, how to load a state.json.

**13.2 Pre-jury audio packet.** One week before review, jurors receive an audio packet: each student's 3-minute walkthrough, plus the brief, plus the studio's vocabulary primer.

**13.3 Tactile handouts per juror.** Each juror gets a personal binder of all students' final PIAF prints + Braille legends. Theirs to mark up.

**13.4 Fixed jury format, 25 minutes per student.** Five-minute student walkthrough, fifteen-minute jury discussion, five-minute student response. No slides. Audible timer.

**13.5 Audio recording with transcription within 24 hours.** All jury feedback recorded and transcribed, delivered with the grade.

**13.6 Tactile-first jury composition.** When inviting external jurors, prioritize critics who have worked in tactile, audio, or accessibility-first practice — disability scholars, blind designers, accessibility consultants — alongside conventional architects.

## 5.14 Faculty workflow

**14.1 John and Daniel split by phase, not by student.** Avoid the "your students / my students" pattern. John leads concept and schematic; Daniel leads DD and final; both attend every crit.

**14.2 Daily 15-minute faculty sync.** End of every studio day, John and Daniel record a 15-minute audio note: what went well, what failed, which student needs intervention. Stored in a shared repo.

**14.3 Office hours as voice sessions.** Twenty-five-minute slots, conducted as conversational design sessions in Claude Code headless. Student speaks, faculty listens to state output, suggests. Recorded by default (with consent).

**14.4 Feedback in shared format.** All faculty written feedback into a per-student markdown file in their project repo, plain text, numbered points. No PDF feedback, no inline Word comments.

**14.5 Faculty toolkit fluency requirement.** Both faculty must, by week 3, demonstrate independent fluency in: `tact convert`, `tasc bay`, `template load`, headless Claude Code, NVDA + Console Toolkit. If a faculty member can't operate the toolkit blind, they can't teach it.

**14.6 The "stuck student" intervention protocol.** When a student misses two consecutive milestones or shows toolkit avoidance, John or Daniel runs a 60-minute paired session in headless mode, no screen looked at, working on the student's own state.json.

## 5.15 Failure modes & how to prevent them

**15.1 "Look at my screen" reflex.** Prevention: monitors face away from the table or off during crit; "no deixis"; tactile-only review checkpoints; faculty model with monitors off.

**15.2 The "accessibility version" trap.** Blind students get assigned the simpler/tactile version while sighted students do the "real" work. Prevention: tactile artifact is the deliverable for everyone; renderings banned; final jury is tactile-only.

**15.3 Tactile-as-deliverable not tactile-as-medium.** Prevention: tactile output required at every weekly milestone, not just finals; pegboards on every table; concept phase requires tactile before screen.

**15.4 Toolkit avoidance via "design first, tool later."** Prevention: week 5 onward, no design move counts unless it's in state.json by end of session.

**15.5 Faculty deixis leakage.** Prevention: faculty pay a token (literal — a jar on the table, $1 per slip) for every deictic during crit.

**15.6 The "voice input is too hard" retreat.** Prevention: ten-minute daily drills; pair work where one student dictates and the other types as ASR substitute; ASR errors don't penalize.

**15.7 Schema drift in state.json.** Prevention: `controller/auditor.py` runs as a pre-commit hook; CI on the studio's git server validates every push; schema version is checked at load.

**15.8 Jury reverts to visual.** Prevention: jury briefing the morning of; tactile binder at every seat; faculty intervene the first time a juror reaches for a laptop.

**15.9 The "I'm visual" identity claim.** Prevention: studio framing from day one is that this is a craft, not an identity; the toolkit accommodates visual thinkers (Rhino Viewer exists); but tactile fluency is a baseline professional skill, not optional.

**15.10 Tools as fixed, not extended.** Prevention: macro hour every Friday; the strongest students contribute back to the toolkit.

---

# 6. Tactile + AI capabilities + hardware

A landscape of AI capabilities and accessibility hardware that could feed into tactile-first architectural workflows. Specific with product/model names. Notes which items already exist in the repo (EasyOCR, liblouis, Claude vision via MCP, Rhino MCP socket bridge) so we don't duplicate them.

## 6.1 Image-to-tactile

- **Claude Sonnet / Opus Vision (Anthropic API).** Best-in-class for architectural drawing reasoning. Already wired into TACT via `extract_text_with_vision` and `describe_image`. Extension: `tact analyze --semantic` returning a structured zone graph for `tact render`. Demo: drop a trace-paper sketch into a watch folder; get a state.json with named zones in 30 seconds.
- **GPT-4o Vision.** Competitive on plan reading; weaker on hand-drawn linework, stronger on photographed scenes. Plug-in: `tact compare-vision` MCP function that runs the same prompt through both models and surfaces disagreements as questions.
- **Gemini 2.5 Pro.** 1M-2M token context — feed entire drawing sets at once. Plug-in: new `tools/multisheet/` ingesting a PDF set and building a sheet-cross-reference index.
- **LLaMA-3.2-Vision 11B (local via Ollama).** Quality below Claude but workable for offline studios. Plug-in: TACT fallback when no network.
- **Florence-2 (Microsoft, 230M / 770M).** Dense region captioning + OCR, sub-second on CPU. Plug-in: first-pass region proposal inside TACT before sending crops to Claude.
- **MiDaS v3.1 / Depth Anything V2.** Monocular depth. Plug-in: `tools/depth/` takes a perspective rendering and emits a heightfield STL. Demo: convert a 19th-century courtyard engraving into a printable bas-relief.
- **Marigold (ETH Zurich).** Diffusion-based depth, sharper edges than MiDaS on architectural drawings. Slower (~10s/image). Demo: turn a Piranesi etching into a tactile interpretation with crisp wall edges.
- **Segment Anything 2 (SAM 2).** Promptable segmentation. Plug-in: new `tact layer` command producing N PIAF sheets (walls only, furniture only, circulation only) for layered tactile reading. Demo: 4-layer tactile booklet of a Mies pavilion.
- **MaskFormer / Mask2Former.** Panoptic segmentation pretrained on ADE20K. Plug-in: TACT preset selector that picks `wall_emphasis` vs `circulation_emphasis` automatically.
- **LSD / ED-Lines (classical) and DeepLSD / LETR (learned).** Line extraction. Plug-in: pre-process scanned hand-drawings before TACT's line extractor. Demo: convert a photo of a whiteboard charrette into a tactile artifact same-day.

## 6.2 Tactile-to-digital

- **OpenCV + ArUco markers.** Free; print 4 fiducials at pegboard corners and a webcam reads coordinates in ms. Plug-in: new `tools/pegboard-cv/`. Demo: student moves pegs on a 24"×36" board, snaps an iPhone photo, controller updates Rhino in 3 seconds.
- **AprilTag (April Robotics Lab, U-Michigan).** Robotics-grade; more robust at angles than ArUco.
- **EasyOCR / PaddleOCR / Tesseract / GPT-4o-Claude vision OCR.** EasyOCR already in TACT. PaddleOCR outperforms on rotated and small text. Vision LLMs beat dedicated OCRs on handwriting.
- **RealityCapture (Epic, free non-commercial).** Photogrammetry — 30-100 photos → textured mesh. Plug-in: `tools/scan/` skill importing a captured mesh and registering to the controller's coordinate system. Demo: print a study model, photograph it after a crit's worth of pencil edits, re-import as a new design state.
- **Meshroom (AliceVision).** Cross-platform open-source photogrammetry. Slower than RealityCapture, no license. Better for a student lab.
- **Polycam ($80/yr) / Scaniverse (free) / 3D Scanner App.** iPhone Pro LiDAR. Exports OBJ/PLY/USDZ. Plug-in: `tact import polycam`. Demo: walk a site with iPhone 15 Pro, return with a textured site mesh, slice to PIAF contours.
- **NeRF / 3D Gaussian Splatting (Nerfstudio, gsplat); Luma AI; KIRI Engine.** Photo-real novel views. Heavier compute; mostly visual. Cite as adjacent.

## 6.3 Voice-driven design

- **Whisper (OpenAI, local).** Tiny → Large-v3. Medium runs realtime on CPU. Plug-in: new `tools/voice/`. Demo: "site twenty by thirty, bay alpha three by three at five, five" produces a Rhino layout hands-free.
- **Whisper.cpp / faster-whisper.** Large-v3 at 1× realtime on M2 Mac CPU. Demo: same on a $600 laptop.
- **OpenAI Realtime API (gpt-4o-realtime-preview).** Speech-in/speech-out with sub-second latency, function calling. ~$0.06/min input + $0.24/min output. Plug-in: full-duplex MCP function wrapping TASC and TACT commands. Demo: 10-minute voice charrette where Claude narrates the design back as it changes.
- **Deepgram Nova-3.** Streaming ASR with sub-300ms latency, $0.0043/min. Demo: live transcription of a studio review piped into the work-session vault note.
- **AssemblyAI Universal-2.** Strong on speaker diarization — useful for crits with multiple voices.
- **Picovoice Porcupine (wake word).** Tiny, Raspberry Pi-class. Custom wake word "hey jig." Demo: ambient "hey jig, rotate bay A thirty degrees" in the studio.
- **Vosk.** Smaller than Whisper, no GPU; CPU-only on a Pi Zero. Demo: a $40 voice puck that controls the controller from across the room.

## 6.4 Audio rendering of geometry

- **pyo (Olivier Belanger).** Python audio synthesis. Plug-in: `tools/sonify/` mapping zones to pitch/pan/duration. Demo: walk a plan north-to-south as a 15-second melody — bay rotations modulate timbre.
- **SuperCollider / Sonic Pi.** Heavier-duty live sonification platforms.
- **Tone.js (web).** Plug-in: a panel in the WebUI that plays the current state.
- **Web Audio API spatial audio (PannerNode + HRTF).** Plug-in: WebUI audio diagram panel — each room is a sound source at its XY. Demo: cursor-on-canvas audio diagram where you "hear where things are."
- **Resonance Audio (Google).** Ambisonic spatial audio with room modeling. Plug-in: render the Rhino model as a spatial soundscape for headphone-based pre-visit.
- **Apple Spatial Audio / AirPods head-tracking.** Plug-in: an iPad companion app that pans audio with head orientation.
- **ElevenLabs / OpenAI TTS / Coqui XTTS-v2 / Piper.** Piper is the local winner (sub-100ms on a Pi). Plug-in: every CLI `OK:` line could optionally route through Piper for studio environments where a screen reader isn't present.
- **Earcons.** Plug-in: every `OK:` command line plays a 100ms earcon. Demo: silent screen-reader-friendly studio session with rich non-speech feedback.

## 6.5 Haptic feedback devices

- **Orbit Reader 20/40.** 20- or 40-cell refreshable Braille. ~$700 / $2,500. USB + Bluetooth.
- **Focus 14/40/80 Blue (Freedom Scientific).** Premium displays, $1,500-$5,000.
- **Hable One.** $300 portable Braille keyboard/display hybrid. Plug-in: site-visit field controller — typed Braille input drives state.json edits.
- **APH Monarch (2024).** Multi-line refreshable tactile display — 10 rows × 32 cells, the first true tactile graphics + Braille hybrid. ~$15,000. Plug-in: render TACT outputs in real-time to the Monarch instead of paper. Demo: live-editable tactile floor plan during a charrette. **Highest aspiration of this list.**
- **Dot Pad.** 300-pin tactile graphics + 20-cell Braille line. ~$10,000. Bluetooth, Mac/iOS-native via Dot's SDK.
- **Graphiti (Orbit Research).** 60×40 pin array, dynamic tactile graphics, ~$15,000.
- **TI DRV2605L haptic driver IC + LRA actuators.** $2-3 per actuator, $8 driver. I2C from any microcontroller. Plug-in: a homemade haptic puck for the pegboard — buzzes when a peg violates a setback.
- **bHaptics TactSuit / Tactosy.** Consumer haptic vests, $300-$500. Spatial haptics for VR site walkthroughs.
- **3D Systems Touch / Touch X.** 6-DOF force-feedback stylus. $700-$3,000. Niche but real haptic CAD. Plug-in: a new `tools/haptic-sculpt/` deforms geometry by stylus input.

## 6.6 Tactile output hardware

- **PIAF (Pictures in a Flash).** ~$1,500. Already the TACT output target.
- **Tactile Image Maker (American Thermoform).** Competitor, similar.
- **Zychem ZyFuse Heater.** ~$700. Budget tier.
- **ViewPlus Tiger (Premier/Elite/Max).** $5,000-$15,000. Combo Braille + tactile graphics embosser — prints actual dot-pattern graphics, not swell. Windows-only driver. Plug-in: new TACT backend `--target tiger`. Demo: 11×17 tactile floor plans with embedded Braille labels in one pass.
- **Index Everest-D V5 / Braille Box.** $5,000-$8,000. Production Braille embosser, double-sided. Demo: produce a class set of 20 Braille legend booklets in 10 minutes.
- **Index Romeo 60.** Single-sided Braille embosser, ~$4,000.
- **Prusa MK4 / MK4S.** $800-$1,100. Reliable FDM for tactile site models at 1:200. Plug-in: `tact export stl` converts heightfield zones into a printable model.
- **Bambu Lab X1 Carbon / P1S.** $700-$1,500. AMS multi-color tactile differentiation. Plug-in: "use AMS slot N for layer M" preset. Demo: 4-color campus model where each color is a different program zone.
- **Formlabs Form 4.** $3,500. SLA resin for fine detail (legible micro-Braille at 1:50).
- **Glowforge / xTool / Epilog laser cutters.** $1,500-$8,000. Plug-in: `tact export svg-layered` produces stack-cut layer files from elevation bands. Demo: 12-layer topographic site model from cardboard.
- **Roland EGX / Vision Engraver / Carvey CNC.** $2,000-$8,000. Engraves Braille and tactile lines into rigid media. Demo: ADA-compliant Braille room signs from a building's state.json.
- **AxiDraw V3 / SE/A3 (Evil Mad Scientist).** $600-$1,000. Pen plotter for drawing on swell paper before heat-swelling.
- **HP DesignJet large-format printer.** $1,500-$4,000. For oversized tactile masters.

## 6.7 Pegboard / physical input

- **Camera + ArUco/AprilTag pegs.** $0 marginal cost over the existing pegboard. Each peg top gets a printed sticker; a webcam reads positions. Plug-in: same `tools/pegboard-cv/` as §6.2.
- **Capacitive pegboard (Bare Conductive Touch Board $80; Adafruit MPR121 $7).** 12 capacitive channels per MPR121, daisy-chainable. Drill holes, run conductive paint to each. Plug-in: serial bridge into the controller — pegs trigger commands by capacitance.
- **Resistive grid (homebrew matrix).** Voltage divider per row/column. Arduino Mega scans. ~$50 educational kit.
- **RFID/NFC tokens (PN532 reader $15; NTAG215 stickers $0.20).** Each peg gets a unique NFC tag. Plug-in: `controller` accepts `peg place <tag-id> at <slot>`. Demo: named-token system where pegs encode building types ("library," "atrium").
- **Conductive 3D-printed pegs (Proto-Pasta Conductive PLA).** Peg geometry encodes identity by contact pattern with a grid. Demo: pegs auto-identify their type to the controller.
- **Tangible Engine / reacTIVision.** Open-source CV libraries specifically for tangible-UI tables. Alternative CV stack.
- **LEGO MINDSTORMS / SPIKE Prime tilt and color sensors.** $400 kit, well-supported by students. A 4×4 educational layout jig built in a workshop afternoon.

## 6.8 Local AI models

- **Whisper sizes.** Tiny (1GB RAM, real-time on Pi, ~10% WER), Base (~7%), Small (~5%), Medium (~3.5%), Large-v3 (~2.7%, needs 10GB VRAM for realtime). Recommended default: Medium via faster-whisper.
- **LLaMA-3.2-Vision 11B.** ~24GB VRAM at 4-bit. Quality below Claude on architectural drawings but usable. Plug-in: TACT offline fallback.
- **LLaMA-3.2-Vision 90B.** ~80GB at 4-bit — A6000 or two 4090s.
- **Qwen2-VL (Alibaba, 2B/7B/72B).** Often beats LLaVA on benchmarks, especially OCR. Plug-in: TACT offline mode with better OCR than EasyOCR fallback. Demo: a $0-marginal-cost EasyOCR + Qwen2-VL stack on a Mac mini.
- **InternVL2 (Shanghai AI Lab).** Strong open-source vision model, 1B-76B sizes.
- **Depth Anything V2.** Small (25M) runs on CPU; Large (335M) needs GPU.
- **Ollama (runtime).** Free, cross-platform, model registry with one-line pulls. Plug-in: TACT and `tools/voice/` call Ollama's OpenAI-compatible API. **Demo: a single `ollama` install behind a `--local` flag everywhere.**
- **LM Studio (runtime).** GUI-driven; OpenAI-compatible endpoint. (Screen-reader-hostile by default; prefer Ollama.)
- **llama.cpp / MLX (Apple Silicon).** Performance-tuned backends. MLX-LM is Apple-native for M-series.

## 6.9 Cloud AI services (orthogonal Claude capabilities)

- **Vision** — TACT uses this.
- **Tool use / function calling** — MCP servers leverage it.
- **Batch API** — 50% cost savings, 24h turnaround. Plug-in: `tact convert --batch *.png` for course-sized jobs. Demo: convert a whole semester's drawings overnight at half cost.
- **Prompt caching** — cache the architectural-vocabulary system prompt for cheap multi-image runs. **Confirm caching is on for your CLAUDE.md** (it's large and stable; material cost savings at studio scale).
- **Citations** — Claude returns source spans for documents. Plug-in: when describing a building from a PDF report, cite the source page.
- **Files API** — upload large drawing sets once, reference by ID.
- **Computer use** — drive Rhino's GUI for the rare commands TASC can't reach.
- **Code execution** — run TACT inside the API for browser-only users.

## 6.10 Bridges to CAD/BIM/GIS

Already in repo: TASC's MCP socket → Rhino. Don't duplicate.

- **grasshopper-mcp / rhino-mcp / blender-mcp (community).** Plug-in: TACT could trigger a Grasshopper definition that produces an STL.
- **AutoCAD (LISP / .NET / ObjectARX).** Plug-in: `tools/autocad-bridge/` imports DWG entities into state.json schema.
- **LibreDWG / ODA File Converter.** Free DWG readers. Dependency-free DWG ingest for the controller.
- **Revit Dynamo + Revit API.** Plug-in: a Dynamo node exporting a room schedule into state.json.
- **revit-mcp (community, exists).** Bidirectional MCP bridge.
- **Speckle.** Open-source platform streaming geometry between Rhino, Revit, Grasshopper, Blender. Free tier. Plug-in: subscribe to a Speckle stream, regenerate tactile output on every commit.
- **IfcOpenShell.** Plug-in: `tools/ifc/` maps IFC spaces to controller zones.
- **QGIS + PyQGIS.** Plug-in: import shapefiles as the "site" layer of a state.json.
- **GDAL / OGR.** Plug-in: `controller import shp`.
- **Mapbox / Maptiler / OSMnx.** Plug-in: `tools/site-context/` pulls neighborhood footprints. Demo: tactile of a 4-block walking radius around a site.
- **Cesium / CesiumJS.** Photo-real terrain alongside tactile.

## 6.11 Sensors and IoT for site studios

- **PurpleAir PA-II.** $230 outdoor air quality. JSON API. Plug-in: `tools/site-sensors/` ingests live PM2.5 into state.json metadata, optionally renders as tactile overlay. Demo: tactile of a site with bumpiness encoding air-quality readings over time.
- **Adafruit / SparkFun environmental sensors (BME280 ~$10, SCD30 CO2 ~$60, VEML7700 lux $5).** I2C, any microcontroller. Plug-in: a Raspberry Pi puck on each studio desk logs CO2/temp into the work-session vault note.
- **Davis Vantage Pro2 weather station.** $600.
- **Decagon / Meter Group soil moisture sensors.** $200-$500. Demo: tactile of a community garden with soil moisture as raised dot density.
- **Ambient sound: Knowles MEMS mics + ESP32.** $30 build. Records dBA into time-series. Demo: tactile soundscape map of a busy street.
- **BLE switch interface (AbleNet Hook / Tecla-e).** $200-$300. Routes accessible switches into BLE keyboard events. Plug-in: bind switches to controller commands.
- **Tobii Eye Tracker 5.** $250. Windows. Plug-in: gaze-driven plan navigation.
- **Logitech accessibility line / Microsoft Adaptive Controller / Xbox Adaptive Controller.** $80-$100. USB HID. Plug-in: bind arbitrary buttons to controller commands.
- **Quha Zono 2 / Jouse3.** Plug-in: bind as keyboard input to TASC. Demo: full design workflow without keyboard or trackpad.
- **Stream Deck (Elgato).** $150. 15 customizable hardware buttons with icon LCDs. Plug-in: a profile mapping to the most common controller commands.

## 6.12 Multi-agent / orchestration

- **Claude Code subagents.** Already in use. Plug-in: spawn a subagent per long-running TACT batch.
- **Anthropic-built MCP servers (filesystem, GitHub, Slack, Postgres, fetch, memory, sequential-thinking).** All free.
- **Browser MCP (puppeteer-mcp, playwright-mcp).** Plug-in: scrape building-code references, archive design precedents. Demo: pull every ADA section relevant to a designed building into a tactile reference booklet.
- **Memory MCP / mem0.** Persistent cross-session memory. Demo: "remember that this student is working on tactile signage" persists across weeks.
- **Sequential-thinking MCP.** Forces explicit chain-of-thought scratchpads. Plug-in: tactile-PDF QA where the model writes its checklist before scoring.
- **n8n / Zapier / Make (low-code).** Plug-in: notify Slack when a new state.json lands, kick off a TACT render. Demo: studio submission portal that auto-produces a tactile PDF and emails it to the instructor.

## 6.13 Top-leverage adds vs. moonshots

- **Highest return per dollar:** camera-based pegboard CV (effectively free), Whisper voice front-end (free), iPhone Pro LiDAR scan import (most students have one), local Ollama fallback (free), Stream Deck command surface ($150).
- **Most aspirational:** APH Monarch and Dot Pad — together they'd let the toolkit do what nothing else in the world does, live tactile editing during a design crit.
- **The biggest unknown:** refreshable tactile graphics device API maturity. Monarch and Dot Pad SDKs are young; building TACT output targets for them is a real engineering investment, not a weekend port.

---

# 7. AI tools beyond Claude

Opinionated stances on the ecosystem outside Claude. You're not switching off Claude — this is what's worth knowing about and possibly integrating.

## 7.1 AI for architecture specifically

- **Midjourney.** Know it exists, skip for studio. Aesthetic vibes only; can't ControlNet, can't pin a plan. The "AI render" cul-de-sac that has captured too many architecture students.
- **Stable Diffusion + ControlNet.** Use it via a frontend. The actual pedagogical win in architecture-AI: feed a hand sketch or a plan, get conditioned renders that respect your geometry. Integration idea: a `tact describe` companion command that takes a generated render and produces a tactile-friendly text description for blind crit partners.
- **Krea.** Use it. Real-time canvas wrapping SD/Flux — the "draw and AI fills in" loop is the most pedagogically honest use of image AI for architecture. Winner over Midjourney for studio.
- **Flux.** Use it. Currently the best open image model for architectural drawings and typography (Midjourney still can't read its own text). Replace SD with Flux for plan/section conditioning.
- **Veo / Sora / Runway.** Watch, don't adopt. Video AI is a year or two away from being useful in architecture pedagogy beyond novelty.
- **Hypar.** Know it exists. Real engineering substance, but audience is BIM-heavy firms.
- **TestFit.** Skip. Developer-pro-forma software dressed as design AI.
- **Spacemaker / Autodesk Forma.** Use it for Superfund site research. Sun/wind/noise simulations on real site polygons are exactly the kind of analysis Superfund sites demand. Integration idea: export Forma's analysis grids and convert them to tactile pressure maps via TACT — a sun exposure heatmap becomes a tactile gradient.
- **Finch3D.** Know it exists. Redundant with the Layout Jig's intent.
- **Maket / ArkDesign.ai.** Skip. Pedagogically thin.
- **Veras (EvolveLAB) / Lookx / Stylar.** Know Veras, skip the others. Veras integrates into Rhino and renders the actual model rather than hallucinating. Doesn't help blind students.
- **Tripo / Meshy / CSM / Luma Genie / Rodin.** Watch. None yet produce architecturally meaningful geometry. Worth piloting: image-to-mesh for furniture/sculpture/landscape elements that could then be 3D-printed as tactile site objects.

## 7.2 Local AI runtimes

- **Ollama.** Use it. The default. `ollama run llama3.2-vision` and a vision model in 60 seconds. Offline fallback when network is down in a tactile fabrication lab; privacy-safe for FERPA-protected work.
- **LM Studio.** Skip. GUI-first = screen-reader-hostile.
- **llama.cpp.** Know it exists. Ollama wraps it.
- **MLX (Apple Silicon).** Use it if you have a Mac with 32GB+. Faster than Ollama on Apple Silicon.
- **Practical hardware guide:**
  - 8GB RAM: 3B–4B parameter models. Autocomplete-tier.
  - 16GB RAM: 7B–8B models. Sweet spot.
  - 32GB unified memory (M-series): 27B–32B (Gemma 2 27B, Qwen 2.5 32B). Approaching GPT-4-mini quality.
  - 64GB+ or 24GB VRAM GPU: 70B quantized. Real Haiku-tier.
  - For studio lab: **a single Mac Studio with 64–128GB unified memory is the best single-machine investment.** One machine, many students, real models.

## 7.3 Vision / OCR / multimodal

- **GPT-4V / Gemini Vision.** Know exists, skip integration except: Gemini's 1M+ token context handles entire architectural drawing sets in one shot. Worth a Google API key for "describe this 80-page DD set."
- **Florence-2 (Microsoft).** Use it. 0.23B–0.77B, runs locally, does detection/segmentation/captioning/OCR all in one.
- **Moondream.** Use it for embedded contexts. 2B-parameter, fast, runs on a Raspberry Pi class device. Integration idea: a tactile-printer companion that describes what was just printed, narrated through Piper TTS — fully offline image-to-tactile-with-narration loop.
- **LLaVA.** Skip. Superseded.
- **Qwen-VL (Qwen 2.5 VL).** Use it. Currently the best open vision model for documents and charts. Winner over LLaVA for architectural drawings.
- **EasyOCR.** Keep it (already in repo).
- **PaddleOCR.** Know it exists. Heavier dependencies; switch only if EasyOCR fails on a specific document type.
- **Tesseract.** Skip for new work.
- **Surya.** Watch. Transformer-based OCR with layout detection; could replace EasyOCR for plan-to-state.json workflow.
- **SAM 2.** Use it. Single most useful vision tool for architecture pedagogy. Click-to-segment lets a student isolate every column, every room, every site feature. Integration idea: `tact segment` takes a Superfund site aerial, runs SAM 2, produces a labeled tactile map where each remediation zone is a distinct tactile texture.

**Winners:** Florence-2 or Qwen-VL for local image description; Claude for cloud (Gemini for huge documents); EasyOCR stays; SAM 2 no contest for segmentation.

## 7.4 Speech / audio / TTS

- **Whisper (OpenAI).** Use it. Best open STT. Cloud API for accuracy, `whisper.cpp` for local.
- **whisper.cpp.** Use it. Integration idea: tactile model walkthrough recorder. Student narrates while touching a 3D-printed site model; whisper.cpp transcribes; Claude annotates the transcript with timestamps tied to which part of the model was being described.
- **ElevenLabs.** Skip for daily use, use for production audio. Pricey but unmatched. For finished deliverables only.
- **OpenAI TTS.** Use for prototyping. Cheap, decent.
- **Cartesia (Sonic).** Use it for interactive contexts. Lowest-latency available, ~75ms. Winner for real-time voice loops.
- **Deepgram / AssemblyAI.** Know exists; Whisper is good enough.
- **Coqui.** Skip. Maintenance limbo.
- **Piper (Rhasspy).** Use it. Sub-100ms on a Pi. The winner for screen-reader-adjacent local TTS. Integration: every CLI `OK:` line could optionally route through Piper.
- **Festival.** Skip.
- **Bark.** Skip. Cute but unreliable.
- **System TTS (NVDA voices, macOS, Windows SAPI).** **This is the actual answer for screen reader users.** Don't replace what NVDA/JAWS already do. Reserve Piper/ElevenLabs for cases without a screen reader in the loop.

**Winners:** Piper for local, Cartesia for interactive cloud, system TTS for screen-reader contexts.

## 7.5 Web search & knowledge

- **Perplexity.** Use the consumer product, skip the API. Best way to teach "AI that shows its work."
- **Exa.ai.** Use it. Semantic web search API for AI agents — returns full document content. Winner for any agent-search context.
- **You.com.** Skip.
- **Tavily.** Use it for student work. Cheap pricing, generous free tier. Default for any classroom-built agent.
- **SerpAPI.** Know it exists. Use when you specifically need real Google rankings.
- **Brave Search API.** Use as a Google alternative.
- **Anthropic web_search (Claude built-in).** Use it. Path of least resistance.

**Winners:** Claude's built-in for Claude-native work, Exa for agentic search, Tavily for cheap.

## 7.6 Agent frameworks beyond Claude

If you are deeply on Claude Code, you do not need an agent framework. Everything below is for teaching literacy, not adoption.

- **LangGraph.** Know it exists. Most production-credible Python framework. Worth one lecture.
- **CrewAI.** Skip. Mostly marketing-grade demos.
- **AutoGen.** Know it exists. More serious than CrewAI, still not a fit.
- **MetaGPT.** Skip.
- **OpenAI Assistants API.** Skip. OpenAI is migrating away.
- **Swarm.** Know it exists. Teaching reference for "agents handing off to other agents."
- **Pydantic AI.** Use it if you write Python agents outside Claude Code. Type-safe, model-agnostic. The only framework here I'd actually recommend touching. Integration idea: a non-Claude agent for offline tactile work, Pydantic AI is the right shape.

**Winner:** Don't switch. Use Claude Code. Teach LangGraph and Pydantic AI for literacy.

## 7.7 MCP server ecosystem

- **Official MCP servers** (`filesystem`, `github`, `postgres`, `puppeteer`, `memory`, `sequential-thinking`, `time`, `fetch`). Use what you need. Add `filesystem` if not already.
- **Playwright MCP.** Use it. Winner over Puppeteer MCP for web scraping or web testing.
- **Slack MCP.** Skip unless the studio runs on Slack.
- **Figma MCP.** Know it exists.
- **Notion MCP.** Skip. Your knowledge base is the Obsidian vault.
- **Linear MCP.** Skip. GitHub Issues works.
- **MCP registry (registry.modelcontextprotocol.io).** Watch. Worth checking quarterly for new architecture/GIS MCPs.
- **mcp-cli.** Use for debugging.
- **MCP Inspector.** Use it when writing your own MCP servers (as you do).
- **A QGIS MCP server doesn't exist yet but would be massively valuable.** Wrap PyQGIS so Claude can query "what's the parcel boundary at this lat/lon" directly. Possible student project.

## 7.8 Accessibility-specific AI tools

- **Be My Eyes / Be My AI.** Use, know well, teach. Most-used AI tool by blind users worldwide. Any accessibility-first architecture pedagogy must treat it as the baseline that any custom tool must beat. Be My AI describes "a room with chairs"; TACT should describe "a 24-by-30-foot lecture hall with 60 seats on a 5-by-12 grid."
- **Aira.** Know it exists. Paid sighted-agent service, used for higher-stakes navigation.
- **Seeing AI (Microsoft).** Use it. Free, no account, multi-feature scanner. Hand to every studio visitor as easiest entry point.
- **JAWS AI add-ons / Picture Smart.** Know exists. Use as comparison point: when testing TACT image descriptions, always compare against Picture Smart. If TACT isn't better for architectural content, TACT has a problem.
- **NVDA-with-Mistral / NVDA AI add-ons.** Watch. Promising but unstable.

**The AI accessibility tools that already exist are good. The opportunity for this toolkit is not to compete on "describe an arbitrary image" but to own the architectural domain.** Be My AI doesn't know what a section drawing is. TACT can.

## 7.9 Architecture + GIS knowledge sources

- **QGIS.** Use it. Mandatory for Superfund. PyQGIS is the scripting on-ramp.
- **OpenStreetMap + Overpass API.** Use it. Essential for site context. Integration idea: `overpass` MCP lets Claude query "all industrial buildings within 1km of these coordinates."
- **Mapbox / Maptiler.** Know exists. Only if you need pretty raster maps for sighted deliverables.
- **EPA Envirofacts / ECHO / EJScreen APIs.** Use them, build wrappers. **This is the gold mine for your Superfund work.** Integration idea: a `superfund` MCP exposing these three APIs to Claude as a single coherent toolset. **The single highest-leverage MCP you could write for your specific pedagogy.**
- **USGS.** Use the elevation API. Tactile model is incomplete without terrain.
- **NOAA.** Use for site analysis, especially Sea Level Rise Viewer data for coastal Superfund sites.
- **NASA Earthdata.** Worth piloting for historical satellite views (very compelling for Superfund work).

**Winner stack:** OSM/Overpass for context, EPA APIs for the site, USGS for terrain, QGIS as desktop tool, plus a custom MCP wrapping all of this for Claude.

## 7.10 Academic / research tools

- **Elicit.** Use it. Best-in-class for literature search with structured extraction. Pair with Claude.
- **Scite.** Know exists. Useful for advanced lit reviews; overkill for most studio work.
- **Semantic Scholar API.** Use it. Free, no rate limit horror. Integration idea: an MCP proposing readings tied to a student's current studio direction.
- **Connected Papers / ResearchRabbit.** Skip Connected Papers (viz only, inaccessible); use ResearchRabbit.
- **Zotero + AI plugins.** Use Zotero, watch plugins.
- **Nougat.** Skip. Marker is better now.
- **MathPix.** Use if you teach computational design with equation-heavy papers.
- **Marker.** Use it. Winner over Nougat for general academic PDFs.
- **Docling.** Watch. Could overtake Marker.

**Winner:** Marker + Semantic Scholar API + Elicit, glued together by Claude.

## 7.11 Diagramming & whiteboarding (accessibility lens)

- **Mermaid.** Use it as default. Text-first, lives in markdown, renders to SVG, screen readers can read the source. Winner of the category for accessibility-first work. Integration idea: `state describe mermaid` exports current `state.json` as a Mermaid graph of zone relationships.
- **PlantUML.** Use for UML specifically.
- **Graphviz.** Use for complex graphs. When Mermaid runs out of layout intelligence.
- **Excalidraw / tldraw / draw.io.** Skip for accessibility-first contexts. Output is visual.

**Winner:** Mermaid, no contest.

## 7.12 Code / dev tools for teaching coding

- **GitHub Copilot vs Claude Code in VS Code.** **Teach Claude Code, mention Copilot.** Copilot is autocomplete; Claude Code is collaboration. The pedagogical difference is everything. Copilot is also screen-reader-weaker than Claude Code's text-mode CLI.
- **Cursor.** Skip. VS Code itself has good Claude integration via the official extension; Cursor's moat is thin.
- **Windsurf.** Skip.
- **Replit.** Use for intro courses. The "no setup" property is gold for week one.
- **Gitpod / GitHub Codespaces.** Use Codespaces. **Every student starts every studio in a Codespace with a prebuilt devcontainer that has the toolkit installed.** Eliminates the "but it doesn't work on my machine" hour-one disaster.
- **DevContainers.** Use them. Build one for the Radical Accessibility Toolkit. Pin Python version, pip-installed `tact` and `tasc`, MCP config, NVDA shortcuts documented. Ship as `.devcontainer/devcontainer.json`. Lets a new student or external collaborator open the repo in Codespaces and have a working environment in under 5 minutes.

**Winner:** Claude Code + VS Code + Codespaces + DevContainers. This is the teaching stack.

## 7.13 Didn't ask but should care

1. **uv (and uvx) — Astral's Python package manager.** Adopt now. Replaces pip, virtualenv, pyenv, pipx in one Rust binary. This will be how all Python in the toolkit is installed within 18 months. `uvx tact convert ...` works without an install step.
2. **Anthropic's Skills feature.** You use it. The wider pattern: **skills are becoming the durable interface to agent capabilities, more than MCPs.** MCPs are protocols; skills are pedagogy. Bet heavier on skills. Your taxonomy in CLAUDE.md is ahead of the curve.
3. **OpenSCAD and CadQuery.** Text-based 3D modeling. For tactile-print pipelines, a CadQuery script that takes `state.json` and emits an STL is more reproducible, more accessible, and more diff-friendly than a Grasshopper definition. Integration idea: `tact stl` emits a 3D-printable tactile model directly from `state.json` via CadQuery, no Rhino dependency.
4. **SQLite + Litestream.** When the toolkit eventually needs to track student submissions, crit comments, tactile-print queues — SQLite + Litestream gives you a single-file durable database with off-site replication and zero ops. Don't reach for Postgres.
5. **PyMuPDF and pdfplumber.** Use pdfplumber. When students hand you scanned architectural PDFs (which they will), pdfplumber + EasyOCR is the path. Marker is for academic papers; pdfplumber is for construction documents and shop drawings.
6. **Datasette (Simon Willison).** Use it. Take EPA Envirofacts data for a Superfund site, load into SQLite, serve with Datasette, and you have an instant accessible per-site data portal. Pair with a static Mermaid site map for navigation. **A 2-hour lab session that produces a real public artifact per studio project.**
7. **Anthropic prompt caching.** Not a tool, a billing detail. With prompt caching, a long `CLAUDE.md` (like yours) costs ~10% on cache hits instead of 100% on every turn. Confirm caching is on for your usage. Material cost savings at studio scale.

---

# 8. Highest-leverage picks (synthesis)

The dossier above is broad by design. If you want a starting line, these are the picks that cross-cut: they advance multiple sections at once, demo a Claude Code feature, build something that ties into both studios, and move toward Daniel's third-year studio.

## 8.1 Build before fall (the "must-haves")

1. **`.devcontainer/devcontainer.json` + Codespaces onboarding.** §7.12. One commit gets every student in either studio installing in 5 minutes instead of 5 hours. Higher pedagogical-time-saved per line of code than anything else in the dossier. **S, infra.**

2. **`.claude/settings.json` + the three existing hooks wired up.** §3.5 and §1.8. The hooks are written (image-detector, conversion-tracker, feedback-capture) but not auto-loaded. Wire them. While you're in there, add a `Notification` hook for screen-reader announcements, and a `PreToolUse` hook validating state.json. **S, infra, accessibility.**

3. **Pin-up board generator** (#19) — `controller_cli pinup --crit fall-final` collects every student's latest state.json, renders plan + axon + tactile booklet, emits one indexed PDF + Braille program. Replaces 4-hour manual prep at every review. **M, classroom, tactile.**

4. **5–8 new SKILL.md packages.** §3.3. Aim for: `/tactile-export`, `/validate-state`, `/ej-audit`, `/rod-parser`, `/describe-my-model` (#38), `/tactile-this` (#39), `/precrit` (#51). The teachable surface area of the toolkit lives in these. **M, ai, infra.**

5. **Image Describer wired through.** §1.10. It's in repo as a stub at `tools/image-describer/arch_alt_text.py`. Add a CLI entry and an MCP function. Small effort, high payoff for tactile workflow. **S, ai, tactile.**

## 8.2 The summer demo with the biggest cross-section

6. **Superfund MCP server** (§4 and §7.9). Wraps Envirofacts + ECHO + EJScreen as MCP functions. Single highest-leverage build in the whole dossier — it powers the entire second-year studio, demonstrates MCP authoring, and is publicly demoable. Pair with a `template load superfund-site-<id>` that pre-populates state.json with contamination zones (#10, #16). **M, ai, mcp, classroom.**

## 8.3 The tactile + voice demos that make the third-year studio possible

7. **Voice-driven Layout Jig** (#8) with Whisper.cpp + a TASC grammar parser. Free, local, instantly demos voice-first design. Pairs with the studio's daily voice drills (§5.2.4, §5.8). **M, voice, accessibility.**

8. **Pegboard digitizer with ArUco** (#28, §6.7). Physical-to-digital round-trip without electronics. Demos the controller/viewer separation principle. Studio-ready by week 2 of the third-year. **L (but L on a fast week), hardware, tactile.**

9. **Tactile booklet (`tact booklet`)** (#3) — multi-page PDF with plans, sections, axon, zones, Braille TOC, and cross-references. The fundamental studio deliverable, automated. **M, tactile, classroom.**

10. **Critique-bot persona library** (#42) + EJ audit (#49). Cheap to build, demos AI-as-critic across both studios, plays into the "no deixis" critique discipline. **S+M, ai, classroom.**

## 8.4 Tactile time-lapse — the studio's signature image

11. **Tactile Time-Lapse for Superfund** (#33, §4 phase 5). Render plume shrinkage at year 0/5/15/30/100 as five PIAF pages. Single artifact that captures the studio's whole pedagogy: contamination modeled, semantically, then made tactile, across time. Use it on the recruiting page. **M, tactile, ai, classroom.**

## 8.5 What to learn about Claude Code first

Mapped to §3.17:

1. CLAUDE.md + Memory. You have one; iterate on it as you build skills.
2. Hooks + settings.json. Wire the existing three; add 2-3 more.
3. MCP servers. You already write them; build the Superfund MCP (§8.2 #6).
4. Skills. Aim for 8-12 by fall (§8.1 #4).
5. Headless mode + GitHub Actions. Wire the studio's CI to validate state.json on every push.

## 8.6 What to skip (so you don't get distracted)

- Midjourney, Cursor, Windsurf, OpenAI Assistants API, CrewAI, AutoGen, MetaGPT, Connected Papers, Excalidraw, draw.io, LM Studio (GUI = screen-reader-hostile), Tesseract, Bark, Coqui (defunct), Nougat (superseded), Veo/Sora/Runway for architecture pedagogy.
- Tripo / Meshy / CSM / Luma Genie / Rodin for buildings (use for furniture/landscape elements only if you bother).
- TestFit, Finch3D, Maket, ArkDesign.ai.

## 8.7 The single biggest unknown

Refreshable tactile graphics device API maturity. APH Monarch and Dot Pad SDKs are young; building TACT output targets for them is real engineering, not a weekend port. But if it works, it would let the toolkit do something nothing else in the world does — live tactile editing during a design crit. If you can swing the hardware budget (~$10-25K combined), one summer pilot here would be worth more than several smaller wins. **L+, hardware, accessibility.**

---

## Closing note

Everything above is "all potential options." You'll pick maybe a quarter of it. The mistake would be doing things in order — pick the items that cross-pollinate, build those first, and let the studio choose the rest.

The pieces most worth doing _before_ the fall semesters start: the devcontainer, the hooks audit, the Superfund MCP, the pin-up generator, the new skills. Everything else can ride alongside the studio.
