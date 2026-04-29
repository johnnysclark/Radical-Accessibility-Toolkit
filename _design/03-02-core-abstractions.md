# 03-02 — Core Abstractions

Five nouns. Everything else in the architecture is either one of these or a relationship between them.

---

## 1. State

A single JSON document on disk. It is the sole source of truth for the design at every moment. Every command reads from it and writes back to it; every renderer reads from it and never writes back. If Rhino crashes, if the agent disconnects, if the process dies mid-command, the design survives as whatever `state.json` last contained. Recoverability is not a feature — it is the defining property of this abstraction.

The state document has a `schema` version field at its root. All code that reads state must handle older versions via migration, not rejection.

---

## 2. Command

An atomic, named, text-addressable mutation of state. A command takes the current state and a set of typed arguments, applies a transformation, and returns a plain-text confirmation string. Commands are the only legal mutation path — nothing writes to state except through the command dispatcher.

Two properties follow from this: commands are trivially undoable (snapshot state before dispatch, restore on undo), and every mutation is auditable (the command name and arguments are the audit record). The command set is domain-specific — what commands exist depends on the design task — but the dispatch mechanism is domain-agnostic.

---

## 3. Schema

The versioned, documented contract that defines the shape of state. The schema is the seam between command handlers and renderers: command handlers write objects that conform to the schema; renderers read only what the schema defines. Neither side depends on implementation details of the other.

Schema changes are migrations, not breaking changes. A migration function upgrades an older document to the current version on load. The schema version field in state.json selects the right migration path. Domain-specific schemas (Layout Jig, future building types) are namespaced under the root schema so the general envelope stays stable.

---

## 4. Renderer

Any read-only consumer of state that produces an artifact. A renderer watches for state changes (by file mtime, by explicit signal, or by explicit invocation) and translates the current state into an output: Rhino geometry, a tactile PDF, a text description, a 3D print file, a braille document. A renderer never writes back to state. If a renderer crashes or is absent, the design is unaffected.

Renderers are pluggable: adding a new output format means writing a new renderer, not modifying the command layer or the schema. The only contract a renderer must honor is the schema it reads.

---

## 5. Hook

A post-mutation callback registered against the dispatch loop. After a command completes and state is saved, the dispatcher fires all registered hooks in order. A hook receives the command name, the arguments, the before-state, and the after-state. Hooks handle every side effect that is not a renderer: TTS announcement, screen reader signals, export triggers, logging, telemetry. Nothing in the mutation path itself produces side effects.

Hooks are registered at startup, not hardcoded into commands. A deployment without a screen reader simply registers no TTS hook. A deployment with Bambu auto-export registers an export hook. The command code is identical in both cases.

---

## Relationships

```
Agent
  → issues Command
    → Command mutates State (atomic write)
      → Hook fires (post-mutation, side effects only)
      → Renderer reads State (produces artifact)
Schema
  → constrains State shape
  → is honored by both Command and Renderer
```
