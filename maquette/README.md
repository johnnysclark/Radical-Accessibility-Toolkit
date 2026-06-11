# Maquette

Model anything in Rhino 8 for Mac by typing or talking. Built
accessibility-first: every line of output is short, prefixed OK: or
ERROR:, and ends with READY: so a screen reader user always knows what
happened. No spinners, no tables, no streaming, nothing visual required.

A maquette is the small working model an architect builds to think with.
This tool is that model, made of text.

What the workflow gives you, end to end:

1. Drive Rhino by typing or talking - geometry appears as you speak.
2. Design schematic architecture from scratch with a small, speakable
   command vocabulary (boxes, cylinders, extrusions, booleans).
3. Get deliverables out: 2D plans and sections as SVG or DXF, a
   watertight STL scaled in millimeters for 3D printing, the .3dm
   itself, or a plain text description.

## The one idea

Your work lives in a journal file, not in Rhino. Every command appends
one line to `journal.jsonl`; Rhino just renders it. Rhino can crash,
close, or never open at all - nothing is lost. `maquette rebuild`
replays the journal and the model comes back.

Three backends, picked automatically:

- live: Rhino 8 is running with the Maquette listener; geometry appears
  as you type and Rhino reports real measured sizes.
- headless: no Rhino, but the rhino3dm package builds a real
  `exports/model.3dm` op by op. Booleans, lofts, and scripts wait
  (marked pending) for the next live rebuild.
- record: nothing installed at all; intent is journaled with computed
  bounding boxes, and everything becomes real later.

A downgrade is always announced out loud, never silent. Plans,
sections, and STL exports always need the live backend, because Rhino
does that geometry math.

## Install (on the Mac)

From the repository root:

    pip install -e "maquette[headless,mcp,chat]"

Then connect Rhino, once:

    maquette install-listener

It prints four numbered steps (add one Rhino startup command, restart
Rhino). When Rhino starts, its command line says:
[Maquette] Listening on 127.0.0.1:6270. After that, check everything:

    maquette doctor

Every problem comes with the exact fix. To verify the whole stack in
one go, run `python3 maquette/scripts/mac_verify.py`: it models into
Rhino, exports an STL and a plan, and prints PASS or FAIL per check.
VERIFY-MAC.md is the long form.

## Design something: a first building

Commands are sentences. Say them in the terminal, or later through
chat. With Rhino open you hear the OK line and the shape appears in
the same breath.

    maquette init studio
    cd studio
    maquette rect 30 20 at 0,0 name "site"
    maquette box 12 10 9 at 2,2,0 name "north wing"
    maquette box 10 8 6 at 16,6,0 name "south wing"
    maquette cylinder radius 2 height 12 at 14,4,0 name "stair core"
    maquette union "north wing" "south wing" "stair core" name "building"
    maquette describe

Every mutation answers with one line, like:
OK: created m2 "north wing" (box), 12 by 10 by 9, at 2,2,0, on layer
MAQ::Default.

Carve a courtyard by subtracting a volume. Booleans consume their
inputs and make a new object, so name the result:

    maquette box 4 4 9 at 6,5,0 name "courtyard void"
    maquette difference "building" minus "courtyard void" name "carved building"

Interrogate and adjust without ever looking at the screen:

    maquette describe "carved building"
    maquette measure "carved building" 0,0,0
    maquette move "carved building" by 0,0,0.5
    maquette undo
    maquette journal

`maquette commands` lists the whole grammar: point, line, polyline,
circle, arc, rect, curve, text, box, sphere, cylinder, cone, extrude,
loft, revolve, union, difference, intersect, move, rotate, scale,
mirror, copy, delete, rename, layer, put, group, ungroup. References
are ids like m3, quoted names like "north wing", or the word last.
Coordinates are comma-joined: 10,0,5. Every command takes
`name "..."` and `layer "..."`.

Undo is real and deep: deletes restore with their transform history,
booleans resurrect their consumed inputs. `maquette journal` reads the
history back, one speakable line per step.

## Drawings and prints

These three commands turn the model into deliverables. All of them
need Rhino running (Rhino computes the cuts and the meshes); if it is
not, the error says exactly that and how to fix it.

Scales read the way architects say them: at 1:100, one meter of
building becomes 10 millimeters on paper or print. The default is
1:100 everywhere; change it with `--scale 1:200` and the spoken
summary always repeats the scale and the resulting size, so nothing
is a surprise at the printer.

### 2D plans

    maquette plan 1.2 exports/plan-ground.svg
    maquette plan 4.5 exports/plan-upper.dxf --scale 1:200

A plan is a horizontal cut at a height in model units. Every solid
and surface the plane passes through contributes its outline. You
hear: where it cut, how many objects, how many outlines, the scale,
and the sheet size in millimeters. If the plane misses the model, the
error tells you the heights the model actually spans.

### 2D sections

    maquette section x 8 exports/section-a.svg
    maquette section y 7 exports/section-b.dxf

A section is a vertical cut: `section x 8` slices across x at 8, and
the drawing keeps z pointing up. Same spoken summary as plans.

SVG opens in any browser and prints directly (swell paper included);
DXF drops into Rhino, Illustrator, or laser cutter software. Both are
drawn in real paper millimeters.

### 3D print (watertight STL)

    maquette export exports/building.stl --scale 1:200

Rhino meshes every solid at render quality; Maquette checks each
shell is closed and writes a binary STL in millimeters. You hear the
triangle count, the print size (so you know it fits the bed before
you walk to the printer), and `watertight: yes` - or a WARNING naming
exactly which objects have open edges and how to close them. Booleans
already merged into one shell print cleanest; overlapping separate
solids also slice fine in modern slicers.

### The model itself

    maquette export exports/building.3dm     full Rhino geometry
    maquette export exports/building.txt     the spoken description

## Talking to Claude

Two ways, same fifteen functions, same spoken output.

### maquette chat

A dedicated conversation in the terminal:

    maq> box 10 10 30 name "tower base"     <- instant, no model involved
    maq> give the tower a sloped roof       <- Claude models it
    maq> cut a ground floor plan to exports/plan.svg
    maq> /scene                              <- what is there now
    maq> /quit

Replies print complete, never word by word. Every session is saved to
`transcripts/` as plain text plus JSONL. Sign-in options, in order of
ease: the Claude Code login you already have (claude login), a token
from `claude setup-token`, or an ANTHROPIC_API_KEY environment variable.

### Claude Code

Add to your `.mcp.json` (project scope) and approve it on first use:

    {
      "mcpServers": {
        "maquette": {
          "type": "stdio",
          "command": "python3",
          "args": ["-m", "maquette.mcp_server", "--project", "/path/to/studio"]
        }
      }
    }

Claude Code then has create_objects, edit_objects, query_scene,
describe_scene, describe_object, measure, run_script, undo, rebuild,
journal_show, export_model, export_plan, export_section, doctor, and
project_info.

### Beyond the vocabulary

`run_script` (or `maquette run-script file.py --intent "..."`) runs
rhinoscriptsyntax inside Rhino, journaled and replayable like
everything else. The required intent sentence is what the journal
reads aloud. That is the "model anything" escape hatch.

## When Rhino crashes

Nothing to do. Reopen Rhino (the listener starts itself), then:

    maquette rebuild

The journal replays; WARNING lines call out any drift. If the listener
ever needs a kick without touching the Rhino UI:

    maquette connect --inject

## Project layout

A project folder holds `maquette.json` (settings), `journal.jsonl`
(the truth), `snapshot.json` (a cache, safe to delete), `exports/`
(your 3dm, STL, and drawing files), and `transcripts/`.

## For developers

    pip install -e "maquette[dev]"          # engine is stdlib-only
    python3 -m pytest maquette/tests -q

The engine never imports outside the standard library (a test enforces
it); rhino3dm, mcp, and claude-agent-sdk live behind extras. The
in-Rhino listener is one self-contained file with seven request types;
all op knowledge - including the meshing and plane-cut queries behind
STL, plan, and section - compiles client-side, so new ops never
require touching the Mac. CI runs the real listener over real sockets.
