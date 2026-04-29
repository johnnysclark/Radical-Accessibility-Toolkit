# Provider Layer

RAP has two directions of LLM interaction that must stay model-agnostic: **inbound** (an agent driving RAP via MCP) and **outbound** (RAP calling an LLM for AI-powered analysis).

---

## Inbound: agents driving RAP

The MCP surface is the inbound interface. MCP is a protocol, not a vendor-specific API, so any MCP-capable agent — Claude, Gemini, GPT-4o, a local model — can call RAP's tools. Write MCP tool docstrings in neutral terms. Do not reference any specific LLM by name in tool descriptions or error messages. Treat any MCP host as a valid caller.

---

## Outbound: RAP calling an LLM

Several output channels require AI inference: image description, alt-text generation, and tactile quality assessment. All of these must route through the provider interface defined in `provider/base.py`. No module outside `provider/` imports a vendor AI SDK directly.

**Implement these three provider classes:**

`AnthropicProvider` — wraps the Anthropic Python SDK. Default for deployments with an `ANTHROPIC_API_KEY` environment variable. Uses `claude-sonnet-4-6` as the default model; the model ID is set in config, not hardcoded in call sites.

`OpenAIProvider` — wraps the OpenAI Python SDK. Works for any OpenAI-compatible endpoint including local models. Default model configurable.

`NullProvider` — returns `"[description unavailable]"` for `describe_image` and `complete`. Does not require network access or credentials. Used in tests and offline deployments.

Provider selection at startup:
```python
provider = get_provider()  # reads RAP_PROVIDER env var, defaults to auto-detect
```

Auto-detect: if `ANTHROPIC_API_KEY` is set, use `AnthropicProvider`; elif `OPENAI_API_KEY` is set, use `OpenAIProvider`; else `NullProvider`.

---

## The provider interface

Defined in `provider/base.py` as a `Protocol`:

```python
class Provider(Protocol):
    def complete(self, prompt: str, images: list[bytes] | None = None) -> str:
        """Send prompt with optional images; return plain-text response."""

    def describe_image(self, image: bytes, context: str) -> str:
        """Return a screen-reader-ready description of an architectural image."""

    def available(self) -> bool:
        """True if credentials are present and the endpoint is reachable."""
```

**What the interface hides:**
- API endpoint URLs and authentication headers
- Model IDs and version strings
- Request/response envelope format (Anthropic vs. OpenAI vs. Vertex)
- Retry logic, rate limiting, and timeout handling
- Streaming vs. batch response handling

**What the interface exposes:**
- Whether the provider is usable right now (`available()`)
- A synchronous call contract — all calls block until the response is ready

The interface does not manage conversation history, tool-call loops, or multi-step reasoning. Those responsibilities belong to the MCP caller or the CLI user.

---

## Calling the provider

Renderer modules and MCP tool handlers that need AI inference receive a `Provider` instance injected at construction or call time — they do not call `get_provider()` themselves. This makes them testable with `NullProvider` without environment setup.

Example in a renderer:

```python
class AltTextRenderer:
    def __init__(self, provider: Provider):
        self.provider = provider

    def render(self, state_path: str, output_path: str, options: dict) -> str:
        image = load_image(options["image_path"])
        description = self.provider.describe_image(image, context="architectural plan")
        write(output_path, description)
        return "OK: " + output_path
```
