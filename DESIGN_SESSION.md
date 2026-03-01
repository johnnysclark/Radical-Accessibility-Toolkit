# Design Session Walkthrough: Elementary School

Last updated: 2026-02-28

A step-by-step example of a blind architecture student using the Layout Jig to design an elementary school. Demonstrates all three interaction modes and the full pipeline from concept to tactile fabrication.

---

## The Designer

Daniel is a blind architecture student. He uses JAWS screen reader, a keyboard, and Claude Code in a terminal. He has a PIAF machine for tactile prints and a Bambu P1S for 3D models. Rhino 8 is open on a second monitor for sighted collaborators, but Daniel never looks at it.

## The Project

Design a single-story elementary school with:
- 6 classrooms in a double-loaded corridor
- A gymnasium
- A cafeteria
- Administrative offices
- Main entrance with vestibule
- ADA-compliant throughout

---

## Phase 1: Site Setup (Mode 1 — Claude Code)

Daniel opens a terminal and starts Claude Code.

Daniel says: "Set up a new site for an elementary school. Make it 300 feet wide and 200 feet deep."

Claude calls the MCP tools:

    set_site(field="width", value=300)
    set_site(field="height", value=200)

Daniel hears from the watcher: chime + "Rebuilt. 0 bays, 0 apertures, 1 room."

Daniel says: "Add bay A for the classroom wing. Put it at origin 10 10. Make it 6 columns wide by 3 deep, with 24-foot spacing."

Claude calls:

    add_bay(name="A", origin_x=10, origin_y=10)
    set_bay(bay="A", field="bays", value="6 3")
    set_bay(bay="A", field="spacing", value="24 24")

Daniel hears: chime + "Rebuilt. 1 bay, 0 apertures, 2 rooms."

Daniel says: "Describe the model."

Claude calls describe. Daniel hears the full state read back: site dimensions, bay A position, grid size, column count. No surprises.

## Phase 2: Classroom Wing (Mode 1 to Mode 2)

Daniel says: "Turn on walls for bay A, half-inch thick. Add a double-loaded corridor along the x-axis at gridline 1, 8 feet wide."

Claude calls:

    set_walls(bay="A", enabled=True, thickness=0.5)
    set_corridor(bay="A", enabled=True)
    set_corridor(bay="A", enabled=True, field="axis", value="x")
    set_corridor(bay="A", enabled=True, field="position", value="1")
    set_corridor(bay="A", enabled=True, field="width", value="8")
    set_corridor(bay="A", enabled=True, field="loading", value="double")

Daniel hears: chime + "Rebuilt. 1 bay, 0 apertures, 2 rooms."

Now Daniel wants fine control. He switches to the interactive CLI terminal (Mode 2).

    >> set bay A spacing_x 24 24 30 24 24 24
    OK: Bay A x-spacing = [24.0, 24.0, 30.0, 24.0, 24.0, 24.0]. Was uniform 24.0.

    >> describe
    (full model state read aloud by TTS)

The wider third bay (30 ft) is for a science classroom that needs extra bench space. Daniel made this decision directly — no AI intermediary.

Now he adds doors to each classroom. Six classrooms need six doors, all opening onto the corridor.

    >> aperture A add d1 door x 0 4 3 7
    OK: Added door d1 to Bay A: axis=x gridline=0 corner=4.0 w=3.0 h=7.0

    >> aperture A add d2 door x 0 28 3 7
    OK: Added door d2 to Bay A: axis=x gridline=0 corner=28.0 w=3.0 h=7.0

    >> aperture A add d3 door x 0 52 3 7
    OK: Added door d3 to Bay A: axis=x gridline=0 corner=52.0 w=3.0 h=7.0

    >> aperture A add d4 door x 2 4 3 7
    OK: Added door d4 to Bay A: axis=x gridline=2 corner=4.0 w=3.0 h=7.0

    >> aperture A add d5 door x 2 28 3 7
    OK: Added door d5 to Bay A: axis=x gridline=2 corner=28.0 w=3.0 h=7.0

    >> aperture A add d6 door x 2 52 3 7
    OK: Added door d6 to Bay A: axis=x gridline=2 corner=52.0 w=3.0 h=7.0

Each command confirms exactly what changed. Daniel counts six OKs — six doors placed.

## Phase 3: Gymnasium and Cafeteria (Mode 1)

Daniel switches back to Claude Code for the bigger moves.

Daniel says: "Add bay B for the gymnasium. Put it east of the classroom wing at 160 10. Make it 4 by 2 with 30-foot spacing for the long spans."

Claude calls:

    add_bay(name="B", origin_x=160, origin_y=10)
    set_bay(bay="B", field="bays", value="4 2")
    set_bay(bay="B", field="spacing", value="30 30")
    set_walls(bay="B", enabled=True, thickness=0.5)
    set_bay(bay="B", field="label", value="Gymnasium")

Daniel says: "Add bay C for the cafeteria above the gym, at 160 80. Make it 3 by 2, 24-foot spacing."

Claude calls:

    add_bay(name="C", origin_x=160, origin_y=80)
    set_bay(bay="C", field="bays", value="3 2")
    set_bay(bay="C", field="spacing", value="24 24")
    set_walls(bay="C", enabled=True, thickness=0.5)
    set_bay(bay="C", field="label", value="Cafeteria")

Daniel says: "Run an audit. Check for ADA issues."

Claude calls audit_model. The report comes back:

    1. Bay B: No corridor defined (may need accessible route)
    2. Bay C: No corridor defined (may need accessible route)
    3. Bay A door d1: Width 3.0 ft meets ADA minimum (3 ft)
    4. Bay A corridor: Width 8.0 ft meets ADA minimum (5 ft)

Daniel says: "Add a corridor to bay B along the y-axis at gridline 0, 8 feet wide. Single-loaded — the gym is open plan on one side."

Claude calls:

    set_corridor(bay="B", enabled=True, field="axis", value="y")
    set_corridor(bay="B", enabled=True, field="position", value="0")
    set_corridor(bay="B", enabled=True, field="width", value="8")
    set_corridor(bay="B", enabled=True, field="loading", value="single")

Daniel says: "Add a double door from the corridor to the gym. 6 feet wide."

Claude calls:

    add_aperture(bay="B", id="d1", type="door", axis="y", gridline=0, corner=10, width=6, height=7)

Daniel says: "Describe circulation."

Claude calls describe_circulation. Daniel hears which bays have corridors, where the doors connect, and whether there are dead ends. He catches that bays B and C are not connected to bay A yet. He will fix this later with a linking corridor or portal.

## Phase 4: Learning Scripting (Mode 3)

Daniel has been using Modes 1 and 2 for a week. Now he wants to understand what is happening under the hood.

Daniel says: "Generate a script that reads state.json and prints every room name with its type."

Claude calls generate_script:

    generate_script(
        name="list-rooms",
        description="Read state.json and print all room names with types",
        code="""import json
import os

here = os.path.dirname(os.path.abspath(__file__))
state_path = os.path.join(here, "..", "state.json")

with open(state_path, "r") as f:
    state = json.load(f)

rooms = state.get("rooms", {})
print("Rooms in the model:")
for name, info in sorted(rooms.items()):
    label = info.get("label", name)
    rtype = info.get("type", "unknown")
    print("  {0}: {1} (type: {2})".format(name, label, rtype))

print("")
print("Total: {0} rooms".format(len(rooms)))""")

Daniel hears: "OK: Script saved to scripts/list-rooms.py"

He opens the file in Notepad (JAWS reads it line by line). He reads the teaching comments. He understands json.load() opens a file. He sees .get() with defaults. He sees .format() for string building.

He modifies the script: adds a line to also print each bay's column count. He calculates it himself: (nx+1) * (ny+1) for rectangular bays.

He saves and runs it in Rhino's EditPythonScript (F5). The output appears in Rhino's command line. JAWS reads it.

Later, Daniel says: "Generate a script that draws a circle at every column position in bay A."

Claude generates it. Daniel opens it, changes the circle radius from 0.75 to 1.5, runs it, and sees (through his sighted collaborator) that the circles are now larger. He is learning rhinoscriptsyntax by doing.

Over the semester, Daniel builds a personal library of scripts in the scripts/ folder. Some he wrote from scratch. Some Claude generated and he modified. Each one teaches him something about Python and Rhino geometry.

## Phase 5: Room Naming and Hatching (Mode 2)

Daniel returns to the CLI for detailed room work.

    >> auto_corridor_cells A
    OK: Marked 6 corridor cells in Bay A.

    >> cell A 0 0 name Classroom-1
    OK: Cell (0,0) in Bay A named 'Classroom-1'.

    >> cell A 1 0 name Classroom-2
    OK: Cell (1,0) in Bay A named 'Classroom-2'.

    >> cell A 2 0 name Classroom-3
    OK: Cell (2,0) in Bay A named 'Classroom-3'.

    >> cell A 0 2 name Classroom-4
    OK: Cell (0,2) in Bay A named 'Classroom-4'.

    >> cell A 1 2 name Classroom-5
    OK: Cell (1,2) in Bay A named 'Classroom-5'.

    >> cell A 2 2 name Classroom-6
    OK: Cell (2,2) in Bay A named 'Classroom-6'.

    >> cell A 0 0 hatch diagonal
    OK: Cell (0,0) hatch = diagonal.

    >> cell A 0 2 hatch crosshatch
    OK: Cell (0,2) hatch = crosshatch.

Each classroom gets a distinct hatch pattern so Daniel can tell them apart on the PIAF tactile print. Adjacent rooms get different patterns (diagonal vs crosshatch vs dots) for maximum contrast under fingertips.

## Phase 6: Legend and Presentation (Mode 1)

Daniel says: "Turn on the legend. Put it in the bottom-right corner. Make sure braille labels and hatches are shown."

Claude calls:

    run_command("legend on")
    run_command("legend position bottom-right")

Daniel says: "Add braille labels to bay A."

    set_bay(bay="A", field="braille", value="Classroom Wing")

Daniel says: "Save a snapshot called school-v1."

    save_snapshot(name="school-v1")

Daniel hears: "OK: Snapshot saved: school-v1"

He can always come back to this point.

## Phase 7: Section Cut

Daniel says: "Take a section cut along the x-axis at 40 feet. That should cut through the corridor and show classrooms on both sides."

Claude calls:

    run_command("section x 40")

The watcher generates a section line across the plan. On the PIAF print, this will appear as a dashed line showing where the building is cut.

## Phase 8: Fabrication

### PIAF Tactile Print

Daniel says: "Export the plan for PIAF printing."

The system exports a high-contrast black-and-white drawing:
- Heavy lines (1.4mm) for columns
- Medium lines (0.25mm) for walls
- Light lines (0.08mm) for the structural grid
- Corridor dashed lines (0.35mm)
- Hatch patterns at appropriate scales
- Grade 2 contracted braille labels
- Legend with hatch swatches

Daniel laser-prints this on PIAF microcapsule paper using carbon-based toner. He feeds the paper through the PIAF heater. The carbon absorbs heat, the microcapsules swell, and the black lines rise off the page.

Daniel reads his own floor plan with his fingers. He traces the corridor, finds each classroom door, counts columns, reads the braille legend. He catches that Classroom-3 (the science room with the wider span) feels noticeably larger — the 30-foot spacing is tangible.

### 3D Printed Model

Daniel says: "Turn on tactile 3D and export the STL."

Claude calls:

    run_command("tactile3d on")
    run_command("tactile3d wall_height 9")

The system generates a watertight triangle mesh: walls at 9 feet tall, floor slab at 0.5 inches, doors cut as openings. The STL is scaled 1:200 for the Bambu P1S printer.

Daniel prints the model. He holds it during design review — walls, corridor, door openings all physically present. He can feel the gymnasium's open span versus the tight classroom bays. The cafeteria's different grid rhythm is obvious to touch.

## Phase 9: Design Review

Daniel brings three things to the review:
1. His PIAF tactile floor plan
2. His 3D printed model
3. His laptop running Claude Code

The instructor asks: "How wide is the main corridor?"

Daniel types in Claude Code: "Describe bay A corridor."

He hears: "Bay A corridor: axis x, position 1, width 8.0 feet, double-loaded." He reads this aloud.

A sighted peer looks at the Rhino viewport and confirms the same.

The instructor asks: "What if we made the gym corridor wider for assembly egress?"

Daniel, in the CLI:

    >> corridor B width 12
    OK: Bay B corridor width = 12.0 ft. Was 8.0.

The watcher rebuilds. The sighted peers see the change in Rhino. Daniel re-exports and can verify the change on his next PIAF print.

The instructor reviews the state.json diff (semantic, auditable):

    corridor.width: 8.0 -> 12.0

One line changed. The intent is clear. No geometry sifting required.

## Phase 10: Saving and Continuing

Daniel says: "Save snapshot school-final and push to GitHub."

    save_snapshot(name="school-final")

The state.json is committed to version control. Next session, Daniel opens Claude Code, loads the snapshot, and continues where he left off. The model survived Rhino restarts, power outages, and three crashes. It always rebuilds from the JSON.

---

## Key Observations

1. No step required vision. Every action produced text or audio feedback.
2. Daniel used all three modes: Claude for big moves, CLI for precision, scripts for learning.
3. The model survived independently of Rhino. State.json is the truth.
4. Fabrication (PIAF and 3D print) closed the loop — digital to physical, readable by touch.
5. Design review worked across sighted and blind participants using the same data.
6. The AI explained and generated, but Daniel made every design decision himself.
7. Over time, Daniel's Mode 2 and Mode 3 usage increased as he learned the vocabulary.
