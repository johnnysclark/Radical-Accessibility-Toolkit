# Radical Accessibility Project — One-Pager

**An accessibility harness for AI-mediated design: replacing the visual viewport as architecture's sole source of truth with a sense-agnostic design state.**

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

Three direct options. Any combination. Equipment, fabrication, and lab costs are covered through UIUC — this ask is about people and access.

1. **Money** — student stipends for Ethan, Isaac, Laura, and a co-designer stipend for Daniel. ~$60K–$80K/year covers the four of them plus modest travel for paper presentation.
2. **Credits** — Claude API + Claude Code credits to uncap student and primary-user usage during batch image description, OCR, and day-to-day design-conversation work.
3. **Expertise** — time from the people at Anthropic who own Claude Code accessibility, MCP, and Skills. Code review on our webui + screen-reader hooks. A design partner who can tell us what to upstream.

## Why Anthropic

The toolkit is already Claude-native. Switching providers would require rebuilding it. We chose Claude because MCP is the only protocol designed for the kind of semantic, auditable, multi-tool integration accessibility requires — and because Claude Code is the only agentic interface a screen-reader user can reasonably extend. Funding RAP demonstrates Claude in a use case competitors cannot credibly claim: AI as infrastructure for human authorship by people the discipline locked out.

## Status & credibility

- Working software, in daily use, since 2025
- ACADIA paper in flight: *The Full Stack of Inclusion*
- Team: 2 faculty leads, 3 student researchers, 1 primary co-designer
- Open source, MIT licensed: github.com/johnnysclark/Radical-Accessibility-Toolkit

## Contact

John Clark · UIUC School of Architecture · [contact info to fill in]
