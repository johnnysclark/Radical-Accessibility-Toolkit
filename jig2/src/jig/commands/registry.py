"""Command registry: one grammar shared by the CLI, the REPL, and MCP.

A command is registered under a tuple of words ("bay", "add"); dispatch
matches the longest registered prefix of the input line, then splits the
remainder into positional arguments and --flag values. Handlers receive
(session, args, flags) and return a one-line speakable message; they raise
CommandError for user-correctable problems.
"""

import shlex
from dataclasses import dataclass


class CommandError(Exception):
    """User-facing command failure; message must be speakable."""


@dataclass
class CommandSpec:
    words: tuple
    usage: str
    summary: str
    mutating: bool
    handler: object


_REGISTRY = {}


def command(name, usage, summary, mutating=True):
    words = tuple(name.split())

    def register(handler):
        if words in _REGISTRY:
            raise RuntimeError("duplicate command: {}".format(name))
        _REGISTRY[words] = CommandSpec(words, usage, summary, mutating, handler)
        return handler

    return register


def all_commands():
    return [_REGISTRY[w] for w in sorted(_REGISTRY)]


def find(tokens):
    """Longest registered prefix of tokens -> (spec, remaining_tokens)."""
    for length in range(min(3, len(tokens)), 0, -1):
        spec = _REGISTRY.get(tuple(tokens[:length]))
        if spec:
            return spec, tokens[length:]
    return None, tokens


def tokenize(line):
    try:
        return shlex.split(line)
    except ValueError as exc:
        raise CommandError("could not read the command: {}".format(exc))


def split_flags(tokens):
    """Remaining tokens -> (positional_args, {flag: value}).

    A --flag consumes the next token as its value; a --flag followed by
    another flag or end of line is boolean True.
    """
    args, flags = [], {}
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.startswith("--"):
            key = token[2:]
            if i + 1 < len(tokens) and not tokens[i + 1].startswith("--"):
                flags[key] = tokens[i + 1]
                i += 2
            else:
                flags[key] = True
                i += 1
        else:
            args.append(token)
            i += 1
    return args, flags


def dispatch(session, line):
    """Run one command line against a session. Returns the OK message text;
    raises CommandError on failure. Mutating commands snapshot for undo and
    persist on success; a failed handler never leaves a half-mutated state."""
    tokens = tokenize(line)
    if not tokens:
        raise CommandError("empty command")
    spec, rest = find(tokens)
    if spec is None:
        raise CommandError(
            "unknown command: {}. Say help for the command list.".format(tokens[0]))
    args, flags = split_flags(rest)
    if spec.mutating:
        return session.run_mutation(spec, args, flags)
    return spec.handler(session, args, flags)
