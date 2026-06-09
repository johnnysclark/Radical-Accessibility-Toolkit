"""jig command line: one grammar, three front-ends.

    jig site set 180 260          run one command and exit
    jig repl                      interactive session
    jig run "site set 180 260; bay add a 6x4 --spacing 24"

Output contract (screen-reader first): every response starts with OK: or
ERROR:, one fact per line, READY: marks the end of each command, no
spinners, no tables, no decorative characters.
"""

import argparse
import sys

from jig.commands import CommandError, Session
from jig import tts


def build_parser():
    parser = argparse.ArgumentParser(
        prog="jig", add_help=False,
        description="Accessibility-first semantic layout controller for Rhino 8.")
    parser.add_argument("--state", default="state.json",
                        help="path to the state file (default state.json)")
    parser.add_argument("--say", action="store_true",
                        help="speak responses with the macOS say command")
    parser.add_argument("--no-ready", action="store_true",
                        help="suppress the READY: sentinel line")
    parser.add_argument("words", nargs=argparse.REMAINDER,
                        help="a jig command, or repl, or run \"cmd; cmd\"")
    return parser


def respond(message, ok=True, say=False, ready=True):
    prefix = "OK: " if ok else "ERROR: "
    lines = message.split("\n")
    print(prefix + lines[0])
    for line in lines[1:]:
        print(line)
    if ready:
        print("READY:")
    sys.stdout.flush()
    if say:
        tts.speak(lines[0])


def run_line(session, line, say=False, ready=True):
    try:
        message = session.execute(line)
    except CommandError as exc:
        respond(str(exc), ok=False, say=say, ready=ready)
        return False
    respond(message, ok=True, say=say, ready=ready)
    return True


def repl(session, say=False):
    print("OK: jig ready. State file {}. Say help for commands, quit to leave.".format(
        session.state_path))
    print("READY:")
    while True:
        try:
            line = input("jig> ")
        except (EOFError, KeyboardInterrupt):
            print()
            print("OK: goodbye")
            return 0
        line = line.strip()
        if not line:
            continue
        if line in ("quit", "exit"):
            print("OK: goodbye")
            return 0
        run_line(session, line, say=say)


def main(argv=None):
    args = build_parser().parse_args(argv)
    words = list(args.words)
    if words and words[0] == "--":
        words = words[1:]

    if not words:
        print("OK: usage: jig COMMAND, jig repl, or jig run \"cmd; cmd\". "
              "Say jig help for the command list.")
        print("READY:")
        return 0

    session = Session(args.state)

    if words[0] == "repl":
        return repl(session, say=args.say)

    if words[0] == "run":
        if len(words) < 2:
            respond("run needs a quoted list of commands separated by semicolons",
                    ok=False, ready=not args.no_ready)
            return 1
        lines = [part.strip() for part in " ".join(words[1:]).split(";")]
        try:
            outputs = session.run_script(lines)
        except CommandError as exc:
            respond(str(exc), ok=False, say=args.say, ready=not args.no_ready)
            return 1
        respond("\n".join(outputs) if outputs else "nothing to do",
                say=args.say, ready=not args.no_ready)
        return 0

    ok = run_line(session, " ".join(words), say=args.say, ready=not args.no_ready)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
