# 03-09 — Open Design Questions

Each question is stated cleanly, the tradeoff sketched briefly, and a tentative lean given. The implementing team decides; these leans are recommendations, not requirements.

---

## Q1: Single domain vs. multi-domain state envelope

Should `state.json` hold one domain object at the root (`"domain": {...}`) or a named map (`"domain": { "layout_jig": {...}, "site": {...} }`)?

**Single:** simpler schema, simpler migration, simpler renderer contracts. Every deployment has one domain type; there is no current use case for composing two.

**Multi:** future-proofs composite designs (e.g. a site model and a building model coexisting). Adds schema complexity and forces all renderers to declare which domain they read.

**Lean:** single domain with a `"domain_type"` string at the root so renderers can check compatibility. Multi-domain is an extension if the use case arises.

---

## Q2: Hook execution: synchronous vs. asynchronous

Should post-mutation hooks block the REPL until they complete, or fire asynchronously?

**Synchronous:** simpler; `READY:` is only printed after all hooks finish; TTS completes before the next command is accepted.

**Async:** faster perceived response for the user when hooks are slow (e.g. STL export); but `READY:` must be emitted before hooks complete, which weakens its guarantee.

**Lean:** synchronous for TTS and screen reader hooks (they must complete before the next command); async opt-in for slow export hooks (export can lag behind; READY: is still safe to emit).

---

## Q3: Undo stack persistence

Should the undo stack be serialized to disk alongside `state.json` so undo survives process restarts?

**Persist:** undo works across CLI restarts and across CLI/MCP interleaving. Adds a sidecar file and serialization cost per command.

**In-memory only:** simpler; undo is a session convenience, not a durability guarantee. Git history of `state.json` provides coarser-grained recovery.

**Lean:** in-memory for now. If restart-induced undo loss proves a real problem in practice, add persistence then.

---

## Q4: Renderer trigger: mtime poll vs. push signal

Should renderers be triggered by filesystem mtime polling or by an explicit signal written by the dispatcher after each atomic write?

**Mtime poll:** works across all runtimes including IronPython 2.7. No IPC required. Latency is bounded by poll interval (currently 0.5s).

**Push signal:** lower latency, more precise (includes command name so renderers can skip irrelevant rebuilds). Requires IPC that works across Python 3 and IronPython 2.7 — the options are limited (named pipe, sidecar file, UDP). A sidecar-file push signal is essentially mtime polling with a richer payload.

**Lean:** mtime poll for the Rhino watcher (IronPython forces it). Optional sidecar-file signal for Python 3 renderers that want the command name.

---

## Q5: Optional domain-specific MCP functions

Should the MCP surface allow optional domain-specific function sets to be registered alongside the core ~15 functions?

**Fixed surface only:** enforces the small-API discipline; agents learn one surface and it works everywhere.

**Optional extensions:** a Layout Jig deployment can register `add_bay`, `set_wall`, etc. as shortcuts. Reduces agent turn count for frequent workflows. Risks the surface growing back to 71.

**Lean:** allow extensions declared in a config file with a cap (e.g. 20 max). Core surface is fixed; extensions are deployment-specific.

---

## Q6: Template vs. macro unification

Should templates (startup state generators) and macros (command sequences) be unified under one `run_macro` function with a `--template` flag, or kept as separate MCP functions?

**Unified:** smaller surface; the distinction between "replace state" and "replay commands" is an implementation detail the agent should not need to track.

**Separate:** the distinction is semantically meaningful and prevents accidents (an agent running a template mid-session overwrites the current design).

**Lean:** keep separate. The overwrite risk justifies the extra function name. Use `load_template` and `run_macro` as the two names.
