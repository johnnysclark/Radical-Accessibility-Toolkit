// acclaude-channel.ts — Claude Code Channel server for accessible web UI
// Bridges chat messages between the browser and Claude Code via MCP stdio transport.
// Serves index.html, handles chat/edit/permission HTTP endpoints, and pushes SSE events.
//
// Object queries and edits go through Claude → RhinoMCP (not file-based inventory).

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { resolve, dirname } from "node:path";
import { readFileSync } from "node:fs";
import { z } from "zod";
import { cleanText } from "./text-cleaner";

// ---------------------------------------------------------------------------
// Paths
// ---------------------------------------------------------------------------

const __dirname = dirname(new URL(import.meta.url).pathname);
const INDEX_HTML_PATH = resolve(__dirname, "index.html");

// ---------------------------------------------------------------------------
// SSE client management
// ---------------------------------------------------------------------------

type SSEClient = {
  controller: ReadableStreamDefaultController;
  sender: string;
};

const sseClients: Set<SSEClient> = new Set();

function broadcastSSE(data: Record<string, unknown>): void {
  const payload = `data: ${JSON.stringify(data)}\n\n`;
  for (const client of sseClients) {
    try {
      client.controller.enqueue(new TextEncoder().encode(payload));
    } catch {
      sseClients.delete(client);
    }
  }
}

// ---------------------------------------------------------------------------
// Sender allowlist
// ---------------------------------------------------------------------------

const ALLOWED_SENDERS = new Set(["local"]);

function getSender(req: Request): string {
  return req.headers.get("x-sender") || "local";
}

function isAllowedSender(req: Request): boolean {
  return ALLOWED_SENDERS.has(getSender(req));
}

// ---------------------------------------------------------------------------
// Chat ID counter
// ---------------------------------------------------------------------------

let chatIdCounter = 0;
function nextChatId(): string {
  chatIdCounter += 1;
  return String(chatIdCounter);
}

// ---------------------------------------------------------------------------
// MCP Server setup (low-level Server for custom channel capabilities)
// ---------------------------------------------------------------------------

const mcpServer = new Server(
  {
    name: "acclaude-channel",
    version: "2.0.0",
  },
  {
    capabilities: {
      tools: {},
      experimental: {
        "claude/channel": {},
        "claude/channel/permission": {},
      },
    } as any,
    instructions: [
      "Messages arrive from a blind/low-vision user using JAWS screen reader.",
      "Output plain text only. No markdown, emojis, or tables.",
      "One fact per line. Short sentences.",
      "",
      "You have TWO reply tools:",
      "1. reply — for normal chat responses. Use this for conversation, status updates, and confirmations.",
      "2. inventory_reply — for Model Navigator data ONLY. Use this when the message contains 'refresh inventory'.",
      "",
      "For inventory_reply: query rhinomcp get_document_info, then call inventory_reply with the objects JSON.",
      "The objects parameter must be a JSON string of an array. Each object needs: name, id, type, layer, and bounding_box (with min/max arrays).",
      "",
      "Always pass the chat_id from the channel tag to whichever reply tool you use.",
      "When modifying Rhino objects, describe what changed after each action.",
      "Use rhinomcp tools for all Rhino queries and modifications.",
    ].join("\n"),
  }
);

// Register tools: reply (chat) and inventory_reply (model navigator)
mcpServer.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "reply",
        description:
          "Send a text reply to the user in the accessible web chat UI. " +
          "Use the chat_id from the channel notification to route the response.",
        inputSchema: {
          type: "object" as const,
          properties: {
            chat_id: {
              type: "string",
              description: "The chat_id from the incoming channel notification",
            },
            text: {
              type: "string",
              description: "Plain text response to send to the user",
            },
          },
          required: ["chat_id", "text"],
        },
      },
      {
        name: "inventory_reply",
        description:
          "Send structured object inventory data to the Model Navigator pane. " +
          "Use this ONLY when the user requests a model refresh (message contains 'refresh inventory'). " +
          "The objects JSON must be an array of objects, each with: name, id, type, layer, and optionally bounding_box.",
        inputSchema: {
          type: "object" as const,
          properties: {
            chat_id: {
              type: "string",
              description: "The chat_id from the incoming channel notification",
            },
            objects: {
              type: "string",
              description:
                "JSON string of an array of objects. Each object must have: " +
                'name (string), id (string), type (string like "Curve" or "Surface"), ' +
                "layer (string), and optionally bounding_box with min [x,y,z] and max [x,y,z]. " +
                'Example: [{"name":"wall_1","id":"abc-123","type":"Curve","layer":"Default",' +
                '"bounding_box":{"min":[0,0,0],"max":[10,5,0]}}]',
            },
          },
          required: ["chat_id", "objects"],
        },
      },
    ],
  };
});

mcpServer.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "reply") {
    const chatId = (args as any)?.chat_id ?? "0";
    const rawText = (args as any)?.text ?? "";
    const cleaned = cleanText(rawText);

    broadcastSSE({
      type: "reply",
      chat_id: chatId,
      text: cleaned,
    });

    return {
      content: [
        {
          type: "text" as const,
          text: `Reply sent to chat ${chatId}`,
        },
      ],
    };
  }

  if (name === "inventory_reply") {
    const chatId = (args as any)?.chat_id ?? "0";
    const objectsStr = (args as any)?.objects ?? "[]";

    let objects: any[];
    try {
      objects = JSON.parse(objectsStr);
    } catch {
      objects = [];
    }

    broadcastSSE({
      type: "inventory",
      chat_id: chatId,
      objects,
    });

    return {
      content: [
        {
          type: "text" as const,
          text: `Inventory sent with ${objects.length} objects`,
        },
      ],
    };
  }

  return {
    content: [
      {
        type: "text" as const,
        text: `Unknown tool: ${name}`,
      },
    ],
    isError: true,
  };
});

// Handle permission request notifications from Claude Code
const PermissionRequestSchema = z.object({
  method: z.literal("notifications/claude/channel/permission_request"),
  params: z.object({
    request_id: z.string(),
    tool_name: z.string(),
    description: z.string(),
    input_preview: z.string(),
  }),
});

mcpServer.setNotificationHandler(
  PermissionRequestSchema,
  async (notification) => {
    const params = notification.params;
    broadcastSSE({
      type: "permission",
      request_id: params.request_id,
      tool_name: params.tool_name,
      description: params.description,
    });
  }
);

// ---------------------------------------------------------------------------
// HTTP server (Bun.serve)
// ---------------------------------------------------------------------------

const PORT = 8788;

Bun.serve({
  port: PORT,
  hostname: "0.0.0.0",
  idleTimeout: 0,
  async fetch(req: Request): Promise<Response> {
    const url = new URL(req.url);
    const method = req.method;

    // -----------------------------------------------------------------------
    // GET / — serve index.html
    // -----------------------------------------------------------------------
    if (method === "GET" && url.pathname === "/") {
      try {
        const html = readFileSync(INDEX_HTML_PATH, "utf-8");
        return new Response(html, {
          headers: { "Content-Type": "text/html; charset=utf-8" },
        });
      } catch {
        return new Response("ERROR: index.html not found", { status: 500 });
      }
    }

    // -----------------------------------------------------------------------
    // GET /events — SSE stream
    // -----------------------------------------------------------------------
    if (method === "GET" && url.pathname === "/events") {
      const stream = new ReadableStream({
        start(controller) {
          const client: SSEClient = {
            controller,
            sender: getSender(req),
          };
          sseClients.add(client);

          // Send connected event
          controller.enqueue(new TextEncoder().encode(": connected\n\n"));

          // Clean up on abort
          req.signal.addEventListener("abort", () => {
            sseClients.delete(client);
            try {
              controller.close();
            } catch {
              // Already closed
            }
          });
        },
      });

      return new Response(stream, {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          Connection: "keep-alive",
          "Access-Control-Allow-Origin": "*",
        },
      });
    }

    // -----------------------------------------------------------------------
    // POST /chat — receive chat message, forward as channel notification
    // -----------------------------------------------------------------------
    if (method === "POST" && url.pathname === "/chat") {
      if (!isAllowedSender(req)) {
        return new Response("ERROR: Sender not allowed", { status: 403 });
      }

      let body: any;
      try {
        body = await req.json();
      } catch {
        return new Response("ERROR: Invalid JSON", { status: 400 });
      }

      const text = body.text ?? "";
      const sender = body.sender ?? getSender(req);
      const chatId = nextChatId();

      // Send as channel notification to Claude Code via MCP
      try {
        await mcpServer.notification({
          method: "notifications/claude/channel",
          params: {
            content: text,
            meta: { chat_id: chatId, sender },
          },
        } as any);
      } catch (err) {
        console.error("Failed to send channel notification:", err);
      }

      return new Response(JSON.stringify({ ok: true, chat_id: chatId }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    // -----------------------------------------------------------------------
    // POST /edit — receive edits from Model Navigator, forward as chat
    // Edits are sent as a structured chat message that Claude will
    // execute using RhinoMCP modify_object tools.
    // -----------------------------------------------------------------------
    if (method === "POST" && url.pathname === "/edit") {
      if (!isAllowedSender(req)) {
        return new Response("ERROR: Sender not allowed", { status: 403 });
      }

      let body: any;
      try {
        body = await req.json();
      } catch {
        return new Response("ERROR: Invalid JSON", { status: 400 });
      }

      const edits = body.edits ?? [];
      if (!Array.isArray(edits) || edits.length === 0) {
        return new Response("ERROR: No edits provided", { status: 400 });
      }

      // Format edits as a plain-text instruction for Claude
      const lines = edits.map((edit: any) => {
        const { object_id, object_name, action, params } = edit;
        const name = object_name || object_id;
        if (action === "move") {
          return `Move "${name}" to position (${params.x}, ${params.y}, ${params.z ?? 0}).`;
        }
        if (action === "rename") {
          return `Rename "${name}" to "${params.name}".`;
        }
        if (action === "modify") {
          const changes = Object.entries(params)
            .map(([k, v]) => `${k}=${v}`)
            .join(", ");
          return `Modify "${name}": ${changes}.`;
        }
        return `Apply ${action} to "${name}" with params: ${JSON.stringify(params)}.`;
      });

      const chatId = nextChatId();
      const instruction =
        "Apply the following edits using rhinomcp modify_object. " +
        "Report each result as a single line.\n" +
        lines.join("\n");

      try {
        await mcpServer.notification({
          method: "notifications/claude/channel",
          params: {
            content: instruction,
            meta: { chat_id: chatId, sender: "navigator" },
          },
        } as any);
      } catch (err) {
        console.error("Failed to send edit notification:", err);
      }

      return new Response(JSON.stringify({ ok: true, chat_id: chatId, count: edits.length }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    // -----------------------------------------------------------------------
    // POST /permission — receive permission verdict
    // -----------------------------------------------------------------------
    if (method === "POST" && url.pathname === "/permission") {
      if (!isAllowedSender(req)) {
        return new Response("ERROR: Sender not allowed", { status: 403 });
      }

      let body: any;
      try {
        body = await req.json();
      } catch {
        return new Response("ERROR: Invalid JSON", { status: 400 });
      }

      const requestId = body.request_id ?? "";
      const behavior = body.behavior ?? "deny";

      try {
        await mcpServer.notification({
          method: "notifications/claude/channel/permission",
          params: {
            request_id: requestId,
            behavior,
          },
        } as any);
      } catch (err) {
        console.error("Failed to send permission response:", err);
      }

      return new Response(JSON.stringify({ ok: true }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    // -----------------------------------------------------------------------
    // 404
    // -----------------------------------------------------------------------
    return new Response("Not found", { status: 404 });
  },
});

console.error(`[acclaude-channel] HTTP server listening on http://localhost:${PORT}`);

// ---------------------------------------------------------------------------
// Connect MCP server to stdio transport (Claude Code connects here)
// ---------------------------------------------------------------------------

const transport = new StdioServerTransport();
await mcpServer.connect(transport);

console.error("[acclaude-channel] MCP server connected via stdio");
