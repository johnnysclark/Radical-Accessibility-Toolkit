"""Chat REPL: routing, direct execution, the ask path with a fake
client, graceful degradation without SDK or credentials, transcripts."""

import asyncio
import json
import os

import pytest

pytest.importorskip("claude_agent_sdk")

from claude_agent_sdk import (AssistantMessage, ResultMessage,  # noqa: E402
                              TextBlock, ToolUseBlock)

from maquette import chat  # noqa: E402
from maquette.chat import ChatREPL, route  # noqa: E402


def test_route():
    assert route("") == "empty"
    assert route("   ") == "empty"
    assert route("/quit") == "quit"
    assert route("exit") == "quit"
    assert route("/help") == "meta"
    assert route("/journal 5") == "meta"
    assert route("box 10 10 30") == "direct"
    assert route('rename m1 "tower"') == "direct"
    assert route("make me a spiral stair") == "ask"
    assert route("how tall is the tower?") == "ask"


class ExplodingFactory:
    """A client factory that must never be called."""

    def __init__(self):
        self.called = False

    async def __call__(self):
        self.called = True
        raise AssertionError("the LLM must not be involved")


class FakeClient:
    def __init__(self, messages):
        self.messages = messages
        self.queries = []

    async def query(self, text):
        self.queries.append(text)

    async def receive_response(self):
        for message in self.messages:
            yield message

    async def disconnect(self):
        pass


def make_repl(project, factory=None):
    return ChatREPL(project, backend="record", client_factory=factory)


def handle(repl, line):
    return asyncio.run(repl.handle(line))


def test_direct_commands_never_touch_the_model(project, capsys):
    factory = ExplodingFactory()
    repl = make_repl(project, factory)
    assert handle(repl, "box 10 10 30 name \"tower base\"") is True
    assert handle(repl, "/scene") is True
    assert handle(repl, "/undo 1") is True
    out = capsys.readouterr().out
    assert 'OK: created m1 "tower base" (box)' in out
    assert "1 object on 1 layer." in out
    assert "undoing step 1" in out
    assert out.count("READY:") == 3
    assert factory.called is False
    asyncio.run(repl._close())


def test_ask_path_speaks_buffered_reply(project, capsys, monkeypatch):
    monkeypatch.setattr(chat, "have_auth", lambda: True)
    fake = FakeClient([
        AssistantMessage(content=[
            ToolUseBlock(id="t1", name="mcp__maquette__create_objects",
                         input={})], model="m"),
        AssistantMessage(content=[
            TextBlock(text="Done. The tower base is ten by ten by thirty.")],
            model="m"),
        ResultMessage(subtype="success", duration_ms=1, duration_api_ms=1,
                      is_error=False, num_turns=1, session_id="s"),
    ])

    async def factory():
        return fake

    repl = make_repl(project, factory)
    assert handle(repl, "please make a tower base") is True
    out = capsys.readouterr().out
    assert "OK: asking Claude." in out
    assert "OK: Claude uses create_objects." in out
    assert "CLAUDE: Done. The tower base is ten by ten by thirty." in out
    assert out.rstrip().endswith("READY:")
    assert fake.queries == ["please make a tower base"]
    asyncio.run(repl._close())


def test_ask_without_sdk_names_the_extra(project, capsys, monkeypatch):
    monkeypatch.setattr(chat, "sdk_available", lambda: False)
    repl = make_repl(project, ExplodingFactory())
    handle(repl, "model something")
    out = capsys.readouterr().out
    assert "pip install 'maquette[chat]'" in out
    assert "Direct commands still work" in out
    asyncio.run(repl._close())


def test_ask_without_credentials_gives_numbered_fixes(project, capsys,
                                                      monkeypatch):
    monkeypatch.setattr(chat, "have_auth", lambda: False)
    repl = make_repl(project, ExplodingFactory())
    handle(repl, "model something")
    out = capsys.readouterr().out
    assert "ERROR: no Claude credentials found." in out
    assert "1. Easiest: sign in to Claude Code" in out
    assert "3. Or set the ANTHROPIC_API_KEY" in out
    asyncio.run(repl._close())


def test_client_error_is_spoken_not_raised(project, capsys, monkeypatch):
    monkeypatch.setattr(chat, "have_auth", lambda: True)

    async def factory():
        raise RuntimeError("no internet")

    repl = make_repl(project, factory)
    assert handle(repl, "model something") is True
    out = capsys.readouterr().out
    assert "ERROR: the Claude call failed: no internet" in out
    asyncio.run(repl._close())


def test_tool_server_exposes_all_thirteen(project):
    repl = make_repl(project)
    tools = repl._build_tools()
    assert {tool.name for tool in tools} == set(chat.TOOL_NAMES)
    server_config = repl._tool_server()
    assert server_config.get("type") == "sdk"
    asyncio.run(repl._close())


def test_tool_handler_echoes_to_stdout_and_transcript(project, capsys):
    repl = make_repl(project)
    by_name = {tool.name: tool for tool in repl._build_tools()}
    result = asyncio.run(by_name["create_objects"].handler({"ops": [
        {"op": "create_box", "params": {"corner": [0, 0, 0],
                                        "size": [5, 5, 5]}}]}))
    out = capsys.readouterr().out
    assert 'OK: created m1 "box 1" (box)' in out
    assert "box 1" in result["content"][0]["text"]
    # The model and the user heard exactly the same words.
    assert result["content"][0]["text"].splitlines()[0] in out
    asyncio.run(repl._close())
    transcript = open(repl.transcript.text_path, encoding="utf-8").read()
    assert "box 1" in transcript


def test_transcript_files(project, capsys):
    repl = make_repl(project, ExplodingFactory())
    handle(repl, "box 2 2 2")
    handle(repl, "/quit")
    asyncio.run(repl._close())
    text = open(repl.transcript.text_path, encoding="utf-8").read()
    assert "YOU: box 2 2 2" in text
    assert 'created m1 "box 1" (box)' in text
    assert "YOU: /quit" in text
    with open(repl.transcript.jsonl_path, encoding="utf-8") as handle_:
        rows = [json.loads(line) for line in handle_]
    assert rows[0]["role"] == "YOU"
    assert any(row["role"] == "STATUS" for row in rows)
    assert os.path.dirname(repl.transcript.text_path).endswith("transcripts")
