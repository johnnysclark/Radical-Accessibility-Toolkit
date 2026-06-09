"""Export commands."""

import os

from jig.commands.registry import command
from jig.commands.util import need_args


@command("export 3dm", "export 3dm PATH",
         "Write the model to a Rhino .3dm file. Rhino does not need to be running.",
         mutating=False)
def export_3dm(session, args, flags):
    need_args(args, 1, "export 3dm PATH")
    from jig.export.threedm import export_3dm as run_export
    path = os.path.abspath(args[0])
    count = run_export(session.state, path)
    return "wrote {} objects to {}".format(count, path)


@command("export text", "export text PATH",
         "Write the full prose description to a text file.", mutating=False)
def export_text(session, args, flags):
    need_args(args, 1, "export text PATH")
    from jig.export.text import export_text as run_export
    path = os.path.abspath(args[0])
    run_export(session.state, path)
    return "wrote description to {}".format(path)
