"""The maquette command line.

Hand-rolled argument handling so every line of output follows the
screen reader contract: OK:/ERROR:/WARNING: prefixes, short lines,
READY: when the command finishes, no usage walls.

    maquette init tower
    maquette box 10 10 30 at 0,0,0 name "tower base"
    maquette describe
    maquette undo
"""

from __future__ import annotations

import json as json_mod
import sys

from maquette import VERSION, describe, grammar, say
from maquette.engine import Engine, USER_ERRORS
from maquette.project import find_project, init_project

HELP_LINES = [
    "Maquette {0}: model anything in Rhino by typing or talking.".format(VERSION),
    "Project commands:",
    "  maquette init NAME            start a new project folder",
    "  maquette describe [OBJECT]    say what is in the model",
    "  maquette measure A B          distance between objects or points",
    "  maquette journal              recent steps (--last N, --search WORD)",
    "  maquette undo [N]             undo the last N steps",
    "  maquette rebuild              replay the journal into the backend",
    "  maquette export PATH          write 3dm, stl for printing, or txt",
    "  maquette plan HEIGHT PATH     cut a 2D floor plan, write svg or dxf",
    "  maquette section x|y AT PATH  cut a 2D section, write svg or dxf",
    "  maquette run-script FILE      run Python in Rhino, journaled (--intent)",
    "  maquette doctor               check the setup and say what to fix",
    "  maquette install-listener     put the listener script where Rhino finds it",
    "  maquette connect              check or start the Rhino connection",
    "  maquette listener-stop        stop the listener inside Rhino",
    "  maquette chat                 talk to Claude about the model",
    "  maquette commands             list modeling commands",
    "Modeling commands run directly, for example:",
    '  maquette box 10 10 30 name "tower base"',
    "  maquette move m1 by 0,0,10",
    "Global flags: --project PATH, --backend record|headless|live|auto,",
    "  --scale 1:100 (for stl, plan, section), --all (no output cap),",
    "  --json (machine readable line at the end).",
]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    flags, args = _take_flags(args)
    code, payload = 0, {"ok": True, "lines": [], "warnings": []}
    try:
        code = _dispatch(args, flags, payload)
    except USER_ERRORS + (ValueError, OSError) as exc:
        say.err(str(exc))
        payload.update(ok=False, error=str(exc))
        code = 1
    except KeyboardInterrupt:
        say.err("stopped.")
        payload.update(ok=False, error="interrupted")
        code = 1
    if flags["json"]:
        print(json_mod.dumps(payload))
    say.ready()
    return code


def _take_flags(args: list[str]) -> tuple[dict, list[str]]:
    flags = {"project": None, "backend": "auto", "json": False, "all": False,
             "units": "meters", "intent": None, "format": None,
             "last": None, "search": None, "name": None, "dest": None,
             "model": None, "inject": False, "scale": None}
    kept = []
    index = 0
    valued = {"--project": "project", "-p": "project", "--backend": "backend",
              "--units": "units", "--intent": "intent", "--format": "format",
              "--last": "last", "--search": "search", "--name": "name",
              "--dest": "dest", "--model": "model", "--scale": "scale"}
    booleans = {"--json": "json", "--all": "all", "--inject": "inject"}
    while index < len(args):
        arg = args[index]
        if arg in valued:
            if index + 1 >= len(args):
                kept.append(arg)
                index += 1
                continue
            flags[valued[arg]] = args[index + 1]
            index += 2
        elif arg in booleans:
            flags[booleans[arg]] = True
            index += 1
        else:
            kept.append(arg)
            index += 1
    return flags, kept


def _engine(flags: dict, actor: str = "cli") -> Engine:
    project = find_project(flags["project"])
    return Engine(project, backend=flags["backend"], actor=actor)


def _report(result: dict) -> None:
    lines = result.get("lines") or ["done."]
    say.ok(lines[0])
    for line in lines[1:]:
        say.info(line)
    for warning in result.get("warnings", []):
        say.warn(warning)


def _dispatch(args: list[str], flags: dict, payload: dict) -> int:
    if not args or args[0] in ("help", "--help", "-h"):
        say.ok(HELP_LINES[0])
        say.page(HELP_LINES[1:], show_all=True)
        payload["lines"] = HELP_LINES
        return 0
    command = args[0]
    rest = args[1:]

    if command == "version":
        say.ok("maquette {0}.".format(VERSION))
        return 0

    if command == "commands":
        lines = grammar.help_lines()
        say.page(lines, show_all=flags["all"])
        payload["lines"] = lines
        return 0

    if command == "init":
        if not rest:
            say.err("say the project name: maquette init NAME")
            payload["ok"] = False
            return 1
        project = init_project(flags["project"] or rest[0], name=rest[0],
                               units=flags["units"])
        say.ok("created project {0} at {1}, units {2}.".format(
            project.name, project.root, project.units))
        say.info("next: cd {0}, then try: maquette box 10 10 30".format(
            project.root))
        payload["lines"] = ["created project {0}".format(project.root)]
        return 0

    if command == "describe":
        engine = _engine(flags)
        scene = engine.scene()
        if rest:
            ref = " ".join(rest)
            obj = scene.find(ref)
            if obj is None and rest[0] == "object" and len(rest) > 1:
                # Tolerate the spoken filler: describe object "tower base".
                ref = " ".join(rest[1:])
                obj = scene.find(ref)
            if obj is None:
                say.err("no object called {0!r}. Try: maquette describe".format(ref))
                payload["ok"] = False
                return 1
            lines = describe.object_detail(obj, scene)
        else:
            lines = describe.brief(scene) if not flags["all"] else describe.full(scene)
        say.ok(lines[0])
        say.page(lines[1:], show_all=flags["all"])
        payload["lines"] = lines
        return 0

    if command == "measure":
        if len(rest) != 2:
            say.err("usage: maquette measure A B "
                    "(objects by id or quoted name, or points like 0,0,0)")
            payload["ok"] = False
            return 1
        engine = _engine(flags)
        lines = describe.measure(engine.scene(), rest[0], rest[1])
        say.ok(lines[0])
        for line in lines[1:]:
            say.info(line)
        payload["lines"] = lines
        return 0

    if command == "journal":
        engine = _engine(flags)
        last = int(flags["last"]) if flags["last"] else (0 if flags["all"] else 10)
        lines = describe.journal_lines(engine.entries(), last=last,
                                       search=flags["search"])
        say.ok("journal for project {0}:".format(engine.project.name))
        say.page(lines, show_all=flags["all"])
        payload["lines"] = lines
        return 0

    if command == "undo":
        steps = int(rest[0]) if rest else 1
        result = _engine(flags).undo_steps(steps)
        _report(result)
        payload.update(result)
        return 0

    if command == "rebuild":
        result = _engine(flags).rebuild(
            None if flags["backend"] == "auto" else flags["backend"])
        _report(result)
        payload.update(result)
        return 0

    if command == "export":
        if not rest:
            say.err("usage: maquette export PATH "
                    "(ending in .3dm, .stl, or .txt)")
            payload["ok"] = False
            return 1
        result = _engine(flags).export(rest[0], flags["format"],
                                       flags["scale"])
        _report(result)
        payload.update(result)
        return 0

    if command == "plan":
        if len(rest) != 2:
            say.err("usage: maquette plan HEIGHT PATH "
                    "(svg or dxf; --scale 1:100)")
            payload["ok"] = False
            return 1
        result = _engine(flags).export_plan(rest[0], rest[1], flags["scale"])
        _report(result)
        payload.update(result)
        return 0

    if command == "section":
        if len(rest) != 3:
            say.err("usage: maquette section x|y POSITION PATH "
                    "(svg or dxf; --scale 1:100)")
            payload["ok"] = False
            return 1
        result = _engine(flags).export_section(rest[0], rest[1], rest[2],
                                               flags["scale"])
        _report(result)
        payload.update(result)
        return 0

    if command == "run-script":
        if not rest:
            say.err("usage: maquette run-script FILE --intent \"what it does\"")
            payload["ok"] = False
            return 1
        with open(rest[0], "r", encoding="utf-8") as handle:
            code = handle.read()
        op = {"op": "script",
              "params": {"code": code, "intent": flags["intent"] or ""}}
        if flags["name"]:
            op["name"] = flags["name"]
        result = _engine(flags).run_op(op)
        _report(result)
        payload.update(result)
        return 0

    if command == "doctor":
        from maquette import doctor
        return doctor.run(flags, payload)

    if command == "install-listener":
        from maquette import install
        return install.run(flags, payload)

    if command == "connect":
        from maquette import doctor
        return doctor.connect(flags, payload)

    if command == "listener-stop":
        from maquette import doctor
        return doctor.listener_stop(flags, payload)

    if command == "chat":
        from maquette import chat
        return chat.run(flags, payload)

    if grammar.is_command(command):
        result = _engine(flags).run_op(grammar.parse_tokens(args))
        _report(result)
        payload.update(result)
        return 0

    say.err("unknown command {0!r}. Try: maquette help".format(command))
    payload["ok"] = False
    return 1


if __name__ == "__main__":
    sys.exit(main())
