// announce-bridge.ts — Announce text via JAWS/NVDA/SAPI using existing announce.ps1
// Calls PowerShell from WSL2, passing text on stdin

import { execFileSync } from "child_process"
import { existsSync } from "fs"
import { resolve } from "path"

const PROJECT_DIR = resolve(__dirname, "../..")
const PS1_PATH = resolve(PROJECT_DIR, "src/hooks/screen-reader/announce.ps1")

// Convert /mnt/DRIVE/... to DRIVE:\... without calling wslpath
function toWinPath(wslPath: string): string | null {
  const match = wslPath.match(/^\/mnt\/([a-z])\/(.*)$/)
  if (!match) return null
  const drive = match[1].toUpperCase()
  const rest = match[2].replace(/\//g, "\\")
  return drive + ":\\" + rest
}

let cachedWinPath: string | null | undefined

function getWinPath(): string | null {
  if (cachedWinPath !== undefined) return cachedWinPath
  if (!existsSync(PS1_PATH)) {
    cachedWinPath = null
    return null
  }
  cachedWinPath = toWinPath(PS1_PATH)
  return cachedWinPath
}

export function announce(text: string): void {
  if (!text?.trim()) return

  const trimmed = text.trim().substring(0, 800)
  const script = getWinPath()
  if (!script) return

  try {
    execFileSync(
      "powershell.exe",
      ["-ExecutionPolicy", "Bypass", "-File", script],
      {
        input: trimmed,
        encoding: "utf8",
        timeout: 10000,
        windowsHide: true,
        stdio: ["pipe", "pipe", "pipe"],
      }
    )
  } catch {
    // Non-fatal: JAWS may not be running, or we're not on Windows
  }
}
