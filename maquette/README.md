# Maquette

Model anything in Rhino 8 for Mac by typing or talking. Built
accessibility-first: every line of output is short, prefixed OK: or
ERROR:, and ends with READY: so a screen reader user always knows what
happened. No spinners, no tables, no streaming, nothing visual required.

A maquette is the small working model an architect builds to think with.
This tool is that model, made of text.

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

A downgrade is always announced out loud, never silent.

## Install (on the Mac)

    pip install -e "maquette[headless,mcp,chat]"

Then connect Rhino, once:

    maquette install-listener

It prints four numbered steps (add one Rhino startup command, restart
Rhino). After that, check everything:

    maquette doctor

Every problem comes with the exact fix. `python3 maquette/scripts/mac_verify.py`
runs the full PASS/FAIL checklist; VERIFY-MAC.md is the long form.

## Quick start

    maquette init tower
    cd tower
    maquette box 10 10 30 at 0,0,0 name "tower base"
    maquette cylinder radius 3 height 40 at 20,0,0
    maquette describe
    maquette move "tower base" by 0,0,5
    maquette undo
    maquette export exports/tower.3dm

`maquette commands` lists the whole grammar: point, line, polyline,
circle, arc, rect, curve, text, box, sphere, cylinder, cone, extrude,
loft, revolve, union, difference, intersect, move, rotate, scale,
mirror, copy, delete, rename, layer, put, group, ungroup. References
are ids like m3, quoted names like "tower base", or the word last.
Coordinates are comma-joined: 10,0,5. Every command takes
`name "..."` and `layer "..."`.

Undo is real and deep: deletes restore with their transform history,
booleans resurrect their consumed inputs. `maquette journal` reads the
history back, one speakable line per step.

## Talking to Claude

Two ways, same thirteen functions, same spoken output.

### maquette chat

A dedicated conversation in the terminal:

    maq> box 10 10 30 name "tower base"     <- instant, no model involved
    maq> give the tower a sloped roof       <- Claude models it
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
          "args": ["-m", "maquette.mcp_server", "--project", "/path/to/tower"]
        }
      }
    }

Claude Code then has create_objects, edit_objects, query_scene,
describe_scene, describe_object, measure, run_script, undo, rebuild,
journal_show, export_model, doctor, and project_info.

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
(the truth), `snapshot.json` (a cache, safe to delete), `exports/`,
and `transcripts/`.

## For developers

    pip install -e "maquette[dev]"          # engine is stdlib-only
    python3 -m pytest maquette/tests -q

The engine never imports outside the standard library (a test enforces
it); rhino3dm, mcp, and claude-agent-sdk live behind extras. The
in-Rhino listener is one self-contained file with seven request types;
all op knowledge compiles client-side, so new ops never require
touching the Mac. CI runs the real listener over real sockets.
