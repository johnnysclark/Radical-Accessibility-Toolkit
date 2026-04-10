#!/bin/bash
export PATH="$HOME/.bun/bin:$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"
exec bun run channel-server.ts 2>/tmp/webui-channel-err.log
