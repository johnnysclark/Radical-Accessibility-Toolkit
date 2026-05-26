# Radical Accessibility Project — One-Pager

**An accessibility-first architectural design system, built on Claude.**

UIUC School of Architecture · Led by John Clark and Hugh Swiatek · Co-designed with Daniel Bein, a blind architecture student

---

## The problem

Architecture assumes you can see. Every mainstream design tool — CAD viewports, drawing sheets, pin-up critiques, the vocabulary of studio culture — treats vision as a prerequisite for participation. A blind student is locked out of the discipline. Existing accommodations retrofit visual tools. We rebuilt the tools.

## What we built

A working design platform where a blind architect builds a building by typing or speaking, hears every change confirmed, audits the design for ADA compliance, prints it on PIAF swell paper, reads it with their fingers, 3D-prints it to scale, and presents it — without a sighted intermediary at any step. Daniel Bein uses this daily.

**Built on Claude:**
- Two MCP servers (58 + 7 functions) bridge Claude Code to the entire design pipeline
- Skills (Anthropic agent-skills format) package reusable capabilities
- An accessible web client wraps Claude Code for JAWS/NVDA users (Claude Code's Ink TUI is not screen-reader compatible — we shipped the fix)
- Claude Code lifecycle hooks announce events via the JAWS TTS API

This is, as far as we know, the deepest production accessibility deployment of Claude's full product stack.

## Who it's for

- Blind and low-vision architecture students and practitioners
- Architects with motor impairments (voice + macros instead of mouse)
- Designers with cognitive fatigue or TBI (deterministic state; nothing lost)
- Deafblind users (refreshable braille displays + braille labels on every output)
- Sighted instructors reviewing blind students' work on equal footing

The same input/logic/output separation generalizes beyond vision loss. Build for the hardest case; the easier cases follow.

## What we're asking Anthropic for

A staged conversation, smallest first:

1. **Claude API / Claude Code credits** so student usage isn't capped by personal subscriptions
2. **Reference deployment / co-marketing** — RAP as Anthropic's flagship accessibility case study for Claude Code, MCP, and Skills
3. **Claude Code accessibility partnership** — paid pilot to upstream our webui + screen-reader hooks work
4. **Sponsored research grant (12 months)** — student stipends, PIAF supplies, equipment, conference travel, course buyout

## Why Anthropic

The toolkit is already Claude-native. Switching providers would require rebuilding it. We chose Claude because MCP is the only protocol designed for the kind of semantic, auditable, multi-tool integration accessibility requires — and because Claude Code is the only agentic interface a screen-reader user can reasonably extend. Funding RAP demonstrates Claude in a use case competitors cannot credibly claim: AI as infrastructure for human authorship by people the discipline locked out.

## Status & credibility

- Working software, in daily use, since 2025
- ACADIA paper in flight: *The Full Stack of Inclusion*
- Team: 2 faculty leads, 3 student researchers, 1 primary co-designer
- Open source, MIT licensed: github.com/johnnysclark/Radical-Accessibility-Toolkit

## Contact

John Clark · UIUC School of Architecture · [contact info to fill in]
