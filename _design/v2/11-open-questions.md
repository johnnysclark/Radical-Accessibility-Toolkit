# Open Design Questions

Each question is stated cleanly, the tradeoff sketched briefly, and a tentative lean given. The implementing team decides; these leans are recommendations, not requirements.

---

## Q1: Single domain vs. multi-domain state envelope

Should `state.json` hold one domain object (`"domain": {...}`) or a named map (`"domain": { "layout_jig": {...}, "site": {...} }`)?

**Single:** simpler schema, simpler migration, simpler renderer contracts. One domain per deployment covers all known use cases.

**Multi:** future-proofs composite designs (e.g. a site model and a building model coexisting in one file). Adds schema complexity and forces all renderers to declare which domain they consume.

**Lean:** single domain with a `"domain_type"` string at the root. Multi-domain is a future extension.

---

## Q2: Hook execution: synchronous vs. asynchronous

Should post-mutation hooks block the dispatcher until they complete, or fire asynchronously?

**Synchronous:** `READY:` is only emitted after all hooks finish. TTS completes before the next command is accepted. Simpler to reason about.

**Async:** hooks that are slow (e.g. STL export) don't delay the user. But `READY:` must be emitted before hooks complete, which weakens its guarantee for export-dependent workflows.

**Lean:** synchronous for TTS and screen reader hooks; async opt-in for export hooks where latency matters. The hook registration API should accept a `sync: bool` flag.

---

## Q3: Undo stack persistence

Should the undo stack serialize to disk alongside `state.json` so undo works across process restarts?

**Persist:** undo survives CLI restarts and CLI/MCP interleaving.

**In-memory only:** simpler; undo is a session convenience. The state file and git history provide coarser-grained recovery.

**Lean:** in-memory only for the initial implementation. Add persistence if users report it as a real problem.

---

## Q4: Renderer trigger: mtime poll vs. push signal

Should renderers be triggered by mtime polling or by an explicit sidecar signal written by the dispatcher?

**Mtime poll:** works across Python 3 and IronPython 2.7. No IPC required. Latency bounded by poll interval.

**Push signal:** lower latency; `command` field lets renderers skip irrelevant rebuilds. Requires a sidecar write per command.

**Lean:** mtime poll for the Rhino watcher (IronPython forces it). Optional sidecar signal for Python 3 renderers.

---

## Q5: Optional domain-specific MCP functions

Should deployments be allowed to register extra named MCP functions (e.g. `add_bay`, `set_wall`) alongside the core 14?

**Fixed surface only:** enforces small-API discipline.

**Optional extensions:** shortcuts reduce agent turn count for frequent workflows. Risk: the surface grows back over time.

**Lean:** allow extensions declared in a config file, capped at 20. Core surface is fixed; extensions are deployment-specific and must delegate to `run_command` internally.

---

## Q6: Template vs. macro naming

Should `load_template` and `run_macro` be merged into a single `run_macro` function with a `--template` flag?

**Unified:** smaller surface; the distinction is an implementation detail.

**Separate:** the distinction matters — templates are destructive (they replace state); macros are additive (they replay commands on existing state). Keeping them separate prevents an agent from accidentally overwriting a design.

**Lean:** keep separate. Use `load_template` and `run_macro` as the two names. The destructive/additive distinction is worth a separate function name.

---

## Q7: Domain registration mechanism

How does a domain module register its commands with the dispatcher at startup?

**Config file:** `deployment.json` lists the domain module path; the dispatcher imports it.

**Entry points:** domain modules declare a `rap.domain` entry point in `pyproject.toml`; the dispatcher discovers them via `importlib.metadata`.

**Lean:** config file for simplicity. Entry points are better for third-party domains but add packaging complexity that isn't needed for the initial implementation.
