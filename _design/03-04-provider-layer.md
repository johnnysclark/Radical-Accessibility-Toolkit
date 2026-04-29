# 03-04 — Provider Layer

RAP has two directions of LLM interaction that need to stay model-agnostic: **inbound** (an agent driving RAP via MCP) and **outbound** (RAP calling an LLM for AI-powered analysis). Both currently assume Claude. Neither should.

---

## Inbound: agents driving RAP

The MCP surface (section 03-05) is the inbound interface. MCP is a protocol, not a Claude-specific API, so any MCP-capable agent — Claude, Gemini, GPT-4o, a local model — can call RAP's tools. The inbound direction is already structurally model-agnostic.

What currently breaks that guarantee:
- The MCP server's setup documentation and `.mcp.json` reference Claude Code by name.
- Some MCP tool docstrings contain Claude-specific phrasing ("ask Claude to…").
- `extend_controller` writes Python source into the controller at runtime — a feature that assumes a Claude Code session with file-write access.

The fix is editorial and architectural: write tool docstrings in neutral terms, remove the `extend_controller` escape hatch, and treat Claude Code as one possible MCP host rather than the only one.

---

## Outbound: RAP calling an LLM

Three places in the current codebase call an LLM directly:

1. `tools/image-describer/arch_alt_text.py` — calls Anthropic REST with a hardcoded `claude-3-5-sonnet` model ID.
2. `tools/tact/src/tact/mcp_server/tools.py` — `describe_image` and `extract_text_with_vision` call the Anthropic SDK directly.
3. `image_to_piaf` accepts a `claude_text_json` parameter, making Claude both the caller and a data provider in the same request.

All three should route through a provider abstraction.

---

## The provider interface

The abstraction is minimal — RAP only needs two operations from an LLM:

```
complete(prompt: str, images: list[bytes] | None) -> str
```

A text prompt with optional image attachments; returns a plain text response. No streaming, no tool calls, no conversation history. If the use case grows, the interface grows — but start with this.

```
describe_image(image: bytes, context: str) -> str
```

A specialized form of `complete` for image description, included separately because it is called in hot paths and may benefit from a different model or caching strategy than general completions.

**What the abstraction must hide:**
- API endpoint URLs and authentication
- Model IDs and version strings
- Request/response envelope format (Anthropic vs. OpenAI vs. Vertex)
- Retry logic, rate limiting, timeout handling
- Streaming vs. batch response handling

**What the abstraction must expose:**
- Whether the provider is available (so callers can degrade gracefully)
- The model identifier being used (for logging and audit, not for routing)
- A synchronous call interface — RAP's output pipeline is not async

---

## Provider implementations

Three implementations cover the realistic deployment cases:

- `AnthropicProvider` — wraps the Anthropic SDK; default for Claude Code deployments.
- `OpenAIProvider` — wraps the OpenAI SDK; covers GPT-4o and compatible endpoints.
- `NullProvider` — returns a fixed "description unavailable" string; used in tests and offline deployments where no LLM key is present.

The provider is selected at startup via an environment variable or config entry. The rest of the codebase imports the provider interface, not any vendor SDK.

---

## What this does not cover

The provider layer is not a general agent framework. It does not manage conversation history, tool-call loops, or multi-step reasoning. Those are the agent loop's responsibility (section 03-06). The provider layer is a thin, synchronous call boundary — the smallest seam needed to make vendor SDKs swappable.
