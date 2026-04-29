# Agent Loop

## Two callers, one dispatcher

The system has two kinds of driver: a human at a terminal (CLI REPL) and an LLM agent over MCP. Both route through the same command dispatcher. The dispatcher does not know or care which caller it is serving — it receives a command string, runs it, and returns a confirmation string.

```
Human:  stdin → tokenize → dispatcher → stdout
Agent:  MCP call → run_command() → dispatcher → return value
```

---

## Turn lifecycle

A single turn is:

1. **Receive** — a command string arrives (typed line or MCP argument).
2. **Load** — read `state.json` from disk. Run schema migration if needed.
3. **Snapshot** — `copy.deepcopy(state)` onto the undo stack.
4. **Dispatch** — look up the command handler by name; call it with state and parsed args.
5. **Validate** — the handler returns the mutated state. Check required schema fields are present.
6. **Write** — `_atomic_write`: serialize to `.tmp`, fsync, `os.replace`. State is now durable.
7. **Hook** — fire all registered hooks in order with the `HookPayload`.
8. **Confirm** — print or return the `OK:` / `ERROR:` string, then `READY:` on a new line.

Steps 2–8 happen inside a single call. No turn is left half-done — the atomic write either completes or the previous file remains intact.

---

## State is on disk, not in memory

The dispatcher reloads state from disk at the start of every turn. It does not hold state in a long-lived object between turns. This is what makes the system safe across crashes, process restarts, and simultaneous access from the CLI and MCP server against the same file.

The undo stack is the one in-memory exception: it lives in the REPL process and is lost on restart. `state.json` is the durable record; the undo stack is a session convenience.

---

## How a turn completes for an agent

`READY:` on its own line at the end of every response is the agent's signal that the turn is finished and state is durable. An agent must not issue the next command until it receives a line containing only `READY:`. This convention:
- Replaces streaming indicators (forbidden — screen reader hostile)
- Eliminates the need to poll for completion
- Survives across both synchronous and async transport

For multi-command sequences, the agent issues one command at a time and waits for `READY:` between each. Use `run_macro` to compress a deterministic sequence into one call.

---

## What the agent loop does not do

- **Render geometry.** The Rhino watcher reacts to file changes asynchronously. The dispatcher does not wait for it.
- **Call an LLM.** The provider layer is invoked by specific MCP functions in Group 4, not by the dispatcher.
- **Manage conversation history.** The calling agent owns its context window. The dispatcher is stateless between turns.
- **Watch for external changes to `state.json`.** If an external process modifies state, the next CLI turn picks up the change on load.

---

## The REPL vs. single-call distinction

`cli/repl.py` adds a readline input loop, `help`, and a graceful quit above the dispatcher. It is a thin shell. The MCP `run_command` function is identical to one iteration of that loop minus readline and help. Both call `apply_command` with the same arguments.

---

## Screen reader output rules

All output from the dispatcher must follow these rules — they are not optional:

- Every response begins with `OK:` or `ERROR:`.
- Every response ends with `READY:` on its own line.
- No tables, no multi-column layout, no box-drawing characters.
- No progress spinners or streaming partial output.
- No lines longer than 120 characters.
- When listing items, one item per line with a label prefix.
