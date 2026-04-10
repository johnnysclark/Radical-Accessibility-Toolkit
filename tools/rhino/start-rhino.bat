@echo off
REM start-rhino.bat — Start Rhino fully configured for accessible modeling
REM
REM What this does:
REM   1. Launches Rhino 8 with no splash screen
REM   2. Auto-runs startup.py which loads:
REM      - Layout Jig watcher (file watching, inventory, pending edits)
REM      - RhinoMCP server (mcpstart)
REM      - LightPen display mode on ALL viewports
REM      - Model units set to Feet
REM
REM After Rhino is loaded, run start-webui.bat to start the web interface.

set RHINO_PATH=C:\Program Files\Rhino 8\System\Rhino.exe
set STARTUP_SCRIPT=%~dp0startup.py
set STARTUP_FWD=%STARTUP_SCRIPT:\=/%

if not exist "%RHINO_PATH%" (
    echo ERROR: Rhino 8 not found at %RHINO_PATH%
    pause
    exit /b 1
)

if not exist "%STARTUP_SCRIPT%" (
    echo ERROR: Startup script not found at %STARTUP_SCRIPT%
    pause
    exit /b 1
)

echo Starting Rhino with accessible modeling tools...
start "" "%RHINO_PATH%" /nosplash /runscript="_-RunPythonScript %STARTUP_FWD%"

echo Rhino is starting. Wait for the command line to show:
echo   [STARTUP] Ready. Watcher active. RhinoMCP started. LightPen on all viewports.
echo Then double-click start-webui.bat to start the web interface.
