# Radical Accessible Pedagogy: What a Blind Architecture Student Reveals About the Future of Computational Design Education

**John Clark**, University of Illinois Urbana-Champaign
**[Collaborator Name]**, [Institution]

---

## Abstract

This paper introduces Radical Accessible Pedagogy — a pedagogical framework in which architectural design tools are designed for blindness first, producing a learning environment that is not merely inclusive but embodies pedagogical principles the discipline has long advocated yet never operationalized. We present a complete tool ecosystem developed for Daniel, a blind graduate student in the architecture program at UIUC: a CLI-driven parametric floor plan generator, a JSON-based canonical model artifact, a Rhino file-watching viewer, an automated tactile output pipeline, and an AI-assisted description system. Each tool was built using Claude Code, an AI-assisted development environment, which collapsed the implementation effort from a multi-year lab project to a system deployed in a live graduate studio within a single academic year. The paper makes three claims. First, designing for blindness as the primary case produces tools whose properties — semantic-first interaction, explicit verbal feedback, crash-resilient architecture, and version-controlled process — constitute better pedagogy for all students. Second, AI-assisted development (not AI-assisted design) is the critical enabler: the AI built the tools; the student designs the architecture. Third, the resulting tool ecosystem demonstrates that the field's convergence on text-to-geometry pipelines has overlooked a fundamental problem — non-visual verification — that accessibility-first design solves. We document Daniel's workflow in a graduate studio, present the tool architecture and its pedagogical rationale, and argue that Radical Accessible Pedagogy offers computational design education a model it did not know it needed.

**Keywords:** accessible design tools, blind architecture student, CLI-driven CAD, computational design pedagogy, AI-assisted development, screen reader, tactile fabrication

---

## 1. Introduction

ACADIA 2026 arrives at a moment when AI-assisted architectural design has become routine. Text-to-geometry pipelines translate natural language into parametric models (El Hizmi et al. 2024; Khan et al. 2024). LLM-powered plugins generate and modify Grasshopper definitions from conversational prompts (Rietschel et al. 2024; Ant 2026). Voice-driven interfaces enable speech-to-geometry workflows (Atakan et al. 2025). The question is no longer whether AI can participate in design but who AI-assisted design includes and what it makes possible that was previously impossible.

This paper does not present another AI-to-geometry system. It presents a pedagogy — Radical Accessible Pedagogy — in which architectural design tools are designed for a blind user as the primary case, and the resulting tool ecosystem embodies pedagogical principles that benefit all students. The AI contribution is distinctive: we used Claude Code, an AI-assisted development environment, not to generate architecture but to build the accessible infrastructure that enables a blind graduate student to author parametric floor plans in a live studio setting. The AI is in the tool-building loop, not the design loop.

Daniel is a blind graduate student in the architecture program at the University of Illinois Urbana-Champaign. He cannot see Rhino's viewport, cannot manipulate Grasshopper's visual canvas, and cannot click through Revit's interface. Standard computational design tools assume a sighted operator at every layer of their architecture — from mouse-driven input to viewport-based feedback to screen-dependent verification. These tools do not merely lack accessibility features; they structurally encode an epistemology in which spatial knowledge is visual knowledge (Pallasmaa 2005; Heylighen and Herssens 2014). When a tool can only be operated by looking at it, it does not merely exclude blind users — it enforces a particular model of design cognition.

The Radical Accessibility Project responds not by retrofitting accessibility onto existing tools but by building a fundamentally different tool ecosystem where blindness is the design case, not the edge case. The result is a CLI-driven pipeline — controller, JSON state file, Rhino viewer, tactile output, AI description — that a blind student operates through a screen reader and braille display. And the properties this pipeline required for accessibility turn out to articulate pedagogical principles the field has advocated but never implemented: semantic-first reasoning (Piaget and Inhelder 1956; Millar 1994), explicit reflective dialogue (Schon 1983), version-controlled design process, and embodied physical-digital fluency (Sass 2024).

We make three contributions. First, we define Radical Accessible Pedagogy and demonstrate its six principles through a working tool ecosystem deployed in a graduate studio. Second, we document the role of AI-assisted development in enabling a lone researcher to build accessible design infrastructure at the speed the field needs. Third, we identify the non-visual verification gap in the text-to-geometry literature and show how accessibility-first design solves it.

## 2. Background

### 2.1 The Ocularcentric Stack

Architecture's dependence on vision has been critiqued at the level of the built environment (Pallasmaa 2005; Jay 1993; Zumthor 2006) and at the level of design cognition (Heylighen and Herssens 2014). But this critique has rarely descended into the tools. Rhino, Grasshopper, and Revit are not neutral instruments that happen to be visual. They are artifacts with politics (Winner 1980) — instruments that make visuality a prerequisite for architectural thought. The computational design community has called for equity and access (Noel et al. 2021; Cupkova et al. 2023) but has not interrogated the visual assumptions embedded in its own tool stack.

Gissen (2018) identified three structural barriers excluding disabled people from architecture: inaccessible facilities, a curriculum that romanticizes physical intensity, and inaccessible construction sites. We identify a fourth: inaccessible design software. Crawford et al. (2024) documented a co-design session in which a blind participant's screen reader could not interpret TinkerCAD. Billah et al. (2023) found that inaccessible digital tools prevent blind people from leading the design of tactile media they consume. The exclusion is structural, not incidental.

### 2.2 Text-to-Geometry and the Verification Gap

Between 2022 and 2026, text-based interfaces to CAD became mainstream. Rietschel, Guo, and Steinfeld (2024) built an LLM-to-JSON-to-Grasshopper pipeline. El Hizmi et al. (2024) developed LLMto3D, a multi-agent system translating natural language to parametric objects. Jones et al. (2025) designed AIDL, a domain-specific language for LLM-driven CAD that eliminates the need for visual verification by the code-generating AI. Khan et al. (2024) demonstrated Text2CAD, the first end-to-end transformer generating parametric models from language. Atakan et al. (2025) built Kakadoo, a voice-driven Grasshopper plugin.

Every one of these systems shares an assumption: the user verifies output visually. The human types a prompt, the system generates geometry, and the human looks at the viewport to confirm the result matches the intent. What happens when the user cannot look? The verification problem — confirming that the system produced what you intended without visual inspection — is unsolved in every text-to-geometry pipeline because it was never the problem they set out to solve. Our project solved it first, because it had to.

### 2.3 Accessible 3D Modeling

The HCI and accessibility communities have built tools for blind users to create 3D content. Siu et al. (2019) developed shapeCAD, combining OpenSCAD with a 2.5D shape display. Siu et al. (2025) extended this with A11yShape, adding GPT-4o for AI-assisted modeling with a four-facet representation. Both target general 3D modeling rather than architectural design, and both wrap an existing programming language (OpenSCAD) rather than building a domain-specific, screen-reader-native interface.

Clepper et al. (2025) documented blind tactile graphics creators trapped between accessible low-fidelity tools and inaccessible high-fidelity ones. Flores-Saviaga et al. (2025) found that AI coding assistants exacerbate accessibility barriers through suggestion overload. Gurita and Vatavu (2025) showed that LLM-generated interfaces do not spontaneously produce accessible code. The message is consistent: accessibility cannot be bolted on. It must be structural.

Seo et al. (2024) coined the term "born-accessible" for educational environments designed from the ground up for blind learners. Our project extends this concept from pedagogy to tools: born-accessible CAD is architectural software designed for a blind user from line one, not retrofitted with screen reader support after the fact.

### 2.4 Blind Spatial Cognition

A substantial body of cognitive science demonstrates that spatial reasoning does not require vision. Millar (1994, 2008) showed that spatial cognition is modality-independent when adequate reference frames are provided. Loomis, Klatzky, and Golledge (2001) found that spatial representations derived from spatial language function equivalently to those derived from direct perception. Thinus-Blanc and Gaunet (1997) demonstrated that discrepancies in blind spatial cognition research stem from strategy differences — what reference frames and tools are available — rather than fundamental cognitive limitations. Giudice (2018) confirmed that blind spatial cognition is sequential, landmark-based, and language-mediated.

These findings provide the cognitive foundation for our tool architecture. The CLI's sequential command structure, named spatial entities, and verbal feedback are not compromises imposed by a blind user's limitations. They are aligned with how spatial cognition actually works without vision — and they enforce a semantic rigor that visual tools allow students to bypass.

## 3. Radical Accessible Pedagogy

We define Radical Accessible Pedagogy as a pedagogical approach in which the primary design case is non-visual, the student is a co-designer of the tools, and the resulting tool architecture embodies pedagogical principles that benefit all learners. It rests on six principles, each derived from what Daniel needs to participate as a full author in graduate studio.

### 3.1 Semantic-First Spatial Reasoning

Daniel works with named bays, corridors, and spatial relationships before any geometry is rendered. He types `set bay A bays 6 3` to establish a six-by-three column grid, `corridor A on` to activate a circulation spine, `set bay A rotation 30` to orient the bay. Each command names what is being changed and specifies the change in architectural terms. The geometry follows the semantics.

This is how spatial cognition develops. Piaget and Inhelder (1956) demonstrated that spatial understanding moves from topological (qualitative relationships) to metric (precise coordinates). Millar (1994) showed that blind spatial reasoning achieves equivalent performance to sighted reasoning when semantic reference frames are available. The CLI enforces the semantic step that visual CAD allows students to skip — the step where the designer articulates, in language, what the spatial relationships are before pushing geometry around on screen.

### 3.2 Explicit, Auditable Design Dialogue

Every command Daniel issues receives a verbal response: `OK: Bay A rotation set to 30 degrees. READY:` or `ERROR: Gridline index 7 out of range for bay A (max 6).` The design process is a literal conversation — typed command in, spoken confirmation out through the screen reader.

Schon (1983) defined design as a reflective conversation with the situation, where each action reveals new qualities and suggests new moves. In visual CAD, the situation "talks back" through silent viewport changes that the designer must notice. In the CLI, the talk-back is explicit. The design dialogue becomes a transcript: auditable, diffable, and repeatable. A student can review the sequence of commands that produced a design state, revert to any prior state via the undo stack, and compare two design states through a text diff of the JSON files. This is Schon's reflective practitioner made operational through a screen-reader-native protocol.

### 3.3 Recoverable, Version-Controlled Process

Daniel's work lives in a JSON state file, not in Rhino's memory. Every mutation triggers an atomic write: write to a temporary file, flush to disk, then replace the original. If the process is interrupted at any point, the previous state remains intact. The JSON file is the Canonical Model Artifact (CMA) — the authoritative representation of the design. Rhino is a disposable viewer. If Rhino crashes, nothing is lost. Restart Rhino, run the watcher script, and every element rebuilds from the CMA.

This was built because a blind user cannot visually confirm crash recovery. But it is the process infrastructure every design studio should have. When every state is a file on disk, students can version-control their design process with Git, branch to explore alternatives, revert failed experiments, and submit a complete design history alongside a final product. Architecture studios have never had the equivalent of software engineering's version control. The CMA makes it possible.

### 3.4 Physical-Digital Fluency

Daniel authors a design through the CLI, then exports it to PIAF swell paper — a raised-line tactile drawing produced at 300 DPI with columns, walls, corridors, room hatches, and Braille labels. He explores the physical output with his hands, identifies spatial relationships, and feeds observations back through CLI commands. In the other direction, he constructs spatial configurations on a pegboard using wire, and an overhead camera digitizes the wire positions into the model.

This bidirectional flow — digital to tactile, tactile to digital — is not accommodation. It is the embodied design loop that fabrication-centered pedagogy advocates (Sass 2024). The physical artifact is not a representation of the design; it is a medium through which the student thinks about the design. Sennett (2008) described the craftsman's intelligence as a dialogue between hand and head. Daniel's hands on the tactile drawing are his primary cognitive interface with the spatial organization of his floor plan.

### 3.5 Mixed-Ability Collaboration

The separation between the CMA (the model) and Rhino (one possible viewer) enables a form of collaboration that conventional tools cannot support. Daniel works in the CLI. A sighted classmate observes the same design in the Rhino viewport. Both are accessing the same authoritative model through different modalities. Neither modality is primary. The JSON file is the shared artifact; the CLI and the viewport are alternative interfaces to it.

This architectural decision — controller/viewer separation via a shared state file — was born from accessibility necessity. But it solves a problem the field has not recognized: how to enable genuine mixed-ability teamwork in a design studio where students work with different tools and different senses. Potluri et al. (2022) addressed analogous mixed-ability collaboration in software development with CodeWalk. Our tool ecosystem applies the same principle to architectural design.

### 3.6 Student as Co-Designer

Daniel does not receive tools passively. His feedback reshapes the CLI weekly. When he reported that corridor commands required too many steps, the command structure was simplified. When he needed to understand room areas before making partition decisions, a cell-listing command was added. When he found that verbose output overwhelmed his screen reader, the response protocol was tightened to single-line summaries with an option for detail.

This is constructionism (Papert 1980) applied to accessibility: the student constructs the instrument of his own architectural education. The tools evolve from Daniel's experience, not from assumptions about his experience. Charlton's (1998) principle — "nothing about us without us" — is enacted not as consultation but as co-design. Daniel is not a test subject recruited for evaluation. He is a collaborator who shapes tool requirements, identifies spatial relationships sighted developers miss, and uses the tools in the same graduate studio as his sighted classmates.

## 4. The Tool Ecosystem

The six pedagogical principles are realized through seven interconnected tools. Each tool exists because Daniel identified a need; each embodies a pedagogical commitment that extends beyond his individual use.

### 4.1 Layout Jig CLI

The command-line controller is a Python 3 application with zero external dependencies. It operates through a command dispatch architecture: the user types a command (`set bay A rotation 30`), the dispatcher routes it to the appropriate handler function, the handler mutates the in-memory state, the state is persisted to the CMA via atomic write, and a confirmation message is printed (`OK: Bay A rotation set to 30.0 degrees.`).

The command vocabulary is architectural, not geometric. Students work with bays, corridors, walls, apertures, and rooms — named entities with semantic meaning — rather than points, lines, and surfaces. This vocabulary is the CLI's pedagogical contribution: it forces students to think in terms of spatial organization before engaging with geometric form.

The output protocol is screen-reader-native by design. Every response begins with `OK:` or `ERROR:`. Each response is a single line. No tables, no multi-column layouts, no decorative formatting. After every command, `READY:` is printed so the screen reader detects the state change. This protocol was designed for Daniel's NVDA screen reader, but it is also more machine-parseable, more scriptable, and more debuggable than the status messages of any conventional CAD tool.

### 4.2 Canonical Model Artifact

The CMA is a JSON file containing every parameter of the design: site dimensions, bay configurations (grid type, dimensions, spacing, origin, rotation), wall properties, corridor settings, apertures (doors, windows, portals with position, size, hinge, and swing), room names and hatches, style settings, and metadata. It is human-readable with two-space indentation, schema-versioned for forward compatibility, and designed for diffability — changing a bay's rotation from 30 to 45 degrees produces a one-line diff.

The CMA embodies a claim about architectural representation: the design model is the structured semantic description, not any particular geometric rendering. Evans (1997) proved that drawings are active agents shaping what can be designed. The CMA is a different kind of drawing — a textual one, readable by screen readers and braille displays, queryable through CLI commands, versionable through Git. It generates different architectural possibilities than a viewport-based representation, not fewer.

### 4.3 Rhino Watcher

An IronPython 2.7 script hooks into Rhino's idle event and polls the CMA for changes by checking file modification time. When a change is detected, the watcher performs a full rebuild: it deletes all existing jig geometry (identified by JIG_OWNER metadata tags), reads the current CMA, and regenerates columns, walls, corridors, apertures, hatches, labels, and section cuts on dedicated Rhino layers.

The watcher is read-only with respect to the CMA. It never writes to the state file. This one-directional data flow — CLI writes CMA, watcher reads CMA, Rhino displays geometry — is the architectural decision that makes the system crash-proof. If Rhino hangs, the user kills the process. The CMA on disk is untouched. Restart Rhino, load the watcher, and every element rebuilds identically. Same inputs, same state file, same geometry.

### 4.4 Tactile Output Pipeline

The rendering engine reads the CMA directly — no Rhino required — and produces 300 DPI black-and-white images suitable for PIAF swell paper printing. It draws column grids as filled circles, walls as thick polylines, corridors as dashed centerlines, apertures as standard architectural symbols (arc swings for doors, break lines for windows), room hatches as pattern fills, and labels in both English text and Grade 1 Braille.

The pipeline includes a density checker that measures black pixel percentage and warns when density exceeds 40% — the threshold above which swell paper produces excessive swelling and loss of tactile detail. Multiple presets support different source types (floor plans, photographs, sketches) for converting external images to tactile format.

### 4.5 Pegboard and Computer Vision

A physical pegboard provides Daniel with a tangible medium for spatial exploration. He places pegs and stretches wire between them to construct walls, corridors, and spatial boundaries. An overhead camera captures the configuration, and an OpenCV pipeline extracts wire positions as line segments. Audio feedback confirms what was captured: "Three walls detected. Longest wall: 24 feet along the north edge."

This closes the physical-digital loop. The tactile output pipeline translates digital to physical; the pegboard translates physical to digital. Daniel can sketch with his hands — the most intuitive spatial medium available to him — and have the sketch enter the computational model.

### 4.6 MCP Server

A Model Context Protocol server wraps the CLI controller with 21 structured tools, 3 resources, and 2 prompt templates. It enables AI agents — including Claude — to read, query, and modify the design model through typed function calls rather than raw text commands. The server is the bridge between the accessibility pipeline and the emerging ecosystem of AI-assisted design tools.

Through the MCP server, Daniel can engage in conversational design exploration: "Describe the circulation path from the entrance to room C3." "What is the total area of corridor space?" "Compare the current state to the snapshot I saved before rotating bay B." The AI becomes a design interlocutor — not generating form, but helping the student reason about spatial relationships through language.

### 4.7 AI Description Pipeline

For studio activities that remain irreducibly visual — pin-up critiques, site visits, precedent analysis — an AI description pipeline translates visual information into screen-reader-parseable text. Ray-Ban Meta glasses provide real-time scene narration during physical site visits. The Claude API generates architectural descriptions of Rhino viewport screenshots at multiple levels of detail, following Lundgard and Satyanarayan's (2022) four-level model: what elements exist (L1), their dimensions and quantities (L2), spatial relationships and patterns (L3), and design implications (L4).

The AI describes; it does not design. This distinction is the ethical boundary the project maintains. Daniel's authorship must remain his own. The AI expands what he can perceive, not what he decides.

## 5. AI-Assisted Development: The Enabler

The entire tool ecosystem — CLI controller, CMA schema, Rhino watcher, tactile renderer, MCP server, computer vision pipeline, and AI description system — was built by a single faculty member using Claude Code as the primary development environment. This is the paper's distinctive AI claim, and it requires careful framing.

We are not arguing that AI generated the architecture Daniel designs. We are arguing that AI-assisted development enabled one researcher to build the accessible design infrastructure that the field has called for (Noel et al. 2021; Cupkova et al. 2023) but that no one has had the resources to construct. The pipeline that lets Daniel design in studio exists because Claude Code collapses the development effort from what would traditionally require a multi-year funded research lab to something one person can build and maintain iteratively, responding to a student's needs week by week.

Claude Code operates within hard constraints defined by the project's CLAUDE.md file: Python stdlib only, no pip dependencies, IronPython 2.7 compatibility for the Rhino watcher (no f-strings, no pathlib), screen-reader-friendly output (OK:/ERROR: prefixes, no tables, no progress spinners), and atomic file writes for crash safety. These constraints are non-negotiable accessibility requirements. Claude Code respects them across every code generation task, maintaining consistency that would be difficult for a human developer switching between multiple codebases and two Python runtimes.

The development velocity is the critical factor. Daniel identifies a need on Monday — "I need to know which cells overlap the corridor before I name the rooms." By Wednesday, the `auto_corridor_cells` command exists, tested, documented, and deployed. Traditional academic software development cannot achieve this responsiveness. AI-assisted development can, and the result is tools that evolve in real time from a disabled student's lived experience rather than from a researcher's assumptions about that experience.

This is a different kind of AI contribution than the text-to-geometry papers filling the ACADIA pipeline. Those papers use AI in the design loop — generating geometry, suggesting forms, optimizing parameters. Our paper uses AI in the tool-building loop — constructing the infrastructure that makes design accessible to someone the field has excluded. The distinction matters because it positions AI not as a replacement for design agency but as an amplifier of inclusion.

## 6. Discussion

### 6.1 The Curb Cut Effect

The tools were designed for Daniel. They turn out to be better for everyone. The CLI's semantic command vocabulary forces students to articulate spatial relationships before manipulating geometry — a pedagogical discipline that visual CAD lacks. The CMA's text-based, diffable representation enables version-controlled design processes that no conventional CAD workflow supports. The crash-only viewer architecture eliminates the data loss that plagues every Rhino user. The OK:/ERROR: output protocol is more machine-parseable than any CAD tool's status messages, enabling automated testing and scripting.

Pullin (2009) documented this pattern: designing for disability drives innovation that benefits everyone. The CLI-to-JSON-to-Rhino pipeline was designed because a blind user cannot interact with Grasshopper's visual canvas. The fact that the same pipeline is more auditable, more scriptable, more crash-resilient, and more version-control-friendly than conventional workflows is the curb cut effect applied to computational design tools.

### 6.2 The Verification Gap

The text-to-geometry literature assumes visual verification. When Rietschel et al. (2024) translate a text prompt into Grasshopper geometry, the user looks at the result. When El Hizmi et al. (2024) generate parametric objects from language, the user inspects the viewport. Jones et al. (2025) designed AIDL specifically for "blind" AI code generation — eliminating visual verification for the AI — but never considered blind human users.

Our project solved the verification problem through structured textual feedback: the OK:/ERROR: protocol confirms every operation, the `describe` command generates multi-level spatial narratives, and the `audit` command validates the model against dimensional, accessibility, and structural rules. This verification architecture is not merely an accessibility accommodation. As AI generates increasing volumes of geometry, no human — sighted or not — can visually verify every element. The structured, queryable, machine-parseable verification system we built for Daniel is the verification system that text-to-geometry pipelines will eventually need for everyone.

### 6.3 Introducing Disability Studies to ACADIA

Winner (1980) asked whether artifacts have politics. Applied to CAD: Rhino's viewport, Grasshopper's visual canvas, and Revit's click-and-drag interface enforce a social arrangement in which sighted people design and blind people are excluded. Hamraie (2017) identified the "normate template" — the assumed user around whom tools are designed. In computational design, the normate template is a sighted, mouse-using, screen-watching architect.

The Radical Accessibility Project replaces this template. Daniel is not a user of accommodations. He is, in the language of Hamraie and Fritsch (2019), a crip technoscientist — a disabled person who is a knower and maker, not merely a consumer. His disability experience generates architectural knowledge that sighted tool designers cannot access: the insight that the model is not the viewport, that semantic structure is more fundamental than geometric projection, that verbal feedback is more rigorous than visual ambient change.

Gissen (2022) argued that disability in architecture must go beyond access. We agree. The project does not make Rhino "accessible." It builds a fundamentally different tool ecosystem in which blindness is the primary design condition — and discovers that the resulting architecture is, in specific technical dimensions, superior to the visual-first alternative it replaces.

### 6.4 Limitations and Future Work

The system has been deployed with one student. The pedagogical claims require evaluation with a broader population — both blind students and sighted students using the CLI as an alternative or supplement to visual CAD. We plan controlled comparisons in which sighted students complete design tasks in both Grasshopper and the CLI to test the claim that semantic-first interaction produces different (and in measurable ways, richer) spatial reasoning.

The sonification pipeline remains unrealized. Blesser and Salter (2007) define aural architecture and map spatial properties to sound parameters. A real-time sonification layer — where changing a corridor width produces an audible change in perceived spatial enclosure — would add a modality the current system lacks.

The AI description pipeline is necessary but imperfect. Scene descriptions from Ray-Ban Meta glasses and the Claude API vary in quality and architectural specificity. Stangl et al. (2021) demonstrated that blind users need different descriptions for different contexts. The pipeline does not yet adapt its description strategy to the task at hand (design review vs. wayfinding vs. critique evaluation).

The pegboard-to-digital pipeline is a prototype. The computer vision system detects wire positions but does not yet reliably distinguish between wall, corridor, and boundary elements. Robust classification would require either visual markers (colored wire) or a constrained physical grammar (specific wire gauges for specific elements).

## 7. Conclusion

Radical Accessible Pedagogy is not a concession to disability. It is a pedagogical framework that produces tools with properties the discipline needs: semantic-first interaction that enforces spatial reasoning before form-making, explicit verbal dialogue that makes the design conversation auditable, crash-proof architecture that treats process as a first-class artifact, and physical-digital fluency that embodies the making-as-thinking ethos fabrication pedagogy advocates.

The tools exist because Daniel needed them. They were built at the speed of a graduate studio because Claude Code collapsed the development effort. They work because the cognitive science of blind spatial reasoning (Millar 1994; Loomis et al. 2001; Giudice 2018) validates what the tool architecture assumes: that spatial knowledge can be constructed through language, touch, and structured feedback as effectively as through vision.

The field is converging on text-to-geometry as the future of design interaction. We arrived at the same architecture by a different route — not convenience, but necessity. The fact that accessibility-first design produced the verification system, the process infrastructure, and the semantic rigor that the field's text-to-geometry pipelines will eventually need is not a coincidence. It is the curb cut effect, and it is the strongest argument we can make: design for exclusion, and you discover better patterns for everyone.

---

## References

Atakan, A.O. et al. 2025. "Kakadoo: LLM Enabled Speech Interface for Enhanced Human-Computer Interaction." In *Proceedings of the 43rd eCAADe Conference*, Ankara.

Billah, S.M. et al. 2023. "Designing While Blind: Nonvisual Tools and Inclusive Workflows for Tactile Graphic Creation." In *Proceedings of ASSETS '23*. ACM.

Blesser, B. and L.-R. Salter. 2007. *Spaces Speak, Are You Listening? Experiencing Aural Architecture.* Cambridge, MA: MIT Press.

Carpo, M. 2011. *The Alphabet and the Algorithm.* Cambridge, MA: MIT Press.

Charlton, J.I. 1998. *Nothing About Us Without Us: Disability Oppression and Empowerment.* Berkeley: University of California Press.

Clepper, G. et al. 2025. "'What Would I Want to Make? Probably Everything': Practices and Speculations of Blind and Low Vision Tactile Graphics Creators." In *Proceedings of CHI 2025*. ACM.

Crawford, S. et al. 2024. "Co-designing a 3D-Printed Tactile Campus Map with Blind and Low-Vision University Students." In *Proceedings of ASSETS '24*. ACM.

Cupkova, D. et al. 2023. "AI, Architecture, Accessibility, and Data Justice." *International Journal of Architectural Computing* 21(2).

El Hizmi, B. et al. 2024. "LLMto3D: Generating Parametric Objects from Text Prompts." In *Proceedings of ACADIA 2024*, Vol. 1, 157-166.

Evans, R. 1997. *Translations from Drawing to Building and Other Essays.* Cambridge, MA: MIT Press.

Flores-Saviaga, C. et al. 2025. "The Impact of Generative AI Coding Assistants on Developers Who Are Visually Impaired." In *Proceedings of CHI 2025*. ACM.

Giudice, N.A. 2018. "Navigating without Vision: Principles of Blind Spatial Cognition." In *Handbook of Behavioral and Cognitive Geography*. Edward Elgar.

Gissen, D. 2018. "Why Are There So Few Disabled Architects and Architecture Students?" *The Architect's Newspaper*, June 15.

Gissen, D. 2022. *The Architecture of Disability: Buildings, Cities, and Landscapes beyond Access.* Minneapolis: University of Minnesota Press.

Gurita, A.-E. and R.-D. Vatavu. 2025. "When LLM-Generated Code Perpetuates User Interface Accessibility Barriers." In *Proceedings of W4A '25*. ACM.

Hamraie, A. 2017. *Building Access: Universal Design and the Politics of Disability.* Minneapolis: University of Minnesota Press.

Hamraie, A. and K. Fritsch. 2019. "Crip Technoscience Manifesto." *Catalyst: Feminism, Theory, Technoscience* 5(1).

Heylighen, A. and J. Herssens. 2014. "Designerly Ways of Not Knowing: What Designers Can Learn about Space from People Who Are Blind." *Journal of Urban Design* 19(3): 317-332.

Jay, M. 1993. *Downcast Eyes: The Denigration of Vision in Twentieth-Century French Thought.* Berkeley: University of California Press.

Jones, B.T. et al. 2025. "AIDL: A Solver-Aided Hierarchical Language for LLM-Driven CAD Design." *Computer Graphics Forum*.

Khan, S. et al. 2024. "Text2CAD: Generating Sequential CAD Designs from Beginner-to-Expert Level Text Prompts." In *Proceedings of NeurIPS 2024*.

Loomis, J.M., R.L. Klatzky, and R.G. Golledge. 2001. "Cognitive Mapping and Wayfinding by Adults Without Vision." In *Navigating through Environments*. Springer.

Lundgard, A. and A. Satyanarayan. 2022. "Accessible Visualization via Natural Language Descriptions: A Four-Level Model of Semantic Content." *IEEE Transactions on Visualization and Computer Graphics* 28(1).

Millar, S. 1994. *Understanding and Representing Space.* Oxford: Oxford University Press.

Millar, S. 2008. *Space and Sense.* Hove: Psychology Press.

Noel, V.A.A., Y. Boeva, and H. Dortdivanlioglu. 2021. "The Question of Access: Toward an Equitable Future of Computational Design." *International Journal of Architectural Computing* 19(4): 496-511.

Pallasmaa, J. 2005. *The Eyes of the Skin: Architecture and the Senses.* 2nd ed. Chichester: Wiley.

Papert, S. 1980. *Mindstorms: Children, Computers, and Powerful Ideas.* New York: Basic Books.

Piaget, J. and B. Inhelder. 1956. *The Child's Conception of Space.* London: Routledge.

Potluri, V. et al. 2022. "CodeWalk: Facilitating Shared Awareness in Mixed-Ability Collaborative Software Development." In *Proceedings of ASSETS '22*. ACM.

Pullin, G. 2009. *Design Meets Disability.* Cambridge, MA: MIT Press.

Rietschel, M., F. Guo, and K. Steinfeld. 2024. "Mediating Modes of Thought: LLMs for Design Scripting." In *Proceedings of ACADIA 2024*, Calgary.

Sass, L. 2024. ACADIA Teaching Award of Excellence. ACADIA 2024 ("Designing Change"), Calgary.

Schon, D.A. 1983. *The Reflective Practitioner: How Professionals Think in Action.* New York: Basic Books.

Sennett, R. 2008. *The Craftsman.* New Haven: Yale University Press.

Seo, J.Y. et al. 2024. "Designing Born-Accessible Courses in Data Science and Visualization." In *Eurographics / IEEE VGTC Conference on Visualization*.

Siu, A.F. et al. 2019. "shapeCAD: An Accessible 3D Modelling Workflow for the Blind and Visually-Impaired Via 2.5D Shape Displays." In *Proceedings of ASSETS '19*. ACM.

Siu, A. et al. 2025. "A11yShape: AI-Assisted 3-D Modeling for Blind and Low-Vision Programmers." In *Proceedings of ASSETS '25*. ACM.

Stangl, A. et al. 2021. "Going Beyond One-Size-Fits-All Image Descriptions to Satisfy the Information Wants of People Who Are Blind or Have Low Vision." In *Proceedings of ASSETS '21*. ACM.

Thinus-Blanc, C. and F. Gaunet. 1997. "Representation of Space in Blind Persons: Vision as a Spatial Sense?" *Psychological Bulletin* 121(1): 20-42.

Winner, L. 1980. "Do Artifacts Have Politics?" *Daedalus* 109(1): 121-136.

Zumthor, P. 2006. *Atmospheres: Architectural Environments — Surrounding Objects.* Basel: Birkhauser.
