# RAP Service Management

Auto-start configurations for the MCP server on macOS and Windows.

## macOS (launchd)

1. Edit `com.rap.mcp-server.plist` and update paths for your system.
2. Copy to LaunchAgents:
   cp services/com.rap.mcp-server.plist ~/Library/LaunchAgents/
3. Load the service:
   launchctl load ~/Library/LaunchAgents/com.rap.mcp-server.plist
4. Check status:
   launchctl list | grep com.rap.mcp-server
5. View logs:
   tail -f ~/Projects/rap/logs/mcp-stdout.log
6. To stop:
   launchctl unload ~/Library/LaunchAgents/com.rap.mcp-server.plist

## Windows (NSSM)

1. Download NSSM from https://nssm.cc/download and place nssm.exe in your PATH.
2. Edit `install-windows-service.ps1` and update paths for your system.
3. Run as Administrator:
   powershell -ExecutionPolicy Bypass -File services\install-windows-service.ps1
4. Check status:
   nssm status RAP-MCP-Server
5. View logs:
   type C:\Users\RAP\Projects\rap\logs\mcp-stdout.log
6. To stop:
   nssm stop RAP-MCP-Server
7. To remove:
   nssm remove RAP-MCP-Server confirm

## Environment Variables

Both configurations set RAP_PROJECT_ROOT to the project directory.
The MCP server uses this to locate state.json and other resources.
