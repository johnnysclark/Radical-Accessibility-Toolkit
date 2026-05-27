---
source: User-uploaded ACADIA 2026 paper docx (b903ffd0-ACADIA_2026_Radical_Accessibility_Project.docx)
purpose: Canonical source material for NEH DHAG proposal drafting. Quote and cite freely.
status: Authoritative as of upload date 2026-05-27.
---

# Radical Accessibility Project: Accessibility Harness & Adaptive Pedagogy for Non-Visual Design Authorship

*ACADIA 2026 Paper Submission*

## Abstract

Architectural education is overwhelmingly visual. Design studio relies on drawings, models, screen-based software, and pin-up critique; the underlying pedagogy assumes a sighted learner. For a blind or low-vision (BLV) student, nearly every routine task — from drafting to peer review — currently requires sighted mediation. Prior accessibility work in this domain has been tool-shaped: a tactile graphic generator, an accessible CAD substitute, an alt-text rubric, each retrofitting access onto a pedagogy that itself remains visual. This paper describes the Accessibility Harness, a configuration pattern that wraps a large language model with a sense-agnostic design state, multiple tactile and linguistic renderers, and an LLM-scaffolded skill ramp, in order to let a BLV student author CAD geometry independently inside the same studio as sighted peers. The paper formalizes the pattern in terms of five constitutive properties — sense-agnostic state, renderer parity, multiple authoring channels, LLM skill scaffolding, and auditability — and closes by drawing implications from this single case for studio practice more broadly, framed as candidate hypotheses for future work rather than as a validated portable practice.

**Keywords: accessibility, pedagogy, large language models, tactile, CAD**

## 1. Introduction: The Visual Culture of Architecture

Architecture education traditionally relies heavily on visual representation, creating significant accessibility barriers for blind and visually impaired students. Typical studio pedagogy practices, such as reviewing plans, sections, renderings, and digital models, lack adequate accessibility integration, posing persistent obstacles to equitable participation. Accessibility features in traditional CAD and BIM software are minimal or nonexistent, and though a small discipline of architecture accessibility attempts to remedy this through standalone tools, these lack significant integration with pedagogical practices.

Our response is two-fold. First, the Accessibility Harness — a configuration pattern that wraps a large language model (LLM) with a set of domain tools to instantiate a Digital Assistant (DA) — holds a textual, sense-agnostic design state at the center, surrounds it with tactile and linguistic renderers, and treats the student's natural-language intent as an authoring channel. The student drives the work; the DA serves as the translation interface to an otherwise sighted-default discipline. The Harness is not a replacement CAD application and not a single accessible tool; it is a coordination layer. Second, an adaptive pedagogical method works alongside the Harness to shift the studio culture of design methods and production toward parity rather than accommodation. (Figure 1 shows a representative swell-paper axonometric produced through the Harness.)

Our goal is to empower blind students to engage fully and autonomously in architectural design studios in parity with sighted peers by redistributing where interdependence lies, so that the student depends on the studio's infrastructure, AI tools, and classmates in the same way every other student does, rather than on bespoke sighted mediation. This paper outlines our preliminary efforts to identify barriers in design tools, methods, and pedagogy, and to develop workflows that enable students with visual impairments to fully participate in design education independently. This research is a work in progress.

> Figure 1: Swell Paper Tactile Axonometric Drawing Print

## 2. Rationale & Technical Background

Our inquiry focused on these primary questions confronting a BLV architecture student:

How can blind students independently create, manipulate, and interpret architectural geometries?

Which interfaces (tactile, auditory, linguistic, etc.) most effectively support conceptual design workflows?

How can AI-driven natural language coding bridge the gap between spoken design intent and digital parametric modeling?

What curricular adjustments are needed to ensure equitable situations for BLV students in design studios?

While we identified several approaches to answering these questions, we also encountered several significant challenges.

Architectural education is a visual-centric curriculum which relies heavily on visual media such as drawings, images, and diagrams. Challenging this ocular-centrism by incorporating sensory diversity through touch, sound, and kinesthetic learning expands the range of architectural exploration and production in design studios.

A major challenge is the limited accessible tactile materials and tools available. Educators must rely on custom-created models or drawings tailored specifically for a single student. Teachers need the capability to quickly produce custom 3D models on demand. The standard suite of tools used in design education relies almost entirely on graphical user interfaces. Users with visual impairments leverage screen-reading software to make software accessible. We have tested the suite of tools that students use throughout their architectural education (Rhino, AutoCAD, Revit, Adobe Creative Suite) with the JAWS screen reader and have found that they are not compatible, thus preventing access to the interface of any of these tools. In addition, due to the heavy reliance of all existing software on a graphical user interface (GUI), even if the compatibility issue were to be resolved, barriers will remain for full accessibility.

Architecture relies heavily on visual methods for evaluation and feedback. Traditional methods of design assessment (visual pin-ups, graphical portfolios) are inherently inaccessible for blind students in their current incarnation. While teaching adaptations are emerging, evaluation requires similarly adapted methodologies, including tactile displays, oral descriptions, or spatial narratives accompanying physical models. Formal guidelines on these assessment practices remain scarce. Studio pedagogy relies heavily on iteration and feedback. Students learn both through direct feedback from instructors and through the feedback that their peers receive. In order to fully participate in a design studio, all students need to have access to the work of their peers.

## 3. Two Gaps in the Literature

The literature relevant to this work runs along three roughly parallel tracks: accessible-CAD and tactile-graphic engineering; disability studies and architectural ocularcentrism; and the recent, fast-moving literature on LLM-driven CAD and agentic harnesses. Read together, two gaps emerge that motivate the Harness design. (Figure 2 frames the Digital Assistant's role as the translation interface to a sighted-default discipline.)

> Figure 2: Digital Assistant as translation interface in BLV architectural education.

### 3.1. Accessible CAD and Tactile Architectural Communication

The earliest direct precedent for translating visual architectural information into a tactile channel is Way and Barner's TACTICS system (Way and Barner 1997a, 1997b), which combined Sobel edge detection and K-means segmentation to convert visual images into raised-line tactile graphics. More recent work in the same vein includes RainbowTact (Ka and Kim 2024), which demonstrated a pattern-based color-to-tactile encoding that preserves chromatic information in raised-line printing, and Kennedy's earlier theoretical and empirical work on touch as a graphic modality (Kennedy 1993), which established that blind readers can read certain pictorial conventions tactilely. Within architectural pedagogy specifically, Celani et al. (2013) and Watanabe et al. (2014) explored digitally fabricated scale models and tactile-map automation; Kłopotowska and Magdziak (2021) catalogue practical applications of typhlographic architectural drawings. The closest accessible-CAD precedent for the present work is A11yShape (Zhang et al. 2025), which uses a multimodal LLM to provide structured descriptions of OpenSCAD models for blind programmers — a turning point that confirmed an LLM-mediated approach can be effective for design tasks. Earlier accessible-CAD attempts generally proposed parallel accessible substitutes rather than wrapping the existing professional software stack.

### 3.2. Disability Studies and Architectural Ocularcentrism

The disciplinary literature on architectural ocularcentrism and disability has framed the pedagogical stakes of this work most sharply. Aimi Hamraie's Building Access (2017) traces how architecture has been designed around a "normate" body and complicates universal design rhetoric as both emancipatory and prone to absorption into market logics; this framework underlies our caution about offering the harness as a universal solution. The Bartlett's Architecture Beyond Sight program with the DisOrdinary Architecture Project (DisOrdinary Architecture Project and The Bartlett 2018–22) and the essays collected in Boys (2014) chart practitioner-side responses that re-imagine architectural practice itself in light of disability rather than retrofitting access onto a settled practice. Within studio pedagogy proper, Schön (1987) frames the iteration-and-critique loop that the Harness is designed to preserve and make non-visually traversable. Wainwright (2019) and Gipe-Lazarou (2025) raise the same questions from journalistic and vocational-behavior perspectives respectively, and Ghosh and Coppola (2024) document the lived experience of students with disabilities in adjacent computing-education contexts.

### 3.3. LLM-Driven CAD and Agentic Harnesses

The past two years have produced an explosion of natural-language-to-CAD systems, including Text2CAD (Khan et al. 2024), CAD-Llama (Li et al. 2025), and CAD2Program (Wang et al. 2025), along with CAD foundation models embedded directly in incumbent CAD applications. These developments largely target sighted users, but the underlying capability — natural language driving a CAD environment — is the prerequisite for BLV-accessible design work that does not require recreating the CAD application itself. Concurrently, the LLM agent-harness ecosystem has matured. Claude Code (Anthropic 2026) and similar developer-oriented harnesses have standardized a pattern of wrapping an LLM with a stable execution context, exposing tools via the Model Context Protocol (Anthropic 2024), and offering a chat-style interface. Community efforts such as rhino-mcp (Chen 2025) opened this tool exposure for any LLM-driven harness to operate professional CAD software. None of these harnesses are accessible by default: they assume a sighted operator at a terminal or graphical editor.

### 3.4. The Two Gaps

Two gaps emerge. First, accessible-CAD work has been tool-oriented — individual tactile converters, alt-text systems, parallel CAD substitutes — rather than pattern-oriented. Each tool addresses one slice of the studio workflow; none coordinates them around a single, sense-agnostic representation of the design. Second, the LLM agent-harness pattern, which is the most promising substrate for connecting BLV users to the visual software stack, has not been adapted for accessibility. The Accessibility Harness fills both gaps. It is a pattern, not a tool; and it is an accessibility adaptation of the LLM agent-harness pattern, not a parallel substitute. (Figure 3 diagrams the overall Harness topology.)

> Figure 3: Diagram of the overall Radical Accessibility Project Harness

## 4. Accessibility Harness: Potentials for Non-Visual Frameworks of Design

The Accessibility Harness is the configuration we built around a legally blind undergraduate architecture student enrolled at a major public university in the United States. The student is the protagonist of this section; the Harness is the supporting cast. We describe it from the inside out: first the student and the design-verification loop the system has to preserve; then the configuration pattern itself — a Controller, a State JSON, a Watcher, and Channels — that holds the loop together; then the tactile renderers and the physical workstation we call The Desk; then the linguistic renderers; and finally the five constitutive properties of the pattern, stated formally.

### 4.1. The Student and the Verification Loop of Design

For an architecture student with blindness or low vision, the central problem of GUI-driven design software is that the studio's standard feedback loop runs through sight. Where a sighted student executes a command and looks at the viewport to confirm the result, the BLV student is not able to either access the interface or complete the verification step. The conventional workaround is to use a sighted assistant, giving up independence. This work aims to close the loop differently, through artifacts that can be perceived non-visually.

The dominant trajectory of AI-assisted CAD builds on this visual culture, with the viewport remaining the design's source of truth. Our method makes the CLI the authoring layer instead. An embedded AI assistant performs three roles: (1) it drives RhinoPython to edit model state; (2) it tutors the student on the code and on RhinoPython itself; and (3) it queries the model on demand, returning spoken summaries that the BLV user uses to verify intent. The CLI serves as the guardrail and container that lets the user drive and inspect the model without engaging the inaccessible GUI. (The Harness's inputs and outputs are diagrammed in Figure 4.)

> Figure 4: Diagram of Harness Tools (Inputs and Outputs)

### 4.2. The Configuration Pattern: Controller, State, Watcher, Channels

We use "Harness" in the sense the LLM agent ecosystem has settled on: the scaffolding of instructions, code, workflows, context, standards, and tool access that wraps around a model. Interfaced by the Harness, the LLM can be made to work with screen readers and voice input/output, can describe and edit drawings and models on request, and can link to real-world tools such as cameras, the PIAF (Pictures in a Flash) tactile printer, and 3D printers. Our particular configuration is built around Rhino as the primary CAD environment. Custom code, developed with Claude Code (Anthropic 2026) as the coding agent, exposes a Controller — a command-line interface that allows the student to directly edit a persistent State JSON file. A small Rhino Python file we call the Watcher reads from the State JSON and renders the model in Rhino. In effect, the design lives in the JSON as parameters — as pure text — and Rhino is reduced to one of several peripheral renderers that consume the canonical state.

Default agent terminal user interfaces (TUIs) are illegible to screen readers: the agents' reasoning, tool calls, and responses stream as character-by-character output, partial frame redraws, and looping status spinners; colors carry meaning that screen readers cannot recover; and modal redraws break the flat document model JAWS expects. Claude Code's Channels feature offered a way around this. We use Channels to expose each agent turn to a custom web client that re-renders the turn as structured, navigable HTML: chat history delineated by ARIA landmarks, tool calls in expandable disclosures, and a parallel pane that surfaces the canonical State JSON as a navigable tree. The web client is the screen-reader-legible face of an otherwise screen-reader-hostile substrate. (Figure 5 traces the resulting design-feedback loop and Figure 6 shows the accessible web UI alongside Rhino.)

> Figure 5: Diagram of Design Feedback Loop for BLV Rhino user.

> Figure 6: Screenshot of Accessible Web UI and Rhino interface.

### 4.3. Tactile Renderers and The Desk

Where the configuration pattern provides the authoring layer and the canonical state, the tactile peripherals are where the loop physically closes. Three verification channels run in parallel from the canonical state: an LLM-based querier that answers natural-language questions about the model; PIAF (Pictures In A Flash) raised-line prints on swell paper for tactile reading of plans, sections, and elevations; and automated water-tight meshes that drive a Bambu 3D printer for tactile reading of massing and detail. Both the PIAF and the 3D printer have been moved into the studio rather than living in a separate fabrication lab, co-locating tactile fabrication with the design surface to shorten the feedback loop. Adjacent explorations have included a tactile gridded baseboard for analog wire-models, a rubber mat that lets a ballpoint pen on cardstock produce a readable tactile drawing, and a 3D-printing pen for free-form study, together with laser cutting of sheet stock from Rhino. A set of in-house tactile graphic standards governs the output of the PIAF and the 3D printer; the same standards are reused to convert pictures from the wider world (reference images and classmates' work) into legible tactile drawings. (Figure 7 illustrates the development of these standards.)

Tactile authorship sits at a workstation we call The Desk: an all-in-one configuration that integrates the CLI host, the PIAF printer, a consumer 3D printer, scanning and capture devices, and ergonomic analog tools at consistent locations. The Desk is the physical instantiation of the principle that the digital and the tactile share authority over the design. The student sits at a computer with the CLI host; a PIAF print emerges within arm's reach; a 3D-printed mass can be lifted off the printer bed without changing rooms; the scanning station for reading classmates' work is on the same surface. Each tool's position is fixed across sessions so that the workflow loop — author, verify by touch, return to the CLI, revise — is preserved as a continuous bodily routine rather than a sequence of room changes. The Desk is the answer to a pedagogical question the digital harness alone cannot answer: how should the physical organization of the studio support non-visual design authorship? It is also a deliberately low-cost, reproducible intervention. Any architecture program can co-locate a PIAF printer and a consumer 3D printer with a CLI workstation, and the rest of the configuration is mostly software.

> Figure 7: Development of Tactile Graphic Standards for CAD Drawings

### 4.4. Linguistic Renderers

Description is the second primary non-visual channel, and the system treats it as an authoring concern rather than as an accessibility annotation bolted onto visual work. Three components handle description.

The first is alt-text generation specific to architectural images. We developed a custom image description tool that produces alt-text following a Whole-to-Part methodology. Images are described first as a Whole — a high-level Macro description of the overall composition. Then, a Meso level treats different parts of the image in moderate depth. Finally, a Micro level catalogues finer-grain features. This methodology, developed for lecture slides and classroom-instruction images, structures description as a navigable hierarchy rather than a flat paragraph. Lessons were learned about the legibility of tactile images, especially perspective images, versus verbal image descriptions (below). (Figures 8 and 9 show this comparison.)

> Figure 8: Test of a perspective photograph of Notre-Dame du Haut to a half-tone dot pattern.  Tone can be represented, but not depth.  Building: Notre-Dame du Haut, Ronchamp, France. Le Corbusier, 1955.

> Figure 9: Example of Macro / Meso / Micro Description of perspective photograph of Notre-Dame du Haut.

The second is the LLM querier described earlier, a conversational interface that answers natural-language questions about the current state of the model. "Where is the front door?" "How many windows are on the east elevation?" "What is the spacing of the columns in the second bay?" The querier reads directly from the JSON state and returns spoken summaries that the student uses to verify design intent in lieu of viewing.

The third is the use of description as a design input. Spoken design intent is translated into CLI flags and JSON edits by the LLM scaffold. This inverts the typical accessibility relationship between description and image: rather than describing what is already there, the system uses description as the primary act of authorship. "Using your words" becomes a refrain and a frame of reference for collaborators and faculty engaged with BLV users, as the necessity for specific and layered descriptions becomes clear.

### 4.5. The Five Constitutive Properties

Taken together, the Controller, the State JSON, the Watcher and Channels, the tactile renderers at The Desk, and the linguistic renderers (alt-text generator, querier, and description-as-authorship) do not constitute a single tool. They constitute a pattern. We name the pattern's five constitutive properties here.

Sense-agnostic state. The canonical design state lives in a JSON file that is sense-agnostic by construction. The state itself privileges no modality; any renderer can be plugged in to consume it.

Renderer parity. The visual viewport, the tactile media, and the CLI and web interfaces all consume the same canonical state. None is privileged over the others; the viewport is one renderer among several rather than the source of truth.

Multiple authoring channels. CLI commands, voice transcribed to CLI, direct JSON edits, and LLM-translated natural-language design intent all reach the same state. The student picks the channel that fits the task.

LLM skill scaffolding. The LLM acts in three coordinated roles: querier (to understand what is in the model), coder (to model and extend it), and tutor (to learn the underlying RhinoPython and Rhino concepts within the system). The same model fills all three roles, scaffolded by Harness prompts that distinguish them.

Auditability. Every authoring action is reversible and inspectable. The State JSON is human-readable and version-controllable; every CLI command and every LLM tool call is logged; the student can replay or audit any session. "Trust but verify" is enforced by the substrate, not just by discipline.

## 5. Implications for Adaptive Studio Practice

The Harness is BLV-specific. The implications we draw from it for studio practice are not necessarily BLV-specific, but they are drawn from a single case and we frame them here as candidate hypotheses for further engagement rather than as a tested portable practice. The reader should treat this section accordingly. The system in Section 4 was built around the absence of the visual surface that the default studio toolchain assumes — the viewport, the GUI panel, the visual confirmation step — and several of its components serve that specific absence. What the BLV case revealed, and what we offer for discussion, is that design authorship in a digital studio does not have to be coupled to any one channel of perception. We name four candidate implications below.

First, an explicit textual design state. The Harness keeps a JSON file as the canonical representation of the design, with the viewport as one renderer among several. This is a useful arrangement for any studio that wants a stable, version-controllable, queryable record of where a design stands,  not only for BLV students. The candidate hypothesis is that studios in which the canonical state is textual will support a wider range of authoring channels (voice, eye-tracking, CLI, direct JSON, natural language) without ad-hoc adaptation. This has not been tested outside the single BLV case we describe.

Second, multi-modal critique. Once the canonical state is sense-agnostic, critique can run through tactile prints, spoken description, and the viewport in parallel rather than treating the pin-up as the privileged forum. We have practiced multi-modal critique in the studio that surrounds the student we worked with, and it has changed how sighted classmates describe their own work. We do not yet have evidence about whether sighted students whose studios do not include a BLV peer would benefit similarly. The candidate hypothesis is that they would, because pin-up critique already under-supports students whose verbal facility runs ahead of their drawing skill or whose drawing skill runs ahead of their verbal facility.

Third, AI-scaffolded verification. The Harness uses an LLM querier to answer natural-language questions about the canonical state, and this querier is the primary verification surface for the BLV student. The same querier is in principle a verification surface for any student who wants to ask a model what is actually in their file. The hypothesis is that AI-scaffolded verification, for example "what did I just do?" "what layer are the columns on?" "what is the square footage of the rooms that were just laid out?”,  will become a standard component of studio toolchains, and that the Harness's particular pattern of grounding the querier in a textual state rather than in a screenshot is the version of this idea that survives.

Fourth, communication protocols designed for access. The studio around the student we worked with developed habits of description, for example "using your words" as a refrain, structured Macro/Meso/Micro alt-text on shared images, written design notes circulated alongside drawings, that began as access workarounds and became, in our experience, useful to the studio more broadly. The candidate hypothesis is that communication protocols designed for access do better than communication protocols retrofitted for access. The supporting evidence is one studio over only four semesters; the broader claim is testable but not yet tested.

We note also that the AI scaffolding pattern at the core of the Harness — LLM as querier, coder, and tutor, mediated by a stable substrate of standards and tool access — is the component we expect to be most portable across access needs. Other populations whose engagement with the default toolchain departs from its assumptions — students with significant learning differences, students with chronic illness whose sessions are short and interrupted, students whose mobility limitations affect authoring, neurodivergent students for whom synchronous studio interaction is exhausting — are populations whose access requirements should be co-designed with them rather than inferred from the BLV case. We name them here as directions for future engagement, not as cases for which we have operational claims. The system described in this paper has been built with and for one student; the practice question that follows is whether studios that have done this for one student more readily do it for the next. (Figure 10 shows the student working with tactile artifacts produced through the Harness.)

> Figure 10: BLV architecture student reading 3D printed braille / english legend along with PIAF swell paper sections and plans.  Part of a “Pop-Up Architectural Graphic Novel” for 2nd Year Undergraduate Design Studio.

## 6. Reflections, Limitations, and Disclosure

This paper makes two contributions. The first is a working accessibility harness for a blind architecture student: a sense-decoupled design state, peer authoring with tactile and linguistic renderers, LLM-scaffolded skill acquisition, and a workstation that holds digital and tactile representations in parity. The second is a position derived from that work: a studio that takes one student's access seriously ends up building infrastructure other studios should adopt anyway — explicit textual design state, multi-modal critique, AI-scaffolded verification, and communication protocols designed for access rather than as an exception to it.

We hope the paper's structure makes the difference between the specificity of the harness and the stance towards openness and accessibility that it allows to be legible: a specific tool, correctly disability-specific, and a portable practice that the BLV case forced the studio to build. Future work will extend the harness to uncover other ways to engage the senses in the production of architecture and design artifacts and experiences.

The authors acknowledge using Claude (Anthropic 2026) for the development of the Accessibility Harness, drafting support, and editorial review during the development of this manuscript. All conceptual contributions, technical implementations, and conclusions remain the authors' own. Code for the Controller, Watcher, and Image-to-Tactile pipeline will be released upon acceptance under an open-source license.

> Figure 11: Snippet of JSON state code and generated plan layouts.

## References

Anthropic. 2024. Model Context Protocol. Specification. https://modelcontextprotocol.io.

Anthropic. 2026. Claude Code. https://www.anthropic.com/claude-code.

Boys, Jos, ed. 2014. Doing Disability Differently: An Alternative Handbook on Architecture, Dis/ability and Designing for Everyday Life. London: Routledge.

Celani, Gabriela, Vinicius Zattera, Maria F. de Oliveira, and Jorge V. L. da Silva. 2013. "'Seeing' with the Hands: Teaching Architecture for the Visually-Impaired with Digitally-Fabricated Scale Models." In CAAD Futures 2013. Shanghai: CAAD Futures.

Chen, Jingcheng. 2025. rhino-mcp: Rhino 3D Integration via the Model Context Protocol. GitHub repository. https://github.com/jingcheng-chen/rhinomcp.

DisOrdinary Architecture Project and The Bartlett (UCL). 2018–22. Architecture Beyond Sight. Program archive and podcast. https://disordinaryarchitecture.co.uk/archive/architecture-beyond-sight.

Ghosh, Soumyaditya, and Shannon Coppola. 2024. "'This Class Isn't Designed For Me…': Experiences of Students with Disabilities in Computing Education." arXiv:2403.15402. https://arxiv.org/abs/2403.15402.

Gipe-Lazarou, Andreas. 2025. "Accessing Architecture: Career Exploration Opportunities for Aspiring Architects with Vision Impairment." Journal of Vocational Behavior. https://www.sciencedirect.com/science/article/pii/S0142694X25000298.

Hamraie, Aimi. 2017. Building Access: Universal Design and the Politics of Disability. Minneapolis: University of Minnesota Press.

Ka, Hyun W., and Rachel Kim. 2024. "RainbowTact: An Automatic Tactile Graphics Translation Technique That Brings the Full Spectrum of Color to the Visually Impaired." In Computers Helping People with Special Needs: 19th International Conference, ICCHP 2024. Lecture Notes in Computer Science. Cham: Springer. https://doi.org/10.1007/978-3-031-62846-7_33.

Kennedy, John M. 1993. Drawing and the Blind: Pictures to Touch. New Haven: Yale University Press.

Khan, Mohammad Sadil, Sankalp Sinha, Talha Uddin Sheikh, Didier Stricker, Sk Aziz Ali, and Muhammad Zeshan Afzal. 2024. "Text2CAD: Generating Sequential CAD Models from Beginner-to-Expert Level Text Prompts." In Advances in Neural Information Processing Systems 37 (NeurIPS 2024). https://arxiv.org/abs/2409.17106.

Kłopotowska, Agnieszka, and Monika Magdziak. 2021. "Typhlographics: Tactile Architectural Drawings — Practical Application and Potential." Sustainability 13 (11): 6216. https://doi.org/10.3390/su13116216.

Li, Jiahao, Weijian Ma, Xueyang Li, Yunzhong Lou, Guichun Zhou, and Xiangdong Zhou. 2025. "CAD-Llama: Leveraging Large Language Models for Computer-Aided Design Parametric 3D Model Generation." In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 18563–73.

Schön, Donald A. 1987. Educating the Reflective Practitioner: Toward a New Design for Teaching and Learning in the Professions. San Francisco: Jossey-Bass.

Wainwright, Oliver. 2019. "Can Blind People Make Great Architects?" The Guardian, September 2, 2019. https://www.theguardian.com/world/2019/sep/02/can-blind-people-make-great-architects.

Wang, Xilin, Jia Zheng, Yuanchao Hu, Hao Zhu, Qian Yu, and Zihan Zhou. 2025. "From 2D CAD Drawings to 3D Parametric Models: A Vision-Language Approach." In Proceedings of the AAAI Conference on Artificial Intelligence 39. https://arxiv.org/abs/2412.11892.

Watanabe, Tetsuya, Toshimitsu Yamaguchi, Susumu Koda, and Kazunori Minatani. 2014. "Tactile Map Automated Creation System Using OpenStreetMap." In Computers Helping People with Special Needs: 14th International Conference, ICCHP 2014. Lecture Notes in Computer Science 8548. Cham: Springer. https://doi.org/10.1007/978-3-319-08599-9_7.

Way, Thomas P., and Kenneth E. Barner. 1997a. "Automatic Visual to Tactile Translation, Part I: Human Factors, Access Methods, and Image Manipulation." IEEE Transactions on Rehabilitation Engineering 5 (1): 81–94.

Way, Thomas P., and Kenneth E. Barner. 1997b. "Automatic Visual to Tactile Translation, Part II: Evaluation of the TACTile Image Creation System." IEEE Transactions on Rehabilitation Engineering 5 (1): 95–105.

Zhang, Zhuohao Jerry, Haichang Li, Chun Meng Yu, Faraz Faruqi, Junan Xie, Gene S-H Kim, Mingming Fan, Angus G. Forbes, Jacob O. Wobbrock, Anhong Guo, and Liang He. 2025. "A11yShape: AI-Assisted 3-D Modeling for Blind and Low-Vision Programmers." In Proceedings of the 27th International ACM SIGACCESS Conference on Computers and Accessibility (ASSETS '25). New York: ACM. https://doi.org/10.1145/3663547.3746362.
