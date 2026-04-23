# Faculty Guide

A plain-language overview of the Radical Accessibility Toolkit for
architecture faculty who will be working with Daniel Bein in the coming
academic year. This guide is not a developer reference. It is here to give
you a working mental model of the tools Daniel uses, the vocabulary the
project uses to talk about them, and enough footing to participate in
reviews, respond to a tactile print, and know which tool to reach for when
a student asks a question.

For setup and installation, see the root [README](../README.md). A student
TA or Daniel himself will typically handle any install work. You are not
expected to run `git` or Python from a terminal to use this guide.

---

## Who This Guide Is For

The project is co-designed with Daniel Bein, a blind architecture student
at UIUC. His daily workflow — designing, reviewing, fabricating,
presenting — is the test case for every tool in this repository. The
faculty leads are John Clark and Hugh Swiatek, with student researchers
Ethan Anderson, Isaac Tu, and Laura Heuser.

If you are a visiting, adjunct, or new faculty colleague joining the
studio or a related course, this guide is the short path into how Daniel
works and how you can participate. You do not need to write code. You do
need to understand what each tool produces, so that when Daniel hands you
a tactile print, plays a screen-reader description, or pushes a change to
the project, you can meet him halfway.

---

## The One Rule

The project has one core commitment:

> If it can't be heard, felt, or read by a screen reader, it doesn't ship.

Everything else follows from this. The design itself lives in a single
plain-text file called `state.json`. The 3D model in Rhino is a viewer,
not the source of truth. If Rhino crashes or nothing is on screen, the
design is still intact — it is the JSON file. This matters for you
because it changes what a design review looks like. You are not looking
at a screen together. You are both working from the same text record,
the same tactile print, and the same 3D print.

---

## How The System Is Organized

The project uses six terms precisely. Knowing them will save you hours
of confusion. The full definitions are in [CLAUDE.md](../CLAUDE.md); the
short forms are below.

**Tool.** A major capability module. Layout Jig, TACT, TASC, Image
Describer, Rhino Viewer, Web UI. When we say "the tools," we mean these.

**Command.** A single action inside a tool. `set bay A rotation 30` is a
command. `wall A on` is a command. Commands always print a one-line
confirmation starting with `OK:` or `ERROR:`.

**Macro.** A saved sequence of commands that Daniel can replay, like a
keyboard shortcut that runs a recipe. Stored as JSON.

**Template.** A starting state — a blank floor plan set up for a studio
project, for example. Loading a template replaces the current design.

**Skill.** A capability that Claude Code, the AI assistant, knows how to
invoke on its own. Different from a macro; skills are for the AI, macros
are for the human.

**MCP function.** The technical name for how Claude talks to the tools.
You will not use these directly, but you may hear them referenced.

---

## The Tools

Each tool below follows the same shape: what it is, when to reach for
it, a minimal example, and a pointer to the full reference.

### Layout Jig — the primary design tool

*What it is.* The main modeler. Walls, bays, corridors, zones, rooms,
doors, windows, structural grids, section cuts, legends, and exports all
live here.

*When to reach for it.* Any time Daniel is placing or changing building
geometry. This is the tool he lives in.

*Minimal example.*

    >> set bay A rotation 30
    OK: Bay A rotation = 30 degrees.

*Full reference.* [docs/MANUAL.md](./MANUAL.md) has the complete command
list. Entry point is `python controller/controller_cli.py`.

### Image Describer — turn an image into readable text

*What it is.* Takes an architectural image — plan, section, photograph,
precedent, sketch — and produces a structured text description at three
scales: Macro (what it is), Meso (how it is organized), Micro (specific
elements and measurements).

*When to reach for it.* When a sighted collaborator or instructor
shares an image — a precedent study, a trace-paper sketch, a reference
photograph — and Daniel needs to understand it without looking.

*Minimal example.*

    >> describe farnsworth_plan.jpg

*Full reference.* See the Image Describer section of the root
[README](../README.md). Source lives at `tools/image-describer/`.

### TACT — tactile graphics on swell paper

*What it is.* Converts either an image or the current `state.json` into
a PIAF-ready tactile drawing. PIAF is a thermal swell paper: black lines
rise off the page as raised ridges Daniel can read by touch. TACT handles
the scaling, density, OCR of any embedded text, and Grade 2 Braille
labels.

*When to reach for it.* Every review. Every pin-up equivalent. Any time
Daniel needs a physical plan in his hands.

*Minimal example.*

    >> tact render state.json --output plan.pdf

*Full reference.* [tools/tact/README.md](../tools/tact/README.md).

### TASC — site-scale scripting

*What it is.* A command-line tool aimed at site-scale moves: place a
site boundary, drop zones, lay out bays, export. Complementary to Layout
Jig, which is oriented to building-scale detail.

*When to reach for it.* Early-phase site work. Master-planning problems.
Projects where the first moves are zones and bays rather than walls and
doors.

*Minimal example.*

    >> tasc site 300 200

*Full reference.* [tools/tasc/README.md](../tools/tasc/README.md).

### Rhino Viewer — the 3D consumer

*What it is.* A passive watcher running inside Rhino 8. It reads
`state.json`, and whenever the file changes, it rebuilds the 3D model.
Daniel does not interact with Rhino directly. You may, if you want to
see the design on a screen during a review.

*When to reach for it.* Never deliberately for Daniel's workflow. For
sighted participants in a review, it can be useful as a reference view
on a second monitor.

*Minimal example.* None — the watcher runs in the background and
responds to file changes automatically.

*Full reference.* `tools/rhino/rhino_watcher.py` and the RhinoScript
quick reference in [CLAUDE.md](../CLAUDE.md).

### 3D Tactile Export — printable scale models

*What it is.* A pure-Python exporter that turns `state.json` into a
watertight STL mesh, scaled for a Bambu Lab P1S printer. Walls,
corridors, and door openings are physically present at 1:200.

*When to reach for it.* When a tactile print on paper is not enough —
vertical relationships, open spans, the rhythm of structural bays. The
3D print is slow (hours), so plan the review around the turnaround.

*Minimal example.* Triggered from inside Layout Jig:

    >> tactile3d on

*Full reference.* Source at `tools/rhino/tactile_print.py`. The Layout
Jig section of [docs/MANUAL.md](./MANUAL.md) documents the related
commands.

### Web UI — the accessible Claude Code client

*What it is.* A browser-based interface for Claude Code that strips
markdown, ANSI codes, and emoji so JAWS and NVDA screen readers can
read it cleanly. Daniel uses this instead of the default terminal UI.

*When to reach for it.* Any session that involves Claude Code and a
screen reader. If you see Daniel working in a browser window rather
than a terminal, this is why.

*Minimal example.* Launched with `start-webui.sh` on WSL or
`start-webui.bat` on Windows.

*Full reference.* [tools/webui/README.md](../tools/webui/README.md).

### Screen Reader Hooks — audio event announcements

*What it is.* Small scripts that fire when Claude Code does something
noteworthy — detects an image, finishes a conversion, captures feedback —
and speak a short announcement through JAWS's TTS API.

*When to reach for it.* You will not invoke these directly. They are
worth knowing about because when you hear a chime or short phrase
during Daniel's sessions, that is the hook speaking, not Daniel or the
model.

*Full reference.* `tools/webui/hooks/`.

---

## Working With Daniel

A studio review when the design lives in text and tactile prints works
differently from a pin-up. The shape below is drawn from
[DESIGN_SESSION.md](../DESIGN_SESSION.md), the project's worked example
of Daniel designing an elementary school end to end. Read it in full at
least once.

### Bring the right artifacts

Daniel typically arrives at a review with three things: a PIAF tactile
print of the current plan, a 3D print of the model (when the geometry
warrants it), and a laptop running Claude Code. Any of the three is a
valid starting point for discussion. All three describe the same
`state.json`.

### Read the printout, not the screen

During review, avoid describing what you see on the Rhino viewport or
on your own screen. Read what the CLI printed. Every command prints a
one-line confirmation — "Bay A corridor width = 12.0 ft. Was 8.0." —
that describes the change in plain language. That line is the shared
vocabulary for the room.

### Tactile turnaround times

A PIAF print takes a few minutes: laser print on microcapsule paper,
feed through the heater, read. A 3D print takes hours. Plan the review
session around the artifact you actually need. Quick iteration is
PIAF. A milestone review with formal presentation is 3D.

### Read state.json like a pull request

The design file is human-readable text with stable IDs. A change from
`corridor.width: 8.0` to `corridor.width: 12.0` is as easy to parse as
a commit diff — arguably easier. If you are comfortable reading code
review diffs, you can review a plan change the same way. Git history
on the state file gives you the full design history.

### Pacing

Daniel's sessions tend to be short and deterministic. The system is
built so that nothing is lost between sessions — the state file
survives crashes, restarts, and power cuts — so there is no penalty to
stopping cleanly and resuming later. If you are used to all-nighter
charettes, recalibrate. Short, repeated, reviewable sessions are the
grain of this workflow.

### Screen reader etiquette

Keep pauses in your speech. JAWS reads on command, not continuously,
and Daniel is often toggling between you and the reader. Do not
describe images unless asked — the Image Describer is the tool for
that, and it does it more precisely than a live description. When in
doubt, ask.

---

## Common First Tasks

If you have thirty minutes and want to get oriented, try these in
order. None requires you to install anything; all are things you can
ask Daniel or a student TA to show you.

1. *Hear the current design.* In Layout Jig, run `describe`. The full
   model state reads back in plain language. This is the single best
   way to understand what is currently designed.

2. *Print a tactile plan.* Run `tact render state.json` and feed the
   output through the PIAF heater. Hold the result. Trace a corridor.
   Find a door. This is what a review artifact feels like.

3. *Understand a precedent image.* Pick an image Daniel is working
   from and run the Image Describer on it. Read the Macro, Meso, and
   Micro output.

4. *See the 3D model.* Open Rhino 8 with the watcher running. Make a
   small change in Layout Jig (`corridor A width 10` is safe). Watch
   Rhino rebuild.

After those four, you have touched every tool in this guide at least
once.

---

## Where To Go Next

In reading order:

1. [README.md](../README.md) — project vision, setup, full tool list.
2. [CLAUDE.md](../CLAUDE.md) — the authoritative taxonomy and coding
   conventions. Skim the first two sections.
3. [DESIGN_SESSION.md](../DESIGN_SESSION.md) — a complete worked
   example of Daniel designing an elementary school across all three
   interaction modes. The most useful single document for faculty.
4. [docs/MANUAL.md](./MANUAL.md) — the complete command reference.
   Treat this as a lookup, not bedtime reading.
5. [docs/MCP_GUIDE.md](./MCP_GUIDE.md) — how the AI integration works
   under the hood. Read if you are curious about how Claude Code talks
   to the tools.
6. Per-tool READMEs under [tools/](../tools/) — deep dives on TACT,
   TASC, and the Web UI.

---

## Glossary

*Tool.* A major capability module. Layout Jig, TACT, TASC, Image
Describer, Rhino Viewer, Web UI.

*Command.* A single action inside a tool, typed at the `>>` prompt.

*Macro.* A saved, replayable sequence of commands.

*Template.* A starting state that replaces the current design when
loaded.

*Skill.* A Claude Code capability packaged as SKILL.md.

*MCP function.* The technical entry point Claude uses to call into the
tools.

*state.json.* The single source of truth for the design. Plain text.
Version-controlled.

*PIAF.* Thermal microcapsule swell paper. Black toner absorbs heat and
raises into tactile ridges.

*Watcher.* The Rhino-side script that reads `state.json` and rebuilds
the 3D model whenever the file changes.

*Controller.* The Layout Jig CLI — the authoritative source of design
intent.
