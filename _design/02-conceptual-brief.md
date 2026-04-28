# 02 — Conceptual Brief

## What RAP is

RAP is a non-visual, agentic CAD design pipeline. A designer — human or AI agent — issues semantic design intentions through a text interface. Those intentions are recorded in a plain-text JSON file that is the sole source of truth for the design. Downstream renderers — geometry engines, tactile print pipelines, alt-text generators — are read-only consumers of that file. Vision is never required at any stage.

RAP exists because every mainstream design tool treats sight as a prerequisite. Non-visual interaction is the primary design case here; sighted interaction is a bonus layer on top.

## Why it exists

The co-designer is a blind architecture student. His daily workflow — designing a building, reviewing it, fabricating tactile models, presenting to critics — is the test suite for every tool. A feature that can't be heard, felt, or read by a screen reader doesn't ship.

That constraint is generative rather than limiting. To make design accessible without vision, you must make design legible through language; you must separate what a thing *is* from where it appears on screen; you must make every mutation auditable and every state recoverable. These are not accommodations — they are engineering virtues the discipline should have had regardless.

## What "non-visual, agentic CAD pipeline" means in practice

Three properties define the system:

**Non-visual.** Every command has a text form. Every response has a text form. No step requires a viewport, a click, or a look. Physical output — swell-paper tactile graphics, 3D-printed models — closes the loop for users whose primary sense is touch.

**Agentic.** A language model can drive the entire pipeline: issue commands, read state, evaluate geometry, trigger output. The JSON state file is the handoff between the agent's reasoning and the geometry engine's execution. The agent does not need to know Rhino exists.

**CAD pipeline.** The system is grounded in real geometry — meter-accurate plans, structural grids, fabrication-ready exports. The design artifacts it produces go to a laser cutter, a braille embosser, or an architecture critic.

## Why this generalizes beyond one building type

The current codebase carries a large amount of accidental specificity: the Layout Jig's bay-and-wall geometry, hard-coded schema keys, inlined column math. But the underlying architecture — command dispatcher → JSON state → read-only renderers — has no inherent dependency on any of those specifics. It applies to any Rhino design task where the designer works through language rather than a viewport.

The rewrite should distill this general architecture from the specific application. A clean implementation looks like: a small command core that reads and writes a well-defined state schema; a renderer boundary that consumes the schema without knowing where it came from; and an agent-facing API surface that exposes the schema clearly enough that any LLM can drive it.

## The elegance bar

The rewrite succeeds if a new implementer — given only this document — can build a system where a blind architecture student designs, reviews, and fabricates a building without touching a mouse or screen, and where a language model can do the same with no special affordances beyond the documented API. Everything else is negotiable.
