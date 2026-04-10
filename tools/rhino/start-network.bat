@echo off
REM start-network.bat — Set up WSL2 port forwarding for RhinoMCP
REM Run this AS ADMINISTRATOR after each Windows restart (or add to Task Scheduler)
REM
REM This creates a portproxy rule so WSL2 can reach RhinoMCP on Windows.
REM The rule persists until reboot.

echo Setting up WSL2 port forwarding for RhinoMCP...

REM Get the WSL2 gateway IP dynamically
for /f "tokens=3" %%i in ('wsl ip route show default') do set GATEWAY_IP=%%i

if "%GATEWAY_IP%"=="" (
    echo ERROR: Could not determine WSL2 gateway IP.
    echo Make sure WSL2 is running.
    pause
    exit /b 1
)

echo WSL2 gateway IP: %GATEWAY_IP%

REM Remove old rule if exists (ignore errors)
netsh interface portproxy delete v4tov4 listenport=1999 listenaddress=%GATEWAY_IP% >nul 2>&1

REM Add new rule: WSL2 gateway:1999 -> Windows localhost:1999 (RhinoMCP)
netsh interface portproxy add v4tov4 listenport=1999 listenaddress=%GATEWAY_IP% connectport=1999 connectaddress=127.0.0.1

echo.
echo Port forwarding configured:
echo   %GATEWAY_IP%:1999 -^> 127.0.0.1:1999 (RhinoMCP)
echo.
netsh interface portproxy show v4tov4
echo.
echo Done. This rule persists until Windows restarts.
pause
