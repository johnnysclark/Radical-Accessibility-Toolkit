@echo off
REM start-network.bat — OBSOLETE under WSL2 mirrored networking.
REM
REM This script used to add a `netsh portproxy` rule so WSL2 could reach
REM RhinoMCP on the Windows host. Since mirrored networking was enabled
REM in %USERPROFILE%\.wslconfig, WSL shares the Windows loopback directly
REM — no portproxy rule is needed. Running it today just accumulates
REM stale rules that confuse future diagnostics.
REM
REM If Rhino MCP won't connect from Claude, from WSL run:
REM
REM     bash tools/rhino/rhino-doctor.sh
REM
REM It will diagnose port conflicts, zombie processes, stale portproxy
REM rules (and print the exact admin-PowerShell commands to clean them),
REM and duplicate firewall rules — without touching Windows state.

echo.
echo start-network.bat is obsolete under WSL2 mirrored networking.
echo.
echo If Rhino MCP won't connect, from WSL run:
echo     bash tools/rhino/rhino-doctor.sh
echo.
echo Doing nothing. Press any key to close.
pause >nul
exit /b 0
