---
name: rhino-doctor
description: Diagnose why Rhino MCP won't connect. Runs a single non-admin script that checks mirrored networking, Rhino process state, who holds ports 1998/1999, WSL→Windows TCP reachability, stale portproxy rules, and duplicate firewall rules — then prints exact remediation commands without mutating Windows state. Trigger when the user says "rhino doctor", "fix rhino", "rhino won't connect", "check rhino ports", "diagnose rhino mcp", "rhino mcp broken", "port 1999 stuck", "rhino port conflict", or otherwise reports Rhino MCP / port connectivity trouble.
---

# Rhino Doctor Skill

When the user reports Rhino MCP connection trouble, run the diagnostic script and relay its output. The script is non-admin, read-only, and screen-reader-friendly by design — it does not modify Windows state, so it's safe to run repeatedly.

The underlying script is `tools/rhino/rhino-doctor.sh`.

## How to run it (Claude's job)

From the repo root:

```bash
bash tools/rhino/rhino-doctor.sh
```

Relay the output verbatim — every line is already prefixed (`OK:` / `WARN:` / `ERROR:` / `INFO:` / `HINT:`) and safe for a screen reader.

## Reading the exit code

| Exit | Meaning | What to tell the user |
| --- | --- | --- |
| 0 | All checks pass | Rhino MCP should work. If Claude still can't connect, the problem is elsewhere (MCP tool approval, Claude restart needed). |
| 1 | User action needed | Summarize the top `ERROR:` or `WARN:` line and quote the matching `HINT:` line verbatim. |
| 2 | Can't reach Windows from WSL | `cmd.exe` interop is broken. Suggest `wsl --shutdown` from admin PowerShell, then reopen. |
| 3 | Rhino not running | Tell the user to double-click `tools/rhino/start-rhino.bat` and wait for `[STARTUP] Ready`. |

## When the script prints an admin-PowerShell command

Hand the exact line to the user — **do not improvise**. Past troubleshooting sessions accumulated duplicate portproxy and firewall rules because admin commands were tweaked on the fly. The script's `HINT:` lines are copy-paste-ready and intentionally the minimum change.

Specifically:

- `netsh interface portproxy delete v4tov4 listenport=<P> listenaddress=<A>` — run in admin PowerShell; removes one stale rule.
- `Remove-NetFirewallRule -DisplayName '<NAME>'` — removes every firewall rule with that display name (duplicates included). Only run if the user confirms the rule is theirs, not Windows Defender's.
- `taskkill.exe /PID <pid> /F` — kills the named process. If the owner shown is the user's own account, no admin is required and Claude can run this directly from WSL after user approval.

## Common diagnoses and fixes

| Script says | What's happening | Fix |
| --- | --- | --- |
| `ERROR: Rhino is not running` | Self-explanatory | Start Rhino via `tools/rhino/start-rhino.bat`. |
| `ERROR: port 1999 is not bound — _mcpstart never succeeded` | Rhino is running but the plugin didn't start (often a license prompt, sometimes a silent plugin error) | In Rhino's command line: type `_mcpstart`. If it still fails, restart Rhino. |
| `ERROR: port 1999 bound by <name> (PID <pid>) — not Rhino` | Zombie process holding the port (often a leftover from a previous Rhino crash, or a python testing the port) | Run the `taskkill` line from the HINT. Then tell Rhino to retry: `_mcpstart`. |
| `WARN: stale portproxy rules present` | Leftovers from `start-network.bat` runs before mirrored networking was enabled | Under mirrored networking these are redundant. User should paste the `netsh delete` lines into admin PowerShell. Not blocking in most cases but surfaces as confusion when something else breaks. |
| `WARN: N firewall rules touch ports 1998/1999 (duplicates)` | Past fixes added rules without cleaning old ones | Enumerate with the provided `Get-NetFirewallPortFilter` command. If obvious duplicates by name, `Remove-NetFirewallRule -DisplayName '<NAME>'` collapses them. |
| `ERROR: WSL cannot reach port 1999 on the Windows host` (but it's bound) | Mirrored networking is off, or Windows Firewall is blocking WSL's virtual adapter | Re-check `.wslconfig` first. If mirrored is on, the firewall blocked the WSL vEthernet — see `project_windows_firewall_blocks_wsl` memory for the `New-NetFirewallRule` line. |

## Not in scope

- Fixing the external `rhinomcp` (uvx) package itself. The doctor doesn't touch it.
- Installing or repairing Rhino. If Rhino crashed hard, user has to restart it.
- Silent execution of admin commands. This is deliberate — every mutation happens with a human at the keyboard.

## When to re-run

The script is idempotent and safe to run as many times as needed. Re-run after each remediation step to confirm the fix took.
