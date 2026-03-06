#!/usr/bin/env node
// announce.js - Screen reader announcement bridge for Claude Code
// Works from both WSL2 and native Windows
// Handles: Stop (response finished), Notification (permission prompt), AskUserQuestion
//
// Usage: Receives hook JSON on stdin, extracts relevant text, pipes to announce.ps1

const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const os = require("os");

const MAX_LENGTH = 800;
const DEBUG = process.env.SCREEN_READER_DEBUG === "1";

function log(msg) {
  if (!DEBUG) return;
  const logPath = path.join(os.homedir(), ".claude", "screen-reader-debug.log");
  fs.appendFileSync(logPath, `${new Date().toISOString()} ${msg}\n`);
}

function speak(text) {
  if (!text || !text.trim()) return;
  const trimmed = text.trim().substring(0, MAX_LENGTH);
  log(`Speaking: ${trimmed.substring(0, 100)}...`);

  const scriptDir = __dirname;
  const ps1Path = path.join(scriptDir, "announce.ps1");

  // Convert WSL path to Windows path for PowerShell
  let winPs1Path;
  try {
    winPs1Path = execSync(`wslpath -w "${ps1Path}"`, { encoding: "utf8" }).trim();
  } catch {
    // Not in WSL, use path directly
    winPs1Path = ps1Path;
  }

  try {
    execSync(
      `powershell.exe -ExecutionPolicy Bypass -File "${winPs1Path}"`,
      {
        input: trimmed,
        encoding: "utf8",
        timeout: 30000,
        windowsHide: true,
      }
    );
  } catch (e) {
    log(`Speech error: ${e.message}`);
  }
}

function getLastAssistantMessage(transcriptPath) {
  try {
    const content = fs.readFileSync(transcriptPath, "utf8");
    const lines = content.trim().split("\n").reverse();
    for (const line of lines) {
      try {
        const entry = JSON.parse(line);
        if (entry.type === "assistant" && entry.message && entry.message.content) {
          const textBlocks = entry.message.content.filter((b) => b.type === "text");
          if (textBlocks.length > 0) {
            return textBlocks.map((b) => b.text).join("\n");
          }
        }
      } catch {
        continue;
      }
    }
  } catch (e) {
    log(`Transcript read error: ${e.message}`);
  }
  return null;
}

function main() {
  let input = "";
  try {
    input = fs.readFileSync(0, "utf8");
  } catch {
    return;
  }

  let hookData;
  try {
    hookData = JSON.parse(input);
  } catch {
    log("Failed to parse hook JSON");
    return;
  }

  log(`Hook event: ${JSON.stringify(hookData).substring(0, 200)}`);

  const hookEvent = hookData.hook_event || hookData.event || "";
  const toolName = hookData.tool_name || "";

  // Handle Stop event - announce last response
  if (hookEvent === "Stop" || hookEvent === "stop") {
    const transcriptPath = hookData.transcript_path || hookData.session_id;
    if (transcriptPath) {
      const msg = getLastAssistantMessage(transcriptPath);
      if (msg) {
        speak(msg);
      }
    }
    return;
  }

  // Handle Notification event - permission prompts
  if (hookEvent === "Notification" || hookEvent === "notification") {
    const message = hookData.notification?.message || hookData.message || "";
    if (message) {
      speak(`Claude needs permission. ${message}. Press 1 to allow, 2 to always allow, 3 to deny.`);
    }
    return;
  }

  // Handle AskUserQuestion - announce the question and options
  if (toolName === "AskUserQuestion") {
    const toolInput = hookData.tool_input || hookData.input || {};
    const questions = toolInput.questions || [];
    if (questions.length === 0) return;

    const parts = ["Claude is asking a question."];
    for (const q of questions) {
      parts.push(q.question || "");
      if (q.options && q.options.length > 0) {
        parts.push("Options are:");
        q.options.forEach((opt, i) => {
          const label = opt.label || `Option ${i + 1}`;
          const desc = opt.description ? `, ${opt.description}` : "";
          parts.push(`${i + 1}. ${label}${desc}`);
        });
        parts.push("You can also type a custom answer.");
      }
    }
    speak(parts.join(" "));
    return;
  }

  // Handle tool use notifications
  if (hookEvent === "PostToolUse" || hookEvent === "post_tool_use") {
    if (toolName === "Bash") {
      const exitCode = hookData.tool_result?.exit_code ?? hookData.exit_code;
      if (exitCode !== undefined && exitCode !== 0) {
        speak(`Command failed with exit code ${exitCode}.`);
      }
    }
    return;
  }
}

main();
