# Module Structure

## Directory layout

```
rap/
  core/
    dispatcher.py     # apply_command(), load_state(), _atomic_write(), undo stack
    schema.py         # CURRENT_VERSION, load_with_migration(), migration functions
    hooks.py          # HookRegistry, HookPayload, register(), fire()
  cli/
    repl.py           # readline REPL — thin shell over dispatcher
  mcp/
    server.py         # FastMCP server, ~15 @mcp.tool() functions
  provider/
    base.py           # Provider protocol
    anthropic.py      # AnthropicProvider
    openai.py         # OpenAIProvider
    null.py           # NullProvider (offline / test)
  renderer/
    base.py           # Renderer protocol
    rhino/
      watcher.py      # IronPython 2.7 file-watch loop (runs inside Rhino)
      draw.py         # per-object-type draw functions, dispatched by watcher
    tact/
      pdf.py          # state.json → PIAF tactile PDF
      image.py        # raster image → PIAF tactile PDF (RainbowTact pipeline)
    text/
      describe.py     # state → structured verbal description
      audit.py        # state → labeled accessibility / structural check report
  domain/
    layout_jig/       # Layout Jig domain (replace or extend for other domains)
      commands.py     # all Layout Jig command handlers
      schema.py       # Layout Jig domain schema definition
```

`rap/core/` has zero pip dependencies — Python stdlib only. `mcp/`, `provider/`, and `renderer/tact/` may use pip packages.

---

## Key interfaces

```python
# core/dispatcher.py
def apply_command(state: dict, tokens: list[str], state_file: str) -> str:
    """Dispatch one command. Returns 'OK: ...' or 'ERROR: ...'."""

def load_state(path: str) -> dict:
    """Read state.json. Runs schema migration on every load."""

def _atomic_write(path: str, content: str) -> None:
    """Write to .tmp, fsync, os.replace. Never leaves a partial file."""
```

```python
# renderer/base.py
from typing import Protocol

class Renderer(Protocol):
    def render(self, state_path: str, output_path: str, options: dict) -> str:
        """Produce an artifact. Returns 'OK: <path>' or 'ERROR: <reason>'."""

    def supports_schema(self, version: str) -> bool:
        """Return True if this renderer can consume this schema version."""
```

```python
# provider/base.py
from typing import Protocol

class Provider(Protocol):
    def complete(self, prompt: str, images: list[bytes] | None = None) -> str:
        """Send a prompt; return plain-text response."""

    def describe_image(self, image: bytes, context: str) -> str:
        """Return a screen-reader-ready description of an image."""

    def available(self) -> bool:
        """Return True if credentials are present and the endpoint is reachable."""
```

```python
# core/hooks.py
from typing import TypedDict, Callable

class HookPayload(TypedDict):
    command: str
    args: dict
    result: str        # the OK:/ERROR: string
    elapsed_ms: int
    state_path: str

HookFn = Callable[[HookPayload], None]

class HookRegistry:
    def register(self, fn: HookFn) -> None: ...
    def fire(self, payload: HookPayload) -> None: ...
```

---

## Dependency rules

- `core/` imports nothing outside stdlib.
- `cli/` imports `core/` only.
- `mcp/` imports `core/` and optionally `provider/` and `renderer/`.
- `renderer/` imports `core/schema` and nothing else from `rap/`.
- `provider/` imports nothing from `rap/`.
- `domain/` imports `core/dispatcher` to register its commands; nothing else.
- No module imports from `domain/` directly — domain registration happens at startup via config.
