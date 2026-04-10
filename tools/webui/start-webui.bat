@echo off
REM start-webui.bat — Launch the accessible Rhino modeling interface
REM Step 2 of 2: Run this AFTER Rhino is open (via start-rhino.bat)
REM
REM What this does:
REM   1. Starts Claude Code with the channel server in WSL2
REM   2. Waits 15 seconds for you to accept the experimental prompt
REM   3. Opens the accessible web UI in your default browser

REM Resolve project root (two levels up from this script)
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..\..\

echo Starting Claude Code with channel server...
echo.
echo IMPORTANT: A new terminal window will open.
echo Accept the experimental channels prompt in that window.
echo The browser will open in 15 seconds.
echo.

REM Convert Windows path to WSL path for the start script
for /f "tokens=*" %%i in ('wsl wslpath -a "%SCRIPT_DIR%start-webui.sh"') do set WSL_SCRIPT=%%i

REM Start Claude Code in a separate window
start "Claude Code" wsl bash "%WSL_SCRIPT%"

REM Wait for user to accept the prompt and server to start
echo Waiting 15 seconds for Claude Code to start...
timeout /t 15 /nobreak

echo Opening browser...
start http://localhost:8788

echo.
echo If the page doesn't load, refresh the browser after a few seconds.
echo Close this window when done.
pause
