---
name: update
description: Pull the latest master from the project's upstream repo (johnnysclark/Radical-Accessibility-Toolkit), fast-forward the teammate's local copy, and walk them through any post-pull housekeeping (setup.py rerun, dependency reinstall, Rhino restart, MCP tool re-approval). Safe with uncommitted local changes — pauses and asks before touching them. Trigger when the user says "update", "update my code", "pull latest", "check for updates", "get the latest", "sync from github", "sync from master", or "what's new on master".
---

# Update Skill

Keeps a teammate's local checkout in sync with the latest merged work on the project's upstream `master` branch. Designed for teammates who don't want to think about whether their origin is their fork or the main repo, whether they need to rerun `setup.py`, or which tools need a restart after pull.

The underlying script is `scripts/update.sh`. This SKILL.md is the Claude-facing wrapper — when the user says "update my code", Claude invokes the script and relays the output.

## How to run it (Claude's job)

From the repo root:

```bash
bash scripts/update.sh
```

The script is self-contained. It:

1. **Auto-detects** which of the user's git remotes points at `johnnysclark/Radical-Accessibility-Toolkit` (could be named `origin`, `upstream`, or anything else).
2. **Checks for uncommitted changes** and handles them per the flag:
   - No flag, non-interactive (Claude's path) → exits with `ERROR:` asking for a decision.
   - No flag, interactive terminal → prompts the teammate directly.
   - `--stash` → stashes + pulls + pops.
   - `--abort` → refuses if dirty.
3. **Fetches** the upstream `master`.
4. **Fast-forwards** local `master` if incoming commits are a linear advance.
5. **Reports** incoming commits (git log --oneline style) and which post-pull steps the teammate should run, based on which files changed.
6. **Pops the stash** if one was created.

## When the script asks for help

If the script exits with code 1 and prints "ERROR: refusing to update with uncommitted changes", ask the user one question: "You have uncommitted work — stash it and continue, or cancel?" Then:

- **Stash** → rerun as `bash scripts/update.sh --stash`
- **Cancel** → stop; the teammate can commit or discard manually and rerun.

If the script exits with code 3 ("local master has diverged"), don't try to auto-recover. The teammate has local commits on `master` itself, which means they've been committing without a feature branch — that's a situation worth understanding before flattening. Summarize the divergence (`git log master..upstream/master` and `git log upstream/master..master`) and hand control back to the user.

## What the script's post-pull recommendations mean

The script lists which teardown-and-rerun steps are necessary based on *which files actually changed*. Translate each line if the user asks:

| Recommendation | Why |
| --- | --- |
| `python setup.py` | The MCP server code, root `setup.py`, or `.mcp.json` moved — regenerate `.mcp.json` with fresh absolute paths for this machine. |
| `pip install -e tools/tact` | TACT's package metadata changed — editable install needs refreshing. |
| `pip install -e tools/tasc` | Same, for TASC. |
| `cd tools/webui && bun install` | webui's `package.json` moved — new TS deps. |
| Restart Rhino | Something under `tools/rhino/` changed — the watcher and `startup.py` only load once at Rhino launch. |
| Re-approve MCP tools in Claude Code | `mcp/mcp_server.py` changed — renamed or new tools won't match the teammate's cached allowlist. |

## Not in scope

- Pulling open PR branches (this skill is master-only). If the user wants to test an unmerged PR, use `gh pr checkout <n>` directly or the per-PR checkout commands in [WORKFLOW.md](WORKFLOW.md).
- Pushing local commits to the upstream. This is a one-way pull.
- Sync between the teammate's fork (`origin`) and `upstream` on GitHub. The script leaves the fork alone; if the teammate wants to keep their fork's `master` in step, they run `git push origin master` after the skill finishes.
