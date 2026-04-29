# Conceptual Brief

## What RAP is

RAP is a non-visual, agentic CAD design pipeline. A designer — human or AI agent — issues semantic design intentions through a text interface. Those intentions are recorded in a plain-text JSON file that is the sole source of truth for the design. Downstream renderers — geometry engines, tactile print pipelines, alt-text generators — are read-only consumers of that file. Vision is never required at any stage.

Non-visual interaction is the primary design case; sighted interaction is a bonus layer on top.

## Why it exists

The co-designer is a blind architecture student. His daily workflow — designing a building, reviewing it, fabricating tactile models, presenting to critics — is the test suite for every tool. A feature that can't be heard, felt, or read by a screen reader doesn't ship.

That constraint is generative rather than limiting. To make design accessible without vision, you must make design legible through language; you must separate what a thing *is* from where it appears on screen; you must make every mutation auditable and every state recoverable. These are not accommodations — they are engineering virtues the discipline should have had regardless.

## What "non-visual, agentic CAD pipeline" means in practice

Three properties define the system:

**Non-visual.** Every command has a text form. Every response has a text form. No step requires a viewport, a click, or a look. Physical output — swell-paper tactile graphics, 3D-printed models — closes the loop for users whose primary sense is touch.

**Agentic.** A language model can drive the entire pipeline: issue commands, read state, evaluate geometry, trigger output. The JSON state file is the handoff between the agent's reasoning and the geometry engine's execution. The agent does not need to know Rhino exists.

**CAD pipeline.** The system is grounded in real geometry — meter-accurate plans, structural grids, fabrication-ready exports. The design artifacts it produces go to a laser cutter, a braille embosser, or an architecture critic.

## Why this generalizes across design tasks

The architecture — command dispatcher → JSON state → read-only renderers — has no inherent dependency on any specific building type or geometric vocabulary. It applies to any design task where the designer works through language rather than a viewport. A clean implementation separates the general infrastructure (dispatch, undo, atomic write, renderer boundary) from the domain-specific content (what objects exist, what commands operate on them). Swapping in a new design domain means writing new commands and a new schema — the infrastructure is unchanged.

## The success bar

The system succeeds if a blind architecture student can design, review, and fabricate a building without touching a mouse or screen, and if a language model can do the same with no special affordances beyond the documented API. Everything else is negotiable.
