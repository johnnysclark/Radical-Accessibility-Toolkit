# Claude Code Screen Reader Setup Guide

How to configure Claude Code for use with JAWS, NVDA, or other screen readers. Written for blind and low-vision users who interact with the terminal via speech output and braille displays.

---

## Quick Start

1. Open cmd.exe (not Windows Terminal).
2. Install the NVDA Console Toolkit add-on (if using NVDA).
3. Create a settings file to disable animations (see Step 2 below).
4. Run Claude Code.

---

## Step 1: Choose the Right Terminal

Use **cmd.exe**. Open it from the Start menu or press Win+R, type `cmd`, press Enter.

Do not use Windows Terminal, PowerShell ISE, or VS Code's integrated terminal for screen reader sessions. These terminals add visual layers (tabs, animations, split panes) that create noise for assistive technology. cmd.exe produces clean text output that screen readers handle reliably.

If you prefer Git Bash, it also works. Run it from cmd.exe:

```
"C:\Program Files\Git\bin\bash.exe"
```

---

## Step 2: Configure Claude Code Settings

Create or edit the file at `%USERPROFILE%\.claude\settings.json` with these settings:

```json
{
  "preferences": {
    "prefersReducedMotion": true,
    "terminalProgressBarEnabled": false,
    "spinnerTipsEnabled": false
  }
}
```

What each setting does:

- `prefersReducedMotion` disables spinners, shimmer effects, and all animations. Without this, the terminal fills with rapidly changing characters that screen readers announce continuously.
- `terminalProgressBarEnabled` set to false disables visual progress bars that produce meaningless output for screen readers.
- `spinnerTipsEnabled` set to false disables rotating tip text that appears while Claude is thinking. These tips change every few seconds and create speech interruptions.

To create this file from the command line:

```
mkdir "%USERPROFILE%\.claude" 2>NUL
notepad "%USERPROFILE%\.claude\settings.json"
```

Paste the JSON above, save, and close.

---

## Step 3: NVDA Console Toolkit Add-on

If you use NVDA, install the Console Toolkit add-on from the NVDA Add-ons Store:

1. Open NVDA menu (Insert+N).
2. Go to Tools, then Add-on Store.
3. Search for "Console Toolkit."
4. Install it and restart NVDA.

Console Toolkit improves how NVDA tracks and announces text changes in command-line windows. Without it, NVDA may miss output or announce it out of order.

---

## Step 4: JAWS Configuration

If you use JAWS, no special add-on is needed. JAWS handles cmd.exe output natively. Two tips:

- Set JAWS to use "Line" echo mode in the terminal (Insert+S to cycle speech modes) so it reads complete lines rather than individual characters.
- If output is long, use Insert+Page Down to read from the cursor to the bottom of the screen.

---

## Step 5: Headless Mode (Non-Interactive)

For scripted or one-shot tasks, use headless mode. This avoids the interactive UI entirely and produces clean, non-streaming text output:

```
claude -p "your prompt here" --output-format text
```

Flags:

- `-p` (or `--print`) runs Claude non-interactively: it processes the prompt and exits.
- `--output-format text` produces plain text with no streaming tokens, no spinners, no interactive elements.

Example:

```
claude -p "list all python files in this folder" --output-format text
```

For structured output that scripts can parse:

```
claude -p "your prompt" --output-format json
```

Do not use `--output-format stream-json` with a screen reader. It produces token-by-token streaming output that creates a flood of speech announcements.

---

## Step 6: Interactive Mode Tips

When running Claude Code interactively (just type `claude` at the prompt), these practices help:

**Reduce permission dialogs.** Each time Claude wants to run a tool, it asks for permission. You can pre-approve tools to reduce interruptions:

```
claude --allowedTools "Read,Glob,Grep,Bash(git *)"
```

This allows Claude to read files, search, and run git commands without asking each time.

**Wait for the prompt.** After Claude finishes a response, it prints a prompt character. Listen for silence, then the prompt, before typing your next input.

**Use paste for long prompts.** If your prompt is multiple sentences, type it in a text editor first, copy it, then paste into the terminal. This avoids partial input being misinterpreted.

**Review output in chunks.** If Claude produces a long response, use your screen reader's review cursor to navigate line by line (NVDA: Numpad 7/8/9 for top/current/bottom line review; JAWS: Insert+Up/Down).

---

## Step 7: Environment Variables

Optional environment variables that may help:

```
set CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
```

This prevents Claude Code from changing the terminal window title, which some screen readers announce as an interruption each time it updates.

Set this before running Claude:

```
set CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
claude
```

Or add it permanently via System Properties, Environment Variables.

---

## Step 8: Braille Display

If you use a braille display alongside speech:

- cmd.exe output maps directly to braille lines. Each printed line from Claude becomes one braille line.
- Headless mode (`-p --output-format text`) is especially clean for braille reading since there is no streaming or partial output.
- Set your braille display to "structured" or "line" mode rather than "character" mode for terminal use.

---

## Troubleshooting

**Problem: Screen reader announces rapid gibberish during Claude thinking.**
Fix: Ensure `prefersReducedMotion` is true in settings.json. This disables the spinner animation.

**Problem: Output appears but screen reader does not announce it.**
Fix: If using NVDA, install Console Toolkit add-on. If using JAWS, press Insert+Page Down to force a screen read.

**Problem: Permission dialogs interrupt workflow constantly.**
Fix: Use `--allowedTools` flag to pre-approve common tools. Or set permissions in `%USERPROFILE%\.claude\settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(git *)"
    ]
  }
}
```

**Problem: Claude produces tables or wide-format output.**
Fix: Add to your project's CLAUDE.md or system prompt: "Never use tables or multi-column layouts. Output one item per line with a label prefix."

**Problem: Windows Terminal launches instead of cmd.exe.**
Fix: Windows may default to Windows Terminal. To ensure cmd.exe opens, run it explicitly: Win+R, type `cmd.exe`, press Enter. Or set the default terminal in Windows Settings: System, For Developers, Terminal, set to Windows Console Host.

---

## Summary of Recommended Configuration

Terminal: cmd.exe
Screen reader: NVDA with Console Toolkit add-on, or JAWS
Headless usage: `claude -p "prompt" --output-format text`

Settings file at `%USERPROFILE%\.claude\settings.json`:

```json
{
  "preferences": {
    "prefersReducedMotion": true,
    "terminalProgressBarEnabled": false,
    "spinnerTipsEnabled": false
  }
}
```

Environment variable: `CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1`

These settings eliminate animations, spinners, progress bars, and title bar changes, leaving clean text output that screen readers handle reliably.
