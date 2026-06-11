"""Maquette: accessible, crash-only modeling CLI for Rhino 8 for Mac.

One engine, three frontends (CLI, MCP server, chat REPL) and three
backends (record, headless rhino3dm, live Rhino listener). The journal
is the source of truth; everything else is derived or disposable.
"""

VERSION = "0.1.0"

PROJECT_SCHEMA = "maquette-project-1"
SNAPSHOT_SCHEMA = "maquette-snapshot-1"
JOURNAL_VERSION = 1
PROTO_VERSION = 1

DEFAULT_PORT = 6270  # "MAQ" on a phone keypad
DEFAULT_HOST = "127.0.0.1"
DEFAULT_LAYER = "MAQ::Default"
