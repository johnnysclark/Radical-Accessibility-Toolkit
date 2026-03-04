#!/usr/bin/env npx tsx
// acclaude.ts — Accessible Claude client for JAWS screen readers
//
// Wraps `claude -p` (headless mode) so Daniel can use Claude Code
// on his subscription without the Ink TUI that breaks JAWS.
//
// Each turn spawns: claude -p "MSG" --output-format json --session-id ID
// Terminal stays silent during processing. Response is cleaned and announced.

import { spawn, execSync } from "child_process"
import * as readline from "readline/promises"
import { cleanText } from "./text-cleaner"
import { announce } from "./announce-bridge"
import { MemoryStore } from "./memory-store"
import { resolve } from "path"

// --- Configuration ---

const PROJECT_DIR = resolve(__dirname, "../..")
const ALLOWED_TOOLS =
  "Read,Write,Edit,Glob,Grep,Bash,mcp__rhinomcp__*,mcp__tactile__*"

const SYSTEM_PROMPT =
  "You are helping Daniel, a blind architecture student using JAWS screen reader. " +
  "Output plain text only. No markdown. No emojis. No tables. " +
  "One fact per line. Short sentences. When done, say Done."

const TIMEOUT_MS = 120_000 // 2 minutes max per turn
const ANNOUNCE_TIMEOUT_MS = 60_000 // announce "still working" after 60s

// --- State ---

const memory = new MemoryStore()
let sessionId: string | null = memory.getRecentSessionId()
const history: Array<{ prompt: string; response: string }> = []
let lastResponse = ""

// --- Claude runner ---

interface ClaudeResult {
  type: string
  subtype: string
  session_id: string
  result: string
  cost_usd?: number
  is_error: boolean
  duration_ms?: number
  num_turns?: number
}

function runClaude(message: string): Promise<ClaudeResult> {
  return new Promise((resolve, reject) => {
    const args = [
      "-p",
      message,
      "--output-format",
      "json",
      "--allowedTools",
      ALLOWED_TOOLS,
      "--append-system-prompt",
      SYSTEM_PROMPT,
    ]
    if (sessionId) {
      args.push("--resume", sessionId)
    }

    // Strip CLAUDECODE env var so nested sessions are allowed
    const env = { ...process.env }
    delete env.CLAUDECODE

    const proc = spawn("claude", args, {
      cwd: PROJECT_DIR,
      stdio: ["pipe", "pipe", "pipe"],
      env,
    })

    let stdout = ""
    let stderr = ""

    proc.stdout.on("data", (chunk: Buffer) => {
      stdout += chunk.toString()
    })
    proc.stderr.on("data", (chunk: Buffer) => {
      stderr += chunk.toString()
    })

    const timer = setTimeout(() => {
      proc.kill("SIGTERM")
      reject(new Error("Claude timed out after 2 minutes."))
    }, TIMEOUT_MS)

    proc.on("close", (code) => {
      clearTimeout(timer)
      if (stdout.trim()) {
        try {
          resolve(JSON.parse(stdout.trim()))
        } catch {
          reject(
            new Error(
              "Failed to parse Claude response. Raw output: " +
                stdout.substring(0, 200)
            )
          )
        }
      } else if (stderr.trim()) {
        reject(new Error(stderr.trim().substring(0, 500)))
      } else {
        reject(new Error("Claude returned no output. Exit code: " + code))
      }
    })

    proc.on("error", (err) => {
      clearTimeout(timer)
      reject(new Error("Failed to start claude: " + err.message))
    })

    // Close stdin so claude doesn't wait for input
    proc.stdin.end()
  })
}

// --- Slash commands ---

function showHelp(): void {
  const lines = [
    "Commands:",
    "/help    Show this help",
    "/repeat  Re-read the last response",
    "/history Show prompts from this session",
    "/new     Start a fresh session",
    "/quit    Save and exit",
    "",
    "Type anything else to send it to Claude.",
  ]
  const text = lines.join("\n")
  process.stdout.write(text + "\n")
  announce("Help. " + lines.slice(0, 6).join(". "))
}

function repeatLast(): void {
  if (!lastResponse) {
    process.stdout.write("No previous response.\n")
    announce("No previous response.")
    return
  }
  process.stdout.write(lastResponse + "\n")
  announce(lastResponse.substring(0, 500))
}

function showHistory(): void {
  if (history.length === 0) {
    process.stdout.write("No prompts yet.\n")
    announce("No prompts yet.")
    return
  }
  const lines = history.map(
    (h, i) => (i + 1) + ". " + h.prompt.substring(0, 80)
  )
  const text = lines.join("\n")
  process.stdout.write(text + "\n")
  announce(history.length + " prompts this session.")
}

function startNewSession(): void {
  memory.clearSession()
  sessionId = null
  history.length = 0
  lastResponse = ""
  process.stdout.write("New session started.\n")
  announce("New session started.")
}

// --- Startup checks ---

function checkClaude(): boolean {
  try {
    execSync("which claude", { encoding: "utf8", stdio: "pipe" })
    return true
  } catch {
    return false
  }
}

// --- Main ---

async function main(): Promise<void> {
  // Verify claude is available
  if (!checkClaude()) {
    process.stdout.write(
      "Error: claude is not installed or not on PATH.\n" +
        "Install Claude Code first: https://docs.anthropic.com/en/docs/claude-code\n"
    )
    announce("Error. Claude is not installed.")
    process.exit(1)
  }

  // Create readline interface
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  })

  // Startup message
  const resumeMsg = sessionId ? " Resuming previous session." : ""
  process.stdout.write("Accessible Claude." + resumeMsg + " Type your message.\n")
  announce("Accessible Claude. Ready." + resumeMsg)

  // SIGINT handler
  let exiting = false
  process.on("SIGINT", () => {
    if (exiting) process.exit(0)
    exiting = true
    memory.saveSessionRecord()
    process.stdout.write("\nSession saved. Goodbye.\n")
    announce("Session saved. Goodbye.")
    setTimeout(() => process.exit(0), 1500)
  })

  // Main loop
  while (true) {
    let input: string
    try {
      input = await rl.question("> ")
    } catch {
      // EOF or readline closed
      break
    }

    const trimmed = input.trim()
    if (!trimmed) continue

    // Slash commands
    if (trimmed === "/quit" || trimmed === "/exit") {
      memory.saveSessionRecord()
      process.stdout.write("Session saved. Goodbye.\n")
      announce("Session saved. Goodbye.")
      break
    }
    if (trimmed === "/help") {
      showHelp()
      continue
    }
    if (trimmed === "/repeat") {
      repeatLast()
      continue
    }
    if (trimmed === "/history") {
      showHistory()
      continue
    }
    if (trimmed === "/new") {
      startNewSession()
      continue
    }

    // Send to Claude
    process.stdout.write("Thinking...\n")
    announce("Thinking.")
    memory.trackPrompt(trimmed)

    // "Still working" timer
    const stillWorking = setTimeout(() => {
      process.stdout.write("Still working...\n")
      announce("Still working.")
    }, ANNOUNCE_TIMEOUT_MS)

    try {
      const result = await runClaude(trimmed)
      clearTimeout(stillWorking)

      if (result.is_error) {
        const errText = "Error: " + cleanText(result.result)
        process.stdout.write(errText + "\n")
        announce(errText.substring(0, 500))
        lastResponse = errText
      } else {
        const cleaned = cleanText(result.result)
        process.stdout.write(cleaned + "\n")
        announce(cleaned.substring(0, 500))
        lastResponse = cleaned
        sessionId = result.session_id
        memory.saveSessionId(sessionId)
      }

      history.push({ prompt: trimmed, response: lastResponse })
    } catch (err: any) {
      clearTimeout(stillWorking)
      const errMsg = "Error: " + (err.message || String(err))
      process.stdout.write(errMsg + "\n")
      announce(errMsg.substring(0, 300))
      lastResponse = errMsg
      history.push({ prompt: trimmed, response: lastResponse })
    }
  }

  rl.close()
  process.exit(0)
}

main()
