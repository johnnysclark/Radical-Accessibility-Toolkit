# 03-06 — Agent Loop

## Two callers, one dispatcher

The system has two kinds of driver: a human at a terminal (CLI REPL) and an LLM agent over MCP. Both route through the same command dispatcher. The dispatcher does not know or care which caller it is serving — it receives a command string, runs it, and returns a confirmation string. This is the invariant that must survive the rewrite.

```
Human:  stdin → tokenize → dispatcher → stdout
Agent:  MCP call → run_command() → dispatcher → return value
```

---

## Turn lifecycle

A single turn is:

1. **Receive** — a command string arrives (typed line or MCP argument).
2. **Load** — read `state.json` from disk. Apply any pending schema migration.
3. **Snapshot** — `copy.deepcopy(state)` onto the undo stack.
4. **Dispatch** — find the command handler by name; call it with state and parsed args.
5. **Validate** — the handler returns the mutated state. Basic schema invariants are checked.
6. **Write** — `_atomic_write`: serialize to `.tmp`, fsync, `os.replace`. State is now durable.
7. **Hook** — fire all registered post-mutation hooks in order (TTS, export triggers, etc.).
8. **Confirm** — print or return the `OK:` / `ERROR:` string, then `READY:`.

Steps 2–8 happen inside a single Python call. No turn is left half-done — the write either completes atomically or the old file remains intact.

---

## State is on disk, not in memory

The dispatcher reloads state from disk at the start of every turn. It does not hold state in a long-lived object between turns. This is not inefficiency — it is the property that makes the system safe across crashes, process restarts, and multi-process access (CLI and MCP server can run simultaneously against the same file).

The undo stack is the one in-memory exception: it lives in the REPL process and is lost on restart. This is acceptable because `state.json` is the durable record; the undo stack is a convenience within a session. An open question (see 03-09) is whether the undo stack should be serialized alongside state for persistence across restarts.

---

## How a turn completes for an agent

The `READY:` suffix on every confirmation is the agent's signal that the turn is finished and state is durable. An agent must not issue the next command until it has received a string ending with `READY:`. This convention replaces streaming indicators (forbidden — screen reader hostile) and eliminates the need for the agent to poll for completion.

For multi-command sequences, the agent issues commands one at a time, waiting for `READY:` between each. Macros exist precisely to compress known sequences into a single MCP call — an agent should prefer `run_macro` over issuing a sequence of `run_command` calls when the sequence is deterministic.

---

## What the agent loop does not do

- It does not render geometry. That is the Rhino watcher's job (section 03-07).
- It does not call an LLM. That is the provider layer's job (section 03-04) invoked by specific MCP functions.
- It does not manage conversation history or multi-step reasoning. That is the calling agent's job — the dispatcher is stateless between turns.
- It does not watch for external changes to `state.json`. If another process modifies state, the next CLI turn will pick up the change on load; the MCP server will too.

---

## The REPL vs. single-call distinction

The CLI REPL adds one layer above the dispatcher: a `readline`-backed input loop, a help command, and a graceful quit. This layer is thin and has no access to state beyond what it passes into the dispatcher. The MCP `run_command` function is identical to one iteration of that loop minus the readline and help.
