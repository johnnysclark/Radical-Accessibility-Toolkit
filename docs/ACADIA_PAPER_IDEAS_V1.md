# ACADIA 2026 Paper Ideas V1

**Project:** Radical Accessibility Project (UIUC School of Architecture)
**Authors:** John Clark + [collaborator]
**Started:** 2026-03-05
**Status:** Active brainstorm

---

## The Core Positioning Problem

ACADIA 2026 will be flooded with AI papers. Every other submission will demonstrate an LLM generating geometry, a diffusion model producing floor plans, or a chatbot driving Grasshopper. The novelty of "we used AI to make architecture" has evaporated. The question is no longer *can* AI assist design — it can — but *who does AI-assisted design include, and what does it make possible that was previously impossible?*

Our paper must not be another AI paper. It must be a pedagogy paper that happens to use AI. The distinction matters: AI papers describe what a system can do; pedagogy papers describe what a student can learn, and how the tools reshape the learning itself.

## What We Are Actually Arguing

**Radical Accessible Pedagogy** — the idea that designing architectural education tools for blindness first produces a pedagogy that is not merely inclusive but genuinely different and, in specific measurable ways, better.

This is not "we made Rhino accessible." This is: we built a complete CLI-driven design pipeline — controller, JSON state file, Rhino watcher, tactile output, AI description — where a blind graduate student authors parametric floor plans in studio. And the tool ecosystem we built to make that possible turns out to embody pedagogical principles the field has been arguing for but never operationalized:

- **Semantic over geometric.** The student works with named bays, corridors, and spatial relationships before coordinates. This is how spatial cognition develops (Piaget & Inhelder 1956, Millar 1994) and how blind spatial reasoning works (Loomis et al. 2001, Giudice 2018) — but it is also better pedagogy for everyone. Sighted students in visual CAD skip semantic understanding and go straight to pushing geometry around. The CLI forces the semantic step.

- **Explicit reflective conversation.** Every command gets a verbal response. The design dialogue is auditable, diffable, and repeatable. Schon's "reflective practitioner" made operational through a screen-reader-native protocol. Visual CAD's feedback is silent and ambient — you have to look to see what changed. The CLI tells you.

- **Crash-proof, version-controlled design process.** The student's work lives in a JSON file, not in Rhino's memory. Every state is recoverable. Every change is tracked. This was built because a blind user cannot visually confirm crash recovery — but it is the design process infrastructure every studio should have.

- **Physical-digital round-trip as default.** Tactile output (PIAF swell paper, 3D prints) and tactile input (pegboard) are not accommodations bolted on — they are integral to the workflow. The blind student authors through CLI, evaluates through touch, feeds back through CLI. This is the embodied design loop that fabrication-centered pedagogy (Sass, ACADIA 2024 Teaching Award) calls for, made concrete.

## How Claude Code Fits

This is where we distinguish ourselves from the AI-paper crowd. We are not using Claude to generate architecture. We are using Claude Code — specifically, as an AI-assisted development environment — to build the accessibility infrastructure itself.

Claude Code is the development tool that makes the Radical Accessibility pipeline possible at the speed a single faculty member and a graduate student need. It writes the CLI handlers, constructs the MCP server, generates the IronPython watcher scripts, builds the tactile rendering pipeline, and maintains the whole system while respecting the project's hard constraints: Python stdlib only, IronPython 2.7 compatibility for Rhino, screen-reader-friendly output, atomic file writes, zero external dependencies.

The argument is not "AI generates design." The argument is: **AI-assisted development tools (Claude Code) enable a lone researcher to build the accessible design infrastructure that the field has called for but no one has had the resources to construct.** The pipeline that lets Daniel design in studio exists because Claude Code collapses the development effort from a multi-year funded research lab project to something one person can build and maintain iteratively, in real time, responding to Daniel's needs week by week.

This is a different kind of AI contribution:
- Most AI papers: "AI generates geometry for designers"
- Our paper: "AI-assisted development enables a researcher to build tools that make design accessible to people the field has excluded"

The AI is not in the design loop. The AI is in the tool-building loop. That distinction is the paper's contribution to the AI discourse.

## How We Stand Out

The ACADIA 2026 submission pool will contain:

1. **LLM-to-geometry papers** (Raven, Ant, Text2CAD descendants). Our paper is not this. We are not generating geometry with LLMs. We are building accessibility infrastructure with AI-assisted development.

2. **AI-for-sustainability papers.** Different topic entirely.

3. **Diffusion/image-generation papers.** We have no images. We have a CLI.

4. **AI agent papers** (ConvoAI, CADialogue descendants). Closer to us, but their agents assist sighted designers. Our pipeline serves a blind designer, and the agent (Claude Code) built the pipeline, not the architecture.

5. **Equity/inclusion papers** (Noel, Cupkova lineage). We share their concerns but deliver a working system, not a call to action.

Our paper occupies a unique position: **a pedagogy paper about a blind student in a graduate architecture studio, where the accessible tools were built using AI-assisted development (Claude Code), and the resulting tool architecture embodies pedagogical principles that benefit all students.** No other submission will combine disability, pedagogy, tool-building, and AI in this configuration.

## What "Radical Accessible Pedagogy" Means — Working Definition

A pedagogical approach in which:

1. **The primary design case is non-visual.** Tools are designed for a blind user first. Sighted use is a secondary projection of a system that works without vision.

2. **The student is a co-designer of the tools, not a consumer.** Daniel's feedback reshapes the CLI weekly. The tools evolve from his experience, not from assumptions about his experience.

3. **The medium of design is text, not image.** Commands, state files, and verbal feedback constitute the design conversation. This is not a limitation — it is a pedagogical commitment to semantic explicitness.

4. **Physical artifacts are integral, not supplementary.** Tactile output and tactile input are part of the core workflow, not accommodations. Every student — blind or sighted — benefits from the physical-digital round-trip.

5. **The tool ecosystem is open, auditable, and recoverable.** JSON state files, atomic writes, version control, zero dependencies. The infrastructure of the learning environment is as considered as the curriculum.

6. **AI assists the toolmaker, not the designer.** Claude Code builds and maintains the pipeline. The student designs through the pipeline. The AI never makes a design decision on Daniel's behalf.

---

## Paper Outline

Our paper occupies a unique position: **a pedagogy paper about a blind student in a graduate architecture studio, where the accessible tools were built using AI-assisted development (Claude Code), and the resulting tool architecture embodies pedagogical principles that benefit all students.** No other submission will combine disability, pedagogy, tool-building, and AI in this configuration.

### 1. Pedagogical Goals — What Radical Accessible Pedagogy Demands

The paper opens by defining what architectural education looks like when blindness is the primary design case — not as accommodation but as pedagogical method. Each goal is grounded in what Daniel actually needs to participate as a full author in graduate studio, and each turns out to articulate a principle the field has argued for but never operationalized.

- **Semantic-first spatial reasoning.** The student must be able to construct, query, and modify a design through named spatial relationships before any geometry is rendered. The pedagogical claim: this is how spatial cognition develops (Piaget & Inhelder), how blind spatial reasoning works (Millar, Loomis et al.), and how all students *should* engage a design before jumping to form-making. The tool must enforce the semantic step that visual CAD lets students skip.

- **Explicit, auditable design dialogue.** Every design move must produce a verbal response the student can hear through a screen reader. No silent viewport changes. No ambient visual feedback. The pedagogical claim: Schon's "reflective conversation with the situation" is more rigorous when the conversation is literally verbal — typed command in, spoken confirmation out. The design process becomes a transcript, not a memory.

- **Recoverable, version-controlled process.** The student's work must survive any tool failure. No data lives in Rhino's memory. Every state is a file on disk. The pedagogical claim: design education should treat process as a first-class artifact. When every state is recoverable, students can take risks, revert, branch, and compare — the version-controlled design process that software engineering takes for granted but architecture studios have never had.

- **Physical-digital fluency.** The student must be able to move between digital authoring (CLI) and physical evaluation (tactile prints, models, pegboard) without leaving the design conversation. The pedagogical claim: embodied making is not a supplement to digital design — it is design. The physical-digital round-trip that Sass's fabrication pedagogy calls for, realized through a workflow where tactile output is automated and tactile input is digitized.

- **Mixed-ability collaboration.** The blind student and sighted classmates must be able to work on the same design simultaneously, each through their own modality, without either being secondary. The pedagogical claim: architecture is collaborative. A tool ecosystem that separates the authoritative model (JSON state file) from any single viewing modality (Rhino viewport, CLI text, tactile print) enables genuine mixed-ability teamwork where no one's interface is "the real one."

- **Student as co-designer of the learning environment.** Daniel does not receive tools — he shapes them. His weekly feedback changes the CLI. His spatial intuitions become command structures. The pedagogical claim: the deepest form of learning is building the tools you learn with. This is Papert's constructionism applied to accessibility — the student constructs the instrument of his own architectural education.

### 2. The Tools — What We Built to Achieve Those Goals

Each tool is presented as a response to a specific pedagogical goal from Section 1. The emphasis is on *why* each tool exists (what Daniel needed) and *what pedagogical principle it embodies* (why it matters beyond Daniel).

#### 2a. Layout Jig CLI — The Controller

The command-line interface where Daniel authors floor plans. Python 3, stdlib only, zero dependencies. Commands like `set bay A rotation 30`, `corridor A width 8`, `show bays`, `describe`. Every command returns `OK:` or `ERROR:` with a single-line summary. Undo stack via deep copy. State persisted to JSON after every mutation via atomic write.

- **Pedagogical goal served:** Semantic-first reasoning, explicit design dialogue, recoverable process
- **Key design decisions:** Screen-reader-native output protocol; named spatial entities over coordinates; sequential command structure matching blind spatial cognition; command vocabulary that forces students to articulate *what* they are changing and *why* before the geometry updates

#### 2b. The Canonical Model Artifact (CMA) — state.json

The JSON file that *is* the design. Human-readable, schema-versioned, diffable. Contains every parameter: bay dimensions, column grids, corridor widths, wall thicknesses, aperture positions, room names, hatch patterns, braille labels. The CMA is the authoritative representation — not Rhino, not the CLI, not any particular view.

- **Pedagogical goal served:** Recoverable process, mixed-ability collaboration
- **Key design decisions:** 2-space indent for readability; stable IDs for all objects; schema migration on load (old files never break); the CMA is what gets version-controlled, shared, and critiqued — the "drawing" the student submits

#### 2c. Rhino Watcher — The Viewer

IronPython 2.7 script that monitors state.json for changes and rebuilds all geometry in Rhino on every save. Rhino is a consumer, never a source of truth. If Rhino crashes, nothing is lost — restart, run watcher, full rebuild.

- **Pedagogical goal served:** Crash-proof process, mixed-ability collaboration (sighted users see the design in Rhino while Daniel works in CLI)
- **Key design decisions:** Full rebuild on every change (correctness over speed); all objects tagged with JIG_OWNER/JIG_ID metadata; file-watching via mtime polling (no dependencies); crash-only viewer philosophy — Rhino is disposable

#### 2d. Tactile Output Pipeline — PIAF Swell Paper + 3D Prints

Automated rendering from state.json to 300 DPI black-and-white tactile graphics (PDF/PNG) for PIAF swell paper printing. Draws columns, walls, corridors, apertures, room hatches, labels in English and Braille. Also exports to 3D print for section models.

- **Pedagogical goal served:** Physical-digital fluency
- **Key design decisions:** Born-accessible rendering (designed for touch, not sight); Braille labels generated automatically; hatch patterns designed for tactile distinguishability; density checking for PIAF print quality; no Rhino required — renders directly from state.json

#### 2e. Pegboard + Computer Vision — Tactile Input

Physical pegboard where Daniel constructs spatial relationships with wire. Overhead camera + OpenCV digitizes wire positions into geometry. Audio feedback confirms what was captured.

- **Pedagogical goal served:** Physical-digital fluency (the return path — physical to digital)
- **Key design decisions:** Low-tech physical interface (accessible, cheap, portable); the digitization closes the loop that tactile output opens; Daniel can sketch with his hands and have the sketch enter the digital model

#### 2f. MCP Server — The Integration Layer

Model Context Protocol server (21 tools, 3 resources) that wraps the CLI controller, enabling Claude and other AI agents to read, query, and modify the design model through structured tool calls. The bridge between the accessibility pipeline and the AI ecosystem.

- **Pedagogical goal served:** AI assists the toolmaker (and potentially the student, through conversational design queries)
- **Key design decisions:** All tools are thin wrappers on CLI commands (zero business logic duplication); enables "describe my design" conversations; future direction for conversational design exploration

#### 2g. AI Description Pipeline — Scene Understanding for the Blind Student

Ray-Ban Meta glasses + AI scene description for physical site visits and desk crits. Claude API for generating rich text descriptions of Rhino viewport content, translating visual information into screen-reader-parseable text.

- **Pedagogical goal served:** Mixed-ability collaboration (Daniel can "see" what sighted classmates see, through language)
- **Key design decisions:** Description quality varies by context (design review vs. navigation vs. critique, following Stangl et al. 2021); multiple levels of detail (following Lundgard & Satyanarayan's four-level model); the AI describes, it does not design

### 3. AI Ideas — Where Intelligence Meets Accessibility

This section addresses the AI dimension honestly: what role does AI play, what role should it play, and what role must it never play?

#### 3a. AI as Tool-Builder (What We Did)

Claude Code as the development environment that made the entire pipeline possible. The argument: a single faculty member cannot build a CLI controller, MCP server, IronPython watcher, tactile renderer, computer vision pipeline, and AI description system in one academic year using traditional development methods. Claude Code collapses the implementation bottleneck. It writes handlers, debugs IronPython 2.7 compatibility issues, generates screen-reader-friendly output, maintains the CLAUDE.md constraints, and iterates on Daniel's feedback in real time.

This is the paper's distinctive AI contribution: **AI did not design the architecture. AI built the tools that let a blind student design architecture.** The development velocity that AI-assisted coding provides is what transforms "interesting research idea" into "working system deployed in a graduate studio this semester."

#### 3b. AI as Design Interlocutor (What We Are Exploring)

The MCP server opens the door to conversational design interaction. Daniel could ask: "Describe the spatial relationship between bay A and the corridor." "What happens to the column grid if I rotate bay B by 15 degrees?" "Compare the current plan to snapshot 'v3'." The AI becomes a design conversation partner — not generating form, but helping the student reason about the design through language.

This is closer to Di Marco's (2025) "Design Partner" mode but with a critical difference: for Daniel, the conversational interface is not a convenience — it is the *only* way to access certain kinds of design information that sighted students get from a glance at the viewport.

#### 3c. AI as Accessibility Bridge (What We Need Next)

The hardest unsolved problem: how does Daniel participate in a pin-up critique where sighted classmates present drawings on the wall? How does he evaluate a precedent building he cannot visit? How does he read a site plan from a planning document?

AI scene description (via glasses, phone camera, or screenshot analysis) is the emerging answer. The paper can describe the current state: Ray-Ban Meta glasses provide real-time scene description; Claude API generates architectural descriptions of Rhino viewports; the quality is improving but inconsistent. The honest assessment: AI description is necessary, imperfect, and improving fast enough that it will be a core part of the pipeline within a year.

#### 3d. AI Ethics in Accessible Design (What We Must Protect)

The line we draw: AI assists Daniel's access to information and assists the toolmaker in building infrastructure. AI does not make design decisions on Daniel's behalf. Daniel's architectural authorship must remain his own. The risk — well-documented by Flores-Saviaga et al. (2025) — is that AI assistants become so helpful that the student's agency erodes. The CLI's explicit command structure is a safeguard: every design move is a deliberate command Daniel types, not a suggestion an AI generates.

The paper should articulate this ethic clearly: **Radical Accessible Pedagogy uses AI to expand who can participate in design, not to replace design participation with AI output.**

---

## Open Questions for Collaborator Discussion

- **Paper format:** Full paper (4,000–6,000 words) or short paper / demo / poster? The demo format lets us show the system in action, which is compelling. The full paper lets us make the theoretical argument. Can we do both — a full paper with a video supplement?

- **Framing emphasis:** Do we lead with pedagogy ("here is a new model for inclusive architectural education") or with the tool architecture ("here is what happens when you design CAD for blindness first, and by the way it is better pedagogy")? The brainstorm rearrangement document argues for leading with the field's current moment (text-to-geometry, AI) and revealing the pedagogy. But a pedagogy-first framing might hit differently.

- **Daniel's voice:** How much of the paper should be in Daniel's words? A co-authored paper where Daniel describes his experience is more powerful than a third-person case study. What is his comfort level?

- **Claude Code disclosure:** How explicitly do we describe the role of Claude Code in building the tools? Full transparency is consistent with the project's values. But we need to frame it carefully: "AI built the tools that make accessible design possible" is very different from "AI does the design." The risk is reviewers conflating the two.

- **Evaluation:** What evidence do we present? Options:
  - Daniel's studio work products (plans authored through CLI)
  - Before/after comparison (what Daniel could do before the tools vs. after)
  - Comparative task analysis (same design task in Grasshopper vs. CLI)
  - Qualitative interview with Daniel about the experience
  - Description of specific design sessions with command logs

- **Scope:** Do we cover the full pipeline (CLI + watcher + tactile + AI description + MCP) or focus on one slice? The full pipeline is more impressive but harder to describe in 6,000 words. A focused paper on the CLI + CMA + watcher triangle with the pedagogy argument might be tighter.

- **Title candidates:**
  - "Radical Accessible Pedagogy: What a Blind Architecture Student Reveals About Computational Design Education"
  - "The Model Is Not the Viewport: Born-Accessible Architectural Computing and the Text-to-Geometry Blind Spot"
  - "Not Another AI Paper: How AI-Assisted Development Enables Accessible Architectural Pedagogy"
  - "Blindness as Method: Constraint-Driven Innovation in Computational Design Pedagogy"
  - [your ideas here]

---

## Next Steps

- [ ] Collaborator reads brainstorm rearrangement doc and this document
- [ ] Align on framing emphasis (pedagogy-first vs. tool-first)
- [ ] Decide on Daniel's role in authorship and voice
- [ ] Decide on paper format (full / short / demo)
- [ ] Identify 3–5 key citations that anchor the argument
- [ ] Write a 300-word abstract as a forcing function
- [ ] Check ACADIA 2026 submission deadline and format requirements
