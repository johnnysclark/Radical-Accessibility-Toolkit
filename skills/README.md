# skills/ — SKILL.md-Packaged Capabilities

This directory holds **skills** in the Anthropic agent-skills sense: SKILL.md-packaged capabilities that Claude Code auto-discovers and invokes when a user's request matches the skill's triggers.

Each skill lives in its own folder:

    skills/
      <skill-name>/
        SKILL.md          # frontmatter (name, description, triggers) + instructions
        WORKFLOW.md       # optional: operator-facing step-by-step doc
        quick-start.md    # optional: short cheatsheet
        ...any other assets the skill needs

The code a skill invokes typically lives under `tools/` (or in the controller), not in this folder. `SKILL.md` is an *instruction wrapper* that tells Claude how to use the underlying tool.

## Not to be confused with macros

The project has another concept called a **macro** — a saved JSON sequence of controller commands, living in `controller/macros/`. Macros are data; skills are Claude-invocable instructions + code pointers.

| | Macro | Skill |
|---|---|---|
| File | `controller/macros/<name>.json` | `skills/<name>/SKILL.md` |
| Shape | JSON: name, description, commands, params | Markdown with YAML frontmatter |
| Invoked by | `macro_run <name>` CLI / MCP call | Claude matching the trigger in conversation |
| Purpose | Replay a fixed command sequence | Package a whole workflow (prompts + scripts + docs) |
| Scope | Controller commands only | Arbitrary — may involve Rhino, TACT, shell tools, etc. |

See `CLAUDE.md` at the repo root for the full taxonomy.

## Current skills

- [`laser-export/`](laser-export/) — Rhino → Adobe Illustrator (.ai) export for the Siebel Center for Design 24″×40″ laser cutter.
