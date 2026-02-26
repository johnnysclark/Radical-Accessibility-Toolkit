# Claude Code Best Practices and Keyboard Shortcuts

A practical reference for running Claude Code effectively, with emphasis on screen-reader-friendly workflows. Written for the Radical Accessibility Project at UIUC.

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

Slash commands:

- /help: Show help
- /clear: New conversation
- /compact: Compress context
- /plan: Enter plan mode
- /model: Change model
- /resume: Resume old session
- /copy: Copy last response
- /cost: Show token usage
- /exit: Quit
