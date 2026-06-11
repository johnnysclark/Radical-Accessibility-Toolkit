"""maquette chat: a screen-reader-first modeling conversation.

Plain input()/print() loop, prompt "maq> ". No TUI, no streaming, no
spinners. Three kinds of line:

  /commands        meta: /help /scene /journal N /undo N /transcript /quit
  grammar words    run locally, instantly, no model: box 10 10 30
  anything else    goes to Claude, who models through the same fifteen
                   functions the MCP server exposes

Claude's replies print complete (never token by token); every tool call
echoes its one-line OK confirmation as it lands, so progress is audible;
each turn ends with READY:.

Works without the SDK installed: direct commands still run; asking
Claude explains what to install. Auth comes from the Claude Code login
(subscription), CLAUDE_CODE_OAUTH_TOKEN, or ANTHROPIC_API_KEY.
"""

from __future__ import annotations

import asyncio
import os
import shutil

from maquette import describe, grammar, say
from maquette.engine import Engine, USER_ERRORS
from maquette.project import find_project
from maquette.service import MaquetteService
from maquette.transcripts import Transcript

META_HELP = [
    "/help        these commands plus the modeling grammar",
    "/scene       what is in the model right now",
    "/journal N   the last N steps (default 10)",
    "/undo N      undo the last N steps (default 1)",
    "/transcript  where this conversation is being saved",
    "/quit        leave the chat",
    "Anything that starts with a modeling word runs instantly.",
    "Anything else is a question or request for Claude.",
]

SYSTEM_PROMPT = """\
You are Maquette, a 3D modeling assistant working with a blind architect
in Rhino. Everything you say is read aloud by a screen reader, and your
only view of the model is through your tools, which return the same text
the user hears.

Rules:
- Use the tools for every read or change. Never guess model state;
  query_scene or describe_object when unsure.
- Prefer create_objects and edit_objects vocabulary ops. Use run_script
  with rhinoscriptsyntax only for shapes the vocabulary cannot express,
  and give it a one-sentence intent: it is read aloud from the journal.
- Plain speakable text only: no markdown, no headings, no bullet
  symbols, no code fences, no tables. Short sentences, one fact each.
- Keep replies under ten short lines. The tool confirmations already
  tell the user what happened; do not repeat them, just summarize.
- When you need a decision, ask one question and number the options.
- Dimensions are in the project's units. Name important objects so the
  user can refer to them by name.
- Objects from booleans, lofts, and scripts may be pending until a live
  rebuild in Rhino; their notes say so. Mention it only when relevant.
- Deliverables: export_model writes .3dm, .txt, or .stl for 3D printing;
  export_plan and export_section write 2D drawings as .svg or .dxf.
  STL, plans, and sections need Rhino connected and take a paper scale
  like 1:100. Default file home is the exports folder.
"""

TOOL_NAMES = ("create_objects", "edit_objects", "query_scene",
              "describe_scene", "describe_object", "measure", "run_script",
              "undo", "rebuild", "journal_show", "export_model",
              "export_plan", "export_section", "doctor", "project_info")


def auth_hint() -> list[str]:
    return [
        "1. Easiest: sign in to Claude Code once on this Mac (claude login).",
        "2. Or run: claude setup-token, and keep the token it stores.",
        "3. Or set the ANTHROPIC_API_KEY environment variable.",
    ]


def have_auth() -> bool:
    return bool(os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
                or os.environ.get("ANTHROPIC_API_KEY")
                or shutil.which("claude"))


def sdk_available() -> bool:
    try:
        import claude_agent_sdk  # noqa: F401
        return True
    except ImportError:
        return False


def route(line: str) -> str:
    """Classify one input line: quit, meta, empty, direct, or ask."""
    stripped = line.strip()
    if not stripped:
        return "empty"
    if stripped in ("/quit", "/exit", "quit", "exit"):
        return "quit"
    if stripped.startswith("/"):
        return "meta"
    if grammar.is_command(stripped):
        return "direct"
    return "ask"


class ChatREPL:
    def __init__(self, project, backend: str = "auto",
                 model: str | None = None, client_factory=None):
        self.project = project
        self.engine = Engine(project, backend=backend, actor="chat-user")
        self.service = MaquetteService(project, backend=backend,
                                       actor="chat-llm")
        self.model = model
        self.transcript = Transcript(project.transcripts_dir)
        self._client = None
        self._client_factory = client_factory or self._make_client

    # -- one line in, spoken lines out -----------------------------------------

    async def handle(self, line: str) -> bool:
        """Process one line. Returns False when the chat should end."""
        kind = route(line)
        if kind == "empty":
            return True
        self.transcript.write("YOU", line)
        if kind == "quit":
            say.ok("bye. Transcript saved at {0}".format(
                self.transcript.text_path))
            return False
        if kind == "meta":
            self._meta(line.strip())
        elif kind == "direct":
            self._direct(line)
        else:
            await self._ask(line)
        say.ready()
        return True

    def _say(self, line: str) -> None:
        print(line)
        self.transcript.write("STATUS", line)

    def _meta(self, line: str) -> None:
        parts = line.split()
        word, rest = parts[0], parts[1:]
        if word == "/help":
            for help_line in META_HELP + grammar.help_lines():
                self._say(help_line)
        elif word == "/scene":
            for out in describe.brief(self.engine.scene()):
                self._say(out)
        elif word == "/journal":
            last = int(rest[0]) if rest else 10
            for out in describe.journal_lines(self.engine.entries(), last=last):
                self._say(out)
        elif word == "/undo":
            self._direct("undo " + (rest[0] if rest else "1"), undo=True)
        elif word == "/transcript":
            self._say("transcript: {0}".format(self.transcript.text_path))
        else:
            self._say("ERROR: unknown command {0}. Try /help".format(word))

    def _direct(self, line: str, undo: bool = False) -> None:
        try:
            if undo:
                result = self.engine.undo_steps(int(line.split()[1]))
            else:
                result = self.engine.run_text(line)
        except USER_ERRORS as exc:
            self._say("ERROR: " + str(exc))
            return
        for out in result["lines"]:
            self._say("OK: " + out if not out.startswith(
                ("OK:", "ERROR:", "WARNING:", "NOTE:")) else out)
        for warning in result["warnings"]:
            self._say("WARNING: " + warning)

    async def _ask(self, text: str) -> None:
        if not sdk_available():
            self._say("ERROR: talking to Claude needs the chat extra.")
            self._say("fix: pip install 'maquette[chat]'")
            self._say("Direct commands still work; try /help.")
            return
        if self._client is None and not have_auth():
            self._say("ERROR: no Claude credentials found.")
            for hint in auth_hint():
                self._say(hint)
            return
        self._say("OK: asking Claude.")
        try:
            if self._client is None:
                self._client = await self._client_factory()
            await self._client.query(text)
            await self._speak_response()
        except Exception as exc:  # noqa: BLE001 - spoken, never a traceback
            self._say("ERROR: the Claude call failed: {0}".format(exc))
            for hint in auth_hint():
                self._say(hint)
            self._client = None

    async def _speak_response(self) -> None:
        from claude_agent_sdk import (AssistantMessage, ResultMessage,
                                      TextBlock, ToolUseBlock)
        async for message in self._client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock) and block.text.strip():
                        reply = block.text.strip()
                        say.page(["CLAUDE: " + line for line in
                                  reply.splitlines()], ask=self._more)
                        self.transcript.write("CLAUDE", reply)
                    elif isinstance(block, ToolUseBlock):
                        self._say("OK: Claude uses {0}.".format(
                            block.name.split("__")[-1]))
            elif isinstance(message, ResultMessage):
                if getattr(message, "is_error", False):
                    self._say("ERROR: Claude stopped with an error: {0}".format(
                        getattr(message, "result", "") or "unknown"))

    def _more(self, question: str) -> bool:
        try:
            answer = input(question + " ")
        except (EOFError, KeyboardInterrupt):
            return False
        return answer.strip().lower() in ("y", "yes", "more")

    # -- SDK wiring ---------------------------------------------------------------

    async def _make_client(self):
        from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
        options = ClaudeAgentOptions(
            tools=[],  # no built-in tools; the model only models
            mcp_servers={"maquette": self._tool_server()},
            allowed_tools=["mcp__maquette__" + name for name in TOOL_NAMES],
            system_prompt=SYSTEM_PROMPT,
            permission_mode="bypassPermissions",
            setting_sources=[],
            cwd=self.project.root,
            model=self.model,
            max_turns=80,
        )
        client = ClaudeSDKClient(options=options)
        await client.connect()
        return client

    def _tool_server(self):
        from claude_agent_sdk import create_sdk_mcp_server
        return create_sdk_mcp_server(name="maquette",
                                     tools=self._build_tools())

    def _build_tools(self):
        from claude_agent_sdk import tool

        def text_result(out: str) -> dict:
            return {"content": [{"type": "text", "text": out}]}

        def echoing(function):
            async def handler(args: dict) -> dict:
                out = function(**args)
                for line in out.splitlines():
                    print(line)
                self.transcript.write("TOOL", out)
                return text_result(out)
            return handler

        def schema(properties: dict, required: list[str]) -> dict:
            return {"type": "object", "properties": properties,
                    "required": required}

        ops_schema = schema(
            {"ops": {"type": "array", "items": {"type": "object"}}}, ["ops"])
        service = self.service
        tools = [
            tool("create_objects",
                 "Create geometry from a list of op dicts. Each item: "
                 '{"op": NAME, "params": {...}, "name"?: str, "layer"?: str}. '
                 "Ops and params: create_point {at:[x,y,z]}; create_line "
                 "{start,end}; create_polyline {points,closed}; create_circle "
                 "{center,radius}; create_arc {p1,p2,p3}; create_rectangle "
                 "{corner,width,depth}; create_curve {points,degree}; "
                 "create_text {text,at,height}; create_box {corner,"
                 "size:[w,d,h]}; create_sphere {center,radius}; "
                 "create_cylinder {base,radius,height}; create_cone "
                 "{base,radius,height}; extrude {source,height|vector}; loft "
                 "{sources}; revolve {source,axis_start,axis_end,angle}; "
                 "boolean_union {inputs}; boolean_difference {keep,cut}; "
                 "boolean_intersection {inputs}. Reference objects by id "
                 "(m3), exact name, or last.",
                 ops_schema)(echoing(service.create_objects)),
            tool("edit_objects",
                 "Change existing objects. Ops: move {ids,vector}; rotate "
                 "{ids,angle,center?,axis?}; scale {ids,factors,center?}; "
                 "mirror {ids,plane_point,plane_normal}; copy {ids,vector,"
                 "count?}; delete {ids}|{all:true}; set_name {id,name}; "
                 "set_layer {ids,layer}; create_layer {name}; group "
                 "{members,name?}; ungroup {gid}.",
                 ops_schema)(echoing(service.edit_objects)),
            tool("query_scene",
                 "List alive objects, filtered by layer, kind, or name part.",
                 schema({"layer": {"type": "string"},
                         "kind": {"type": "string"},
                         "name_contains": {"type": "string"}}, []))(
                echoing(service.query_scene)),
            tool("describe_scene",
                 "Spoken model summary; level brief or full.",
                 schema({"level": {"type": "string"}}, []))(
                echoing(service.describe_scene)),
            tool("describe_object",
                 "Detail one object by id, exact name, or last.",
                 schema({"ref": {"type": "string"}}, ["ref"]))(
                echoing(service.describe_object)),
            tool("measure",
                 "Distance and axis deltas between objects or x,y,z points.",
                 schema({"a": {"type": "string"}, "b": {"type": "string"}},
                        ["a", "b"]))(echoing(service.measure)),
            tool("run_script",
                 "Run rhinoscriptsyntax Python in Rhino for shapes beyond "
                 "the vocabulary. Journaled and replayable. intent: one "
                 "plain sentence, read aloud. Namespace: rs, sc, Rhino; "
                 "append created guids to __maq_created__.",
                 schema({"code": {"type": "string"},
                         "intent": {"type": "string"},
                         "name": {"type": "string"}}, ["code", "intent"]))(
                echoing(service.run_script)),
            tool("undo", "Undo the last N steps.",
                 schema({"steps": {"type": "integer"}}, []))(
                echoing(service.undo)),
            tool("rebuild",
                 "Replay the journal into a backend: live or headless.",
                 schema({"backend": {"type": "string"}}, []))(
                echoing(service.rebuild)),
            tool("journal_show", "Recent steps, one line each.",
                 schema({"last": {"type": "integer"},
                         "search": {"type": "string"}}, []))(
                echoing(service.journal_show)),
            tool("export_model",
                 "Write the model to a file: .3dm, .stl (3D print mesh "
                 "in millimeters, scale like 1:100), or .txt.",
                 schema({"path": {"type": "string"},
                         "format": {"type": "string"},
                         "scale": {"type": "string"}}, ["path"]))(
                echoing(service.export_model)),
            tool("export_plan",
                 "Cut a horizontal plane at a height (model units) and "
                 "write the 2D floor plan as .svg or .dxf at a paper "
                 "scale like 1:100. Needs Rhino connected.",
                 schema({"height": {"type": "number"},
                         "path": {"type": "string"},
                         "scale": {"type": "string"}}, ["height", "path"]))(
                echoing(service.export_plan)),
            tool("export_section",
                 "Cut a vertical plane at x or y (axis plus position in "
                 "model units) and write the 2D section as .svg or .dxf "
                 "at a paper scale like 1:100. Needs Rhino connected.",
                 schema({"axis": {"type": "string"},
                         "position": {"type": "number"},
                         "path": {"type": "string"},
                         "scale": {"type": "string"}},
                        ["axis", "position", "path"]))(
                echoing(service.export_section)),
            tool("doctor", "Check the setup; say what to fix.",
                 schema({}, []))(echoing(service.doctor)),
            tool("project_info", "Project name, units, journal, listener.",
                 schema({}, []))(echoing(service.project_info)),
        ]
        return tools

    # -- the loop --------------------------------------------------------------------

    async def run(self) -> None:
        say.ok("maquette chat for project {0}. Type /help for commands, "
               "/quit to leave.".format(self.project.name))
        if not sdk_available():
            say.warn("the chat extra is not installed; direct commands work, "
                     "asking Claude will not. fix: pip install 'maquette[chat]'")
        elif not have_auth():
            say.warn("no Claude credentials found; direct commands work, "
                     "asking Claude will not until you sign in.")
        say.ready()
        while True:
            try:
                line = await asyncio.to_thread(input, "maq> ")
            except EOFError:
                say.ok("bye. Transcript saved at {0}".format(
                    self.transcript.text_path))
                break
            except KeyboardInterrupt:
                say.ok("interrupted. Type /quit to leave.")
                continue
            try:
                if not await self.handle(line):
                    break
            except KeyboardInterrupt:
                say.ok("stopped that. Type /quit to leave.")
        await self._close()

    async def _close(self) -> None:
        if self._client is not None:
            try:
                await self._client.disconnect()
            except Exception:  # noqa: BLE001 - exiting anyway
                pass
            self._client = None
        self.transcript.close()


def run(flags: dict, payload: dict) -> int:
    project = find_project(flags.get("project"))
    repl = ChatREPL(project, backend=flags.get("backend", "auto"),
                    model=flags.get("model"))
    asyncio.run(repl.run())
    return 0
