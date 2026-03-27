# The Full Stack of Inclusion: Building an Accessible Architecture Studio from Workstation to Workflow

**John Clark**, University of Illinois Urbana-Champaign
**Hugh Swiatek**, University of Illinois Urbana-Champaign
**[Additional Authors]**

---

## Abstract

Enrolling a blind student in a graduate architecture studio exposes not one barrier but an entire stack of them — from inaccessible software to visual-only assessment methods, from the absence of tactile materials to the lack of institutional precedent. Removing any single barrier is insufficient; the student remains locked out by the others. This paper presents the Radical Accessibility Project at UIUC: a comprehensive initiative that addresses the full stack of inclusion simultaneously — physical workstation, text-based CAD pipeline, tactile output system, AI-powered description tools, physical-digital feedback loops, and institutional coordination across disability services, instructional media, and digital accessibility offices. We describe the integrated system built for Daniel, a blind graduate architecture student, over one academic year: The Desk (an all-in-one accessible workstation with PIAF printer, 3D printer, tactile baseboard, and overhead camera), The Code (a command-line interface that drives Rhino through explicit text commands with screen-reader-native output), and the workflows connecting them — from spoken design intent to parametric model to tactile print to physical evaluation and back. We document what worked, what did not, and what the process revealed about the gap between accommodation as policy and inclusion as practice. The paper argues that accessible architectural education requires not a single tool but a complete ecosystem — physical, digital, pedagogical, and institutional — and that building this ecosystem produces insights about studio pedagogy that benefit all students.

**Keywords:** accessible architecture studio, blind architecture student, command-line CAD, tactile workstation, PIAF swell paper, 3D printing, AI image description, institutional accessibility, inclusive pedagogy

---

## 1. Introduction: The Stack Problem

When a blind student enrolls in a graduate architecture studio, the immediate question is: what software can they use? But this question, urgent as it is, conceals the actual problem. The actual problem is that every layer of studio culture — from the tools students use to the materials they produce, from the feedback they receive to the assessments they face, from the desk they sit at to the pin-up wall they present on — assumes vision. Solving the software problem alone still leaves the student unable to read a precedent drawing, evaluate their own physical model, understand a classmate's critique presentation, or meet assessment criteria designed around visual deliverables.

We call this the stack problem. Accessibility in architecture education is not a single challenge with a single solution. It is a stack of interdependent challenges — software, hardware, materials, feedback mechanisms, assessment methods, communication protocols, institutional support — where solving any one layer in isolation leaves the student blocked by the others.

The Radical Accessibility Project at UIUC addresses the full stack. Over the 2025-26 academic year, we built and deployed an integrated system for Daniel, a blind graduate student in architecture: a physical workstation (The Desk), a text-based CAD pipeline (The Code), tactile output systems (PIAF swell paper and 3D printing), AI-powered visual description tools, physical-to-digital capture systems, and institutional coordination protocols. This paper documents the system, the process of building it, and what we learned — about blindness, about tools, and about the studio pedagogy we thought we understood.

## 2. Background: Four Questions

Our research was organized around four questions that any architecture program enrolling a blind student must answer. We present these as the working document's original formulations, because the questions themselves reveal the discipline's assumptions.

**Question 1: How can blind students independently create, manipulate, and interpret architectural geometries?**

The word "independently" carries the weight. Blind students in architecture programs have historically depended on sighted assistants to operate software, describe images, and interpret drawings. The assistant model is not accommodation — it is dependency that removes authorship. When someone else moves the mouse, the blind student is directing, not designing. Our research sought tools that restore full authorship: the student operates the software, evaluates the output, and makes design decisions without intermediation.

**Question 2: Which interfaces — tactile, auditory, linguistic — most effectively support conceptual design workflows?**

We confirmed early that text-based interfaces (Command Line Interface) rather than graphical user interfaces are necessary for blind users to drive digital design tools. The insight is not surprising — screen readers parse text, not graphics — but its implications are radical. Replacing the GUI with a CLI does not just change the input method. It changes the design vocabulary, the feedback mechanism, the process record, and the relationship between the designer and the model.

**Question 3: How can AI-driven natural language coding bridge the gap between spoken design intent and digital parametric modeling?**

AI proved invaluable in two distinct roles. First, Claude Code as the development environment that built the entire tool ecosystem at the speed a single researcher needs. Second, AI as a design interlocutor — translating natural language into CLI commands, generating image descriptions, and providing structured spatial narratives of the model state. The critical distinction: AI assists access to design, not design itself. Daniel's authorship remains his own.

**Question 4: What curricular adjustments are needed to ensure blind students participate equitably in design studios?**

This question remains the most difficult and the least resolved. Our research reinforced the inherent visual-centrism of architecture education. Traditional assessment methods — visual pin-ups, graphical portfolios, drawing-based evaluation — are inaccessible in their current form. Alternative assessment methodologies exist in principle but lack formal guidelines. We found that the tools themselves — the CLI transcript, the version-controlled state file, the tactile outputs — suggest new forms of assessment that are arguably more rigorous than visual pin-ups for all students.

## 3. The Desk: Physical Infrastructure for Non-Visual Design

One of the chief aims of this work is to shorten the feedback loop for a blind student. In conventional studio, a student models geometry on screen and immediately sees the result. The visual feedback loop is instantaneous. For a blind student, the equivalent feedback — understanding the spatial configuration of what was just modeled — requires translation into a modality the student can perceive: tactile, auditory, or linguistic.

The Desk is an all-in-one workstation designed to minimize the distance between digital action and physical feedback:

**Core components:**
- Tactile gridded baseboard for wire models — a physical surface where Daniel constructs spatial layouts by hand using wire and pegs on a measured grid, aligned with the digital coordinate system
- PIAF microcapsule paper and heater — for producing raised-line tactile drawings directly from the design model
- Laser printer with carbon-based toner — carbon absorbs heat from the PIAF machine; where toner is printed, microcapsules in the paper swell, and black lines rise as tactile ridges
- Bambu Lab P1S 3D printer — for producing tactile scale models that Daniel holds during design review
- Large high-contrast monitor — for any residual vision or for sighted collaborators working alongside Daniel
- Keyboard, screen reader, and braille display — the primary interface to the digital pipeline

**Design rationale:** The components are not separate tools. They are stations in a feedback loop. Daniel types a command, the model updates, the PIAF printer produces a tactile plan, he reads it with his fingers, identifies what needs to change, and types the next command. The 3D printer adds a third modality — physical volume in addition to raised-line plan. The tactile baseboard provides the return path: Daniel constructs a spatial configuration by hand, and an overhead camera digitizes it into the model.

The Desk's gridded coordinate system is physically aligned with the digital model's coordinate system. A peg at grid position (3, 5) on the baseboard corresponds to coordinates (3, 5) in the digital model. This alignment is not cosmetic — it is the mechanism that keeps the physical and digital representations in register, allowing Daniel to move between modalities without losing spatial coherence.

**Future components under development:**
- Overhead camera with computer vision for digitizing wire constructions on the baseboard
- Smart baseboard with embedded sensors for detecting component placement
- Plug-and-play jigs, stops, and physical components for analog spatial modeling

## 4. The Code: Text-Based CAD Pipeline

### 4.1 Why a CLI

The graphical user interfaces of Rhino, Grasshopper, and most CAD/BIM software depend on continuous visual targeting and mouse selection — icons, ribbons, floating panels, viewport picking — and on color and lineweight feedback. We tested these tools with screen readers (JAWS and NVDA) and confirmed what the accessibility literature predicts: they are not compatible. The modeling and Grasshopper canvases are not exposed in a screen-reader-usable way, keyboard paths are inconsistent, and modal dialogs frequently interrupt focus. Independent, auditable modeling through these tools is impractical for a blind user.

The CLI replaces pointer actions with explicit text parameters, makes every step speakable and logged, supports keyboard-only and voice workflows, and synchronizes tactile and digital states — restoring independence, repeatability, and parity in studio work.

### 4.2 Architecture

The system follows a controller-viewer separation pattern:

```
Terminal (typed/spoken commands)     Claude Code (natural language)
        |                                   |
        | writes                            | calls controller
        v                                   v
              state.json (canonical model artifact)
                      |
                      | watches (file modification time)
                      v
              Rhino 8 (geometry rebuild)
                      |
                      v
        2D plan  |  PIAF tactile print  |  3D printed model
```

The controller is a Python 3 CLI with zero external dependencies. It operates through a command dispatch architecture: the user types a command, the dispatcher routes it to the appropriate handler, the handler mutates the in-memory state, the state is persisted to a JSON file via atomic write (write to temporary file, flush, replace), and a confirmation is printed.

The command vocabulary is architectural:

```
>> set bay A bays 6 3
OK: Bay A grid = 6 x 3.

>> set bay A spacing 24 24
OK: Bay A spacing = (24.0, 24.0).

>> wall A on
OK: Bay A walls ON, 6-inch thick.

>> corridor A on
OK: Bay A corridor ON.

>> corridor A width 8
OK: Bay A corridor width = 8.0 ft.

>> aperture A d1 door x 0 2 3 7
OK: Added door d1 to bay A. Axis x, gridline 0, corner 2.0, width 3.0, height 7.0.
```

Every response begins with `OK:` or `ERROR:`. Every response is a single line. No tables, no multi-column layouts, no decorative formatting. After every command, `READY:` is printed so the screen reader detects the state change. This protocol was designed for Daniel's NVDA screen reader, but it is also more machine-parseable, more scriptable, and more debuggable than the status messages of any conventional CAD tool.

### 4.3 The Canonical Model Artifact

The JSON state file — the Canonical Model Artifact (CMA) — contains every parameter of the design: site dimensions, bay configurations (grid type, dimensions, spacing, origin, rotation), wall properties, corridor settings, apertures (doors, windows, portals with position, size, hinge, and swing), room names and hatches, style settings, and metadata. It is human-readable with two-space indentation, schema-versioned for forward compatibility, and designed for diffability.

The CMA is the authoritative representation. Not Rhino, not the CLI output, not any particular view. Rhino is a disposable viewer that reads the CMA and renders geometry. If Rhino crashes, nothing is lost — restart it, run the watcher script, and every element rebuilds identically from the file on disk.

### 4.4 Exposed Workflows

The CLI exposes nine workflow categories, each addressing a specific aspect of architectural production:

**A. 3D Modeling.** Parametric primitives (box, cylinder, sphere, cone, torus) grid-snapped to the Desk coordinate system. Curve-to-surface/solid operations (loft, sweep, revolve). Modifiers (fillet, chamfer, shell, thicken). Boolean operations with error-aware retries. Piping for tactile rod models. Arrays and transforms. All geometry is tagged with metadata (layers, names, GUIDs) for reproducibility.

**B. 2D Drawing Generation.** Automated section cuts, hidden-line vector generation, hatching for cut regions, title-block stamping. Export to PDF/SVG with page size and DPI flags. Every drawing operation is a command with explicit parameters — no mouse-driven clipping plane placement.

**C. Camera-to-CAD Ingest.** Board calibration via AprilTag or ArUco grid markers. Pin detection with sub-pixel accuracy. Wire tracing via threshold, skeletonize, and polyline fitting. Geometry emitted to Rhino as named layers with timestamps.

**D. Tactile Output for PIAF.** Rasterize vectors to black-and-white at 300 DPI. Auto-thicken lineweights below tactile threshold. Page tiling and registration marks aligned to the Desk grid. Density checking — above 40% triggers a warning, above 45% rejects the output because excessive swelling destroys tactile detail.

**E. Watertight STL Export.** Mesh generation with controlled edge length. Solid checks (naked edges, self-intersections, hole-fill). Per-part bounding-box and volume report. Direct handoff to the Bambu P1S slicer.

**F. Grasshopper Integration.** Launch and edit Grasshopper definitions via ghpythonlib. Set and read parameters from the CLI. Bake results to named layers. Library of reusable parametric jigs.

**G. Voice/LLM/MCP Integration.** Natural language to command compilation through a Model Context Protocol server with 53 structured functions. Speak-back of current state and parameter deltas. Error-aware retries from stack traces. The MCP server enables three interaction modes: Claude Code with natural language, interactive CLI with typed commands, and editable IronPython scripts the user can study, modify, and run independently in Rhino.

**H. Validation and QA.** Units, tolerance, and bounding-box sanity checks. ADA compliance auditing (door widths, corridor widths). Regression scripts that rebuild a scene from the log. Accessibility audit for PIAF thresholds and tactile spacing.

**I. Data Management.** Deterministic filenames. JSON sidecars for parameters and checksums. Export manifests for each run. Snapshot system for named checkpoints with diff capability.

## 5. Tactile Output: Reading Architecture by Touch

### 5.1 PIAF Swell Paper

The primary tactile medium is PIAF (Pictures in a Flash) microcapsule paper. Carbon-based toner is laser printed onto special paper whose surface contains microscopic capsules. When passed through the PIAF heater, the capsules under the black toner swell and rise, creating raised lines that Daniel reads with his fingers.

The rendering pipeline reads the CMA directly — no Rhino required — and produces 300 DPI black-and-white images. It draws column grids as filled circles, walls as thick polylines, corridors as dashed centerlines, apertures as standard architectural symbols (arc swings for doors, break lines for windows), room hatches as pattern fills, and labels in both English text and Grade 1 Braille conforming to BANA standards.

For precedent study, any image — a floor plan, a photograph, a section drawing — can be converted to PIAF-ready output through ten conversion presets optimized for different image types (floor plans, photographs, sketches, diagrams, sections, details, elevations, site plans, maps, and generic images). Each preset tunes the contrast enhancement, threshold, and density limits for its image type.

### 5.2 3D Printed Models

For three-dimensional understanding, the system generates watertight triangle meshes from the parametric model (pure Python, no Rhino dependency) and exports binary STL files scaled for the Bambu Lab P1S printer. Daniel holds printed models during design review — walls, corridors, and openings physically present at 1:200 scale. With automatic export enabled, the STL regenerates after every model change, keeping the physical model synchronized with the digital design.

### 5.3 The Feedback Loop

These two output modalities — raised-line plan and printed volume — close the feedback loop that vision provides for sighted students. The cycle is: type a command, render a tactile print, heat the PIAF paper, trace the raised lines with fingers, identify what needs to change, type the next command. For volumetric questions: export an STL, print it, hold it, feel the spatial relationships, type revisions.

The loop is not instantaneous — a PIAF print takes minutes, a 3D print takes hours. But it is autonomous. Daniel does not need a sighted person to tell him what his design looks like. He reads it himself, through his hands.

## 6. AI Tools: Description, Development, Integration

### 6.1 Image Description

Architecture education is saturated with images — slides in lectures, precedent drawings in textbooks, classmates' work on pin-up walls, site photographs, construction details. Every image is information a blind student cannot access without translation.

We developed an AI-powered image description system using a structured Macro-Meso-Micro methodology, following a whole-to-part approach:

**Macro** (3 sentences): Identifies the medium (photograph, plan, section, diagram), states the principal subject and the image's purpose, and conveys the dominant atmosphere or pedagogical intent.

**Meso** (6 sentences): Decomposes composition and hierarchy, names primary materials and graphical conventions, gives orientation and viewpoint, describes scale cues and lighting, summarizes relationships among parts, and notes annotations.

**Micro** (10+ sentences): Details textures and assemblies, structural logic, environmental strategies, proportional dimensions, multi-sensory analogies (tactile, acoustic, thermal), accessibility cues, historical context, and occlusions. Ends with an interpretive prompt inviting critique.

The system operates through a custom GPT prompt that produces architectural descriptions tuned for a blind student's needs — not generic alt-text but descriptions that build architectural literacy, mapping visual traits to multi-sensory analogies and connecting observed features to structural, environmental, and experiential implications.

### 6.2 AI-Assisted Development

The entire tool ecosystem — CLI controller, CMA schema, Rhino watcher, tactile renderer, MCP server, image converter, 3D print exporter — was built by a single researcher using Claude Code as the primary development environment. AI-assisted development is the mechanism that makes the project feasible at the speed a graduate studio demands.

The project defines hard constraints in a CLAUDE.md file: Python stdlib only for controllers, IronPython 2.7 for the Rhino watcher (no f-strings, no pathlib), screen-reader-friendly output protocol, atomic file writes, zero external dependencies. Claude Code maintains these constraints across every code generation task.

Development velocity matters because Daniel identifies needs in real time. He reports on Monday that the audit command does not check door swing clearances. By Wednesday, the check exists. He discovers that tabloid-size PIAF prints provide better tactile resolution for complex plans. By the next session, the `--paper tabloid` flag is implemented. Tools evolve from the student's lived experience, not from a researcher's assumptions.

### 6.3 MCP Integration

A Model Context Protocol server with 53 functions connects AI agents to every tool in the ecosystem. Through the MCP server, Daniel can work conversationally:

```
Daniel: Create a 6 by 3 bay grid for a school, 24-foot spacing.
Claude: OK: Bay A grid = 6 x 3. Spacing = (24.0, 24.0).

Daniel: Add a double-loaded corridor along the x-axis.
Claude: OK: Bay A corridor ON, x-axis, gridline 1, width 8.0 ft, double-loaded.

Daniel: Check it for ADA compliance.
Claude: OK: All corridors meet ADA minimum width. Door d1 width 3.0 ft
        meets minimum but consider 3.5 ft for comfort.

Daniel: Render that so I can feel it.
Claude: OK: Rendered state_tactile.pdf (Letter, 300 DPI, density 28.3%)
```

The MCP server also generates annotated IronPython scripts that Daniel can open in Rhino's script editor, study, modify, and run independently. Teaching comments explain each code pattern. Over time, the goal is for Daniel to build fluency in scripting his own geometry — the AI is a bridge to self-sufficiency, not a permanent dependency.

## 7. Institutional Infrastructure

### 7.1 The Collaborator Network

No single researcher possesses the expertise to address the full stack. The project coordinates with subject matter experts across campus:

- **Disability Resources and Educational Services (DRES)** — accommodation standards, legal compliance, alternative media production
- **Center for Innovation in Teaching & Learning (CITL)** — instructional media, audio description, captioning
- **Digital Accessibility and Excellence Initiative** — institutional policy, WCAG compliance, Title II implementation
- **Beckman Institute (dis)Ability Design Studio** — innovative 3D representation, assistive technology, empathic design

This network is not supplementary. It is structural. The legal framework — Section 504 of the Rehabilitation Act, Title II of the ADA, the Illinois Information Technology Accessibility Act (IITAA) — mandates that the university ensure accessibility. WCAG 2.1 Level AA is the operational benchmark. But compliance and inclusion are different things. The legal framework ensures the university does not discriminate. The collaborator network helps build the tools and workflows that enable genuine participation.

### 7.2 Communication Protocols

Working with a blind student requires explicit communication practices that most instructors have never considered. All class instruction must include real-time verbal descriptions of visual content. "This" and "here" and "look at this" are meaningless without referents. Instructors must describe what they are pointing at, what is on screen, what the drawing shows — not as an afterthought but as the primary mode of instruction.

Assignment descriptions must be self-contained text, not visual templates. Assessment criteria must specify what constitutes demonstration of mastery without assuming visual deliverables. Studio critiques must be verbalized — not just the student's work but the discussion itself, including references to specific drawings or models on the wall.

These practices, developed for Daniel, improve instruction for all students — including those who miss class, those processing information in a second language, and those who learn better through verbal than visual channels.

## 8. What We Learned

### 8.1 The Software Was the Easy Part

Building the CLI, the CMA, the Rhino watcher, the PIAF pipeline, and the MCP server was the most visible work but not the hardest. The harder problems were institutional: convincing colleagues that a blind student belongs in architecture studio, developing assessment criteria that do not depend on visual deliverables, training instructors to describe what they are showing, establishing communication protocols with the DRES office, and coordinating across administrative silos that do not normally talk to each other.

The tools are necessary but not sufficient. A blind student with a perfect CLI and no institutional support is still excluded from pin-up critiques, from reading classmates' work, from the informal visual culture of studio. The full stack of inclusion requires changes at every level — not just technology.

### 8.2 The Feedback Loop Is Everything

The central insight from the working document: the core challenge is not modeling but verification. How does a blind student confirm that what was modeled matches their design intent? Sighted students verify by looking. Blind students need a different verification mechanism — and every design decision in the project flows from this need.

The CLI's `OK:` / `ERROR:` protocol is textual verification of individual commands. The `describe` command is spatial verification of the overall model. The `audit` command is compliance verification against dimensional and accessibility rules. The PIAF print is tactile verification of the plan. The 3D print is volumetric verification of the massing. Each mechanism addresses a different scale of the verification problem, and all of them together approximate what a sighted student gets from a glance at the viewport.

### 8.3 The Curb Cut Effect Is Real

Tools designed for Daniel's blindness turn out to be better for sighted students in specific, measurable ways:

- The CLI's semantic command vocabulary forces students to articulate spatial relationships before manipulating geometry — a pedagogical discipline visual CAD lacks
- The CMA enables version-controlled design processes — branching, diffing, reverting — that no conventional CAD supports
- The `OK:` / `ERROR:` output protocol is machine-parseable, enabling automated testing and scripting
- The crash-only viewer architecture eliminates data loss from Rhino crashes
- The design transcript — the sequence of commands and responses — makes the design process auditable and teachable

These are not accessibility features repurposed for convenience. They are engineering virtues that visual tools abandoned in favor of graphical immediacy. Designing for the hardest case recovered them.

## 9. Limitations and Next Steps

The system is deployed with one student. Pedagogical claims require evaluation with a broader population. Controlled comparisons — sighted students completing design tasks in both Grasshopper and the CLI — are planned but not yet complete.

The pegboard-to-digital pipeline (camera capture of wire constructions) is a prototype. Wire detection works but does not yet reliably classify element types (wall vs. corridor vs. boundary).

Sonification remains unrealized. Mapping spatial properties to sound — room volume to reverb, wall proximity to tonal shift, ceiling height to pitch — would add a modality the current system lacks.

Assessment methodology is the largest unsolved problem. We have tools that produce non-visual design artifacts. We do not yet have consensus on how to evaluate those artifacts in a studio culture built around visual judgment.

The Desk is a prototype workstation. Its components work but are not yet integrated into a seamless physical system. The overhead camera is not yet connected. The tactile baseboard is not yet smart. Future work includes embedded sensors, automated camera capture, and more sophisticated physical-digital alignment.

## 10. Conclusion

The Radical Accessibility Project did not set out to reform architectural education. It set out to solve a practical problem: how does a blind student participate fully in a graduate architecture studio? The answer turned out to be: not through any single tool but through a complete ecosystem — physical workstation, text-based CAD, tactile output, AI description, institutional coordination — that addresses every layer of the accessibility stack simultaneously.

What surprised us is that the ecosystem we built for Daniel articulates pedagogical principles the discipline has long advocated — semantic engagement, reflective practice, process documentation, embodied making, mixed-ability collaboration — more consistently than the visual tools we hand every other student. The constraints of blindness forced us to build what studio pedagogy should have had all along.

The tools exist. They work. A blind student designs floor plans, produces tactile prints, 3D-prints scale models, studies precedents through AI descriptions, and presents his work in studio critiques using text, touch, and speech. The software was the easy part. The hard part — changing the institutional, pedagogical, and cultural assumptions that make vision a prerequisite for architectural participation — is ongoing. This paper documents where we are. The work continues.

---

## References

Atakan, A.O. et al. 2025. "Kakadoo: LLM Enabled Speech Interface for Enhanced Human-Computer Interaction." In *Proceedings of the 43rd eCAADe Conference*, Ankara.

Billah, S.M. et al. 2023. "Designing While Blind: Nonvisual Tools and Inclusive Workflows for Tactile Graphic Creation." In *Proceedings of ASSETS '23*. ACM.

Charlton, J.I. 1998. *Nothing About Us Without Us: Disability Oppression and Empowerment.* Berkeley: University of California Press.

Clepper, G. et al. 2025. "'What Would I Want to Make? Probably Everything': Practices and Speculations of Blind and Low Vision Tactile Graphics Creators." In *Proceedings of CHI 2025*. ACM.

Crawford, S. et al. 2024. "Co-designing a 3D-Printed Tactile Campus Map with Blind and Low-Vision University Students." In *Proceedings of ASSETS '24*. ACM.

El Hizmi, B. et al. 2024. "LLMto3D: Generating Parametric Objects from Text Prompts." In *Proceedings of ACADIA 2024*, Vol. 1, 157-166.

Evans, R. 1997. *Translations from Drawing to Building and Other Essays.* Cambridge, MA: MIT Press.

Flores-Saviaga, C. et al. 2025. "The Impact of Generative AI Coding Assistants on Developers Who Are Visually Impaired." In *Proceedings of CHI 2025*. ACM.

Giudice, N.A. 2018. "Navigating without Vision: Principles of Blind Spatial Cognition." In *Handbook of Behavioral and Cognitive Geography*. Edward Elgar.

Gipe-Lazarou, A. 2025. "Accessing Architecture: Career Exploration Opportunities for Aspiring Architects with Vision Impairment." *Journal of Vocational Behavior*.

Gissen, D. 2018. "Why Are There So Few Disabled Architects and Architecture Students?" *The Architect's Newspaper*, June 15.

Gissen, D. 2022. *The Architecture of Disability: Buildings, Cities, and Landscapes beyond Access.* Minneapolis: University of Minnesota Press.

Hamraie, A. 2017. *Building Access: Universal Design and the Politics of Disability.* Minneapolis: University of Minnesota Press.

Heylighen, A. and J. Herssens. 2014. "Designerly Ways of Not Knowing: What Designers Can Learn about Space from People Who Are Blind." *Journal of Urban Design* 19(3): 317-332.

Kennedy, J.M. 1993. *Drawing and the Blind: Pictures to Touch.* New Haven: Yale University Press.

Kłopotowska, A. and M. Magdziak. 2021. "Typhlographics: Tactile Architectural Drawings — Practical Application and Potential." *Sustainability* 13(11): 6216.

Loomis, J.M., R.L. Klatzky, and R.G. Golledge. 2001. "Cognitive Mapping and Wayfinding by Adults Without Vision." In *Navigating through Environments*. Springer.

Millar, S. 1994. *Understanding and Representing Space.* Oxford: Oxford University Press.

Noel, V.A.A., Y. Boeva, and H. Dortdivanlioglu. 2021. "The Question of Access: Toward an Equitable Future of Computational Design." *International Journal of Architectural Computing* 19(4): 496-511.

Pallasmaa, J. 2005. *The Eyes of the Skin: Architecture and the Senses.* 2nd ed. Chichester: Wiley.

Pullin, G. 2009. *Design Meets Disability.* Cambridge, MA: MIT Press.

Rietschel, M., F. Guo, and K. Steinfeld. 2024. "Mediating Modes of Thought: LLMs for Design Scripting." In *Proceedings of ACADIA 2024*, Calgary.

Sass, L. 2024. ACADIA Teaching Award of Excellence. ACADIA 2024 ("Designing Change"), Calgary.

Schon, D.A. 1983. *The Reflective Practitioner: How Professionals Think in Action.* New York: Basic Books.

Seo, J.Y. et al. 2024. "Designing Born-Accessible Courses in Data Science and Visualization." In *Eurographics / IEEE VGTC Conference on Visualization*.

Winner, L. 1980. "Do Artifacts Have Politics?" *Daedalus* 109(1): 121-136.
