#!/usr/bin/env bash
#
# update.sh -- pull the latest master from the project's upstream repo
# (johnnysclark/Radical-Accessibility-Toolkit) and report what changed,
# plus any post-pull steps the teammate should run.
#
# Safe to run interactively in a terminal OR non-interactively via the
# `update` skill (Claude calls it for you). Screen-reader friendly:
# every line is an OK:, ERROR:, WARN:, or READY: prefix, one fact per
# line, no spinners, no ASCII art.
#
# Flags (for the non-interactive / Claude path):
#   --stash       Stash uncommitted changes, pull, then pop the stash.
#   --abort       Refuse to run if tree is dirty (default when non-TTY).
#   --dry-run     Show what would happen; make no changes.
#
# Exit codes:
#   0  success (or dry-run)
#   1  dirty tree, no --stash / --abort chosen (user decision needed)
#   2  not a git repo / upstream remote not found / network failure
#   3  master has diverged (local commits on master) -- needs manual
#      resolution; we won't fast-forward over local history
#

set -u -o pipefail

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────
UPSTREAM_REPO_MATCH="johnnysclark/Radical-Accessibility-Toolkit"
MAIN_BRANCH="master"

# ─────────────────────────────────────────────────────────────
# Parse flags
# ─────────────────────────────────────────────────────────────
MODE="ask"       # ask | stash | abort
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --stash)   MODE="stash" ;;
    --abort)   MODE="abort" ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help)
      sed -n '1,35p' "$0"
      exit 0
      ;;
    *) echo "ERROR: unknown flag: $arg"; exit 2 ;;
  esac
done

# If we're not on a TTY and no explicit mode was given, fall back to abort --
# Claude can re-invoke with --stash after asking the user.
if [ "$MODE" = "ask" ] && ! [ -t 0 ]; then
  MODE="abort"
fi

say() { printf "%s\n" "$1"; }

# ─────────────────────────────────────────────────────────────
# Step 0: Sanity
# ─────────────────────────────────────────────────────────────
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  say "ERROR: not inside a git working tree."
  exit 2
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

# Find the remote whose URL points at the upstream repo. Could be named
# anything: "origin" if the teammate cloned johnnysclark directly, or
# "upstream" if they forked.
upstream_remote=""
while read -r name url _; do
  [ -z "$name" ] && continue
  case "$url" in
    *"$UPSTREAM_REPO_MATCH"*) upstream_remote="$name"; break ;;
  esac
done < <(git remote -v | awk '$3=="(fetch)"')

if [ -z "$upstream_remote" ]; then
  say "ERROR: no git remote points at $UPSTREAM_REPO_MATCH."
  say "       Run: git remote -v  to see current remotes. Add one with:"
  say "       git remote add upstream https://github.com/$UPSTREAM_REPO_MATCH.git"
  exit 2
fi

say "OK: upstream remote detected as '$upstream_remote'"

# ─────────────────────────────────────────────────────────────
# Step 1: Dirty tree check
# ─────────────────────────────────────────────────────────────
dirty=0
if ! git diff --quiet;           then dirty=1; fi
if ! git diff --cached --quiet;  then dirty=1; fi
untracked="$(git ls-files --others --exclude-standard)"
[ -n "$untracked" ] && dirty=1

if [ "$dirty" = "1" ]; then
  say "WARN: uncommitted changes in working tree."
  git status --short | sed 's/^/       /'
  case "$MODE" in
    stash)
      if [ "$DRY_RUN" = "1" ]; then
        say "OK: (dry-run) would: git stash push -u -m 'update-skill auto-stash'"
      else
        if ! git stash push -u -m "update-skill auto-stash" >/dev/null; then
          say "ERROR: git stash failed; aborting."
          exit 1
        fi
        say "OK: stashed local changes (will pop after pull)."
        STASHED=1
      fi
      ;;
    abort)
      say "ERROR: refusing to update with uncommitted changes."
      say "       Choose: commit them, stash them (git stash), or rerun with --stash."
      exit 1
      ;;
    ask)
      # Interactive terminal -- prompt
      say "Choose: (s)tash and continue, (c)ancel, (f)orce pull without touching them"
      printf "       > "
      read -r reply || reply=""
      case "${reply:-c}" in
        s|S)
          if ! git stash push -u -m "update-skill auto-stash" >/dev/null; then
            say "ERROR: git stash failed; aborting."
            exit 1
          fi
          say "OK: stashed local changes (will pop after pull)."
          STASHED=1
          ;;
        f|F)
          say "WARN: proceeding without stash (may cause merge conflicts on pull)."
          ;;
        *)
          say "OK: cancelled. No changes made."
          exit 0
          ;;
      esac
      ;;
  esac
fi

# ─────────────────────────────────────────────────────────────
# Step 2: Fetch
# ─────────────────────────────────────────────────────────────
if [ "$DRY_RUN" = "1" ]; then
  say "OK: (dry-run) would: git fetch $upstream_remote"
else
  if ! git fetch "$upstream_remote" "$MAIN_BRANCH" 2>/tmp/update-fetch-err; then
    say "ERROR: git fetch failed. See /tmp/update-fetch-err:"
    sed 's/^/       /' /tmp/update-fetch-err
    exit 2
  fi
  say "OK: fetched $upstream_remote/$MAIN_BRANCH"
fi

# ─────────────────────────────────────────────────────────────
# Step 3: Figure out what's incoming
# ─────────────────────────────────────────────────────────────
base_ref="$upstream_remote/$MAIN_BRANCH"
local_ref="$MAIN_BRANCH"

# Make sure local master exists (some teammates might be on a feature branch
# and not have a local master at all -- git checkout master would then pull
# from the remote automatically, but we want an explicit step).
if ! git show-ref --verify --quiet "refs/heads/$MAIN_BRANCH"; then
  say "WARN: no local '$MAIN_BRANCH' branch; creating from $base_ref"
  [ "$DRY_RUN" = "1" ] || git branch "$MAIN_BRANCH" "$base_ref"
fi

new_commits="$(git log --oneline "$local_ref..$base_ref" 2>/dev/null | wc -l | tr -d ' ')"
ahead="$(git rev-list --count "$base_ref..$local_ref" 2>/dev/null || echo 0)"

if [ "$new_commits" = "0" ] && [ "$ahead" = "0" ]; then
  say "OK: $MAIN_BRANCH is already up to date with $base_ref."
  say "READY:"
  # pop stash if we made one
  if [ "${STASHED:-0}" = "1" ] && [ "$DRY_RUN" = "0" ]; then
    git stash pop >/dev/null 2>&1 && say "OK: restored stashed changes."
  fi
  exit 0
fi

if [ "$ahead" != "0" ] && [ "$new_commits" != "0" ]; then
  say "ERROR: local $MAIN_BRANCH has $ahead commit(s) that aren't on $base_ref,"
  say "       and $base_ref has $new_commits new commit(s) not local."
  say "       This is a diverged branch; refusing to fast-forward."
  say "       Either push your local commits as a PR, or rebase them onto $base_ref manually."
  exit 3
fi

# ─────────────────────────────────────────────────────────────
# Step 4: Fast-forward
# ─────────────────────────────────────────────────────────────
say "OK: $new_commits new commit(s) on $base_ref to fast-forward:"
git log --oneline "$local_ref..$base_ref" | sed 's/^/       /'

# Collect list of changed files so we can flag post-pull work
changed_files="$(git diff --name-only "$local_ref..$base_ref")"

if [ "$DRY_RUN" = "1" ]; then
  say "OK: (dry-run) would fast-forward $MAIN_BRANCH to $base_ref"
else
  current_branch="$(git rev-parse --abbrev-ref HEAD)"
  if [ "$current_branch" = "$MAIN_BRANCH" ]; then
    if ! git merge --ff-only "$base_ref" >/dev/null 2>&1; then
      say "ERROR: fast-forward merge failed (branch diverged?). Aborting."
      exit 3
    fi
  else
    # Fast-forward master without switching to it
    if ! git fetch . "$base_ref:$MAIN_BRANCH" >/dev/null 2>&1; then
      say "ERROR: could not update local $MAIN_BRANCH without checkout."
      say "       Run: git checkout $MAIN_BRANCH && git pull"
      exit 3
    fi
  fi
  say "OK: $MAIN_BRANCH fast-forwarded to $base_ref"
fi

# ─────────────────────────────────────────────────────────────
# Step 5: Post-pull recommendations
# ─────────────────────────────────────────────────────────────
followups=""
flag() {
  followups="$followups\n$1"
}

# .mcp.json rebuild -- any MCP-related code or deps changed
if echo "$changed_files" | grep -qE "^(mcp/|setup\.py$|\.mcp\.json$)"; then
  flag "python setup.py            # regenerate .mcp.json with fresh paths for this machine"
fi

# tact package
if echo "$changed_files" | grep -qE "^tools/tact/setup\.py$"; then
  flag "pip install -e tools/tact  # tact package metadata changed"
fi

# tasc package
if echo "$changed_files" | grep -qE "^tools/tasc/(setup\.py|pyproject\.toml)$"; then
  flag "pip install -e tools/tasc  # tasc package metadata changed"
fi

# webui
if echo "$changed_files" | grep -qE "^tools/webui/package\.json$"; then
  flag "cd tools/webui && bun install   # webui deps changed"
fi

# Rhino-side code (watcher, laser-export, startup, etc.)
if echo "$changed_files" | grep -qE "^tools/rhino/"; then
  flag "Rhino watcher / startup code changed: restart Rhino to pick up changes"
fi

# MCP tool renames
if echo "$changed_files" | grep -qE "^mcp/mcp_server\.py$"; then
  flag "MCP tools may have been renamed. Re-approve them in Claude Code on next use."
fi

if [ -n "$followups" ]; then
  say ""
  say "OK: post-pull steps recommended:"
  printf '%b\n' "$followups" | sed 's/^/       /'
fi

# ─────────────────────────────────────────────────────────────
# Step 6: Pop stash if we created one
# ─────────────────────────────────────────────────────────────
if [ "${STASHED:-0}" = "1" ] && [ "$DRY_RUN" = "0" ]; then
  if git stash pop >/dev/null 2>&1; then
    say "OK: restored stashed changes."
  else
    say "WARN: git stash pop had conflicts. Your stash is still saved --"
    say "       run 'git stash list' to find it and 'git stash pop' manually."
  fi
fi

say "READY:"
exit 0
