# ACADIA 2026 Paper Ideas: Radical Accessibility Project

**Project:** Radical Accessibility Project (UIUC School of Architecture)
**PI:** John Clark
**Last updated:** 2026-02-24

---

## Conceptual Framing Ideas

The following are distinct intellectual frames through which the paper could position its contribution. Each treats the project not as an accessibility accommodation but as a site of disciplinary critique and invention. They are ordered roughly from the most architecturally theoretical to the most technically specific, though the strongest paper will likely weave elements of several.

---

### Framing 1: The Ocularcentric Stack -- How Vision is Hardcoded into Architectural Software

**Working title:** "Ocularcentrism All the Way Down: Designing Architectural Software Without Vision"

**Argument:**

Pallasmaa's *The Eyes of the Skin* (1996) critiqued architecture's dependence on vision at the level of the built environment -- the hegemony of the image, the suppression of tactile, olfactory, and auditory experience. But Pallasmaa's critique stopped at the building. It never descended into the tools. The Radical Accessibility Project argues that ocularcentrism is not merely an attribute of architectural culture; it is structurally encoded in the computational tools architects use to design. Rhino's viewport, Grasshopper's visual canvas, Revit's click-and-drag modeling -- these are not neutral instruments that happen to be visual. They are instruments that make visuality a prerequisite for architectural thought. When a tool can only be operated by looking at it, it does not merely exclude blind users; it enforces a particular epistemology of design in which "knowing the design" means "seeing the design."

The project exposes this by building a complete architectural design pipeline -- from parametric floor plan generation to tactile fabrication output -- that operates without any visual interaction. The CLI controller produces the same Canonical Model Artifact (the JSON state file) whether or not anyone ever looks at it in Rhino. This is not a workaround. It is a demonstration that the architectural model is not the viewport. The model is the structured description of spatial relationships: bay widths, column grids, corridor axes, rotation angles. What Rhino renders is one possible projection of that description -- a visual projection, useful but not essential. By removing the visual projection from the authoring loop, the project reveals that the "design" was never in the viewport to begin with.

This framing draws on Heylighen and Herssens's (2014) argument that architects' visual ways of knowing are simultaneously ways of "not knowing" -- of systematically overlooking non-visual spatial qualities. It extends their argument from design outcomes (buildings) to design instruments (software). It positions the project within ACADIA's explicit turn toward accessibility and equity (Cupkova et al., 2023; Noel et al., 2021) while going further than those calls for change by delivering a working system. And it makes a claim that should provoke ACADIA's computationally literate audience: that the standard architecture of CAD software -- model + viewport + mouse interaction -- is not a neutral technical choice but an ocularcentric one, and that alternative architectures (CLI + JSON + file watcher) are not merely accessible but reveal something about what architectural models actually are.

**Connection to literature review:**
- Pallasmaa (1996): Extends the ocularcentrism critique from buildings to tools
- Heylighen & Herssens (2014): "Designerly ways of not knowing" applied to software design, not just building design
- Noel et al. (2021): The "question of access" made concrete and operational
- Cupkova et al. (2023): Responds directly to ACADIA's AI/accessibility/justice call
- Celani & Vaz (2012): Their finding that scripting is more powerful for generative systems gains new meaning when the alternative (visual programming) is completely inaccessible
- Lit review gap #1: No CumInCAD paper describes a CLI-first screen-reader-native CAD tool

**Why compelling at ACADIA:**
ACADIA audiences are deeply invested in computational tools and care about the relationship between tool design and design thinking. This framing does not ask for sympathy; it makes an architectural theory argument -- that their tools encode epistemological assumptions -- and then demonstrates it by building the alternative. It treats Grasshopper and Rhino not as villains but as case studies in a larger argument about the relationship between interface modality and design knowledge. The audience will recognize the technical architecture (JSON, Python, Rhino) and be forced to confront why that architecture has always assumed a sighted user.

---

### Framing 2: The Canonical Model Artifact -- What is an Architectural Representation?

**Working title:** "The Model is the JSON: Architectural Representation Beyond the Viewport"

**Argument:**

Architectural computing has long debated what constitutes the "model" in digital design. Is it the geometry in the viewport? The parametric definition in Grasshopper? The BIM database? The Radical Accessibility Project introduces an unexpected answer by way of necessity: the model is a JSON file -- a human-readable, schema-versioned, semantically structured text document that a blind user can query, edit, and understand through a screen reader without ever seeing its geometric projection. The project calls this the Canonical Model Artifact (CMA), and its existence forces a question: if the complete design intent is captured in a text file that a screen reader can parse, what exactly is the Rhino viewport adding?

The CMA is not a simplified or degraded representation. It contains every parameter of the design: bay dimensions, column positions, corridor widths, rotation angles, hatch patterns, braille labels. It supports undo via deep copy, schema versioning for forward compatibility, and atomic writes for crash safety. Rhino is a viewer -- one of many possible viewers, and a disposable one. If Rhino crashes, nothing is lost. The user's work lives in the JSON file, not in Rhino's memory. This "crash-only viewer" principle is an accessibility innovation, but it is also an architectural computing insight: the design representation should be independent of any particular rendering environment.

This framing reframes the project's technical architecture as a contribution to the theory of architectural representation. The CMA inherits from a long line of structured design descriptions -- from shape grammars to BIM schemas to IFC -- but it is distinguished by being authored and comprehensible through a non-visual interface. A sighted architect reads the Rhino viewport; Daniel reads the CMA directly, querying it through CLI commands like `show bays` or `describe corridor A`. Both are accessing the same design, through different modalities. The question of which access modality is "primary" turns out to be a question about what the architectural model actually is -- and the project argues that the structured semantic description (the CMA) is more fundamental than any particular geometric rendering.

**Connection to literature review:**
- Maleki & Woodbury (2013): PIM's live script-model link prefigures the CMA, but assumes visual primacy
- Rietschel et al. (2024): Their text-to-JSON-to-Grasshopper pipeline parallels the project's architecture but was built for convenience, not necessity
- Janssen & Chen (2011): Their comparison of visual dataflow systems implicitly reveals what is lost when the only interface is visual
- Miller (2010): The CMA is the shared artifact in a non-standard collaborative workflow
- Lit review gap #6: No paper examines the file-watching pattern as an accessibility architecture

**Why compelling at ACADIA:**
ACADIA has a persistent interest in design representation, data exchange, and interoperability (the perennial IFC/BIM debates). This framing positions the project within those conversations, arguing that the CMA pattern -- where the canonical model is a readable, queryable text artifact and the viewer is a disposable consumer -- is not just an accessibility strategy but a better architecture for computational design. It will resonate with an audience tired of losing work to Rhino crashes and frustrated by Grasshopper definitions that are opaque even to their authors.

---

### Framing 3: Blindness as Method -- Constraint-Driven Innovation in Computational Design

**Working title:** "Blindness as Method: What Non-Visual Design Reveals About Architectural Computation"

**Argument:**

The Radical Accessibility Project's thesis is not that blind people can do architecture despite their blindness. It is that designing for blindness first produces tools and workflows that are often superior to their visual-centric counterparts. This is a strong claim, and it requires evidence. The paper presents three cases where the constraint of non-visual interaction generated innovations that benefit all users.

First: crash resilience. Because a blind user cannot visually confirm that Rhino has recovered after a crash, the project's architecture treats Rhino as a "crash-only viewer" -- a disposable rendering process that can be killed and restarted without data loss. The user's work lives in the JSON state file, written atomically (write to .tmp, fsync, os.replace). This pattern, born from accessibility necessity, is better engineering than the standard approach of trusting Rhino's internal state. Every architect who has lost work to a Rhino crash would benefit from this architecture.

Second: semantic clarity. Because a blind user cannot glance at a viewport to assess a design, every design parameter must be named, structured, and queryable through text. The CLI output protocol (OK:/ERROR: prefixes, one item per line, no tables, no visual-only indicators) forces a level of semantic explicitness that visual tools never achieve. When Daniel types `show bays`, the response lists each bay by name with its dimensions, rotation, and corridor status. A sighted user looking at the same design in Rhino cannot extract this information without measuring, clicking, or reading object properties one by one. The accessible interface is more informative.

Third: auditable design history. Because the CMA is a version-controlled text file, every design change is diffable. Git tracks the evolution of `state.json` with line-level precision. No equivalent audit trail exists for mouse-driven Rhino modeling. The constraint of text-only interaction produces inherently auditable design processes.

The framing draws on a broader disability studies argument -- the "transformative model" of disability, which holds that the experience of disability does not merely reveal barriers in the environment but generates new knowledge and new capacities. Vermeersch and Heylighen's (2012) case study of Carlos Mourao Pereira, a blind architect whose designs became more multi-sensory after losing his sight, provides an individual precedent. The Radical Accessibility Project provides a tool-level precedent: the constraint of blindness, applied to CAD tool design, produces tools with better crash resilience, richer semantic structure, and more auditable design histories.

**Connection to literature review:**
- Vermeersch & Heylighen (2012): Carlos Pereira as individual precedent; the project extends from practitioner to tool ecosystem
- Heylighen & Herssens (2014): "Designerly ways of not knowing" reframed as "designerly ways of not seeing the tool's assumptions"
- Vermeersch et al. (2018): Disability experience as generative knowledge, applied here to software design
- Celani & Vaz (2012): Their finding that scripting is more powerful for generative systems gains an accessibility dimension
- Akbar et al. (2023): Their call for platform-agnostic, coordinates-based pedagogy is realized in the CLI approach
- Lit review gap #5: The project provides the working prototype that equity papers call for

**Why compelling at ACADIA:**
ACADIA audiences respect technical innovation and are skeptical of papers that trade on social justice framing alone. This framing leads with specific technical improvements -- crash resilience, semantic richness, auditability -- and then reveals that they were produced by an accessibility constraint. The argument is that constraint-driven innovation is a legitimate and underexplored design methodology for architectural software, and blindness is the constraint that reveals the most about visual tools' hidden weaknesses. This is a claim the audience can evaluate on technical merits.

---

### Framing 4: The Controller/Viewer Split as Architectural Theory

**Working title:** "Separating Intent from Projection: A Non-Visual Architecture for Architectural Software"

**Argument:**

The Radical Accessibility Project's core technical decision -- separating the controller (CLI) from the viewer (Rhino) via a shared state file -- is not merely a software engineering pattern. It is an epistemological commitment about the nature of architectural design. The controller captures design intent: spatial relationships, dimensional parameters, structural logic. The viewer renders one possible geometric projection of that intent. By making these two concerns independent and decoupled, the project claims that architectural design intent is not visual. It can be expressed, manipulated, and understood entirely through structured text. Vision is one way to verify it, but not the only way, and perhaps not the best way.

This is a radical position within architectural computing, where the dominant paradigm (from Sketchpad to Rhino to Revit) has always fused intent and projection into a single visual environment: you express your design intent by drawing or clicking, and you verify it by looking. The project's architecture denies this fusion. Daniel expresses intent through typed commands (`set bay A rotation 30`, `corridor A width 8`). He verifies it through textual queries (`show bays`, `describe corridor A`) and tactile output (PIAF swell paper, 3D prints). A sighted collaborator verifies through the Rhino viewport. Both are looking at the same CMA; neither's verification modality is privileged.

The controller/viewer separation also mirrors a deep question in architectural theory: the relationship between the building as designed (intent, program, spatial logic) and the building as experienced (light, shadow, view, material). Pallasmaa (1996) argued that architecture has privileged the visual experience over the multi-sensory one. The project's software architecture enacts a parallel argument at the tool level: that architectural computing has privileged the visual projection over the semantic description, and that separating them produces a clearer understanding of both.

**Connection to literature review:**
- Pallasmaa (1996): The intent/projection split in software mirrors the designed/experienced split in buildings
- Maleki & Woodbury (2013): PIM links script and model but assumes visual primacy for both
- Rietschel et al. (2024): Text-to-JSON-to-Grasshopper is a one-directional version of the controller/viewer pattern
- Miller (2010): The CMA as shared artifact in a heterogeneous workflow
- Janssen & Chen (2011): Comparison of visual dataflow systems -- what if the dataflow were not visual?
- Lit review gap #6: The file-watching pattern as accessibility architecture is novel

**Why compelling at ACADIA:**
This framing speaks directly to ACADIA's core intellectual concern: the relationship between computation and design. It does not merely present an accessible tool; it proposes a software architecture that embodies a theory of what architectural models are. The controller/viewer split is a testable technical claim with theoretical implications. ACADIA reviewers who build Grasshopper plugins, develop Rhino tools, or teach computational design will recognize the pattern and be challenged by the argument that fusing intent and projection in a visual environment is a design choice, not a necessity -- and not always the best one.

---

### Framing 5: Text as the Universal Interface -- Against Visual Programming

**Working title:** "Against the Canvas: Text-First Architectural Computing for Universal Access"

**Argument:**

The rise of visual programming in architecture -- Grasshopper, Dynamo, Marionette -- is typically narrated as a democratization story: visual programming makes parametric design accessible to architects who cannot (or do not want to) write code. The Radical Accessibility Project reveals the other side of this story: visual programming makes parametric design completely inaccessible to anyone who cannot see the canvas. Grasshopper's node-and-wire interface is opaque to screen readers. A blind user cannot create, connect, or inspect Grasshopper components. The "democratization" of visual programming is, for blind users, a new exclusion.

The project's response is to return to text -- not as a retreat to an older paradigm, but as an advance toward a more universal one. Text is the interface modality that screen readers, braille displays, speech synthesizers, and sighted eyes can all parse. The CLI command `set bay A rotation 30` is legible to JAWS, NVDA, VoiceOver, a braille display, a sighted collaborator reading the terminal, a log file, a Git diff, and an LLM. No visual programming node achieves this breadth of access. Text is not the accessible alternative to visual programming; text is the universal interface that visual programming abandoned.

This argument has precedent in the computing world (the Unix philosophy of text streams, the resurgence of terminal-based development tools) but has never been made within architectural computing specifically. Celani and Vaz (2012) compared scripting and visual programming pedagogically and found scripting more powerful for generative systems, but they never considered accessibility. Rietschel et al. (2024) built an LLM-to-JSON-to-Grasshopper pipeline that converts text to visual nodes -- a pipeline that would be unnecessary if the text were the interface rather than a translation layer. The project demonstrates that for at least one class of architectural design tasks (parametric floor plan generation), the text-first approach is not merely equivalent to the visual approach but broader in reach and richer in metadata.

**Connection to literature review:**
- Celani & Vaz (2012): Text vs. visual CAD comparison, now with accessibility as a deciding criterion
- Rietschel et al. (2024): LLM-to-Grasshopper as evidence that text-to-geometry is viable; the project cuts out the visual middleman
- Atakan et al. (2025): Kakadoo's speech interface for Grasshopper still depends on visual feedback; the project does not
- Akbar et al. (2023): "Democratizing the toolbox" via platform-agnostic, coordinates-based tools aligns with the CLI approach
- Fricker et al. (2020): "Computational design thinking" does not require visual cognition
- Lit review gap #4: LLM-to-CAD work ignores screen reader compatibility; the CLI output protocol addresses this

**Why compelling at ACADIA:**
This is the most provocative framing for an ACADIA audience, many of whom are deeply invested in Grasshopper and visual programming. The argument is not that Grasshopper is bad, but that its visual-only interface is a limitation masquerading as a feature, and that a text-first alternative achieves equivalent design capability with broader access. The provocation is productive: it forces the audience to consider who their tools exclude and whether visual interaction is necessary or merely habitual. The strongest version of this paper would include a direct comparison -- the same parametric design task performed in Grasshopper (visually) and in the CLI (textually) -- showing that the textual version is no slower, equally expressive, and accessible to a population that the visual version completely excludes.

---

### Framing 6: The Physical-Digital Round-Trip as Inclusive Pedagogy

**Working title:** "Closing the Loop: Physical-Digital Round-Trips for Inclusive Architectural Pedagogy"

**Argument:**

Architectural education has always involved physical artifacts: hand drawings, physical models, pin-up boards, desk crits. The shift to computational tools has increasingly digitized these interactions, but the digital tools assume visual access. The Radical Accessibility Project closes the physical-digital loop in a way that includes a blind student at every step. Daniel authors a parametric floor plan through the CLI. The design is exported to PIAF swell paper (raised-line tactile drawing) or a 3D print. Daniel explores the physical output with his hands. He feeds observations back through the CLI. In the other direction, Daniel constructs spatial relationships on a pegboard using wire; an overhead camera + OpenCV digitizes the wire positions into Rhino geometry; the system provides audio feedback confirming what was captured.

This bidirectional flow -- digital to tactile, tactile to digital -- is not merely an accommodation. It is a pedagogical model. The literature on tactile fabrication for blind users (Celani et al., 2013; Koch et al., 2012) has focused on the output direction: producing tactile artifacts for blind people to understand existing designs. The project closes the loop: the blind student is the author, not just the recipient. Herssens and Heylighen's (2011) haptic design parameters -- texture, weight, compliance, temperature -- are not just qualities of the tactile output; they are design variables that Daniel manipulates through the CLI and evaluates through touch.

The pedagogical implications extend beyond accessibility. The physical-digital round-trip forces explicitness about what a representation conveys and what it omits. A PIAF drawing has limited resolution; a 3D print has no color information; a braille label must be concise. These constraints are not deficits -- they are pedagogical provocations that sharpen design thinking for all students. The project demonstrates an inclusive studio model where a blind student and sighted classmates share a design conversation mediated by artifacts that each can access in their own modality.

**Connection to literature review:**
- Celani et al. (2013): Extends tactile models from output (receiving) to round-trip (authoring + receiving)
- Koch et al. (2012): Rapid prototyping for tactile access; the project adds the CLI-to-fabrication automation
- Herssens & Heylighen (2011): Haptic design parameters as design variables, not just output qualities
- Vermeersch et al. (2018): Participatory design methodology aligns with Daniel as co-designer
- Sass (ACADIA 2024 Teaching Award): Fabrication-centered pedagogy; the project asks what that looks like for a blind student
- Lit review gap #3: Tactile fabrication papers treat blind users as recipients, not authors

**Why compelling at ACADIA:**
ACADIA has a strong interest in digital fabrication and its pedagogical role (cf. Sass's teaching award). This framing connects the project to that interest while introducing a population and a set of constraints that the ACADIA community has not previously considered. The physical-digital round-trip is familiar; the inclusion of a blind student as a full participant in that loop is novel. The paper can include compelling visual evidence: photos of Daniel working with tactile drawings, the pegboard with wire constructions, and the CLI terminal alongside the Rhino viewport showing the same design in two modalities.

---

### Framing 7: Against the Medical Model -- Software Architecture as Disability Justice

**Working title:** "Not Assistive Technology: Architectural Software as Disability Justice"

**Argument:**

Disability studies distinguishes three models of disability. The medical model locates the problem in the disabled body and seeks to fix the person. The social model locates the problem in the environment and seeks to fix the barriers. The transformative model goes further: it holds that the experience of disability generates unique knowledge that benefits everyone. The Radical Accessibility Project embodies the transformative model at the level of software architecture.

The project does not adapt Rhino for a blind user (medical model -- "fix the person's access to the existing tool"). It does not merely provide an alternative interface to an unchanged system (social model -- "remove the barrier"). It builds a fundamentally different software architecture -- CLI controller, JSON Canonical Model Artifact, crash-only viewer -- that emerges from the requirements of a blind user and produces a system that is better for all users. The CMA pattern, born from the need for a screen-reader-parseable design representation, turns out to be more crash-resilient, more auditable, and more interoperable than the standard visual-primary architecture. The CLI output protocol, born from the need for screen-reader-compatible responses, turns out to be clearer and more machine-parseable than Rhino's status messages.

This framing connects the project to the broader disability justice movement in architecture (Noel et al., 2021; eCAADe 2022 conference theme) while grounding it in specific technical decisions. Each architectural choice in the system can be traced to a disability requirement that produced a general improvement. The paper would present a table mapping: (1) accessibility requirement, (2) technical decision, (3) general benefit. For example: "Requirement: blind user cannot visually confirm crash recovery. Decision: atomic file writes + crash-only viewer. General benefit: no data loss for any user, regardless of ability."

**Connection to literature review:**
- Noel et al. (2021): Equity in computational design -- the project moves from call to implementation
- Cupkova et al. (2023): AI, accessibility, and data justice -- the project instantiates this
- Vermeersch et al. (2018): Disability experience as generative knowledge
- Vermeersch & Heylighen (2012): Carlos Pereira as individual precedent for transformative model
- Heylighen & Herssens (2014): "Designerly ways of not knowing" as the mechanism by which visual tools encode exclusion
- Lit review gap #5: Working prototype answering calls for change

**Why compelling at ACADIA:**
This framing is intellectually rigorous but risks being perceived as primarily social-justice framing rather than technical contribution. To succeed at ACADIA, it must lead with the technical architecture and let the disability justice argument emerge from the engineering decisions, not the other way around. The strength of this framing is that it gives the paper a clear evaluative framework: for each design decision, the paper can show that the accessibility requirement produced a general improvement. The risk is that ACADIA reviewers may be less familiar with disability studies terminology. The paper should define its terms carefully and keep the emphasis on software architecture, using disability studies as a lens rather than a lexicon.

---

## Paper Structure Proposals

### Structure A: Theory-Led (Best for Framing 1, 2, or 4)

**Title:** "Ocularcentrism All the Way Down: Designing Architectural Software Without Vision"

**Target length:** 4,000-6,000 words (typical ACADIA full paper) or ~600 words + 10 images (demo/poster format)

1. **Introduction** (600 words)
   - The ocularcentric stack: Pallasmaa's critique extended to software
   - The gap: no architectural design tool treats non-visual interaction as primary
   - The contribution: a CLI-first, screen-reader-native architectural design pipeline and its implications for architectural computing

2. **Background** (800 words)
   - Architecture's ocularcentrism: Pallasmaa, Heylighen & Herssens
   - Equity in computational design: Noel et al., Cupkova et al.
   - Text-based CAD: Celani & Vaz, Rietschel et al.
   - Accessible 3D modeling: Siu et al. (shapeCAD)
   - The gap: no CLI-first screen-reader-native CAD tool in the literature

3. **System Architecture** (1,200 words)
   - The three-file pattern: controller, CMA, viewer
   - The controller/viewer separation as epistemological commitment
   - The CMA: what an architectural model is when it must be non-visual
   - The crash-only viewer: Rhino as disposable renderer
   - CLI output protocol: designing for screen readers

4. **Case Study: School Jig** (1,200 words)
   - Daniel's workflow in the graduate studio
   - Parametric floor plan generation through CLI commands
   - Tactile output and physical-digital round-trip
   - Specific interactions: `set bay A rotation 30`, `show bays`, `swap A`
   - What Daniel knows about the design that sighted users do not (semantic access vs. visual access)

5. **Discussion** (800 words)
   - Blindness as method: constraint-driven innovation
   - Three improvements born from accessibility: crash resilience, semantic clarity, auditability
   - Implications for architectural computing: the viewport is not the model
   - Limitations and future work: sonification, MCP integration, evaluation with more users

6. **Conclusion** (400 words)

### Structure B: System-Led with Evaluation (Best for Framing 3 or 5)

**Title:** "Blindness as Method: What Non-Visual Design Reveals About Architectural Computation"

1. **Introduction** (500 words)
   - Three improvements that came from accessibility constraints
   - Thesis: designing for blindness produces better architectural software
   - The Radical Accessibility Project in one paragraph

2. **Related Work** (600 words)
   - Visual programming vs. text: Celani & Vaz, Grasshopper's accessibility gap
   - Accessible CAD: shapeCAD and its limitations
   - LLM-to-CAD: Rietschel et al., Kakadoo -- text interfaces without accessibility
   - The missing piece: CLI-first, screen-reader-native, architecturally specific

3. **System Design** (1,500 words)
   - Architecture overview: CLI + JSON CMA + Rhino watcher
   - Design decision 1: Crash-only viewer (accessibility requirement -> general improvement)
   - Design decision 2: Semantic-first state representation (accessibility requirement -> general improvement)
   - Design decision 3: Text-only output protocol (accessibility requirement -> general improvement)
   - Design decision 4: Physical-digital round-trip (accessibility requirement -> pedagogical improvement)
   - Each decision structured as: requirement -> solution -> general benefit

4. **Deployment: A Semester in the Studio** (1,000 words)
   - Daniel's use of the tools in "Paradise on the Prairie" studio
   - Specific design tasks and how they were accomplished non-visually
   - Observations from Daniel and sighted classmates
   - What worked, what is still missing

5. **Comparative Analysis** (800 words)
   - The same design task in Grasshopper vs. CLI: expressiveness, time, accessibility
   - The same design task in shapeCAD vs. project tools: architectural specificity, integration
   - What the CLI version reveals that the visual version does not

6. **Discussion and Future Work** (600 words)
   - Sonification as the next modality
   - MCP/LLM integration for conversational design
   - Scaling beyond one user: what the architecture supports

### Structure C: Pedagogy-Led (Best for Framing 6)

**Title:** "Closing the Loop: Non-Visual Design Workflows in the Architecture Studio"

1. **Introduction** (500 words)
   - A blind student in a graduate architecture studio: the challenge and the opportunity
   - The physical-digital round-trip as the core pedagogical innovation

2. **Context** (600 words)
   - Inclusive design pedagogy in architecture: what exists, what is missing
   - Computational design pedagogy: Akbar et al., Fricker et al., Sass
   - The gap: no account of a blind student participating fully in a computational design studio

3. **Tools and Workflows** (1,200 words)
   - The CLI-to-Rhino pipeline: how Daniel designs
   - PIAF swell paper: how Daniel reads architectural drawings
   - 3D printing: how Daniel evaluates spatial form
   - Pegboard + OpenCV: how Daniel inputs physical spatial ideas
   - Ray-Ban Meta + AI: how Daniel participates in pin-ups and desk crits

4. **A Studio Semester** (1,200 words)
   - Chronological account of Daniel's studio experience
   - Key moments: first successful parametric plan, first pin-up critique, first design revision based on tactile feedback
   - Daniel's perspective (co-authored or quoted)
   - John's perspective as instructor

5. **What We Learned** (800 words)
   - What the tools enabled
   - What the tools could not yet do
   - What Daniel's experience revealed about architectural pedagogy for all students
   - The "transformative" benefit: how designing for Daniel improved the studio for everyone

6. **Future Directions** (400 words)
   - Sonification, expanded tool set, multi-user studies, curriculum integration

---

## Visual/Figure Strategy

The following figure plan is designed for maximum impact at ACADIA, where the audience expects computational sophistication, high-quality architectural graphics, and clear system diagrams. Images should do argumentative work, not merely illustrate.

### Figure 1: Hero / Teaser Image
**Content:** Split-screen composition. Left half: Daniel's terminal showing CLI commands and responses (e.g., `set bay A rotation 30` / `OK: Bay A rotation set to 30.`). Right half: the Rhino viewport showing the resulting parametric floor plan with columns, corridors, hatch patterns. Center: the JSON state file, partially visible, bridging the two. Caption makes the argument: same design, two modalities, no visual dependency.

**Why it works at ACADIA:** Immediately communicates the technical architecture and the accessibility innovation in a single image. The ACADIA audience will recognize Rhino and be intrigued by the CLI alongside it.

### Figure 2: System Architecture Diagram
**Content:** Clean diagram showing the three-file pattern: Controller CLI (Python 3) -> state.json (CMA) -> Rhino Watcher (IronPython 2.7) -> Rhino viewport. Arrows show data flow direction (unidirectional). Callouts note: "Screen reader reads here," "Crash here loses nothing," "Sighted collaborator reads here." Extend diagram to show PIAF / 3D print outputs and pegboard input loop.

**Why it works at ACADIA:** ACADIA audiences expect and appreciate clear system diagrams. This one carries the paper's core argument: the unidirectional flow and the labeled access points make visible the controller/viewer separation.

### Figure 3: CLI Interaction Sequence
**Content:** Annotated terminal screenshot showing a complete design session: creating bays, setting dimensions, adding corridors, querying state with `show bays`. Annotations highlight the OK:/ERROR: protocol, the structured one-line-per-item output, and the undo capability.

**Why it works at ACADIA:** Demonstrates that the CLI is not primitive -- it is a carefully designed interface with conventions, feedback patterns, and query capabilities.

### Figure 4: The Canonical Model Artifact (JSON State File)
**Content:** Formatted JSON state file with annotations pointing to key features: schema versioning, semantic bay names, stable IDs, nested corridor objects, irregular spacing arrays. Side-by-side with the Rhino rendering of the same state, with visual correspondence lines mapping JSON fields to geometric features.

**Why it works at ACADIA:** Makes the theoretical argument tangible: the "model" is the JSON, the viewport is one projection. ACADIA audiences who work with data exchange and interoperability will appreciate the schema design.

### Figure 5: Rhino Viewport -- Full Floor Plan
**Content:** High-quality Rhino viewport screenshot of a complex parametric floor plan generated entirely through the CLI. Showing columns on the heavy lineweight layer, corridors on the medium layer, grid on the light layer, hatch patterns, braille labels. This should be a genuinely good architectural drawing -- not a toy example.

**Why it works at ACADIA:** Proves that the non-visual workflow produces professional-quality architectural output. The ACADIA audience needs to see that this is real architecture, not a simplified demo.

### Figure 6: PIAF Swell Paper Tactile Output
**Content:** Photograph of a PIAF swell paper print of the same floor plan shown in Figure 5. Daniel's hands exploring the raised-line drawing. Close-up of braille labels and hatch textures. Side-by-side with the digital version for comparison.

**Why it works at ACADIA:** The physical artifact is visually striking and immediately communicates the physical-digital round-trip. The image of hands reading architecture challenges the audience's assumptions about how architectural knowledge is accessed.

### Figure 7: Pegboard Input System
**Content:** Overhead photograph of the pegboard with wire constructions. Inset: the OpenCV detection output showing detected wire positions. Arrow to the resulting Rhino geometry. Audio feedback waveform or textual description shown alongside.

**Why it works at ACADIA:** Demonstrates the input direction of the physical-digital round-trip. The pegboard is visually compelling and physically tangible in a way that ACADIA's fabrication-oriented audience will appreciate.

### Figure 8: Before/After -- Grasshopper Canvas vs. CLI Session
**Content:** Top: a Grasshopper definition producing a parametric grid (visually complex, screen-reader-opaque). Bottom: the equivalent CLI commands producing the same geometric result (textually clear, screen-reader-compatible). Same output geometry shown for both.

**Why it works at ACADIA:** This is the paper's most provocative figure. It forces the audience to compare the two interfaces and confront the question: which one contains more architectural information? Which one is accessible? The ACADIA audience, many of whom are Grasshopper users, will engage with this comparison.

### Figure 9: Daniel in the Studio
**Content:** Photograph of Daniel working in the "Paradise on the Prairie" graduate studio. Terminal open, braille display visible, PIAF drawings and 3D prints on the desk. Sighted classmates' work visible in the background for context. This is not a clinical lab photo -- it is a studio environment.

**Why it works at ACADIA:** Contextualizes the project in architectural education. ACADIA reviewers who teach in studios will recognize the environment and understand that this is not a HCI lab experiment but a real studio practice.

### Figure 10: Evaluation / Comparison Table
**Content:** Structured comparison of the project's approach vs. shapeCAD (Siu et al., 2019), Kakadoo (Atakan et al., 2025), and standard Rhino/Grasshopper across dimensions: screen reader compatibility, crash resilience, semantic queryability, architectural specificity, industry tool integration, physical-digital round-trip. The project's approach should show clear advantages in most dimensions while acknowledging limitations.

**Why it works at ACADIA:** Provides the evaluative evidence that reviewers will look for. Positions the project within the landscape of prior work and makes explicit what is novel.

---

## Key Claims / Contributions

The paper can credibly make the following novel contributions, each grounded in the project's specific technical and pedagogical work:

### Primary Contributions

- **First CLI-first, screen-reader-native architectural design tool.** No prior system in the CumInCAD database or the broader HCI/accessibility literature describes a command-line interface specifically designed for a blind architecture student to author parametric architectural designs. shapeCAD (Siu et al., 2019) uses OpenSCAD but targets object-scale modeling, not architectural design, and does not integrate with industry-standard CAD.

- **The Canonical Model Artifact (CMA) pattern as accessibility architecture.** The separation of a human-readable, schema-versioned JSON state file from the rendering viewer is not just a software engineering decision; it is an accessibility innovation that decouples the accessible interface from the inaccessible one. This pattern is generalizable to any domain where a visual application needs to be driven by a non-visual controller.

- **The controller/viewer separation as a theory of architectural representation.** The claim that the structured semantic description (CMA) is more fundamental than the geometric rendering (Rhino viewport) is a contribution to architectural computing theory. It extends Pallasmaa's critique of ocularcentrism from buildings to the tools used to design them.

- **Evidence that accessibility constraints produce general improvements.** Three specific cases: crash resilience (atomic writes + crash-only viewer), semantic clarity (structured text output), and design auditability (diffable state files). Each originated from a blind user's requirements and benefits all users.

### Secondary Contributions

- **A complete physical-digital round-trip for inclusive architectural pedagogy.** CLI to PIAF to 3D print to pegboard to Rhino -- a bidirectional loop where the blind student is author, not just recipient.

- **CLI output protocol for screen-reader-compatible CAD feedback.** The OK:/ERROR: prefix convention, one-item-per-line formatting, and no-visual-dependency rule constitute a design pattern for accessible CLI tools in computational design.

- **A working deployment in a graduate architecture studio.** Not a lab prototype or a user study with volunteers, but a tool used daily by a blind graduate student in a real design studio over a full semester.

- **A critique of visual programming (Grasshopper/Dynamo) as exclusionary.** The comparison of a Grasshopper definition with the equivalent CLI session demonstrates that visual programming's "democratization" excludes a population that text-based interfaces include.

---

## Risks and Counterarguments

### Risk 1: "This is a single-user case study -- how generalizable is it?"

**The pushback:** Reviewers may argue that a tool designed for one user (Daniel) cannot claim to be generalizable. n=1 is a legitimate methodological concern.

**Preemption strategy:**
- Frame Daniel's role as co-designer, not just subject. This is participatory design, not a clinical trial. The n=1 is a feature, not a bug: the project builds tools *with* a blind architecture student, not *for* an abstract blind population.
- Cite Vermeersch and Heylighen's (2012) Carlos Pereira case study, which ACADIA accepts as a valid contribution with n=1.
- Emphasize that the architectural claims (CMA pattern, controller/viewer split, crash resilience) are about the software architecture, not about the user. These patterns generalize regardless of the user population.
- Acknowledge the limitation explicitly and describe plans for broader evaluation.

### Risk 2: "This is accessibility/HCI work, not architecture"

**The pushback:** ACADIA reviewers might see this as better suited for CHI or ASSETS, not an architectural computing venue.

**Preemption strategy:**
- This is the most important risk to mitigate. The paper must make architectural arguments, not just accessibility arguments.
- Lead with the contribution to architectural computing: the CMA pattern, the controller/viewer separation, the critique of the ocularcentric stack. These are architectural computing contributions that happen to arise from accessibility work.
- Show that the tool produces real architectural output: floor plans with structural bays, corridors, columns, hatch patterns. This is architecture, not widget manipulation.
- Cite ACADIA's own engagement with accessibility: Cupkova et al. (2023), Karastathi et al. (2024 Vanguard Award), Noel et al. (2021).
- Use the most architecturally specific framing (1, 2, or 4) rather than the most accessibility-specific framing (7).

### Risk 3: "The CLI approach does not scale to complex design tasks"

**The pushback:** Floor plan generation is relatively constrained. Can this approach handle freeform 3D modeling, complex parametric surfaces, or BIM-level coordination?

**Preemption strategy:**
- Acknowledge this honestly. The current tool (School Jig) demonstrates the pattern for 2D parametric plan generation. Freeform 3D modeling is a harder problem.
- Argue that the CMA pattern is extensible: the JSON state file can describe any structured design intent, and the watcher pattern can produce any geometry. The limitation is the CLI's command vocabulary, which can be expanded.
- Point to the planned MCP integration as the path to conversational interaction with more complex models ("describe the north elevation," "make the roof more curved").
- Point to Rietschel et al. (2024) as evidence that LLM-mediated text-to-geometry is viable for complex tasks.
- Do not overclaim. The paper should present what works today and articulate a research agenda for what comes next.

### Risk 4: "The comparison with Grasshopper is unfair"

**The pushback:** Grasshopper does things the CLI cannot (visual debugging of complex parametric logic, interactive parameter sweeps, real-time visual feedback). Comparing them is apples-to-oranges.

**Preemption strategy:**
- Agree that Grasshopper has capabilities the CLI does not. The argument is not that the CLI is better than Grasshopper for sighted users. The argument is that Grasshopper's visual-only interface is a design choice that excludes blind users, and that for the class of tasks the CLI handles, the textual approach achieves equivalent results with broader access.
- Frame the comparison as asking what the visual interface adds vs. what it costs. What it adds: spatial layout of logic, real-time visual preview. What it costs: complete inaccessibility to screen readers, opaque definitions that even sighted users struggle to read, no built-in audit trail. The comparison is not "CLI is better" but "both have tradeoffs, and the visual interface's tradeoffs are hidden because they are normalized."

### Risk 5: "The theoretical framing is overblown for the technical contribution"

**The pushback:** The paper invokes Pallasmaa, disability studies, and architectural epistemology, but the actual tool is a Python CLI that generates floor plans.

**Preemption strategy:**
- This is a real tension. The paper must balance theoretical ambition with technical modesty.
- Be precise about what the tool does and does not do. Show the system clearly, acknowledge its current scope, and let the theory emerge from the specific technical decisions rather than being imposed on top.
- The strongest framings (3, 5) lead with technical specifics and derive theoretical implications. The riskiest framing (7) leads with theory and may feel top-heavy.
- Include enough technical detail (code patterns, JSON schema examples, CLI session transcripts) that reviewers can evaluate the system on its own merits, independent of the theoretical frame.

### Risk 6: "Where is Daniel's voice?"

**The pushback:** A paper about tools co-designed with a blind student should include that student's perspective, not just the PI's framing.

**Preemption strategy:**
- Include Daniel as a co-author.
- Include direct quotes from Daniel about his experience using the tools.
- If possible, include a section written or dictated by Daniel himself.
- Describe specific moments in the studio where Daniel's feedback changed the tool design.
- This is both a methodological strength and an ethical obligation. The paper should model the inclusive co-design it advocates.

---

## Recommended Next Steps

1. **Choose a framing.** Framing 1 (Ocularcentric Stack) and Framing 3 (Blindness as Method) are the strongest candidates. Framing 1 is more theoretically ambitious; Framing 3 is more defensible on technical merit. A hybrid that uses the theoretical frame of 1 with the evidence structure of 3 may be optimal.

2. **Confirm ACADIA 2026 submission format and deadline.** The framings above can support either a full paper (4,000-6,000 words) or a shorter format (poster, demo). The full paper format is recommended for the depth of argument.

3. **Gather studio documentation.** Photographs of Daniel working, CLI session logs, PIAF output samples, pegboard demonstrations. This material is both evidence and figure content.

4. **Draft the Grasshopper comparison.** Implement the same parametric floor plan task in Grasshopper and document it side-by-side with the CLI session. This is the paper's most compelling piece of visual evidence.

5. **Consult Daniel.** Share the framings, get his reaction, identify which resonates with his experience, and plan for co-authorship or co-authoring of specific sections.

6. **Check ACADIA 2026 theme.** ACADIA's annual theme strongly influences what reviewers value. If the theme aligns with any of these framings (especially equity, AI, or pedagogy), prioritize that alignment.
