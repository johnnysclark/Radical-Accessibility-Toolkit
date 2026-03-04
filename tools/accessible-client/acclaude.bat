@echo off
REM acclaude.bat — Launch the accessible Claude client from Windows
REM Double-click this file or pin it to the taskbar
REM Requires WSL2 with Claude Code installed

wsl bash /mnt/c/Users/ethan/fabric-accessible-graphics/bin/acclaude %*
pause
