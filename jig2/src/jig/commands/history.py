"""Undo and snapshot commands.

These manage state themselves, so they register as non-mutating to skip the
automatic undo bookkeeping in Session.run_mutation.
"""

import json
import os

from jig.commands.registry import CommandError, command
from jig.commands.util import need_args, to_int
from jig.model.schema import State


@command("undo", "undo [STEPS]", "Undo the last change, or several.",
         mutating=False)
def undo(session, args, flags):
    steps = to_int(args[0], "steps") if args else 1
    done = session.undo(steps)
    return "undid {} change{}".format(done, "" if done == 1 else "s")


@command("snapshot save", "snapshot save NAME", "Save a named checkpoint.",
         mutating=False)
def snapshot_save(session, args, flags):
    need_args(args, 1, "snapshot save NAME")
    session.snapshot_save(args[0])
    return "snapshot {} saved".format(args[0])


@command("snapshot load", "snapshot load NAME",
         "Restore a named checkpoint. The current state goes on the undo stack.",
         mutating=False)
def snapshot_load(session, args, flags):
    need_args(args, 1, "snapshot load NAME")
    path = session.snapshot_path(args[0])
    if not os.path.exists(path):
        names = ", ".join(session.snapshot_list()) or "none"
        raise CommandError("no snapshot named {}. Snapshots: {}".format(args[0], names))
    with open(path, "r", encoding="utf-8") as fh:
        restored = State.from_dict(json.load(fh))
    session.undo_stack.append(session.state)
    session.state = restored
    session.save()
    return "snapshot {} loaded".format(args[0])


@command("snapshot list", "snapshot list", "List saved checkpoints.",
         mutating=False)
def snapshot_list(session, args, flags):
    names = session.snapshot_list()
    if not names:
        return "no snapshots"
    return "{} snapshots: {}".format(len(names), ", ".join(names))


@command("snapshot diff", "snapshot diff NAME",
         "Say what differs between now and a checkpoint.", mutating=False)
def snapshot_diff(session, args, flags):
    need_args(args, 1, "snapshot diff NAME")
    path = session.snapshot_path(args[0])
    if not os.path.exists(path):
        raise CommandError("no snapshot named {}".format(args[0]))
    with open(path, "r", encoding="utf-8") as fh:
        other = json.load(fh)
    current = session.state.to_dict()
    changes = _diff(other, current, "")
    if not changes:
        return "no differences from snapshot {}".format(args[0])
    lines = ["{} differences from snapshot {}".format(len(changes), args[0])]
    lines += changes[:20]
    if len(changes) > 20:
        lines.append("and {} more".format(len(changes) - 20))
    return "\n".join(lines)


def _diff(old, new, path):
    if isinstance(old, dict) and isinstance(new, dict):
        out = []
        for key in sorted(set(old) | set(new)):
            sub = "{}.{}".format(path, key) if path else key
            if key not in old:
                out.append("added {}".format(sub))
            elif key not in new:
                out.append("removed {}".format(sub))
            else:
                out += _diff(old[key], new[key], sub)
        return out
    if isinstance(old, list) and isinstance(new, list):
        if old != new:
            return ["changed {} ({} items, was {})".format(path, len(new), len(old))]
        return []
    if old != new:
        return ["changed {} to {} (was {})".format(path, new, old)]
    return []
