// memory-store.ts — Persist session IDs and preferences as plain JSON files
// Storage: ~/.radical-accessibility/memory/

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "fs"
import { join } from "path"
import { homedir } from "os"

const MEMORY_DIR = join(homedir(), ".radical-accessibility", "memory")
const PREFS_FILE = join(MEMORY_DIR, "prefs.json")
const SESSIONS_FILE = join(MEMORY_DIR, "sessions.json")

// How long before a session is considered stale (2 hours)
const SESSION_TIMEOUT_MS = 2 * 60 * 60 * 1000

interface Prefs {
  lastSessionId: string | null
  lastTimestamp: number
}

interface SessionRecord {
  sessionId: string
  startedAt: number
  endedAt: number
  promptCount: number
  firstPrompt: string
}

function ensureDir(): void {
  if (!existsSync(MEMORY_DIR)) {
    mkdirSync(MEMORY_DIR, { recursive: true })
  }
}

function readJson<T>(path: string, fallback: T): T {
  try {
    if (!existsSync(path)) return fallback
    return JSON.parse(readFileSync(path, "utf8"))
  } catch {
    return fallback
  }
}

function writeJson(path: string, data: unknown): void {
  ensureDir()
  writeFileSync(path, JSON.stringify(data, null, 2), "utf8")
}

export class MemoryStore {
  private prefs: Prefs
  private sessions: SessionRecord[]
  private currentPromptCount = 0
  private currentFirstPrompt = ""
  private sessionStartTime = Date.now()

  constructor() {
    ensureDir()
    this.prefs = readJson<Prefs>(PREFS_FILE, {
      lastSessionId: null,
      lastTimestamp: 0,
    })
    this.sessions = readJson<SessionRecord[]>(SESSIONS_FILE, [])
  }

  // Returns recent session ID if within timeout window, else null
  getRecentSessionId(): string | null {
    if (!this.prefs.lastSessionId) return null
    const age = Date.now() - this.prefs.lastTimestamp
    if (age > SESSION_TIMEOUT_MS) return null
    return this.prefs.lastSessionId
  }

  // Save session ID after each successful turn
  saveSessionId(sessionId: string): void {
    this.prefs.lastSessionId = sessionId
    this.prefs.lastTimestamp = Date.now()
    writeJson(PREFS_FILE, this.prefs)
  }

  // Track prompts for session record
  trackPrompt(prompt: string): void {
    this.currentPromptCount++
    if (this.currentPromptCount === 1) {
      this.currentFirstPrompt = prompt.substring(0, 100)
    }
  }

  // Save session record on quit
  saveSessionRecord(): void {
    if (!this.prefs.lastSessionId || this.currentPromptCount === 0) return
    this.sessions.push({
      sessionId: this.prefs.lastSessionId,
      startedAt: this.sessionStartTime,
      endedAt: Date.now(),
      promptCount: this.currentPromptCount,
      firstPrompt: this.currentFirstPrompt,
    })
    // Keep last 50 sessions
    if (this.sessions.length > 50) {
      this.sessions = this.sessions.slice(-50)
    }
    writeJson(SESSIONS_FILE, this.sessions)
  }

  // Clear session to force a fresh start
  clearSession(): void {
    this.prefs.lastSessionId = null
    this.prefs.lastTimestamp = 0
    writeJson(PREFS_FILE, this.prefs)
  }
}
