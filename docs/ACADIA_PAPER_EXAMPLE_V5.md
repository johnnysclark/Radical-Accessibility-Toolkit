# AI Built the Ramp: Why the Most Important AI Contribution to Architecture Is Not a Building

**John Clark**, University of Illinois Urbana-Champaign
**[Collaborator Name]**, [Institution]

---

## Abstract

ACADIA 2026 will feature dozens of papers demonstrating AI systems that generate architectural geometry — floor plans from prompts, parametric models from text, Grasshopper definitions from conversation. This paper presents a different AI contribution. We used Claude Code, an AI-assisted development environment, not to design architecture but to build the accessible design infrastructure that enables a blind graduate student to author parametric floor plans in a live studio setting. The AI generated no geometry. It generated the CLI controller, the JSON schema, the Rhino file watcher, the tactile rendering pipeline, and the integration server that together constitute a complete born-accessible CAD pipeline — developed in one academic year by a single researcher, iterating weekly on the student's feedback. We argue that this represents a category of AI contribution the field has overlooked: AI as infrastructure builder, not form generator. The most important thing AI can do for architecture is not produce buildings. It is demolish the barriers that prevent people from participating in producing buildings. The paper documents the pipeline, analyzes the development process, and makes the case that AI-assisted development — AI building tools rather than buildings — has the potential to transform who architecture includes, at a speed and scale that traditional development cannot match.

**Keywords:** AI-assisted development, Claude Code, accessible CAD, born-accessible design tools, development velocity, inclusive architecture, infrastructure not form

---

## 1. Introduction: The AI Paper You Were Not Expecting

You have read this paper's neighbors in the proceedings. The paper before this one probably used an LLM to generate a floor plan. The paper after it probably used a diffusion model to produce a building massing. Somewhere nearby, a voice-driven Grasshopper plugin is being demonstrated, and a multi-agent system is translating natural language into parametric geometry. AI generates architecture now. It is impressive. It is well-documented. And as of 2026, it is no longer novel.

This paper is not that paper. We did not use AI to generate architecture. We used AI to build the tools that let someone generate architecture who could not do so before.

Daniel is a blind graduate student in the architecture program at UIUC. He cannot see Rhino's viewport, cannot manipulate Grasshopper's visual canvas, cannot click through Revit's dialogs. Until this year, his options for participating in computational design were: have a sighted person operate the software on his behalf, or not participate. Neither option is acceptable. The first eliminates his authorship. The second eliminates his presence.

The Radical Accessibility Project built a different option: a complete CLI-driven design pipeline — command-line controller, JSON state file, Rhino file watcher, tactile output system, AI integration server — that Daniel operates through a screen reader and Braille display. He types commands. The system responds with text his screen reader announces. The state file updates. Rhino rebuilds the geometry for sighted collaborators. A tactile printer produces raised-line plans Daniel reads with his hands. He is a full author in studio.

The entire pipeline was built using Claude Code — an AI-assisted development environment — in one academic year, by one researcher, responding to one student's needs week by week. That is this paper's AI contribution. Not a generated building. A demolished barrier.

## 2. The Field's AI Imagination

### 2.1 What AI Papers at ACADIA Look Like

The landscape of AI research in computational design, circa 2026, has a characteristic shape. The input is language (text prompt, voice command, conversational instruction). The output is geometry (parametric model, Grasshopper definition, CAD sequence). The contribution is the pipeline between them: how the system translates intent into form.

Rietschel, Guo, and Steinfeld (2024) built an LLM-to-JSON-to-Grasshopper pipeline that translates conversational prompts into design scripts. El Hizmi et al. (2024) developed LLMto3D, a multi-agent system where specialized LLMs collaborate to generate parametric objects from text. Khan et al. (2024) demonstrated Text2CAD, the first end-to-end transformer generating parametric CAD sequences from language. Atakan et al. (2025) built Kakadoo, a voice-driven Grasshopper plugin enabling speech-to-geometry workflows. Jones et al. (2025) designed AIDL, a domain-specific language for LLM-driven CAD.

These are impressive systems. They expand the palette of design interaction. They lower the barrier to parametric modeling for designers who do not script. They point toward a future in which the primary design interface is conversational.

But they share an assumption about what AI's contribution to architecture should be: AI generates form. AI produces the artifact. AI is in the design loop, making geometric decisions — or at least translating human decisions into geometric output more efficiently than manual methods.

### 2.2 What This Assumption Misses

The form-generation assumption is not wrong. It is incomplete. It imagines AI's contribution to architecture as occurring within the design process — a better tool for people who are already designing. It does not imagine AI's contribution as occurring *before* the design process — building the infrastructure that determines who can design in the first place.

This matters because the field has a persistent and well-documented inclusion problem. Noel, Boeva, and Dortdivanlioglu (2021) surveyed ACADIA's computational design community and found significant barriers to participation for underrepresented groups. Cupkova et al. (2023) connected AI in architecture to questions of data justice and access. Gissen (2018) documented the structural barriers excluding disabled people from the profession. Crawford et al. (2024) showed that blind users cannot operate standard 3D modeling software.

The people excluded from computational design are not excluded because they lack good form-generation tools. They are excluded because the entire infrastructure — the input methods, the feedback systems, the output modalities, the verification mechanisms — was designed for a specific body and mind. AI that generates better geometry within this infrastructure does not help. AI that rebuilds the infrastructure might.

### 2.3 A Different Category of AI Contribution

We propose a distinction:

**AI-assisted design:** AI participates in the design process, generating or modifying architectural geometry in response to human intent. This is what most ACADIA AI papers describe.

**AI-assisted development:** AI participates in the tool-building process, generating or modifying the software infrastructure through which humans design. This is what we did.

The distinction is not trivial. AI-assisted design asks: how can AI help designers design? AI-assisted development asks: how can AI help researchers build the tools that determine who designs? The first question optimizes within the existing system. The second question changes the system.

## 3. What We Built and How AI Built It

### 3.1 The Pipeline

The Radical Accessibility pipeline consists of seven components:

**The CLI Controller.** A Python 3 command-line application where Daniel authors floor plans. Commands like `set bay A rotation 30`, `corridor A width 8`, `add aperture A d1 door y 0 4 3 7`. Every command returns a single-line confirmation: `OK: Bay A rotation set to 30.0 degrees. READY:` or `ERROR: Gridline index 7 out of range.` Zero external dependencies. Undo stack via deep copy. State persisted via atomic file write after every mutation.

**The Canonical Model Artifact (CMA).** A JSON text file that *is* the design. Schema-versioned, human-readable, diffable. Contains every parameter: bay grids, corridors, walls, apertures, rooms, hatches, labels, Braille text. The CMA is the authoritative representation. Not Rhino, not the CLI, not any rendering.

**The Rhino Watcher.** An IronPython 2.7 script that monitors the CMA for changes and performs a full geometry rebuild in Rhino on every save. Rhino is a disposable viewer. If it crashes, restart it and run the watcher — everything rebuilds from the CMA. The watcher never writes to the state file. Data flows one direction: CLI writes CMA, watcher reads CMA, Rhino displays geometry.

**The Tactile Output Pipeline.** Automated rendering from CMA to 300 DPI black-and-white tactile graphics for PIAF swell paper — raised-line drawings with Braille labels, room hatches, and density checking. No Rhino required. Renders directly from the JSON.

**The Pegboard Input System.** A physical board where Daniel constructs spatial layouts with wire. An overhead camera digitizes wire positions into the model, closing the physical-to-digital loop.

**The MCP Server.** A Model Context Protocol server wrapping the CLI with 21 structured tools, enabling AI agents to read, query, and modify the design through typed function calls. The bridge between the accessibility pipeline and the AI ecosystem.

**The AI Description System.** Scene description for contexts that remain irreducibly visual: pin-up critiques via viewport analysis, site visits via smart glasses, precedent study via image description. AI translates visual information into language Daniel's screen reader announces.

### 3.2 How Claude Code Built It

Claude Code is an AI-assisted development environment — an LLM-powered coding agent that writes, debugs, and maintains code within a defined project context. It is not a code-completion tool that suggests the next line. It is a development partner that understands the project's architecture, constraints, and conventions, and that can generate complete functional modules in response to natural language specifications.

The project defines its constraints in a CLAUDE.md file that Claude Code reads at the start of every session:

- Python stdlib only. Zero pip dependencies.
- IronPython 2.7 compatibility for the Rhino watcher: no f-strings, no pathlib, no Python 3 syntax.
- Screen-reader-friendly output: OK:/ERROR: prefixes, single-line responses, no tables, no progress spinners, no multi-column layouts.
- Atomic file writes: write to .tmp, fsync, os.replace. Never corrupt the state file.
- Schema migration on load: old state files must always open. Never break backward compatibility.

These constraints are non-negotiable. They are accessibility requirements. Claude Code respects them across every code generation task — a consistency that is difficult for a human developer to maintain when switching between two incompatible Python runtimes (3.x for the CLI, 2.7 for the watcher) and dozens of command handlers.

### 3.3 The Development Velocity Argument

A single faculty member cannot build a CLI controller (2,000+ lines), a JSON schema with migration logic, an IronPython Rhino watcher, a 300 DPI tactile renderer, a computer vision pipeline, an MCP server with 21 tools, and an AI description system in one academic year using traditional development methods. This is not a modest claim. It is a statement about the scale of infrastructure required to make one discipline accessible to one excluded person.

The accessibility community knows this problem intimately. Billah et al. (2023) documented how blind people are prevented from creating tactile graphics because the tools are inaccessible. Clepper et al. (2025) found that blind creators are trapped between accessible low-fidelity tools and inaccessible high-fidelity ones. Flores-Saviaga et al. (2025) showed that even AI coding assistants — tools ostensibly meant to help — create new accessibility barriers through suggestion overload and visual interface dependencies. The gap between what disabled people need and what exists is vast, and it persists because building accessible infrastructure is expensive, slow, and chronically underfunded.

Claude Code changes the economics. Not the politics — the economics. The development effort that would traditionally require a multi-year funded research lab with dedicated programmers collapses to something one researcher can build and maintain, iterating on a student's feedback in real time.

Here is what that looks like in practice. Daniel reports on Monday that he needs to know which cells overlap the corridor before he can name rooms. By Wednesday, the `auto_corridor_cells` command exists — implemented, tested, documented, and deployed to his working environment. He reports that the `describe` output is too long for his screen reader to parse efficiently. By the next session, the output is restructured into a multi-level system: a one-line summary by default, a detailed narrative on request, and a machine-readable JSON option for scripting.

This responsiveness is not a nice-to-have. It is the difference between tools that evolve from a disabled student's lived experience and tools that are designed from a researcher's assumptions about that experience. Charlton's (1998) principle — nothing about us without us — requires development velocity that matches the pace of a student's learning. Claude Code provides it.

## 4. Why This Matters More Than Another Floor Plan Generator

### 4.1 The Inclusion Argument

AI-assisted design makes existing designers more productive. AI-assisted development can make the profession larger — can change *who designs*. The difference in impact is categorical.

Consider the state of affairs before this project. Daniel, a graduate student with strong spatial reasoning and genuine architectural ambition, could not participate in computational design. Not because he lacked talent. Not because he lacked motivation. Because the tools assumed he could see, and no one had built alternatives. He was excluded by infrastructure, not by ability.

Now consider how many Daniels exist. The World Health Organization estimates 2.2 billion people worldwide have a vision impairment. The number who might pursue architecture is unknowable because the tools have always excluded them. The pipeline's very nonexistence prevents us from knowing who would use it.

Every text-to-geometry paper at ACADIA makes the implicit promise: "AI will change how we design." We make a different promise: "AI can change who designs." The first promise optimizes existing practice. The second promise expands the discipline. We argue the second is more consequential.

### 4.2 The Velocity Argument

The accessibility infrastructure gap exists not because no one cares but because building accessible tools is hard, slow, and expensive. Siu et al. (2019) built shapeCAD — an accessible 3D modeler combining OpenSCAD with a shape display — over multiple years with dedicated HCI research funding. Siu et al. (2025) extended it to A11yShape with GPT-4o integration. Each system required substantial development effort and addressed one segment of the problem.

AI-assisted development does not replace the expertise these researchers bring. It accelerates their work. The constraints, the design decisions, the accessibility requirements — these still require human judgment, domain knowledge, and intimate collaboration with disabled users. What Claude Code replaces is the mechanical labor of translating those decisions into working code. The researcher focuses on what the tool should do. The AI handles how the tool does it. The iteration cycle shrinks from months to days.

If the accessibility research community adopted AI-assisted development as standard practice, the infrastructure gap would close faster. Not because AI knows what disabled users need — it does not — but because AI collapses the implementation bottleneck between knowing what is needed and having it built.

### 4.3 The Curb Cut Argument

The tools we built for Daniel turn out to be better for sighted users too. The CLI's semantic command vocabulary forces students to articulate spatial logic before manipulating geometry — a pedagogical discipline that visual CAD lacks (Piaget and Inhelder 1956). The CMA's text-based representation enables version-controlled design processes that no visual CAD supports. The crash-only viewer architecture eliminates data loss. The OK:/ERROR: output protocol is machine-parseable in ways that enable automated testing and scripting.

Pullin (2009) documented this pattern: designing for disability drives innovation that benefits everyone. The closed caption becomes the subtitle becomes the search-indexable transcript. The curb cut becomes the universal feature of sidewalk design. The screen-reader-native CLI becomes the scriptable, testable, auditable design interface that every computational designer could use.

The curb cut argument strengthens the case for AI-assisted development of accessible infrastructure. The investment is not charity. It is R&D. The tools produced for the most constrained users generate design patterns that improve the tools for all users. AI-assisted development accelerates this R&D. The return on investment — in inclusion, in pedagogical quality, in technical robustness — exceeds what form-generation research delivers.

### 4.4 The Verification Argument

Every text-to-geometry system at ACADIA assumes visual verification: the user types a prompt, the AI generates geometry, the user looks at the result. What happens when the user cannot look? What happens when the generated geometry is too complex for any human to visually inspect?

Our pipeline solved the verification problem — structured textual confirmation of every operation, queryable spatial descriptions, automated model auditing — because Daniel cannot look at the viewport. But this solution anticipates a problem the entire field will face as AI generates increasingly complex outputs. The verification gap is structural, not incidental. It exists in every text-to-geometry pipeline that assumes a sighted human at the end. And it was solved first by an accessibility project that had no choice but to solve it.

This is the strongest version of the infrastructure argument: **the accessible infrastructure we built with AI contains solutions to problems the form-generation community has not yet recognized it has.** The verification system, the semantic queryability, the automated auditing — these were built for one blind student and will be needed by every designer using AI-generated geometry.

## 5. The Ethics of AI in Accessibility

### 5.1 The Agency Line

AI-assisted development raises a question the project takes seriously: does the AI diminish Daniel's agency? If AI built the tools, and Daniel uses the tools, is Daniel's authorship genuinely his own?

The answer is unambiguous. Claude Code generated the code for the CLI controller, the Rhino watcher, the tactile renderer, and the MCP server. Daniel generated the architectural designs — the floor plans, the spatial organizations, the programmatic layouts — that the tools produce. The AI built the instrument. Daniel plays it. No one questions a pianist's authorship because they did not build the piano.

The ethical line is clear: **AI assists Daniel's access to design, not Daniel's production of design.** Every design move is a deliberate command Daniel types. The AI does not suggest bay rotations, corridor positions, or room arrangements. It does not offer design alternatives. It does not optimize parameters. It built the command-line interface through which Daniel expresses his own spatial intentions. The authorship is his.

### 5.2 The Risk

Flores-Saviaga et al. (2025) documented a real risk: AI coding assistants can overwhelm blind developers with suggestions, creating new accessibility barriers in the name of helpfulness. The project guards against this in the tool design itself. The CLI is deterministic: one command, one response. No suggestions, no auto-completions, no ambient intelligence. Daniel is in control. The tool does what he tells it. The AI that built the tool is not present in the tool itself.

This is an architectural decision as much as an ethical one. The CLI's explicit, deterministic, command-response protocol was designed for screen reader compatibility. It happens to also protect against the agency erosion that well-meaning AI assistants can produce. The accessibility requirement and the ethical requirement converge.

### 5.3 Full Disclosure

This paper discloses the role of AI-assisted development fully and without apology. The tools were built with Claude Code. The paper itself was drafted with AI assistance. The project's CLAUDE.md file — the constraint document that defines the development environment's rules — is publicly available in the project repository. Transparency is a project value, not a concession.

The risk is that reviewers conflate "AI built the tools" with "AI designed the architecture." They are not the same. A researcher who uses a compiler does not share authorship with the compiler's developers. A developer who uses an AI coding assistant does not share authorship with the AI. Daniel, who designs through tools built with AI assistance, is the architect. The AI is the tool-builder's tool. The chain of authorship is clear.

## 6. Discussion: What AI Should Be For

The computational design community's conversation about AI has been dominated by the question: what can AI design? We propose a different question: **what can AI make possible?**

If AI can generate a floor plan from a text prompt, that is a convenience for a sighted designer who could have drawn the floor plan manually. If AI can build the accessible infrastructure that enables a blind student to generate a floor plan at all, that is a transformation in who the discipline includes.

The distinction tracks a larger argument about technology's purpose. Technology that makes existing practitioners more efficient operates within the current system. Technology that changes who can practice operates on the system itself. Both matter. But the second is underrepresented in the ACADIA discourse, which tends to evaluate AI contributions by the impressiveness of the generated form rather than by the inclusiveness of the generating process.

We are not arguing against AI-assisted design. We are arguing that AI-assisted development — AI building tools rather than buildings — is an underrecognized category of contribution that has the potential to transform the discipline's demographics, not just its aesthetics.

### 6.1 Limitations

This paper reports on one tool ecosystem built for one student. The generalizability of the approach — using AI-assisted development to build accessible infrastructure for other disabilities, other design domains, other educational contexts — is asserted but not yet demonstrated. Building accessible tools for motor-impaired users, users with learning disabilities, or users with sensory processing differences would require different constraints, different expertise, and different collaboration.

The development velocity claim is based on one researcher's experience with one AI-assisted development tool. A rigorous evaluation would compare development timelines across multiple projects, multiple developers, and multiple AI assistants.

The curb cut claims — that tools built for Daniel are better for sighted users — are observational. Controlled studies comparing sighted students' design reasoning in the CLI versus visual CAD are planned but not yet completed.

## 7. Conclusion: Build Ramps, Not Renderings

The AI research community in architecture has chosen its question: what can AI design? The question is productive. It has generated impressive results. It will generate more.

But it is not the only question, and it may not be the most important one. The question we pose — what can AI make possible? — leads to a different kind of contribution. Not a generated floor plan but a demolished barrier. Not a parametric optimization but an accessible pipeline. Not a form but an infrastructure.

Daniel designs architecture. He does it through a CLI, a JSON file, a tactile printer, and a screen reader. He does it in the same graduate studio as his sighted classmates, on the same design problems, with the same deadlines. He could not do any of this a year ago — not because he lacked ability but because the tools excluded him.

AI built the ramp. Not the building. The ramp. And the ramp turns out to have properties — semantic richness, explicit feedback, crash resilience, version controllability, multi-modal accessibility — that make it a better path for everyone, not just the person it was built for.

That is the AI contribution this paper reports. It is not the most visually impressive contribution in these proceedings. It is, we argue, among the most consequential. Because the question of who architecture includes is more important than the question of what AI can render. And AI-assisted development — AI building infrastructure rather than form — is how the field begins to answer it.

---

## References

Atakan, A.O. et al. 2025. "Kakadoo: LLM Enabled Speech Interface for Enhanced Human-Computer Interaction." In *Proceedings of the 43rd eCAADe Conference*, Ankara.

Billah, S.M. et al. 2023. "Designing While Blind: Nonvisual Tools and Inclusive Workflows for Tactile Graphic Creation." In *Proceedings of ASSETS '23*. ACM.

Charlton, J.I. 1998. *Nothing About Us Without Us: Disability Oppression and Empowerment.* Berkeley: University of California Press.

Clepper, G. et al. 2025. "'What Would I Want to Make? Probably Everything': Practices and Speculations of Blind and Low Vision Tactile Graphics Creators." In *Proceedings of CHI 2025*. ACM.

Crawford, S. et al. 2024. "Co-designing a 3D-Printed Tactile Campus Map with Blind and Low-Vision University Students." In *Proceedings of ASSETS '24*. ACM.

Cupkova, D. et al. 2023. "AI, Architecture, Accessibility, and Data Justice." *International Journal of Architectural Computing* 21(2).

El Hizmi, B. et al. 2024. "LLMto3D: Generating Parametric Objects from Text Prompts." In *Proceedings of ACADIA 2024*, Vol. 1, 157-166.

Flores-Saviaga, C. et al. 2025. "The Impact of Generative AI Coding Assistants on Developers Who Are Visually Impaired." In *Proceedings of CHI 2025*. ACM.

Gissen, D. 2018. "Why Are There So Few Disabled Architects and Architecture Students?" *The Architect's Newspaper*, June 15.

Jones, B.T. et al. 2025. "AIDL: A Solver-Aided Hierarchical Language for LLM-Driven CAD Design." *Computer Graphics Forum*.

Khan, S. et al. 2024. "Text2CAD: Generating Sequential CAD Designs from Beginner-to-Expert Level Text Prompts." In *Proceedings of NeurIPS 2024*.

Noel, V.A.A., Y. Boeva, and H. Dortdivanlioglu. 2021. "The Question of Access: Toward an Equitable Future of Computational Design." *International Journal of Architectural Computing* 19(4): 496-511.

Piaget, J. and B. Inhelder. 1956. *The Child's Conception of Space.* London: Routledge.

Pullin, G. 2009. *Design Meets Disability.* Cambridge, MA: MIT Press.

Rietschel, M., F. Guo, and K. Steinfeld. 2024. "Mediating Modes of Thought: LLMs for Design Scripting." In *Proceedings of ACADIA 2024*, Calgary.

Siu, A.F. et al. 2019. "shapeCAD: An Accessible 3D Modelling Workflow for the Blind and Visually-Impaired Via 2.5D Shape Displays." In *Proceedings of ASSETS '19*. ACM.

Siu, A. et al. 2025. "A11yShape: AI-Assisted 3-D Modeling for Blind and Low-Vision Programmers." In *Proceedings of ASSETS '25*. ACM.
