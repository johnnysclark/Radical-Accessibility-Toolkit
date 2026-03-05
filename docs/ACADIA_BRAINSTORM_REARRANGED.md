# ACADIA 2026 Brainstorm: Literature Rearranged, Framings Rethought

**Project:** Radical Accessibility Project (UIUC School of Architecture)
**PI:** John Clark
**Date:** 2026-03-05
**Purpose:** Reorder the 136-source literature review to lead with the contemporary ACADIA/CumInCAD conversation the paper enters, then rethink framings based on what emerges when the argument starts from the current disciplinary moment.

---

## Why Rearrange?

The original review was organized by theme (phenomenology, cognition, disability studies, etc.) — useful for a comprehensive survey but not for writing a paper. An ACADIA reviewer reads from their own context: what is the field doing *right now*, and what does this paper add? Starting from Merleau-Ponty and working forward requires the reviewer to hold 80 years of philosophy before reaching the contribution.

This document flips the order. It starts with the papers an ACADIA 2026 reviewer is most likely to have read or reviewed in the last two years, establishes what the field is converging on, identifies the blind spot, and then pulls in the deeper foundations only as needed to support the argument.

---

## Part I: The Current Moment — What ACADIA Is Already Doing (2022–2026)

These are the papers that define the conversation the submission enters. They establish that text-to-geometry, AI-assisted design, and equity/access are live topics at ACADIA and CumInCAD venues *right now*. The project's contribution must be positioned relative to this work.

### 1A. Text-to-Geometry Is Now Mainstream

The field has independently converged on text-based interfaces to CAD — not for accessibility, but for convenience, LLM integration, and workflow automation. This is the project's strongest positioning opportunity: the field is arriving at the same architecture the project built out of necessity.

**Rietschel, Guo & Steinfeld (2024).** "Mediating Modes of Thought: LLMs for Design Scripting." *ACADIA 2024, Calgary.* — LLM agents mediate between user intent and Grasshopper, parsing generated JSON. Text-prompt-to-JSON-to-Grasshopper pipeline closely parallels the project's CLI-to-JSON-to-Rhino pipeline. Built for convenience; the project built it for necessity.

**El Hizmi, Shkolnik, Austern & Sterman (2024).** "LLMto3D: Generating Parametric Objects from Text Prompts." *ACADIA 2024.* — Multi-agent LLM pipeline translating natural language to parametric 3D objects. The closest published ACADIA work to the project's text-to-geometry ambition. Zero consideration of accessibility or non-visual verification.

**Rietschel & Steinfeld (2025).** "Intelligent Tools on the Loose: Reasoning Models for Exploratory Computational Design." *IJAC.* — Extends toward conversational, exploratory design interaction. The conversational pattern the project envisions through MCP.

**Rietschel et al. (2024).** "Raven: AI Plugin for Grasshopper." *ACADIA 2024 / UC Berkeley.* — Makes Grasshopper text-controllable via LLMs. Still requires seeing the canvas to verify.

**Ant (2026).** "AI Copilot for Grasshopper." *Food4Rhino.* — Builds, modifies, and explains Grasshopper definitions from natural language. Further evidence the community is moving toward text-to-geometry workflows. Still assumes sighted verification.

**Jones et al. (2025).** "AIDL: A Solver-Aided Hierarchical Language for LLM-Driven CAD Design." *Computer Graphics Forum / MIT CSAIL.* — Domain-specific language designed for LLMs to generate CAD geometry. Key insight: designed for "blind" AI code generation — eliminating the need for visual verification. Hierarchical, constraint-based approach (declare relationships, let solvers handle coordinates) maps directly onto the project's semantic-over-geometric principle. The strongest theoretical ally from the ML/graphics community.

**Khan et al. (2024).** "Text2CAD: Generating Sequential CAD Designs from Beginner-to-Expert Level Text Prompts." *NeurIPS 2024 (Spotlight).* — First end-to-end transformer for parametric CAD from natural language. Demonstrates NL-to-parametric-geometry is a solved problem. The project shows it is *necessary* for a blind designer.

**Atakan et al. (2025).** "Kakadoo: LLM Enabled Speech Interface for Enhanced Human-Computer Interaction." *eCAADe 2025, Ankara.* — Voice-driven Grasshopper plugin. The most directly relevant recent CumInCAD paper. Demonstrates voice/text-to-geometry is viable. The project's CLI achieves the same goal for a user who cannot see the visual feedback.

**Di Marco (2025).** "Agentic, Multimodal LLM for Conversational Architectural Design." *Architectural Science Review.* — ConvoAI: agentic LLM for conversational design. Three engagement modes. The "Design Partner" mode is most relevant to the project's MCP direction.

**CADialogue (2025).** *Computer-Aided Design.* — Conversational parametric CAD through natural language. Assumes multimodal (visual + text) input; the project needs text/speech-only.

**Grasshopper MCP Server (2025).** — Validates that MCP transport works with Rhino/Grasshopper.

**Wu et al. (2024).** "CAD-LLM." *NeurIPS Workshop / Autodesk.* — Fine-tuning language models on engineering sketches. Sequential nature of CAD suits language model architectures — the same property that makes CLI interaction natural.

**What this cluster establishes:** Text-to-geometry is the direction of the field. Everyone is building text/speech/LLM front-ends to visual CAD back-ends. *None of them addresses what happens when the user cannot see the back-end at all.* The project occupies the blind spot: a text-first pipeline where the text interface is not a convenience layer but the primary and sole authoring interface for its user.

### 1B. Equity, Access & Inclusion Are on the Agenda

ACADIA and CumInCAD have signaled that inclusion matters — but the discourse remains at the level of calls-to-action rather than working systems.

**Cupkova, Wit, del Campo & Claypool (2023).** "AI, Architecture, Accessibility, and Data Justice." *IJAC — ACADIA Special Issue.* — The community's most direct engagement with accessibility as a computational design concern. The project responds to this call with a working system.

**Noel, Boeva & Dortdivanlioglu (2021).** "The Question of Access: Toward an Equitable Future of Computational Design." *IJAC.* — Examines the trope of "access" in digital fabrication and design. The project demonstrates what "access" means concretely: a CLI that a screen reader can parse.

**Karastathi et al. (2024).** "Bridging Pixels and Fabrication: Enhancing Accessibility in CNC Knitting." *ACADIA 2024 (Vanguard Award Winner).* — ACADIA recognizes that "accessibility" means making specific tools usable by people currently excluded. The CLI-to-Rhino pipeline shares the pattern: a bridge layer between an accessible interface and an inaccessible tool.

**eCAADe 2022 Conference.** "Co-creating the Future: Inclusion in and through Design." *KU Leuven.* — Entire conference themed around inclusion. The project provides a concrete case study.

**Heylighen et al. (2021–2024).** "How Do Disabled Architects Design?" *Research[x]Design, KU Leuven.* — The strongest ongoing theoretical precedent. She argues through empirical study; the project argues through tool-building.

**Zallio & Clarkson (2021, 2023).** Inclusion in the built environment; challenges designing accessible buildings. — Identifies lack of tools as a key barrier. The project provides exactly the tool-level intervention called for.

**del Campo (2022–2024).** AI + Architecture publications. — Establishes ACADIA's deep engagement with AI-architecture integration. None addresses accessibility. The project shows AI-architecture tools can and must be accessible.

**What this cluster establishes:** The community has named the problem (inequitable access to computational design) but has not built the solution. Papers call for equity; the project delivers a functioning tool. This is the gap the paper fills.

### 1C. Accessible Modeling & Blind Authorship — The HCI Side

These are the papers from CHI, ASSETS, and accessibility venues that address the project's core problem — enabling blind people to create, not just consume, design artifacts. ACADIA reviewers may not have read these; introducing them is itself a contribution.

**Siu et al. (2025).** "A11yShape: AI-Assisted 3-D Modeling for Blind and Low-Vision Programmers." *ASSETS '25.* — OpenSCAD + GPT-4o for accessible 3D modeling. Four-facet representation. The most directly comparable system. Key differences: general 3D modeling vs. architectural design; integrated vs. decoupled (enabling independent blind/sighted collaboration); no screen-reader-specific output protocol.

**Siu, Kim et al. (2019).** "shapeCAD: An Accessible 3D Modelling Workflow for the Blind." *ASSETS '19.* — OpenSCAD + 2.5D shape display. The prior art. The project differs: domain-specific CLI, architectural-scale, integrates with industry-standard Rhino.

**Billah et al. (2023).** "Designing While Blind." *ASSETS '23.* — Blind-led team designing tactile graphics. Central argument: inaccessible digital tools prevent blind people from leading design of media they consume. The exact problem the project solves.

**Clepper et al. (2025).** "'What Would I Want to Make? Probably Everything.'" *CHI 2025.* — BLV tactile graphics creators navigating tradeoffs between accessible low-fidelity tools and inaccessible high-fidelity ones. The closest published parallel to Daniel's position. The project makes high-fidelity CAD operable through an accessible interface.

**Crawford et al. (2024).** "Co-designing a 3D-Printed Tactile Campus Map." *ASSETS '24.* — During co-design, the participant's screen reader was unable to interpret TinkerCAD. Powerfully demonstrates the failure the project addresses.

**Flores-Saviaga et al. (2025).** "The Impact of Generative AI Coding Assistants on Developers Who Are Visually Impaired." *CHI 2025.* — AI assistants exacerbate accessibility barriers through suggestion overload. Validates the CLI's explicit command-response model over inline suggestions.

**Das et al. (2024).** "'I look at it as the king of knowledge.'" *ASSETS '24.* — Blind users face significant accessibility barriers even in AI interfaces. Validates building a purpose-designed, screen-reader-native CLI.

**MAIDR + AI (2024).** *ASSETS '24.* — Co-designed LLM extension for blind users' visual queries about data. The "AI as interpretation layer" pattern needed for describing Rhino viewport content.

**Seo et al. (2024).** "Designing Born-Accessible Courses in Data Science." *Eurographics / IEEE.* — "Born-accessible" concept: designed from the ground up for blind learners. The pedagogical parallel to the project's "accessibility-first" principle. UIUC colleague; natural collaboration target.

**Gurita & Vatavu (2025).** "When LLM-Generated Code Perpetuates UI Accessibility Barriers." *W4A '25.* — LLM-generated interfaces do not spontaneously produce accessible code. Accessibility must be structural, not emergent.

**Madugalla et al. (2020).** "Creating Accessible Online Floor Plans for Visually Impaired Readers." *ACM TACCESS.* — Semi-automatic transcription of architectural drawings into text, tactile, and audio-tactile output. Multi-modal approach validates the project's strategy. Finding: users want both overview and detailed room-by-room info, validating `show` vs. `describe` commands.

**Lundgard & Satyanarayan (2022).** "Accessible Visualization via Natural Language Descriptions: A Four-Level Model." *IEEE VIS.* — L1 construction, L2 statistics, L3 trends, L4 context. Framework for structuring the CLI's describe output.

**Stangl et al. (2021).** "Going Beyond One-Size-Fits-All Image Descriptions." *ASSETS '21.* — Description needs vary by context. Informs how AI descriptions should differ for design review, navigation, critique.

**Potluri et al. (2018).** "CodeTalk." *CHI 2018 (Honorable Mention).* — DGNA framework (Discoverability, Glanceability, Navigability, Alertability) for IDE accessibility. The OK:/ERROR: protocol addresses Glanceability and Alertability.

**Potluri et al. (2022).** "CodeWalk." *ASSETS '22.* — Mixed-ability collaborative development. The controller/viewer separation enables analogous mixed-ability architectural collaboration.

**What this cluster establishes:** HCI/accessibility research has identified the problem (blind people are excluded from design authorship) and built partial solutions for general 3D modeling. No one has built an architecturally-specific, screen-reader-native, industry-tool-integrated system. The project bridges the gap between HCI's accessibility expertise and ACADIA's architectural computing expertise.

### 1D. Scripting, Voice & Text-First CAD — Historical Precedents Within CumInCAD

These papers establish that text-based CAD is not new — it has a lineage within the community — but accessibility was never the motivating concern.

**Maleki & Woodbury (2013).** "Programming In the Model." *ACADIA 2013.* — Bidirectional link between script and model prefigures the CLI-to-Rhino watcher pipeline. Key difference: PIM assumes both windows are visual.

**Celani & Vaz (2012).** "CAD Scripting and Visual Programming Languages." *IJAC.* — Scripting is more powerful for generative systems than visual programming. Never considers accessibility.

**Leitão, Santos & Lopes (2012).** "Programming Languages for Generative Design." *IJAC.* — Text-based interaction often *superior* for complex parametric tasks. Rosetta multi-CAD tool.

**Xue & Yen (2009).** "Natural Voice-Enabled CAD." *CAD Applications.* — Natural language voice commands for CAD. Core insight: CAD should accept natural discourse. Validates text/speech as primary, not accommodative.

**Desolda et al. (2023).** "Digital Modeling for Everyone: Voice-Based 3D Modeling." *CHI 2023.* — Users prefer relational descriptions over coordinates. Validates the CLI's semantic approach.

**Nagakura (1990).** "Shape Recognition: A Script-Based Approach." *CAAD Futures '89.* — Early text-driven geometric manipulation.

**Nembrini et al. (2009).** "Source Studio." *CAAD Futures.* — Teaching programming for architectural design.

**CadQuery.** Open-source Python parametric CAD scripting. — Validates the project's Python-stdlib-only approach.

---

## Part II: The Blind Spot — What No One Is Doing

The rearrangement reveals a pattern: the field is building text-to-geometry pipelines (Part 1A), calling for equity (Part 1B), and HCI researchers are building accessible modeling tools (Part 1C). But:

1. **No ACADIA/CumInCAD paper describes a CLI-first, screen-reader-native CAD tool used in architectural education.** Text-to-geometry work assumes sighted verification. Equity papers don't build tools. Accessible modeling tools don't target architecture.

2. **No one connects the text-to-geometry explosion to the accessibility argument.** AIDL (Jones et al., 2025) designed a language for "blind" AI code generation — and never mentions blind *humans*. Raven, Ant, and Kakadoo add text interfaces to Grasshopper but still require the canvas. The project is the only system where the text interface is the *complete* authoring environment for a user who cannot see the viewer at all.

3. **No paper bridges architectural phenomenology and computational design tools for blind users.** The philosophical critique (Pallasmaa, Evans, Carpo) and the technical work (shapeCAD, Raven, Text2CAD) exist in separate literatures. The project connects them.

4. **No ACADIA paper uses critical disability studies frameworks.** Winner's "Do Artifacts Have Politics?" is among the most cited STS papers ever. Hamraie's "crip technoscience" is well-established in disability studies. Neither appears in the ACADIA/CumInCAD literature. The paper introduces these frameworks to the computational design community.

5. **Blind authorship in architecture is undocumented.** Billah et al. (2023) document that blind people cannot author the tactile media they consume. Crawford et al. (2024) show that even simple CAD tools fail screen readers. The project is the only system where a blind graduate architecture student authors parametric floor plans in studio.

---

## Part III: Foundations — Pull In As Needed

These are the deeper sources. They don't lead the paper; they support specific claims when cited. Organized by the argument they serve.

### 3A. "Architectural Tools Are Not Neutral" — Representation Theory

The argument: the CLI is not a workaround but a different representational medium that generates different architectural possibilities.

**Evans (1997).** *Translations from Drawing to Building.* — Drawings are not transparent; they are active agents that shape what can be designed. If drawings shape design, then the CLI shapes design differently. The single strongest theoretical foundation.

**Carpo (2011, 2017).** *The Alphabet and the Algorithm* / *The Second Digital Turn.* — Notation systems structure design thinking across epochs. The CLI constitutes a new notation with its own design intelligence.

**Allen (2009).** *Practice: Architecture, Technique and Representation.* — Concepts emerge from representational practices. The CLI's command vocabulary produces its own kind of architectural intelligence.

**Burry (2011).** *Scripting Cultures.* — Scripting lets designers escape constraints embedded in commercial software. The CLI is exactly this: a bespoke tool bypassing Rhino's GUI. Elevates from "accommodation" to "design methodology."

**Picon (2010).** *Digital Culture in Architecture.* — CAD software constitutes a culture. The CLI constitutes an alternative digital culture.

**Kolarevic (2003).** *Architecture in the Digital Age.* — "File-to-factory" maps onto "JSON-to-Rhino." Same logic, different assumption about who controls the file.

**Lynn (1999).** *Animate Form.* — A specific tool (animation software) generated an entire architectural vocabulary. Evidence that tools shape design thinking. The CLI will generate its own.

**Easterling (2014).** *Extrastatecraft.* — Infrastructure as political medium. CAD's visual infrastructure excludes; the project builds alternative infrastructure.

**Deamer (2015/2020).** *The Architect as Worker* / *Architecture and Labor.* — Tools are structures of labor. Screen-based CAD renders text-based, tactile work invisible. The CLI makes a blind designer's work visible and authoritative.

### 3B. "Vision Is Not Required for Spatial Cognition" — Cognitive Science

The argument: the CLI is cognitively aligned with how blind users construct spatial knowledge. This is not a compromise; it is a match.

**Millar (1994, 2008).** *Understanding and Representing Space* / *Space and Sense.* — Spatial cognition is modality-independent when adequate reference frames are provided. The CLI provides those frames: named bays, labeled axes, numbered dimensions.

**Loomis, Klatzky & Golledge (2001).** "Cognitive Mapping without Vision." — Spatial representations derived from spatial language function equivalently to those derived from perception. The most powerful single piece of evidence for the CLI approach.

**Thinus-Blanc & Gaunet (1997).** "Representation of space in blind persons." — Discrepancies in blind spatial cognition stem from strategy differences, not fundamental limitations. The CLI provides the strategy-enabling infrastructure.

**Piaget & Inhelder (1956).** *Child's Conception of Space.* — Spatial understanding develops topologically (qualitative relationships) before metric. The CLI encodes topological/semantic relationships first — matching cognitive development.

**Saerberg (2010).** "How Blind and Sighted Pedestrians Negotiate Space." — Blind spatial cognition is sequential, landmark-based. The CLI's sequential command structure aligns.

**Giudice (2018).** "Navigating without Vision." — Blind spatial cognition is language-mediated. Language *is* a spatial medium for blind people.

**Cattaneo & Vecchi (2011).** *Blind Vision.* — Neuroscience evidence that blindness does not preclude rich spatial reasoning.

**Chen et al. (2024).** "Perception beyond sight." — Congenitally blind cognitive maps consist of links, reference points, areas, separators. The CLI's vocabulary (bays, corridors, columns) maps onto this.

**Hatwell, Streri & Gentaz (2003).** *Touching for Knowing.* — Touch achieves equivalent spatial cognition to vision. Validates the tactile output pipeline.

### 3C. "Architecture Is Multi-Sensory" — Phenomenology

The argument: the project operationalizes what phenomenologists have argued theoretically — that architecture exceeds vision.

**Pallasmaa (1996/2012).** *The Eyes of the Skin.* — The canonical critique of architecture's ocularcentrism. The project makes it operational.

**Jay (1993).** *Downcast Eyes.* — The genealogy of visual bias. Architecture's ocularcentrism is epistemological, not just practical.

**Zumthor (2006).** *Atmospheres.* — Nine generators of architectural atmosphere; only one (Light) is primarily visual. The CLI's semantic model captures the others.

**Holl, Pallasmaa & Pérez-Gómez (1994/2006).** *Questions of Perception.* — Architecture is multi-sensory, irreducible to visual representation.

**Böhme (2017).** *Aesthetics of Atmospheres.* — We experience space sensorially before we understand it visually. Tools that bypass vision may access architecture more directly.

**Pérez-Gómez (2016).** *Attunement.* — Architecture as embodied relationship, not picture. Daniel's engagement is a different form of architectural attunement.

**Merleau-Ponty (1945/1962).** *Phenomenology of Perception.* — The "blind man's cane" as extended body schema. The CLI as Daniel's "cane" for architectural design.

**Gibson (1979).** *Ecological Approach to Visual Perception.* — Affordance theory is about action, not sight. CLI commands are linguistic affordances.

### 3D. "Designing for Disability Produces Better Tools" — Disability Studies & Design Justice

The argument: the project is not assistive technology. It is a structural redesign that reveals better patterns.

**Hamraie (2017).** *Building Access.* — "Normate template" concept. Rhino/Grasshopper/Revit designed around a sighted, mouse-using operator. The project replaces this template.

**Hamraie & Fritsch (2019).** "Crip Technoscience Manifesto." — Disabled people as knowers and makers, not just users. Daniel is a maker of architectural knowledge.

**Gissen (2022).** *The Architecture of Disability.* — Beyond access. The project doesn't make Rhino "accessible"; it builds a fundamentally different ecosystem.

**Winner (1980).** "Do Artifacts Have Politics?" — Technologies enforce social arrangements. The project builds artifacts with different politics.

**Costanza-Chock (2020).** *Design Justice.* — Center voices of those most impacted. The project demonstrates that centering a marginalized user produces better tools for everyone.

**Pullin (2009).** *Design Meets Disability.* — Designing for disability drives innovation. The CLI's crash resilience, scriptability, and version control are the curb cut effect.

**Boys (2014).** *Doing Disability Differently.* — Disability as avant-garde. The project's ACADIA contribution is a cutting-edge methodological intervention.

**Reynolds (2017).** "World-Creating Blindness." — Crip phenomenology corrective. Daniel is co-designer, not subject. Tools built *from* his experience, not *about* it.

**Charlton (1998).** *Nothing About Us Without Us.* — Daniel shapes tool requirements, evaluates outputs, identifies spatial relationships sighted developers miss.

**Williamson (2019).** *Accessible America.* — Disability emerges from the material environment. The project eliminates the material barrier.

**Gissen (2018).** "Why are there so few disabled architects?" — Inaccessible CAD software is a structural barrier the article does not name. The project addresses it.

**Lifchez (1987).** *Rethinking Architecture.* — Foundational disability-inclusive pedagogy. Daniel extends this: not consumer/critic of design but primary author.

**Nicholson (2025).** "Where Are My People?" *ACSA.* — The profession has not systematically addressed inclusion of disabled practitioners.

**NAAB (2020).** *Conditions for Accreditation.* — Addresses disability in buildings and student support but is silent on accessible design tools.

### 3E. "The Blind Student's Workflow" — Embodied Cognition & Practice Theory

The argument: the CLI is a medium of design conversation and craft, not a degraded substitute for visual modeling.

**Schön (1983).** *The Reflective Practitioner.* — Design as "reflective conversation with the situation." Each CLI command is a move; each OK:/ERROR: is the situation talking back. The CLI makes the conversation explicit and auditable.

**Varela, Thompson & Rosch (1991).** *The Embodied Mind.* — Cognition is enacted through bodily engagement. Daniel's CLI engagement is a different enactment of spatial cognition, equally valid.

**Clark & Chalmers (1998).** "The Extended Mind." — The CLI is Daniel's extended mind for architectural design. state.json is his architectural memory.

**Sennett (2008).** *The Craftsman.* — Dialogue between hand and head. Daniel's hands on keyboard and braille display are his primary cognitive interface. The CLI creates the rhythmic dialogue Sennett describes.

**Ingold (2013).** *Making.* — Knowledge generated through making, not applied to it. Daniel discovers the plan through commanding and receiving feedback. The CLI is a medium of correspondence, not imposition.

### 3F. Sonification & Aural Architecture — Future Direction

**Blesser & Salter (2007).** *Spaces Speak, Are You Listening?* — Aural architecture: maps spatial properties to sound parameters. The single most important text for the sonification direction.

**Schafer (1977).** *The Soundscape.* — Foundational acoustic ecology. Soundscapes of Daniel's designs for evaluating spatial qualities.

**Garcia (1996).** "Sound Structure." *CAADRIA.* — Sonification for structural education. Early precedent.

**More et al. (2002, 2004).** "Understanding Spatial Information / Designing Spatial Sounds." *ACADIA / eCAADe.* — Rare ACADIA papers investigating aural representation of spatial information.

**Beilharz (2005).** "Architecture as Computer Interface." *eCAADe.* — Gestural interaction producing sonification.

**Grabowski & Barner (1998).** "Force Feedback and Sonification." — Multimodal (haptic + auditory) paradigm.

**Navarro Villacampa et al. (2025).** "Sensing the Invisible." *eCAADe 2025.* — Sonification of invisible phenomena. Growing interest in making the invisible audible.

### 3G. Haptic, Tactile & Fabrication — The Physical Pipeline

**Holloway & Marriott (2018).** "Accessible Maps." *CHI 2018.* — 3D models preferred over tactile graphics, better recall. Informs choice between 3D printing and PIAF.

**Butler et al. (2023).** "TactIcons." *CHI 2023.* — 33 instantly recognizable tactile icons. Design vocabulary for the PIAF pipeline.

**Brulé & Bailly (2021).** "'Beyond 3D Printers.'" *CHI 2021.* — Six years of digital fabrication for blind education. Shift from single-technology to hybrid approaches parallels the project's multi-output strategy.

**Koch et al. (2012).** "Haptic Paintings." *eCAADe.* — Workflows for tactile representations. The project's advantage is automation and CLI integration.

**Celani et al. (2013).** "'Seeing' with the Hands." *CAAD Futures.* — 3D for blind education. The project extends by automating translation and closing the loop (tactile input via pegboard).

**Miele et al. (2006).** "Talking TMAP." — Automated tactile map production. Multi-layer information architecture parallels `show` vs. `describe` commands.

**MIT (2025).** "Tactile Vega-Lite." — Automatic visual-to-tactile translation. Validates automatic conversion over manual recreation.

**Tactile Architectural Drawings Typology (2022).** *Sustainability / MDPI.* — Classification framework for tactile output.

**FlexiBoard (2024).** *MDPI.* — Flexible tangible interface. Relevant to the pegboard system.

**Garcia (1999).** "PUSH." *ACADIA '99.* — Haptic feedback for structural form generation. The pegboard is a low-tech version.

**Sjostrom (2002).** "Non-Visual Haptic Interaction Design." *PhD, Lund.* — Guidelines for haptic interaction specific to non-visual use.

**Pohl & Hirschberg (2011).** "Sensitive Voxel." *CAAD Futures.* — Reactive tangible surface. Similar design space to the pegboard.

**Herssens & Heylighen (2011).** "Haptic Design Parameters." *CAAD Futures.* — Texture, temperature, weight, compliance. Informs the tactile output pipeline.

### 3H. Blind Architects, Pedagogy & Institutional Context

**Downey, Chris.** Blind architect, San Francisco. — Lost sight after 20 years of practice. Uses embossed tactile plans. Works around inaccessible tools; the project builds accessible ones from the ground up.

**Vermeersch & Heylighen (2012).** "Carlos Mourao Pereira." — Blind architect whose designs became more multi-sensory after losing sight. Individual precedent for the project's tool-level argument.

**Heylighen & Herssens (2014).** "Designerly Ways of Not Knowing." — Architects' visual training creates systematic blind spots. The most important theoretical paper for the project.

**Vermeersch et al. (2018).** "Designing from Disability Experience." *PDC.* — Disability experience as generative knowledge. Daniel as co-designer parallels.

**UT Austin (2023).** "If buildings were invisible, what of architecture would remain?" — Graduate studio designing for Texas School for the Blind. Blind experience remains the *subject*; students used conventional visual tools. Contrast with the project: the blind student is authoring geometry.

**Sass (2024).** ACADIA Teaching Award. — Fabrication-centered pedagogy. The project asks what that looks like for a blind student.

**Miller (2010).** "[make]SHIFT." *ACADIA.* — Non-standard workflows for information exchange. The file-watching pipeline as non-standard collaborative workflow.

**Akbar et al. (2023).** "Democratizing the Designer's Toolbox." *eCAADe.* — Platform-agnostic pedagogy. The project: not just platform-agnostic but modality-agnostic.

**Fricker et al. (2020).** "Computational Design Pedagogy." *eCAADe.* — Computational thinking does not require visual cognition.

**Janssen & Chen (2011).** "Visual Dataflow Modelling." *CAAD Futures.* — Comparing visual dataflow systems implicitly reveals what is lost when the only interface is visual.

**Shinohara & Wobbrock (2011).** "In the Shadow of Misperception." *CHI (Best Paper).* — Accessibility should be built into mainstream technologies. The CLI is mainstream architecture tooling that happens to be accessible.

**Wobbrock et al. (2011).** "Ability-Based Design." *ACM TACCESS.* — Seven principles. "What can Daniel do?" not "What can't he?"

**Mankoff et al. (2010).** "Disability Studies as Critical Inquiry for AT." *ASSETS.* — Instead of fixing the individual, question the system. The CLI redesigns the system.

**Ladner (2015).** "Design for User Empowerment." *ACM Interactions.* — Daniel co-designs and provides feedback that reshapes the CLI.

**Imrie (2012).** "Universalism." — "Design for one, extend to many" may be more productive than abstract universalism.

**Steinfeld & Maisel (2012).** *Universal Design.* — Eight goals. CLI scores well on understanding, personalization, awareness.

**Levent & Pascual-Leone (2014).** *The Multisensory Museum.* — Multisensory design enriches experience for everyone.

**Mulligan et al. (2018).** "Inclusive Design in Architectural Education." — Disability taught as subject *for*, not perspective *from*. The project inverts this.

**Sharif et al. (2022).** "Screen-Reader Users + Online Data Viz." *EuroVIS.* — Failure patterns in screen reader visualization navigation.

**Practical CAD for VI (2023).** *Springer LNCS.* — Confirms the problem is recognized. The project's approach is more radical.

---

## Part IV: Rethought Framings

Starting from the contemporary work (Part I) rather than from philosophy changes what the framings emphasize. The original seven framings were organized theory-to-practice. These rethought framings start from what the ACADIA audience is *already working on* and reveal the project as the missing piece.

### Framing A: The Accidental Architecture — Why Text-to-Geometry Needs Blindness

**Working title:** "The Accidental Architecture: What the Text-to-Geometry Revolution Doesn't Know It Needs"

**Core move:** The field is converging on text-to-geometry (Raven, Ant, Text2CAD, AIDL, Kakadoo, LLMto3D). But every one of these systems treats the text interface as a front-end to a visual back-end. The sighted user types a prompt, the system generates geometry, and the user *looks at it* to verify. What happens when the user can't look? The verification problem — confirming that the system produced what you intended — is unsolved in every text-to-geometry pipeline because it was never the problem they set out to solve. The project solved it first because it had to.

**Argument structure:**
1. Survey the text-to-geometry explosion (Rietschel, El Hizmi, Jones/AIDL, Khan, Atakan, Di Marco)
2. Identify the shared assumption: visual verification is available
3. Show that the project, built for a blind user, solved the verification problem through structured textual feedback (OK:/ERROR: protocol, semantic `describe` commands, four-level descriptions following Lundgard & Satyanarayan)
4. Argue that this solution is *better for everyone* — more auditable, more scriptable, more machine-parseable than visual verification
5. Conclude: designing for blindness produced the verification architecture that text-to-geometry pipelines will eventually need, because as AI generates more geometry, no human — sighted or not — can visually verify everything

**Why this framing works:** It meets the ACADIA audience where they are (excited about LLM-to-CAD) and shows them what they're missing. It doesn't ask for sympathy; it offers a technical solution to a problem the audience already has. The "accidental" framing — the project wasn't trying to solve the field's verification problem, it was solving its own accessibility problem, and the solutions turned out to be the same — is the strongest version of the curb-cut argument.

**Key citations:** Rietschel (2024), El Hizmi (2024), Jones/AIDL (2025), Khan/Text2CAD (2024), Atakan/Kakadoo (2025), Lundgard & Satyanarayan (2022), Gurita & Vatavu (2025), Flores-Saviaga (2025), Pullin (2009)

---

### Framing B: The Model Is Not the Viewport — Separating Intent from Projection

**Working title:** "The Model Is Not the Viewport: What a Blind Architect Reveals About Architectural Representation"

**Core move:** Evans (1997) proved that drawings are active agents shaping what can be designed. Carpo (2011, 2017) traced how notation systems structure design thinking. But neither Evans nor Carpo imagined a notation system authored through a screen reader. The project forces the question: if you remove the viewport entirely, what remains of the architectural model? Answer: everything that matters. The JSON state file (the CMA) contains every design parameter. Rhino is one possible viewer — disposable, crashable, replaceable. The model is the structured semantic description, not the geometric rendering.

**Argument structure:**
1. Open with the representation theory claim (Evans, Carpo, Burry)
2. Present the controller/viewer separation as an epistemological commitment, not just a software pattern
3. Show the CMA: what an architectural model looks like when it must be readable by a screen reader
4. Demonstrate that this separation produces concrete advantages: crash resilience, version control, mixed-ability collaboration
5. Connect to the text-to-geometry trend: Rietschel et al., AIDL, and LLMto3D all generate intermediate text representations — the project argues the intermediate representation should be *the* representation

**Why this framing works:** It makes an architectural theory argument using ACADIA's own theoretical canon (Evans, Carpo). It elevates the project from "accessible tool" to "epistemological proposition." ACADIA reviewers who have lost work to Rhino crashes will feel the practical force of the argument.

**Key citations:** Evans (1997), Carpo (2011, 2017), Burry (2011), Allen (2009), Rietschel (2024), Maleki & Woodbury (2013), Jones/AIDL (2025)

---

### Framing C: Born-Accessible — From Retrofit to Redesign

**Working title:** "Born-Accessible CAD: What Happens When You Design Architectural Software for Blindness First"

**Core move:** Seo et al. (2024) coined "born-accessible" for courses designed from the ground up for blind learners. Gurita & Vatavu (2025) showed that LLM-generated interfaces don't spontaneously produce accessible code. Flores-Saviaga et al. (2025) found that AI coding assistants exacerbate barriers for blind developers. The message is consistent: accessibility cannot be bolted on. The project is born-accessible CAD — architectural software designed for a blind user from line one, not retrofitted with screen reader support after the fact. The paper presents three design decisions that could only emerge from born-accessible development and the general improvements they produced.

**Argument structure:**
1. Establish the born-accessible concept (Seo 2024) and the failure of retrofit accessibility (Gurita 2025, Flores-Saviaga 2025, Crawford 2024)
2. Present three born-accessible design decisions:
   - Crash-only viewer (blind user can't visually confirm recovery → atomic writes + disposable Rhino)
   - Semantic-first state (blind user can't glance at viewport → every parameter named and queryable)
   - Text output protocol (screen reader needs structure → OK:/ERROR: prefix, one item per line)
3. For each: accessibility requirement → design decision → general benefit
4. Compare with retrofit approaches: shapeCAD wraps OpenSCAD, A11yShape adds AI to OpenSCAD. The project builds new architecture.
5. Conclude: born-accessible is not just more equitable but better engineering

**Why this framing works:** "Born-accessible" is a clean, memorable concept that positions the paper sharply. The three-decision structure gives the paper concrete technical content. The comparison with shapeCAD/A11yShape gives ACADIA reviewers a benchmark. The "better engineering" claim is testable and provocative.

**Key citations:** Seo (2024), Gurita & Vatavu (2025), Flores-Saviaga (2025), Crawford (2024), Siu/shapeCAD (2019), Siu/A11yShape (2025), Billah (2023), Clepper (2025), Cupkova (2023)

---

### Framing D: Crip Technoscience Meets Computational Design

**Working title:** "Crip Technoscience in the Design Studio: A Blind Student's Architecture of Architectural Software"

**Core move:** Hamraie & Fritsch (2019) define "crip technoscience" as centering disabled people as knowers and makers. Winner (1980) proved that artifacts have politics. Gissen (2022) argued for architecture beyond access. These frameworks have never entered the ACADIA/CumInCAD discourse. The paper introduces them — not as social justice overlay but as analytical tools that reveal why CAD software is structured the way it is and what changes when you restructure it from disability experience.

**Argument structure:**
1. Winner's question applied to CAD: do Rhino, Grasshopper, Revit have politics? (Yes: they enforce sighted operation)
2. Hamraie's "normate template" applied to software: the assumed user is sighted, mouse-using, screen-watching
3. Gissen's "beyond access": the project doesn't make Rhino accessible; it builds a different system where blindness is the primary design case
4. Daniel as crip technoscientist: not a user of accommodations but a co-designer whose disability experience generates architectural knowledge that sighted developers cannot access
5. The curb cut effect: three technical improvements that came from disability-first design

**Why this framing works:** This is the most intellectually ambitious framing. It introduces an entire theoretical vocabulary to ACADIA — one that the community needs. Risk: ACADIA reviewers may be unfamiliar with disability studies. Mitigation: lead with Winner (widely known in STS-adjacent fields), define terms carefully, and ground every claim in specific technical decisions. The strength is that it makes the strongest version of the argument: the project is not accommodation, not even innovation-through-constraint — it is a political reconstruction of who gets to be a maker.

**Key citations:** Hamraie (2017), Hamraie & Fritsch (2019), Winner (1980), Gissen (2022), Gissen (2018), Reynolds (2017), Charlton (1998), Costanza-Chock (2020), Boys (2014), Heylighen & Herssens (2014), Nicholson (2025)

---

### Framing E: The Reflective Conversation — CLI as Design Medium

**Working title:** "The Reflective Conversation with the State File: CLI-Driven Design as Architectural Practice"

**Core move:** Schön (1983) defined design as a "reflective conversation with the situation." In visual CAD, the "situation talking back" is a silent change in the viewport that the designer must notice. In the CLI, the situation talks back *explicitly*: `OK: Bay A rotation set to 30 degrees. READY:`. The project argues that the CLI's verbal feedback loop is not a degraded version of visual feedback but a clearer, more explicit version of the reflective conversation Schön described. The command-response loop makes every design move and every situational response auditable, diffable, and repeatable.

**Argument structure:**
1. Schön's reflective practitioner framework applied to CAD interaction
2. The problem: visual CAD's "talk back" is silent and ambient — the designer must actively look for changes
3. The solution: CLI's "talk back" is explicit and verbal — the feedback is the interface
4. Evidence from practice: Daniel's workflow in studio, specific command sequences, what the verbal protocol reveals that visual feedback obscures
5. Connection to the LLM-to-CAD trend: conversational AI design (Di Marco's ConvoAI, CADialogue) is moving toward the same explicit conversation pattern
6. Broader argument via Sennett and Ingold: the CLI is a medium of craft and correspondence, not just an input method

**Why this framing works:** It reframes the CLI from "text interface for a blind user" to "a design medium with specific qualities that visual CAD lacks." Schön is widely read in architecture schools. The connection to conversational AI makes it forward-looking. It gives the paper a strong practice narrative: Daniel's actual design sessions become evidence for a theoretical claim about the nature of design conversation.

**Key citations:** Schön (1983), Sennett (2008), Ingold (2013), Varela et al. (1991), Clark & Chalmers (1998), Di Marco (2025), CADialogue (2025), Rietschel (2024)

---

## Part V: Recommended Hybrid — What the Paper Should Actually Do

The strongest paper weaves elements of multiple framings. Based on the rearrangement, here is a recommendation:

**Lead with Framing A** (The Accidental Architecture) — it meets the audience where they are and is technically specific. Open with the text-to-geometry explosion and the verification gap.

**Use Framing B** (The Model Is Not the Viewport) as the system architecture section — it gives the controller/viewer/CMA pattern its theoretical weight through Evans and Carpo.

**Use Framing C** (Born-Accessible) as the evaluation framework — the three design decisions, each structured as accessibility requirement → design choice → general benefit, provide the paper's technical contribution.

**Invoke Framing D** (Crip Technoscience) selectively — introduce Winner and Hamraie in the discussion to frame the broader significance without requiring the reviewer to absorb an entire new theoretical vocabulary.

**Use Framing E** (The Reflective Conversation) in the case study section — Daniel's workflow is presented as a reflective conversation, with specific command sequences as evidence.

**Working title suggestion:** "The Model Is Not the Viewport: Born-Accessible Architectural Computing and the Text-to-Geometry Blind Spot"

**Subtitle alternative:** "What a Blind Architecture Student Reveals About the Future of Text-to-Geometry Design"

---

## Part VI: Six Gaps the Paper Fills

Restated from the rearranged perspective:

1. **No text-to-geometry pipeline addresses non-visual verification.** The project's structured feedback protocol is the solution.

2. **No ACADIA/CumInCAD paper presents a screen-reader-native CAD tool used in architectural education.** The paper is a first.

3. **Critical disability studies has not entered computational design discourse.** The paper introduces "crip technoscience," "normate template," and "do artifacts have politics?" to the community.

4. **The "born-accessible" paradigm has not been applied to architectural software.** The paper extends Seo's concept from pedagogy to tools.

5. **Blind authorship in computational architecture is undocumented.** The paper documents Daniel's workflow as both case study and methodology.

6. **Architectural phenomenology and computational design tools for blind users have never been connected.** The paper bridges Pallasmaa/Evans/Carpo and shapeCAD/A11yShape/the project.
