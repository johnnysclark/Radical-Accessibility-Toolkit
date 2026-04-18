# Update Workflow (operator-facing)

Step-by-step for teammates who want to pull the latest merged code from the upstream repo and get their local environment back in sync. Most of this is automated by `scripts/update.sh`; this doc explains what each step does and when to intervene manually.

## The short version

```bash
bash scripts/update.sh
```

That's it in the happy path. Everything below is for when you want to know *why* or when something goes sideways.

## Prerequisites

You must have a git remote pointing at `https://github.com/johnnysclark/Radical-Accessibility-Toolkit.git`. Check with:

```bash
git remote -v
```

If you don't see the johnnysclark URL on any line, add it:

```bash
# If you cloned your own fork, the upstream isn't set. Add it as "upstream":
git remote add upstream https://github.com/johnnysclark/Radical-Accessibility-Toolkit.git
```

The update script will auto-detect which remote name (`origin`, `upstream`, or whatever) points at johnnysclark — you don't have to tell it.

## Running it

### Via Claude

Say "update my code" (or "pull the latest", "check for updates", "sync master"). Claude will run the script and relay what happens. If the script needs a decision — for example, you have uncommitted work — Claude will ask you and rerun with the right flag.

### Via the terminal (directly)

```bash
bash scripts/update.sh
```

If your working tree is clean, it runs end-to-end without prompts. If you have uncommitted changes, it asks:

```
WARN: uncommitted changes in working tree.
       M controller/state.json
       ?? my_scratch_file.md
Choose: (s)tash and continue, (c)ancel, (f)orce pull without touching them
       >
```

- **s** — stashes everything (including untracked files), pulls, then pops the stash.
- **c** — exits without doing anything. You can then commit, discard, or stash manually and rerun.
- **f** — proceeds without stashing. Risky; may cause merge conflicts on pull if the upstream commits touch files you've changed.

Flags for non-interactive use:

- `bash scripts/update.sh --stash` — stash-and-pop without asking.
- `bash scripts/update.sh --abort` — refuse if dirty (default when invoked by Claude or in a script).
- `bash scripts/update.sh --dry-run` — show what would happen; change nothing.

## Post-pull housekeeping

The script looks at which files changed and prints exactly the commands you should run. You don't have to memorize the list — just follow what the script says. Common ones:

| If this changed | Run |
| --- | --- |
| `mcp/` or root `setup.py` | `python setup.py` to regenerate `.mcp.json` with paths for your machine. |
| `tools/tact/setup.py` | `pip install -e tools/tact` to refresh the editable install. |
| `tools/tasc/setup.py` | `pip install -e tools/tasc`. |
| `tools/webui/package.json` | `cd tools/webui && bun install`. |
| Anything under `tools/rhino/` | Restart Rhino — the watcher and `startup.py` only load on launch. |
| `mcp/mcp_server.py` | Re-approve MCP tools in Claude Code on next use (renames change the tool allowlist key). |

None of these run automatically. The script prints them; you decide whether to run them now or later.

## When you can't fast-forward

If you've committed directly to `master` (not a feature branch) and the upstream has also moved, your local `master` is diverged. The script refuses to proceed and exits with:

```
ERROR: local master has N commit(s) that aren't on upstream/master,
       and upstream/master has M new commit(s) not local.
       This is a diverged branch; refusing to fast-forward.
```

Options (from cleanest to dirtiest):

1. **Open a PR for your local commits** and let the normal review/merge flow land them. Then rerun `update` — it'll fast-forward cleanly.
2. **Rebase onto upstream** — `git rebase upstream/master`. Only do this if you know what `git rebase` does and the commits aren't already published.
3. **Reset hard onto upstream** — discards your local `master` commits. Only use if you're sure they're worthless.

The script will never choose one of these for you — divergence is a situational call.

## If the skill doesn't seem to do anything

Check these in order:

1. **Wrong remote name.** Run `git remote -v` — at least one line's URL must contain `johnnysclark/Radical-Accessibility-Toolkit`.
2. **Detached HEAD.** Run `git rev-parse --abbrev-ref HEAD` — it should print a branch name, not `HEAD`. If it says `HEAD`, check out `master` first: `git checkout master`.
3. **Network failure.** Fetch errors get written to `/tmp/update-fetch-err` — open that file for the actual git error.
4. **Everything's already current.** The script prints `OK: master is already up to date` and exits. No new commits to pull.
