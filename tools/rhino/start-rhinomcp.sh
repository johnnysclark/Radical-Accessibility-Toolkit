#!/bin/bash
export PATH="$HOME/.bun/bin:$HOME/.local/bin:$PATH"
export RHINO_MCP_HOST=172.28.208.1
exec uvx rhinomcp 2>/tmp/rhinomcp-err.log
