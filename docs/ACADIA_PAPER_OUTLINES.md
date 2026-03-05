# ACADIA Paper Outlines — Five Approaches from the Working Document

**Source:** "Radical Accessibility Working Group — Summary of Preliminary Research, Summer 2025" (Clark & Swiatek)
**Date:** 2026-03-05
**Purpose:** Five distinct paper outlines for ACADIA 2026, each drawing from the working document and the README but attacking the material from a different framework, audience, and argumentative strategy.

---

## Outline A: "Closing the Loop: Tactile Feedback Cycles in Non-Visual Architectural Design"

### Framework
The working document repeatedly identifies the **feedback loop** as the central problem: sighted students model and immediately see results; blind students need translation into touch, sound, or language before they can evaluate. This paper treats the feedback loop itself as the unit of analysis, documenting each loop the project built and measuring how the loop's speed and fidelity affect design cognition.

### Audience
HCI and design cognition researchers at ACADIA; connects to Sass's fabrication pedagogy and Schon's reflection-in-action.

### Argument
The quality of architectural design thinking is a function of feedback loop speed and modality richness. Visual CAD provides fast, high-bandwidth, single-modality feedback (the viewport). The Radical Accessibility pipeline provides slower but multi-modal feedback (text, tactile plan, 3D print, spoken description), and the multi-modality produces spatial understanding that single-modality feedback does not.

### Outline

**1. Introduction — The Feedback Problem** (~500 words)
- Architecture education depends on design-evaluate-revise cycles
- The viewport provides instantaneous visual feedback; the entire studio model assumes this
- When the student cannot see: the cycle breaks unless alternative feedback exists
- Thesis: multi-modal feedback loops (text + touch + volume) produce different — and in some ways richer — spatial understanding than visual feedback alone

**2. Background — Feedback in Design Cognition** (~800 words)
- Schon (1983): reflection-in-action as a feedback loop between designer and situation
- Sass (2024): fabrication as a feedback modality — physical making as cognitive partner
- Sennett (2008): the hand as thinking organ
- Millar (1994), Giudice (2018): blind spatial cognition as sequential, landmark-based, language-mediated
- Gap: no existing system provides integrated multi-modal feedback for non-visual architectural design

**3. Five Feedback Loops** (~1,500 words)
Document each loop the project built, with timing, modality, and what kind of spatial knowledge it produces:

- **Loop 1: Command → Text confirmation** (milliseconds). The CLI's OK:/ERROR: protocol. Provides operational verification — did the command succeed? Does not provide spatial understanding. Fastest loop, narrowest bandwidth.
- **Loop 2: Command → Describe/Audit** (seconds). Multi-paragraph spatial narrative or compliance report. Provides relational understanding — how elements connect, what dimensions are, where violations exist. Medium speed, rich linguistic bandwidth.
- **Loop 3: Command → PIAF tactile print** (minutes). Raised-line plan drawing. Provides planimetric spatial understanding — layout, proportion, adjacency, circulation. Slow, high-bandwidth haptic channel.
- **Loop 4: Command → 3D printed model** (hours). Physical volume at scale. Provides volumetric spatial understanding — enclosure, height, wall thickness, opening size. Slowest loop, highest spatial bandwidth.
- **Loop 5: Pegboard → Camera → Model** (minutes). Physical construction digitized into the model. Provides the return path — spatial ideas conceived through touch entering the digital model. Closes the bidirectional loop.

**4. Observations from Studio** (~1,000 words)
- How Daniel moves between loops depending on the design question
- When text suffices (dimensional changes, parameter queries) vs. when touch is needed (overall layout evaluation, spatial proportion)
- The role of the 3D print in design review — Daniel holding the model while discussing his design
- Comparison with sighted students who only use the viewport loop

**5. Analysis — Multi-Modal vs. Single-Modal Feedback** (~800 words)
- The viewport provides one loop at one speed in one modality — fast but shallow
- The multi-modal pipeline provides five loops at five speeds in four modalities — slower but deeper
- Hypothesis: the forced slowness of tactile feedback produces more deliberate design reasoning
- Connection to Piaget & Inhelder: the sequential, multi-step feedback process mirrors the topological-to-metric developmental sequence

**6. Limitations and Future Work** (~400 words)
- Sonification as a sixth feedback loop (unrealized)
- Vibrotactile displays as real-time tactile feedback (fast loop, haptic modality)
- Controlled study comparing design outcomes across feedback conditions
- Loop timing constraints: PIAF takes 5 minutes, 3D print takes hours — too slow for some design phases

**7. Conclusion** (~300 words)
- The feedback loop is the unit of design pedagogy, not the tool
- Designing for blindness forced us to build multiple loops; the result is a richer feedback ecology than any single-modality system provides
- The curb cut: all students would benefit from multi-modal feedback; we just never built it because the viewport was fast enough

---

## Outline B: "The Alt-Text Is Not Enough: Translating Visual Architectural Culture for Blind Participation"

### Framework
The working document's Alt-Text Generator and LLM description pipeline reveal a deeper problem: architecture is a visual *culture*, not just a set of visual *tools*. Lectures use slides. Critiques reference drawings on walls. Precedent study is image analysis. Peer learning is watching classmates' pin-ups. Even when the tools are accessible, the culture remains visual. This paper examines what it takes to translate an entire disciplinary culture — not just individual images — into non-visual form.

### Audience
Architecture educators, disability studies scholars, and instructional designers. Connects to Gissen's "beyond access" argument and the working document's communication protocols section.

### Argument
Making tools accessible is necessary but not sufficient. The larger challenge is translating the visual culture of architecture education — lectures, critiques, precedent studies, peer feedback — into modalities a blind student can access. AI-powered description is the emerging mechanism, but its effectiveness depends on architectural specificity, multi-scale structure (Macro/Meso/Micro), and integration with the student's existing spatial models.

### Outline

**1. Introduction — Beyond Tool Access** (~500 words)
- The discipline's accessibility conversation focuses on tools (can the student use Rhino?)
- The harder problem is culture: can the student participate in a lecture, understand a critique, learn from a peer's pin-up, analyze a precedent?
- These are all visual activities that no tool alone can make accessible
- Thesis: accessible architectural education requires translating the discipline's visual culture into text, touch, and sound — and AI-powered description is the key mechanism

**2. The Visual Culture of Architecture Education** (~600 words)
- Lectures: slide-heavy, image-dependent, rarely described
- Critiques: drawings on walls, spatial references ("look at the entry sequence here"), gestural explanations
- Precedent study: analyzing photographs, drawings, and diagrams of existing buildings
- Peer learning: observing classmates' work, hearing feedback addressed to visual artifacts
- Assessment: visual deliverables (plans, sections, renderings, portfolios)
- Each of these is a site where blindness creates exclusion that tools alone cannot solve

**3. The Macro-Meso-Micro Description Framework** (~800 words)
- From the working document: whole-to-part methodology for image description
- Macro: medium, subject, purpose, atmosphere (3 sentences)
- Meso: composition, materials, orientation, scale, relationships, annotations (6 sentences)
- Micro: textures, structure, environment, proportions, multi-sensory analogies, accessibility cues, interpretive prompt (10+ sentences)
- Why architectural description requires domain specificity — generic alt-text fails
- The custom GPT prompt: 100+ lines of instruction that encode architectural literacy
- Example: Copper House 2 by Smiljan Radić — what generic alt-text misses and what the framework captures

**4. Five Sites of Cultural Translation** (~1,500 words)
For each site, describe the current state, the translation mechanism, and what remains unsolved:

- **Lecture slides:** AI description applied to each slide before class; instructor provides real-time verbal description during delivery. Challenge: pacing — descriptions take longer than sighted comprehension.
- **Studio critiques:** Ray-Ban Meta glasses provide real-time scene narration; AI generates descriptions of drawings on the wall. Challenge: the social dynamics of critique — interrupting to ask "what's on the wall" breaks the flow.
- **Precedent study:** Image-to-PIAF conversion + AI description. The student gets both a verbal description and a tactile drawing they can trace. Challenge: the description is an interpretation, not direct access.
- **Peer learning:** How does a blind student learn from watching a classmate receive feedback? The feedback itself can be captured in audio. But the visual reference — "your plan shows X" — requires description of the classmate's drawing.
- **Assessment:** The working document identifies this as the largest gap. Visual pin-ups, graphical portfolios — all inaccessible. Alternative: the CLI transcript, the CMA diff history, the tactile outputs, and a verbal presentation constitute a non-visual portfolio. But the discipline has no consensus on evaluating them.

**5. Communication Protocols as Cultural Infrastructure** (~600 words)
- From the working document: "use your words," describe visual content in real time, no "this" or "here" without referents
- These are not just accessibility accommodations — they are better teaching practices
- Training instructors to describe what they show is harder than building the CLI
- The institutional coordination required: DRES, CITL, digital accessibility office, individual faculty

**6. Limitations** (~400 words)
- AI description quality varies; architectural specificity is inconsistent
- Real-time description in lectures and critiques disrupts timing
- Peer learning translation is largely unsolved
- Assessment methodology is nascent
- One student; cultural translation is context-dependent

**7. Conclusion** (~300 words)
- Tools give the student a way to design; cultural translation gives the student a way to learn
- AI description is the most promising mechanism, but it must be architecturally specific, multi-scale, and integrated
- The discipline's visual culture is not a neutral medium — it is a barrier that requires deliberate, sustained translation

---

## Outline C: "The Desk, The Code, The Print: Designing an Integrated Accessible Workstation for Architectural Education"

### Framework
The working document describes a physical workstation — The Desk — that integrates digital tools, tactile output, and physical modeling surfaces into a single accessible workspace. This paper is a design research paper about the workstation itself: its components, its spatial organization, its alignment with the digital model, and what the integrated physical-digital environment enables that separate tools cannot.

### Audience
Design researchers, fabrication-focused educators, and HCI researchers. Connects to Sass's fabrication pedagogy and the broader maker/fablab movement.

### Argument
Accessible architectural design requires not just accessible software but an accessible *workspace* — a physical environment where digital authoring, tactile output, physical modeling, and digitization are co-located and coordinated. The integration of these components into a single desk, with shared coordinate systems and automated feedback between digital and physical, constitutes a new kind of design workstation that embodies the physical-digital fluency the discipline has advocated.

### Outline

**1. Introduction — The Workstation Problem** (~400 words)
- A blind student's tools are scattered: computer on one surface, PIAF machine in another room, 3D printer elsewhere, tactile baseboard on a table
- The distance between tools is distance in the feedback loop — every step away slows the design cycle
- Thesis: an integrated workstation that co-locates digital authoring, tactile output, physical modeling, and digitization transforms the feedback loop from a multi-location journey into a single-desk workflow

**2. Background — Workstations, Desks, and Design Environments** (~600 words)
- The architect's desk as a design instrument (historical: drafting table, parallel rule, lamp)
- The fablab/makerspace as distributed workstation (laser cutter + 3D printer + CNC + computer)
- The accessible workstation: what exists (adjustable-height desks, screen reader setups, braille displays) and what does not (integrated design-to-fabrication for blind users)
- Gap: no existing workstation integrates digital CAD, tactile output, and physical modeling for non-visual architectural design

**3. The Desk: Components and Organization** (~1,000 words)
Detailed description of each component, its role in the feedback loop, and its physical placement:

- Tactile gridded baseboard — aligned with digital coordinate system, for wire/peg spatial construction
- Computer with CLI + screen reader + braille display — the digital authoring station
- Laser printer — for printing toner on PIAF microcapsule paper
- PIAF heater — for swelling printed toner into raised lines
- Bambu Lab P1S 3D printer — for tactile scale models
- Large high-contrast monitor — for sighted collaborators or residual vision
- (Future) Overhead camera — for digitizing physical constructions on the baseboard
- (Future) Smart baseboard — embedded sensors for component detection

Physical layout: the baseboard adjacent to the keyboard, the PIAF machine within arm's reach, the 3D printer on the same surface. Daniel can type a command, print a tactile sheet, heat it, and read it without leaving his chair.

**4. Coordinate Alignment** (~600 words)
- The critical design decision: the baseboard's grid aligns with the CMA's coordinate system
- A peg at physical position (3, 5) corresponds to digital coordinates (3, 5)
- This alignment enables seamless transition between physical and digital spatial reasoning
- Technical implementation: calibration markers (AprilTag/ArUco), homography computation, coordinate mapping
- Why alignment matters: without it, the physical and digital representations drift, and the student must maintain two separate spatial models

**5. Workflow Through the Desk** (~800 words)
Walk through a complete design session showing how the components interact:
- Daniel places wire on the baseboard to sketch a rough layout
- The overhead camera captures the configuration
- The wire positions enter the digital model as geometry
- Daniel refines through CLI commands
- A PIAF print produces a tactile plan he reads alongside the physical wire model
- He compares the two — the wire sketch and the digital refinement — on the same coordinate grid
- A 3D print adds volumetric understanding
- He holds the 3D print in one hand while tracing the PIAF plan with the other

**6. Design Decisions and Trade-offs** (~600 words)
- Size constraints: everything must fit on a desk, but PIAF machines and 3D printers are bulky
- Noise: the 3D printer operates during design sessions; acoustic interference with screen reader
- Speed: PIAF prints are fast (minutes); 3D prints are slow (hours); different loops for different questions
- Cost: the full Desk costs approximately $X (PIAF machine, Bambu printer, baseboard materials, camera)
- Portability: the Desk is currently a fixed workstation; a portable version for different studios is future work

**7. Evaluation and Next Steps** (~500 words)
- How we tested the Desk with Daniel over the academic year
- What worked: PIAF-adjacent printing shortened the loop dramatically; coordinate alignment reduced spatial confusion
- What did not work yet: camera digitization is prototype-quality; smart baseboard not implemented
- Future: embedded sensors, automated PIAF feeding, voice-activated components, modular design for different disability profiles

**8. Conclusion** (~300 words)
- The Desk is not just furniture — it is a design instrument, as the drafting table was for previous generations
- Integrating digital and physical into a single accessible workspace embodies the physical-digital fluency the discipline advocates
- The Desk, like the CLI, is built for blindness but useful for everyone — any student benefits from having fabrication output within arm's reach of their modeling environment

---

## Outline D: "Nothing About Us Without Us: Co-Designing Accessible CAD with a Blind Architecture Student"

### Framework
The working document emphasizes that the tools evolve from Daniel's weekly feedback — he is a co-designer, not a test subject. This paper is a participatory design / co-design paper in the tradition of Charlton (1998) and disability justice scholarship. The contribution is the methodology: how to co-design accessible design tools with a disabled user as a genuine collaborator, not an informant.

### Audience
Participatory design researchers, disability studies scholars, and architecture educators interested in inclusive design processes.

### Argument
Most accessible tool development follows a consultative model: researchers build a tool, test it with disabled users, and iterate based on usability feedback. The Radical Accessibility Project follows a co-design model: Daniel shapes tool requirements, identifies spatial relationships sighted developers miss, and uses the tools in the same studio as his sighted classmates. His disability experience is expertise, not data. This methodological difference produces fundamentally different tools.

### Outline

**1. Introduction — Who Designs the Tools?** (~500 words)
- Charlton (1998): "Nothing about us without us" — disability rights principle
- Applied to accessible technology: who decides what the tool does? Who defines the requirements? Who evaluates whether it works?
- Most accessible tool research: researchers design, disabled users test
- Our approach: a blind student co-designs the tools he uses in studio, weekly
- Thesis: co-design with a disabled user as genuine collaborator produces tools that consultative design cannot — because the collaborator's disability experience generates requirements the researcher cannot imagine

**2. Background — Participatory Design and Disability** (~700 words)
- Participatory design tradition (Schuler & Namioka 1993)
- Disability-centered co-design: Hamraie & Fritsch (2019) crip technoscience; disabled people as knowers and makers
- Prior work in accessible 3D modeling: Siu et al. (2019, 2025) — user studies with blind participants, but participants are evaluators, not co-designers
- Gap: no published account of a blind user co-designing the architectural CAD tools they use in a live studio setting

**3. The Co-Design Process** (~1,200 words)
Document the actual process across the academic year:

- **Weekly cycles:** Daniel uses the tools in studio → encounters a friction or gap → reports it in next session → researcher implements a solution → Daniel evaluates in studio → the tool evolves
- **Examples of co-designed features:**
  - Auto-corridor cells: Daniel needed to identify which cells overlap the corridor before naming rooms → `auto_corridor A` command created
  - Output verbosity: early responses were multi-line, overwhelming the screen reader → protocol tightened to single-line OK:/ERROR: with optional detail
  - Describe levels: Daniel needed different detail levels for different tasks → multi-level describe command with summary/detail/JSON modes
  - Braille label sizing: initial sizing was model-relative; Daniel's fingers could not read small labels → fixed paper-absolute sizing per BANA standards
  - Tactile density: Daniel's fingers could not distinguish elements on dense PIAF prints → density checker with 40% warning threshold
- **What Daniel contributed that the researcher could not have imagined:**
  - The importance of orientation language ("the corridor runs north-south from the entrance") over coordinate language ("the corridor is at y=48")
  - That the undo stack needs verbal confirmation of what was undone, not just that undo occurred
  - That the `describe` command must work at multiple spatial scales — overall, bay-level, room-level
  - That errors must suggest corrective actions, not just report what went wrong

**4. Methodology: Co-Design vs. Consultation** (~800 words)
- Define the distinction: consultation = researcher designs, user evaluates; co-design = user shapes requirements, researcher implements
- Daniel's role: not a test subject recruited for evaluation but a collaborator who shapes tool requirements as a peer
- Power dynamics: Daniel is a student; the researcher is a faculty member. How do you maintain genuine co-design in an unequal power relationship?
- Documentation: CLI command logs as a design research artifact — every command Daniel types is a record of how he thinks about spatial design

**5. What Co-Design Produced That Consultation Would Not** (~800 words)
- Features that emerged only from Daniel's direct experience in studio, not from the researcher's analysis
- The screen-reader-native output protocol: the researcher designed for clarity; Daniel's screen reader experience reshaped it for parsability
- The crash-only viewer architecture: the researcher designed for robustness; Daniel's inability to visually confirm crash recovery made it non-negotiable
- The tactile output pipeline: the researcher imagined static prints; Daniel's hands-on evaluation produced the density checker, the multi-preset system, and the paper-size options
- Analysis: each example shows how disability experience generates requirements that non-disabled designers cannot access

**6. Ethical Considerations** (~500 words)
- Informed consent and authorship: Daniel as co-author vs. research subject
- Compensation and credit: Daniel's contributions are intellectual, not just experiential
- The risk of instrumentalizing disability: using Daniel's experience as data vs. respecting it as expertise
- Publication ethics: how much of Daniel's personal experience is appropriate to share?

**7. Limitations** (~400 words)
- One co-designer; the methodology is documented through a single case
- The co-design relationship exists within an academic power structure
- Generalizability: would the methodology work with other disabilities? Other design domains?
- The tools remain researcher-implemented; Daniel directs requirements but does not write code (yet)

**8. Conclusion** (~300 words)
- Co-design is not just an ethical practice — it is a superior methodology for accessible tool development
- Daniel's disability experience is the project's most important resource — it generates requirements that no amount of researcher ingenuity can substitute
- "Nothing about us without us" is not a slogan but a design methodology, and the tools it produces are demonstrably different from tools designed by consultation

---

## Outline E: "From Accommodation to Architecture: Why Disability Belongs in the ACADIA Discourse"

### Framework
The working document's legal framework section (Section 504, ADA, IITAA, WCAG 2.1) reveals a tension: the law mandates *accommodation* — modifications that give disabled students equal opportunity. But the project goes beyond accommodation to produce new knowledge about computational design. This paper is a polemic aimed directly at the ACADIA community: disability is not a compliance issue to be handled by the disability office. It is a generative design condition that the computational design community should engage with the same intellectual seriousness it brings to material performance, structural optimization, or environmental simulation.

### Audience
The ACADIA community itself — an argument for why disability belongs in the computational design discourse as a first-class research topic, not a social responsibility sidebar.

### Argument
ACADIA has published extensively on performance-driven design, material computation, and AI-assisted form generation. It has published almost nothing on disability as a computational design problem. This is not because disability is irrelevant to the discourse — it is because the community has ceded the topic to disability services offices and accessibility compliance frameworks. We argue that disability is a design problem at every level ACADIA cares about: interface design, parametric representation, feedback systems, fabrication pipelines, and design cognition. The Radical Accessibility Project is evidence.

### Outline

**1. Introduction — The Missing Topic** (~500 words)
- Survey ACADIA proceedings: thousands of papers on parametric design, material performance, AI, fabrication, environmental simulation
- How many papers on disability? How many blind architects appear in ACADIA's intellectual universe? How many deaf, motor-impaired, neurodiverse?
- The absence is not neutral — it reflects a community that has defined its boundaries around a sighted, able-bodied designer
- Thesis: disability is a computational design problem, and ACADIA is the right community to work on it — if it chooses to

**2. What Disability Is Not** (~600 words)
- Not a compliance problem (that's for the ADA office)
- Not a UX problem (that's for the HCI community)
- Not a social justice problem to be solved by good intentions (that's for the equity panels)
- Reframing: disability is a *design constraint* that produces novel solutions — exactly the logic computational designers apply to material, structural, and environmental constraints

**3. What Disability Is: A Computational Design Problem** (~1,200 words)
Map disability onto ACADIA's core research areas:

- **Interface design:** The GUI is a design decision, not a natural law. A CLI is a different interface decision with different properties (semantic, auditable, scriptable, accessible). This is interface design research, not accommodation.
- **Representation:** The CMA (JSON state file) as an alternative to the viewport is a representation theory question. Evans, Carpo, Oxman — the same discourse ACADIA engages with — applies directly. What happens to architectural representation when vision is removed?
- **Feedback systems:** The text/tactile/3D-print feedback loops are a design cognition question. Schon, Sass, Sennett — the same references ACADIA cites — apply directly. How does non-visual feedback change design thinking?
- **Fabrication:** PIAF swell paper and 3D printing for tactile output are fabrication problems — material selection, resolution limits, density management, watertight mesh generation. ACADIA publishes fabrication research constantly.
- **AI:** The MCP server, the image description pipeline, and AI-assisted development are AI research. ACADIA's 2026 program will be dominated by AI papers. Ours is different — but it is AI research.

**4. Evidence: The Radical Accessibility Project** (~1,000 words)
- Brief description of the full system: The Desk, The Code, tactile output, AI tools
- Frame each component as a computational design research contribution, not an accommodation
- Show that the research questions — how to represent space in text, how to verify geometry without vision, how to close the physical-digital loop — are questions ACADIA already asks, applied to a user the community has not considered

**5. Why ACADIA and Not ASSETS** (~600 words)
- ACM ASSETS (the accessibility computing conference) publishes excellent work on accessible technology
- But ASSETS researchers are not architects — they do not bring architectural knowledge to the problem
- ACADIA researchers are architects but do not bring accessibility thinking to their work
- The gap: no community combines computational design expertise with disability-centered design methodology
- We argue ACADIA should be that community — not instead of ASSETS but alongside it

**6. What the Community Could Do** (~500 words)
- Include disability as a topic area in the call for papers
- Fund accessibility-focused design research with the same seriousness as material or environmental research
- Invite blind, deaf, and motor-impaired designers to present and review
- Require accessibility statements for digital tools published at ACADIA
- Recognize that "designing for disability" is designing for the future — aging populations, temporary impairments, situational disabilities

**7. Conclusion** (~300 words)
- Disability is not at the margins of computational design. It is at the foundation — because the tools' assumptions about who can design determine what the discipline can become
- ACADIA has the expertise to make architecture's tools genuinely inclusive. The question is whether it has the will.
- The Radical Accessibility Project is one lab's attempt. The discourse needs a community.

---

## Summary: How the Five Outlines Differ

| Outline | Title | Lead Framework | Core Argument |
|---------|-------|----------------|---------------|
| **A** | "Closing the Loop" | Design cognition / feedback theory | Multi-modal feedback loops produce richer spatial understanding than single-modality (viewport) feedback |
| **B** | "The Alt-Text Is Not Enough" | Cultural translation / description theory | Accessible tools are necessary but insufficient; the discipline's visual *culture* (lectures, critiques, peer learning, assessment) requires systematic translation |
| **C** | "The Desk, The Code, The Print" | Design research / workstation design | An integrated accessible workstation — co-located digital, tactile, and physical tools with aligned coordinates — transforms the design feedback loop |
| **D** | "Nothing About Us Without Us" | Participatory design / co-design methodology | Co-designing tools *with* a blind student (not *for* him) produces fundamentally different tools than consultative design; disability experience is expertise, not data |
| **E** | "From Accommodation to Architecture" | Disciplinary polemic / community critique | Disability is a computational design problem that belongs in the ACADIA discourse — not in the disability services office — and the community's silence on the topic reflects a bias it should confront |

### Relationship to Previous Drafts (V1–V6)

These five outlines are designed to complement, not duplicate, the six full paper drafts already written:

- **V1** (balanced), **V2** (pedagogy-first), and **V3** (blindness-as-method) focused on pedagogical and epistemological arguments
- **V4** (representation theory) focused on Evans/Carpo and the CMA as notation
- **V5** (AI polemic) focused on AI-assisted development vs. AI-assisted design
- **V6** (full stack) drew from the working document to describe the complete ecosystem

The five new outlines attack dimensions the full drafts did not lead with:
- **A** leads with feedback loop theory (design cognition focus)
- **B** leads with visual culture translation (the description/alt-text dimension from the working document)
- **C** leads with the physical workstation (The Desk, unique to the working document)
- **D** leads with co-design methodology (Daniel's role as collaborator)
- **E** leads with a community-directed polemic (why ACADIA should care)

Any of these outlines could be developed into a full 4,000–6,000 word paper. They can also be mixed: Outline A's feedback loop analysis could be combined with Outline C's workstation description, for example, or Outline D's co-design methodology could frame the tools described in Outline B.
