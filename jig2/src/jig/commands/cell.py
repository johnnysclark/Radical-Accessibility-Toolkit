"""Cell commands: naming the rooms of a bay grid."""

from jig.commands.registry import CommandError, command
from jig.commands.util import need_args, need_bay, to_int
from jig.model.io import mint_id
from jig.model.schema import Cell


def _cell_indices(bay, i_token, j_token):
    i = to_int(i_token, "column index")
    j = to_int(j_token, "row index")
    nx, ny = bay.counts
    if not (0 <= i < nx and 0 <= j < ny):
        raise CommandError("bay {} cells run 0,0 to {},{}; got {},{}".format(
            bay.name, nx - 1, ny - 1, i, j))
    return i, j


@command("cell set", "cell set BAY I J NAME [--label TEXT]",
         "Name the room at grid cell I,J of a bay.")
def cell_set(session, args, flags):
    need_args(args, 4, "cell set BAY I J NAME")
    bay = need_bay(session, args[0].lower())
    i, j = _cell_indices(bay, args[1], args[2])
    name = args[3]
    label = str(flags.get("label", "")) or name
    existing = bay.find_cell(i, j)
    if existing:
        existing.name = name
        existing.label = label
        return "cell {},{} of bay {} renamed to {}".format(i, j, bay.name, name)
    cell = Cell(id=mint_id("c", session.state.all_ids()),
                at=[i, j], name=name, label=label)
    bay.cells.append(cell)
    return "cell {},{} of bay {} named {}".format(i, j, bay.name, name)


@command("cell clear", "cell clear BAY I J", "Remove the name from a cell.")
def cell_clear(session, args, flags):
    need_args(args, 3, "cell clear BAY I J")
    bay = need_bay(session, args[0].lower())
    i, j = _cell_indices(bay, args[1], args[2])
    cell = bay.find_cell(i, j)
    if cell is None:
        raise CommandError("cell {},{} of bay {} has no name".format(i, j, bay.name))
    bay.cells.remove(cell)
    return "cell {},{} of bay {} cleared".format(i, j, bay.name)


@command("cell list", "cell list BAY", "List a bay's named cells.", mutating=False)
def cell_list(session, args, flags):
    need_args(args, 1, "cell list BAY")
    bay = need_bay(session, args[0].lower())
    if not bay.cells:
        return "bay {} has no named cells".format(bay.name)
    lines = ["bay {} has {} named cells".format(bay.name, len(bay.cells))]
    for c in sorted(bay.cells, key=lambda c: (c.at[1], c.at[0])):
        lines.append("cell {},{}: {} labeled {}".format(c.at[0], c.at[1], c.name, c.label))
    return "\n".join(lines)
