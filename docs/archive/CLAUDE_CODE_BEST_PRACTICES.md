# Claude Code Best Practices and Keyboard Shortcuts

A practical reference for running Claude Code effectively, with emphasis on screen-reader-friendly workflows. Written for the Radical Accessibility Project at UIUC.

---

## Table of Contents

1. [Before You Start](#before-you-start)
2. [Essential Keyboard Shortcuts](#essential-keyboard-shortcuts)
3. [Slash Commands](#slash-commands)
4. [Permission Modes](#permission-modes)
5. [Running Shell Commands Directly](#running-shell-commands-directly)
6. [File References](#file-references)
7. [Session Management](#session-management)
8. [Headless Mode (Non-Interactive)](#headless-mode-non-interactive)
9. [Context Window Management](#context-window-management)
10. [Best Practices for Productive Sessions](#best-practices-for-productive-sessions)
11. [Screen Reader Specific Tips](#screen-reader-specific-tips)
12. [Memory System](#memory-system)
13. [Switching Models](#switching-models)
14. [Subagents and Background Tasks](#subagents-and-background-tasks)
15. [Setting Up Custom Agents](#setting-up-custom-agents)
16. [Remote Control](#remote-control)
17. [Quick Reference Card](#quick-reference-card)

---

## Before You Start

Claude Code is an interactive terminal agent. You type prompts in natural language, and it reads, writes, and runs code on your behalf. It works entirely through text in a terminal window.

Prerequisites:
- Claude Code installed (via npm: `npm install -g @anthropic-ai/claude-code`)
- An Anthropic API key or a Claude subscription
- A terminal: cmd.exe recommended for screen reader users, Git Bash also works

Launch Claude Code by typing `claude` at the command prompt.

---

## Essential Keyboard Shortcuts

These are the shortcuts you will use constantly. Learn these first.

### Submitting and Canceling

- Enter: Submit your prompt to Claude.
- Escape: Cancel current input (clears what you have typed).
- Ctrl+C: Interrupt Claude while it is generating a response or running a tool. This is the emergency stop.
- Ctrl+D: Exit Claude Code entirely.

### Multi-Line Input

Sometimes you need to type a prompt that spans multiple lines:

- Backslash then Enter: Type `\` at the end of a line, then press Enter. This continues your input on the next line. Works in all terminals.
- Ctrl+J: Inserts a line break without submitting.
- Paste: Paste a multi-line block directly. Claude Code handles it as a single prompt.

When you are done with multi-line input, press Enter on an empty line to submit.

### Command History

- Up Arrow: Recall the previous prompt you typed.
- Down Arrow: Move forward through prompt history.
- Ctrl+R: Search through your prompt history. Type a few characters and it finds matching previous prompts. Press Ctrl+R again to cycle through matches. Press Enter to use the match, or Escape to cancel.

### Text Editing

- Ctrl+K: Delete from the cursor to the end of the line.
- Ctrl+U: Delete the entire line.
- Ctrl+Y: Paste back text you deleted with Ctrl+K or Ctrl+U.

---

## Slash Commands

Type these at the prompt. They start with a forward slash.

### Commands You Will Use Often

- /help: Show all available commands and shortcuts.
- /clear: Clear the conversation history and start fresh.
- /compact: Compress the conversation to free up context space. Use this when Claude starts forgetting earlier parts of a long session. You can add focus instructions: `/compact focus on the watcher code`.
- /cost: Show how many tokens you have used this session.
- /model: Change which Claude model you are using. Use arrow keys to select.
- /exit: Quit Claude Code. Same as Ctrl+D.

### Commands for Project Work

- /init: Create a CLAUDE.md file for your project. This file tells Claude about your codebase conventions.
- /memory: Edit your project's CLAUDE.md memory files directly.
- /resume: Resume a previous conversation. Without arguments, shows a picker. With a name or ID, resumes directly: `/resume my-session`.
- /plan: Enter plan mode. Claude will analyze code and propose a plan before making changes. Useful for reviewing what Claude intends to do before it touches files.

### Commands for Configuration

- /config: Open the settings interface.
- /status: Show version, model, account, and connectivity information.
- /permissions: View or change which tools Claude can use without asking.
- /doctor: Run a health check on your Claude Code installation.
- /vim: Toggle vim-style text editing mode.
- /fast: Toggle fast output mode. Same model, faster responses.

### Commands for Output

- /copy: Copy Claude's last response to the clipboard. Shows a picker if there were multiple code blocks.
- /export: Save the entire conversation to a file.
- /context: Show how much of the context window is being used.

---

## Permission Modes

Claude asks for permission before running tools (reading files, executing commands, editing code). You can control how strict this is.

### Switching Modes

Press Shift+Tab (or Alt+M on Windows) to cycle through three modes:

1. Normal Mode (default): Claude asks permission for each tool use. You press Y or Enter to approve, N or Escape to reject.
2. Plan Mode: Claude analyzes and plans but does not execute anything. It shows you what it would do and waits for approval.
3. Auto-Accept Mode: Claude runs tools without asking. Use this when you trust the task and want speed. Be cautious with this on unfamiliar code.

### Responding to Permission Prompts

When Claude asks to use a tool:
- Y or Enter: Approve this one action.
- N or Escape: Reject this action.
- Up and Down arrows: Navigate between options if there are multiple choices.

### Pre-Approving Tools

To skip permission prompts for specific tools, launch with the `--allowedTools` flag:

```
claude --allowedTools "Read" "Glob" "Grep" "Bash(git *)"
```

This lets Claude read files and run git commands without asking each time. You can also set this permanently in your settings.

---

## Running Shell Commands Directly

Prefix a command with `!` to run it in the shell without Claude interpreting it:

```
! git status
! python controller_cli.py --help
! ls layout-jig/
```

The command output is added to the conversation, so Claude can see the result and respond to it.

---

## File References

Type `@` to trigger file path autocomplete. This lets you point Claude at a specific file:

```
@layout-jig/controller_cli.py can you explain the undo stack in this file?
```

---

## Session Management

### Continuing a Session

If you close Claude Code and want to pick up where you left off:

```
claude -c
```

This continues the most recent session in your current directory.

### Resuming by Name

```
claude -r "my-session-name" "what was I working on?"
```

Or interactively inside Claude Code:

```
/resume
```

### Naming a Session

```
/rename watcher-refactor
```

This makes it easier to find later with `/resume`.

---

## Headless Mode (Non-Interactive)

For scripted or one-shot tasks where you do not need a conversation:

```
claude -p "list all python files in this folder" --output-format text
```

The `-p` flag runs Claude non-interactively. It processes the prompt and exits. The `--output-format text` flag produces plain text without streaming, spinners, or interactive elements.

This is the best mode for screen reader users doing quick tasks.

For structured output:

```
claude -p "describe the state schema" --output-format json
```

---

## Context Window Management

Claude has a finite context window. Long sessions fill it up. When context runs low, Claude may forget earlier parts of the conversation.

### Signs You Are Running Low

- Claude starts asking questions you already answered.
- Claude forgets files it read earlier.
- The `/context` command shows high usage.

### What To Do

- `/compact`: Compress the conversation. Claude summarizes what happened and frees space. Add focus instructions to preserve what matters: `/compact keep the watcher architecture details`.
- `/clear`: Start a completely fresh conversation. Use when the old context is no longer relevant.
- Break large tasks into smaller sessions. Do one thing, finish it, start a new session for the next thing.

---

## Best Practices for Productive Sessions

### Give Clear, Specific Prompts

Bad: "fix the bug"
Good: "The corridor command in controller_cli.py crashes when bay name is lowercase. Fix the case comparison in the corridor handler."

Include file names, function names, error messages, and expected behavior. The more specific you are, the fewer round trips Claude needs.

### Read Before You Edit

Always ask Claude to read a file before editing it:

```
Read controller_cli.py and then fix the corridor width validation.
```

Claude performs better when it has seen the current code rather than guessing from memory.

### Use Plan Mode for Big Changes

For changes that touch multiple files or involve architectural decisions:

```
/plan
```

Then describe what you want. Claude will analyze the codebase and propose a plan. Review it. Approve it. Then Claude executes.

This prevents Claude from charging ahead with an approach you would have rejected.

### Commit Frequently

Ask Claude to commit after completing each logical change:

```
Commit these changes with a descriptive message.
```

Small, frequent commits mean you can always roll back if something goes wrong.

### Use the Undo Shortcut

Press Escape twice to open the rewind dialog. This lets you roll back both the conversation and any code changes to a previous point. Use this when Claude went down a wrong path.

### Keep Sessions Focused

One task per session works better than cramming everything into one long conversation. If you finish refactoring the watcher and now want to add a new CLI command, start a new session.

---

## Screen Reader Specific Tips

### Disable Animations

Create or edit `%USERPROFILE%\.claude\settings.json`:

```json
{
  "preferences": {
    "prefersReducedMotion": true,
    "terminalProgressBarEnabled": false,
    "spinnerTipsEnabled": false
  }
}
```

This eliminates spinners, progress bars, and animated text that create noise for screen readers.

### Disable Terminal Title Changes

```
set CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
claude
```

Prevents the window title from updating, which some screen readers announce as interruptions.

### Use cmd.exe

Run Claude Code in cmd.exe, not Windows Terminal. cmd.exe produces cleaner text output for JAWS and NVDA. If using NVDA, install the Console Toolkit add-on from the NVDA Add-ons Store.

### Prefer Headless Mode for Quick Tasks

```
claude -p "what does the set command do in controller_cli.py?" --output-format text
```

Headless mode produces a single block of text with no streaming, no prompts, no interactive elements. This is the cleanest output for screen readers.

### Reviewing Long Output

After Claude responds, use your screen reader's review cursor to navigate:
- NVDA: Numpad 7 (top of screen), Numpad 8 (current line), Numpad 9 (bottom). Arrow keys to move line by line.
- JAWS: Insert+Up Arrow (read current line), Insert+Page Down (read from cursor to bottom).

---

## Memory System

Claude Code has a memory system that persists instructions and context across sessions. When you start a new session, Claude reads your memory files and knows your project conventions, preferences, and architecture without being told again.

### The CLAUDE.md File

The core of the memory system is a file called CLAUDE.md. This is a plain text markdown file that you place in your project root. Claude reads it at the start of every session. Think of it as a permanent instruction sheet.

To create one for your project:

```
/init
```

This creates a CLAUDE.md file with a starter template. Edit it to describe your project. Good things to put in CLAUDE.md:

- Build and test commands (how to run the project, how to run tests)
- Code style rules (naming conventions, indentation, import ordering)
- Architecture notes (what the key files are, how modules connect)
- Things Claude should never do (never delete the state file, never use f-strings in IronPython)
- Preferred workflow (always read a file before editing it, always run tests after changes)

### Memory Hierarchy

Claude Code checks multiple locations for instructions, from broadest to most specific. More specific files override broader ones:

1. User memory at `~/.claude/CLAUDE.md`: Your personal preferences that apply to every project. Example: "Always use 2-space indentation. Never add comments unless I ask."
2. User rules at `~/.claude/rules/*.md`: Topic-specific personal rules. You can have separate files like `code-style.md`, `testing.md`, `security.md`.
3. Project memory at `./CLAUDE.md` or `./.claude/CLAUDE.md`: Team-shared project instructions. Checked into git so everyone on the team gets the same rules.
4. Project rules at `./.claude/rules/*.md`: Modular project rules organized by topic.
5. Project local memory at `./CLAUDE.local.md`: Your personal overrides for this project only. Automatically added to .gitignore so it stays private.

### Auto Memory

Claude also maintains automatic memory at `~/.claude/projects/<project-hash>/memory/`. This is where Claude saves things it learns during your sessions, such as patterns it noticed, debugging solutions, or architectural details.

The auto memory directory contains:

- MEMORY.md: A concise index file. The first 200 lines load automatically at the start of every session. Keep it short.
- Topic files like debugging.md, patterns.md, api-conventions.md: Detailed notes that Claude reads on demand when relevant.

To view and edit your memory files:

```
/memory
```

This shows a picker of all memory files. Select one to edit, or toggle auto memory on and off.

### Telling Claude to Remember Something

You can explicitly ask Claude to remember something across sessions:

```
Remember that we always use os.path instead of pathlib in this project.
Remember that Daniel prefers corridor widths in whole numbers.
Always run tests in the layout-jig folder after changing the controller.
```

Claude writes these to your auto memory files. They persist across sessions.

To make Claude forget something:

```
Stop remembering the rule about corridor widths.
```

Claude will find and remove the relevant entry from the memory files.

### Importing Other Files

CLAUDE.md files can reference other files using the @ syntax:

```
@README.md
@docs/architecture.md
```

The first time you use imports in a project, Claude asks for a one-time approval. After that, imported files are pulled in automatically.

### Best Practices for Memory

- Keep MEMORY.md under 200 lines. Only the first 200 lines load automatically.
- Put detailed notes in separate topic files and reference them from MEMORY.md.
- Review your memory files periodically. Remove outdated entries.
- Use project CLAUDE.md for team conventions. Use CLAUDE.local.md for your personal setup.
- Be specific. "Use snake_case for JSON keys" is better than "format code properly."

---

## Switching Models

Claude Code can run different AI models. Each model has different strengths in speed, cost, and reasoning depth.

### Available Models

- Opus: The most capable model. Best for complex reasoning, architectural decisions, multi-file refactoring, and tasks that require deep understanding. Slower and more expensive.
- Sonnet: The balanced model. Good for everyday coding, file edits, bug fixes, and most tasks. Faster and cheaper than Opus.
- Haiku: The fast model. Good for simple tasks, quick lookups, and background work. Fastest and cheapest.

### How to Switch Models

There are four ways to switch.

Method 1, the /model command:

```
/model
```

This opens an interactive picker. Use Up and Down arrow keys to highlight a model. Press Enter to select it. The change takes effect immediately on the next response.

Method 2, the Alt+P shortcut:

Press Alt+P (Option+P on macOS) at any time. This opens the model picker without clearing whatever you have typed in the prompt. Navigate with arrow keys, select with Enter.

Method 3, at launch:

```
claude --model opus
claude --model sonnet
claude --model haiku
```

Method 4, set a permanent default in your settings file at `~/.claude/settings.json`:

```json
{
  "model": "opus"
}
```

### Effort Level (Opus Only)

When using Opus, you can adjust how much reasoning effort it applies. In the /model picker, when Opus is highlighted, use Left and Right arrow keys to adjust:

- Low effort: Faster, cheaper. Good for straightforward tasks.
- Medium effort: Balanced. Good for most work.
- High effort (default): Deepest reasoning. Good for complex problems.

You can also set this in settings:

```json
{
  "effortLevel": "medium"
}
```

Or as an environment variable:

```
set CLAUDE_CODE_EFFORT_LEVEL=medium
```

### Fast Mode

Fast mode makes Opus respond roughly 2.5 times faster at higher token cost. It does not switch to a different model. It is the same Opus with a speed configuration change.

Toggle it on or off:

```
/fast
```

When fast mode is on, a small lightning icon appears next to your prompt. Fast mode is best for interactive work where you are iterating quickly. Turn it off for long autonomous tasks where cost matters more than speed.

### Extended Thinking

Press Alt+T (Option+T on macOS) to toggle extended thinking mode. This lets Claude reason more deeply on complex problems before responding. Useful for architectural decisions, difficult bugs, or when you want Claude to really think through a problem.

### Checking Which Model You Are Using

```
/status
```

This shows your current model, account information, and connectivity status.

---

## Subagents and Background Tasks

Claude Code can run specialized agents in the background while you continue working in the main conversation. This lets you parallelize work: one agent researches the codebase while another runs tests while you continue talking to Claude in the foreground.

### What Subagents Are

Subagents are independent AI sessions that run inside your main Claude Code session. Each subagent gets its own context window and set of tools. When a subagent finishes, its results flow back to the main conversation.

Claude has several built-in subagent types:

- Explore: A fast, read-only agent for searching codebases. It can read files and search but cannot edit anything. Runs on the Haiku model for speed.
- Plan: A research agent that analyzes code and designs implementation plans. Read-only. Cannot make changes.
- General-purpose: A full-capability agent that can read, write, edit, and run commands. Used for complex multi-step tasks.

### How Subagents Get Used

Claude decides when to use subagents based on the task. If you ask Claude to search for something across the codebase, it may automatically launch an Explore subagent. If you ask it to plan a refactor, it may launch a Plan subagent.

You can also ask explicitly:

```
Search the codebase for all files that reference the corridor command. Use the Explore agent.
```

```
Plan how to add a new export command to the CLI. Use the Plan agent.
```

### Running Tasks in Parallel

To run multiple things at the same time, ask Claude directly:

```
In parallel, search for all uses of atomic_write and also find all JSON schema definitions.
```

```
Run these three things in parallel: search for corridor references, search for bay references, and search for void references.
```

Claude launches multiple subagents simultaneously. Each works independently. Results come back as they finish.

### Background Tasks

When Claude is working on something that takes a while, you can send it to the background:

Press Ctrl+B while a task is running. If you use tmux, press Ctrl+B twice (the first Ctrl+B is the tmux prefix).

You can also ask Claude to run something in the background from the start:

```
Run the test suite in the background and let me know when it finishes.
```

```
In the background, search the entire codebase for deprecated function calls.
```

While background tasks run, you can continue typing prompts and getting responses in the foreground. Claude notifies you when a background task completes.

### Managing Background Tasks

To see what is running in the background:

```
/tasks
```

Or press Ctrl+T to toggle the task list in the terminal status area.

The task list shows each background task with its status: pending, in progress, or complete.

To stop all background agents:

Press Ctrl+F twice (press it once, then again within 3 seconds to confirm).

### Practical Examples

Example 1, parallel research:

```
I need to understand how the state file works. In parallel:
1. Find all places that read state.json
2. Find all places that write to state.json
3. Find the schema definition
```

Claude launches three Explore agents simultaneously. Results come back within seconds.

Example 2, background test run:

```
Run the full test suite in the background. While that runs, let's work on the new describe command.
```

Claude starts the tests in the background. You continue working. When tests finish, Claude reports the results.

Example 3, background code review:

```
In the background, review the watcher code for any places where we delete objects we did not create. Meanwhile, let's add the new hatch pattern.
```

### Disabling Background Tasks

If background tasks cause issues, disable them:

```
set CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1
```

Set this environment variable before launching Claude Code.

---

## Setting Up Custom Agents

Beyond the built-in subagents (Explore, Plan, General-purpose), you can create your own agents tailored to specific tasks. Custom agents are defined as markdown files with a YAML header that specifies their name, tools, model, and behavior.

### Where Agent Files Live

Agent definitions are markdown files stored in an `agents` folder inside your `.claude` directory. There are two scopes:

Project agents at `.claude/agents/` in your project folder. These are specific to the project and can be checked into git so your team shares them.

User agents at `~/.claude/agents/` in your home folder. These are personal agents available in every project on your machine.

When a project agent and a user agent have the same name, the project agent takes priority.

### Creating an Agent with /agents

The easiest way to create an agent is interactively:

```
/agents
```

This shows a menu where you can:
- View all available agents (built-in, user-level, project-level)
- Create a new agent (choose user-level or project-level, then configure)
- Edit or delete existing custom agents

Select "Create new agent" and follow the prompts. You can choose "Generate with Claude" to describe what you want and let Claude write the configuration, or "Manually configure" to set each field yourself.

### Agent File Format

An agent file is a markdown file with YAML frontmatter at the top. The frontmatter configures the agent. The markdown body becomes the agent's system prompt, which tells it how to behave.

Here is the general structure:

```
---
name: agent-name
description: When Claude should use this agent
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a specialist in [domain]. When invoked:

1. First step
2. Second step
3. Third step

Focus on:
- Key concern A
- Key concern B
```

### Frontmatter Fields

Required fields:

- `name`: A unique identifier using lowercase letters and hyphens. Example: `code-reviewer`.
- `description`: Tells Claude when to delegate work to this agent. Be specific. Example: "Expert code reviewer. Use after writing or modifying code."

Optional fields:

- `tools`: Which tools the agent can use, as a comma-separated list. If omitted, the agent inherits all tools from the main conversation. Available tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, Task.
- `disallowedTools`: Tools to explicitly deny, even if they would be inherited.
- `model`: Which AI model the agent uses. Options: `opus`, `sonnet`, `haiku`, or `inherit` (same as main conversation, this is the default).
- `maxTurns`: Maximum number of turns before the agent stops. Useful for keeping agents focused.
- `permissionMode`: How the agent handles permission prompts. Options: `default` (ask for each), `acceptEdits` (auto-approve file edits), `plan` (read-only mode).
- `background`: Set to `true` to always run this agent as a background task.
- `memory`: Enable persistent memory across sessions. Options: `user` (all projects), `project` (this project, shared via git), `local` (this project, private).
- `skills`: A list of skill names to preload into the agent's context.

### Example: Read-Only Code Reviewer

Create this file at `.claude/agents/code-reviewer.md`:

```
---
name: code-reviewer
description: Reviews code for quality, security, and maintainability. Use after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a senior code reviewer. When invoked:

1. Run git diff to see recent changes.
2. Read the modified files.
3. Provide structured feedback.

Review checklist:
- Code clarity and readability
- Proper error handling
- No exposed secrets or API keys
- Input validation where needed
- Security vulnerabilities

Organize feedback by priority:
- Critical (must fix before merging)
- Warning (should fix)
- Suggestion (consider improving)

Include specific code examples showing how to fix each issue.
```

This agent can read files and run git commands but cannot write or edit files. It uses Sonnet for speed.

### Example: Debugger

Create this file at `.claude/agents/debugger.md`:

```
---
name: debugger
description: Investigates errors, test failures, and unexpected behavior. Use when encountering bugs or crashes.
tools: Read, Edit, Bash, Grep, Glob
model: inherit
---

You are an expert debugger. When invoked:

1. Capture the error message and stack trace.
2. Identify the file and line where the failure occurs.
3. Read the surrounding code for context.
4. Form a hypothesis about the root cause.
5. Implement a minimal fix.
6. Verify the fix works.

For each issue provide:
- Root cause explanation
- The specific code fix
- How to verify it works
- How to prevent similar issues
```

This agent can edit files to apply fixes.

### Example: Accessibility Checker

Create this file at `.claude/agents/accessibility-checker.md`:

```
---
name: accessibility-checker
description: Verifies CLI output is screen-reader friendly. Use after adding or changing any user-facing output.
tools: Read, Grep, Glob
model: haiku
---

You are an accessibility auditor for CLI tools used by blind and low-vision users with screen readers.

When invoked, check all user-facing output for:

1. Every response starts with OK: or ERROR: prefix.
2. No tables, no multi-column layouts, no box-drawing characters.
3. No ASCII art or decorative separators.
4. Output is under 20 lines where possible.
5. Error messages include what failed, why, and how to fix.
6. All options are numbered when asking questions.
7. No color-only indicators (information must be in the text).
8. READY: printed after completing a command.

Report each violation with the file, line number, and the specific text that needs to change.
```

This agent is read-only and runs on Haiku for speed since it only needs to scan text.

### Invoking Custom Agents

Claude automatically delegates to your custom agents when it recognizes a matching task from the agent's description. You can also invoke them explicitly:

```
Use the code-reviewer agent to check my latest changes.
```

```
Have the debugger investigate why the corridor command crashes.
```

```
Run the accessibility-checker on the controller CLI output.
```

### Agent Memory

Agents can remember things across sessions if you enable the `memory` field:

```
---
name: code-reviewer
description: Reviews code for quality
tools: Read, Grep, Glob, Bash
memory: project
---
```

With `memory: project`, the agent saves learnings to `.claude/agent-memory/code-reviewer/`. It remembers patterns, recurring issues, and conventions it has discovered. This memory persists between sessions.

Memory scope options:

- `user`: Remembered across all projects. Stored at `~/.claude/agent-memory/`.
- `project`: Remembered for this project, shared with team via git. Stored at `.claude/agent-memory/`.
- `local`: Remembered for this project, private to you. Stored at `.claude/agent-memory-local/`.

### Sharing Agents with Your Team

Project agents live in `.claude/agents/` and can be checked into git:

```
git add .claude/agents/
git commit -m "Add code-reviewer and accessibility-checker agents"
git push
```

When teammates clone the repo, they automatically have access to the same agents.

### Restricting Agent Tools for Safety

To create a read-only agent, only list read tools:

```
tools: Read, Grep, Glob
```

To create an agent that can run commands but not modify files:

```
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit
```

To create an agent that can only run specific shell commands, use hooks. Define a `PreToolUse` hook in the agent frontmatter that validates commands before execution:

```
---
name: db-reader
description: Runs read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly.sh"
---
```

The validation script receives the command as JSON on stdin. Exit code 0 allows it, exit code 2 blocks it.

### Defining Agents at Launch

For temporary agents you do not want saved to disk, define them when launching Claude Code:

```
claude --agents "{\"reviewer\": {\"description\": \"Code reviewer\", \"prompt\": \"You are a code reviewer.\", \"tools\": [\"Read\", \"Grep\", \"Glob\"], \"model\": \"sonnet\"}}"
```

These agents exist only for the current session.

### Listing All Available Agents

From the terminal without starting a session:

```
claude agents
```

From inside a session:

```
/agents
```

Both show all available agents grouped by source: built-in, user-level, project-level, and plugin-provided.

---

## Remote Control

Remote Control lets you continue a local Claude Code session from your phone, tablet, or any web browser. Claude keeps running on your machine — nothing moves to the cloud. The web or mobile interface is just a window into the local session.

This is useful when you start a task at your desk and want to monitor or continue it from the couch, from another room, or from your phone while away from the computer. Your local filesystem, MCP servers, tools, and project configuration all stay available because the session is still running locally.

### Requirements

- A Max subscription plan (Pro plan support coming soon). API keys are not supported.
- You must be signed in. Run `claude` and use `/login` if you have not signed in yet.
- You must have run `claude` in your project directory at least once to accept the workspace trust dialog.

### Starting a New Remote Session

Navigate to your project folder and run:

```
claude remote-control
```

The terminal displays a session URL and stays running, waiting for remote connections. Press Spacebar to show a QR code you can scan with your phone.

Optional flags:

- `--verbose`: Show detailed connection and session logs.
- `--sandbox`: Enable filesystem and network sandboxing for the session.
- `--no-sandbox`: Explicitly disable sandboxing (this is the default).

### Starting Remote Control from an Existing Session

If you are already in a Claude Code session and want to make it remotely accessible:

```
/remote-control
```

Or the shorter alias:

```
/rc
```

This carries over your current conversation history and displays the session URL and QR code. Tip: use `/rename` before `/remote-control` to give the session a descriptive name that is easy to find on other devices.

### Connecting from Another Device

Once a remote session is active, connect from another device using any of these methods:

1. Open the session URL in any browser. The URL is displayed in the terminal when you start remote control.
2. Scan the QR code with your phone to open it in the Claude mobile app.
3. Open claude.ai/code or the Claude app and find the session by name in the session list. Remote sessions show a computer icon with a green dot when online.

The Claude app is available for iOS and Android. Inside Claude Code, run `/mobile` to get a download QR code.

### Working from Multiple Devices at Once

The conversation stays in sync across all connected devices. You can send messages from your terminal, your browser, and your phone interchangeably. This means a sighted collaborator can watch the session on a large screen while Daniel operates it from the terminal with a screen reader.

### Keeping Sessions Alive

- The terminal must stay open. If you close the terminal or stop the process, the session ends.
- If your laptop sleeps or your network drops, the session reconnects automatically when your machine comes back online.
- If your machine cannot reach the network for roughly 10 minutes, the session times out and the process exits. Run `claude remote-control` again to start a new one.

### Enabling Remote Control for All Sessions

By default, remote control only activates when you explicitly run it. To enable it automatically for every session:

1. Run `/config` inside Claude Code.
2. Set "Enable Remote Control for all sessions" to true.

Set it back to false to disable automatic remote control.

### Security

Remote control uses outbound HTTPS only. It never opens inbound ports on your machine. All traffic goes through the Anthropic API over TLS. The connection uses short-lived credentials scoped to a single purpose.

### Remote Control vs Claude Code on the Web

Both use the claude.ai/code interface, but they are different:

- Remote Control runs on your machine. Your local files, MCP servers, and configuration stay available. Use this when you are in the middle of local work and want to continue from another device.
- Claude Code on the Web runs on Anthropic cloud infrastructure. Use this when you want to work on a repo you have not cloned locally, or to run multiple tasks in parallel without tying up your machine.

---

## Quick Reference Card

Shortcut, what it does:

- Enter: Submit prompt
- Escape: Cancel input
- Ctrl+C: Stop Claude mid-response
- Ctrl+D: Exit Claude Code
- Up Arrow: Previous prompt from history
- Down Arrow: Next prompt from history
- Ctrl+R: Search prompt history
- Backslash then Enter: Continue typing on next line
- Shift+Tab: Cycle permission mode (Normal, Plan, Auto-Accept)
- Escape Escape: Rewind conversation and code
- Ctrl+L: Clear the terminal screen
- Y or Enter: Approve a tool use
- N or Escape: Reject a tool use
- ! command: Run a shell command directly
- Alt+P: Open model picker
- Alt+T: Toggle extended thinking
- Ctrl+B: Send current task to background
- Ctrl+T: Toggle task list
- Ctrl+F Ctrl+F: Kill all background agents

Slash commands:

- /help: Show help
- /clear: New conversation
- /compact: Compress context
- /plan: Enter plan mode
- /model: Change model
- /fast: Toggle fast mode
- /memory: Edit memory files
- /init: Create CLAUDE.md for project
- /tasks: List background tasks
- /resume: Resume old session
- /copy: Copy last response
- /cost: Show token usage
- /agents: List, create, or edit custom agents
- /remote-control (or /rc): Start remote control from current session
- /status: Show current model and account info
- /exit: Quit

Terminal commands:

- claude remote-control: Start a new remote-accessible session
- claude -c: Continue most recent session
- claude -r "name": Resume a named session
