# install-windows-service.ps1
# Install the RAP MCP server as a Windows service using NSSM.
#
# Prerequisites:
#   1. Download NSSM from https://nssm.cc/download
#   2. Place nssm.exe in your PATH or specify full path below.
#   3. Run this script as Administrator.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File install-windows-service.ps1

$ErrorActionPreference = "Stop"

# ── Configuration (edit these paths for your system) ──────
$ProjectRoot = "C:\Users\RAP\Projects\rap"
$NodeExe     = "C:\Program Files\nodejs\node.exe"
$LogDir      = "$ProjectRoot\logs"

# ── Ensure log directory exists ───────────────────────────
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
    Write-Host "OK: Created log directory: $LogDir"
}

# ── Install the service ──────────────────────────────────
nssm install RAP-MCP-Server "$NodeExe"
nssm set RAP-MCP-Server AppParameters "$ProjectRoot\mcp\mcp_server.py"
nssm set RAP-MCP-Server AppDirectory "$ProjectRoot"
nssm set RAP-MCP-Server Start SERVICE_AUTO_START
nssm set RAP-MCP-Server AppStdout "$LogDir\mcp-stdout.log"
nssm set RAP-MCP-Server AppStderr "$LogDir\mcp-stderr.log"

# ── Set environment variable for project root ─────────────
nssm set RAP-MCP-Server AppEnvironmentExtra "RAP_PROJECT_ROOT=$ProjectRoot"

# ── Start the service ─────────────────────────────────────
nssm start RAP-MCP-Server

Write-Host "OK: RAP MCP Server installed and started."
Write-Host "  Logs: $LogDir"
Write-Host "  To stop:   nssm stop RAP-MCP-Server"
Write-Host "  To remove: nssm remove RAP-MCP-Server confirm"
