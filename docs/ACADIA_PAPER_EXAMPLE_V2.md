# Teaching Architecture Without Vision: How a Blind Student Exposed the Pedagogy We Thought We Had

**John Clark**, University of Illinois Urbana-Champaign
**[Collaborator Name]**, [Institution]

---

## Abstract

What does architectural education look like when the primary student cannot see? This paper presents Radical Accessible Pedagogy — a framework developed through the experience of teaching Daniel, a blind graduate student in a studio-based architecture program at UIUC. Rather than retrofit existing visual tools with accessibility features, we built a fundamentally different design environment where blindness is the primary case. In doing so, we discovered that the pedagogical principles this environment required — semantic-first spatial reasoning, explicit verbal design dialogue, version-controlled process, and embodied physical-digital fluency — are principles the discipline has long advocated but never operationalized. The paper makes a pedagogical argument: designing for blindness does not merely include one more student. It produces a learning environment whose properties expose the hidden assumptions of visual-first design education and offer a model that is, in specific measurable ways, better for all students. We document Daniel's studio experience across one academic year, describe the tool ecosystem built to support his participation, and argue that the field's long-standing calls for semantic engagement, reflective practice, embodied making, and inclusive collaboration are achievable — but only when blindness is treated as a design condition, not an edge case.

**Keywords:** architectural pedagogy, blind architecture student, inclusive design education, semantic reasoning, reflective practice, embodied design, accessible design tools

---

## 1. Introduction: The Student Who Could Not Look

Daniel arrived in our graduate architecture studio in the fall of 2025. He had strong spatial reasoning, years of experience navigating complex environments, and a keen interest in how buildings organize movement and program. He had one limitation that our entire curriculum treated as disqualifying: he could not see.

This paper is not about how we accommodated Daniel. It is about what Daniel's presence revealed about architectural education itself. Every decision we made to enable his participation — designing tools that work through language instead of vision, making the design process auditable through text, separating the model from any single visual rendering, connecting digital design to physical artifacts he could touch — turned out to articulate a pedagogical principle the discipline has argued for but never consistently practiced.

Architectural educators have called for semantic engagement over form-making (Oxman 2008), reflective practice over routine production (Schon 1983), process as a first-class artifact alongside product (Kalay 2004), embodied making as a mode of design thinking (Sass 2024; Sennett 2008), and genuine collaboration across different working styles (Cuff 1991). These ideas appear in curricula, conference talks, and tenure cases. But the tools we hand students — Rhino, Grasshopper, Revit, the visual-first digital stack — systematically undermine every one of them. The viewport rewards visual manipulation over semantic understanding. Silent visual feedback makes the design conversation implicit and unrecoverable. Crash-prone modeling environments treat process as disposable. And the sighted-user assumption built into every interface makes cross-modal collaboration structurally impossible.

Daniel did not cause these problems. He made them visible. His presence in the studio was, in the language of critical disability studies, a form of revelation: the constraints his blindness imposed on our tools were not new constraints but existing failures that sighted students had learned to work around and that we, as educators, had learned not to see.

This paper presents the pedagogical framework that emerged from teaching Daniel — Radical Accessible Pedagogy — and argues that the framework offers computational design education a model it did not know it needed.

## 2. Background: The Pedagogy Gap

### 2.1 What We Preach

Architectural education scholarship has, for decades, articulated principles that would transform studio culture if they were practiced consistently.

Schon (1983) defined design as a reflective conversation with the situation. The designer makes a move, the situation "talks back," the designer responds. This cycle of action and reflection is the engine of design learning. But in a digital environment where the situation talks back through a silent viewport change — geometry moving on screen — the conversation is invisible. There is no record. The student cannot replay the sequence. The instructor cannot audit it. The reflection, if it happens, is internal and unverifiable.

Piaget and Inhelder (1956) demonstrated that spatial understanding develops from topological (qualitative, relational) to projective (directional, ordered) to metric (measured, coordinate-based). The developmental sequence moves from understanding what things are *next to, inside, connected to* toward understanding where things are in precise coordinate space. Visual CAD inverts this sequence. A student opening Rhino for the first time is immediately in metric space — clicking points, drawing lines at specific coordinates — before developing the topological understanding of what those elements mean spatially.

Sass (2024), in his ACADIA Teaching Award address, argued for fabrication as a mode of design thinking — not fabrication as a final output step but physical making as a cognitive partner in the design process. The ideal is a fluid loop between digital model and physical artifact, where each informs the other. In practice, the loop is broken: students model in Rhino, export to a laser cutter, and produce a physical object that has no pathway back into the digital model. The physical artifact is an endpoint, not a conversation partner.

Cuff (1991) documented that architecture is a fundamentally collaborative practice, yet studio pedagogy treats design as individual production. The tools reinforce this: a Rhino file belongs to one person, displays on one screen, and cannot be meaningfully shared across different working modalities.

These principles are not controversial. No architectural educator would argue against semantic engagement, reflective practice, embodied making, or collaboration. The problem is not the ideas. The problem is the tools.

### 2.2 What Our Tools Enforce

Rhino, Grasshopper, and Revit are not neutral instruments. They are, in Winner's (1980) terms, artifacts with politics — objects that embody social arrangements and enforce particular ways of working. The politics of visual-first CAD include:

**Vision as prerequisite.** Every feedback loop passes through the viewport. There is no non-visual way to confirm that a command produced the intended result. This excludes blind users absolutely, but it also means that *all* design feedback is ambient and implicit. You have to look to know what happened. If you are not looking — if you are thinking about something else, if you are distracted, if the change is subtle — you miss it.

**Geometry before semantics.** The primary mode of interaction is manipulating geometric primitives. Students learn to push points and surfaces before they learn to think about spatial relationships. Grasshopper's visual programming canvas compounds this: the student connects nodes to produce geometry, but the semantic meaning of the geometry — this is a corridor, this is a structural bay, this connects the entrance to the core — lives only in the student's head, not in the tool.

**Process as disposable.** Rhino's undo is a linear stack in volatile memory. Close the file, lose the history. Crash Rhino, lose everything since the last save. There is no branching, no version comparison, no design history. The tool treats the current state as the only state that matters.

**Single-modality output.** The viewport is the canonical representation. Physical models, drawings, and prints are derivative outputs. There is no built-in pathway from a physical artifact back into the digital model.

These are not bugs. They are design decisions — decisions that were made for sighted, mouse-using, screen-watching architects and that happen to contradict the pedagogical principles the field espouses.

### 2.3 What Blindness Reveals

Heylighen and Herssens (2014) studied what architects can learn about space from people who are blind. Their finding was that blind spatial experience is not a deficit version of sighted experience — it is a different form of spatial knowledge that reveals aspects of architecture that sighted people overlook. Blind people attend to acoustic qualities, thermal gradients, tactile textures, and spatial sequences that sighted architects routinely ignore because visual information dominates their perception.

We extend this finding from architecture to architectural *tools*. Daniel's blindness did not create new problems with our CAD environment. It revealed problems that were already there — problems that sighted students navigate by workaround and that educators tolerate because the tools are assumed to be the neutral ground on which pedagogy operates.

When Daniel could not use the viewport, we had to ask: where does design feedback actually come from? When he could not manipulate visual geometry, we had to ask: what is the student really doing when they "design" in CAD? When he could not see a crash recovery dialog, we had to ask: whose work is actually safe? The answers exposed a pedagogy gap — between what we say we value and what our tools actually support — that Daniel's blindness made impossible to ignore.

## 3. Radical Accessible Pedagogy: Six Principles

Radical Accessible Pedagogy is a framework in which the primary design case is non-visual and the student is a co-designer of the learning environment. It rests on six principles. Each was derived from what Daniel concretely needed to participate as a full author in graduate studio. Each articulates a pedagogical commitment that extends well beyond his individual case.

### 3.1 Semantic-First Reasoning

Daniel cannot push geometry around a viewport. He cannot click a point and drag it to a new location. His interaction with the design must begin with language: what is this element, what spatial relationships define it, how does it connect to other elements.

In practice, this means Daniel works with named spatial entities — bays, corridors, walls, apertures, rooms — before any geometry exists. He specifies that Bay A is a six-by-three column grid with 24-foot spacing, that the corridor runs along the y-axis at position 3, that a door is located on the south wall of room C2. Each of these statements is semantic: it names what the element is and where it belongs in an organizational structure.

Cognitive science validates this approach. Millar (1994) demonstrated that spatial cognition is modality-independent when adequate reference frames are provided. Loomis, Klatzky, and Golledge (2001) found that spatial representations built from language function equivalently to those built from direct perception. Giudice (2018) confirmed that blind spatial reasoning operates sequentially, through landmarks and named relationships, rather than through simultaneous visual overview.

But here is the pedagogical discovery: semantic-first reasoning is not just how blind students need to work. It is how all students *should* begin a design. Piaget and Inhelder's developmental sequence — topological before metric — implies that students who jump directly to geometric manipulation are skipping a cognitive step. The sighted student who opens Rhino and starts drawing walls has not yet articulated what those walls organize, what spatial relationships they create, or what programmatic logic they serve. Visual CAD allows this skip. The semantic-first environment does not.

### 3.2 Explicit Design Dialogue

Every command Daniel issues receives a verbal confirmation. When he sets a bay's rotation to 30 degrees, the system responds with a single line confirming the change. When he adds a door, the response confirms the door's position, width, and swing direction. When he makes an error — specifying a gridline that does not exist, setting a dimension to zero — the response explains what went wrong and what the valid options are.

This is Schon's (1983) reflective conversation made literal. The design situation talks back not through a silent viewport change but through explicit verbal feedback that the screen reader announces. The conversation is a transcript. Daniel can review the sequence of commands that led to the current state. He can identify the moment a design decision was made. He can share the transcript with an instructor or collaborator and discuss the reasoning behind specific moves.

Sighted students in visual CAD have no equivalent. The design conversation happens in the private theater of the viewport: the student moves geometry, sees the result, and responds internally. There is no record. The instructor sees only the final state, not the process. Schon's reflective practitioner is an aspiration, not an observable practice.

The explicit dialogue protocol was designed because Daniel's screen reader cannot interpret a silent viewport change. But it creates a pedagogical artifact — the design transcript — that makes reflective practice auditable, shareable, and teachable in ways that visual CAD cannot match.

### 3.3 Recoverable Process

Daniel's design exists as a structured text file — a JSON document containing every parameter of the floor plan. This file is written atomically: the system writes to a temporary file, flushes it to disk, and replaces the original in a single operating system operation. If the process is interrupted at any point, the previous state remains intact.

This was built because Daniel cannot visually confirm that a crash recovery worked. He cannot look at the viewport after a restart and judge whether the model is intact. He needs certainty: the file on disk *is* the design, and no tool failure can corrupt it.

But the implications extend beyond crash safety. When the design is a text file, it can be version-controlled with Git. Students can branch to explore alternatives, revert failed experiments, and compare any two design states through a text diff. They can submit a complete design history — not just a final product — as evidence of their process. Instructors can see not just what the student designed but *how they designed it*: which decisions were made first, which were revised, which were explored and abandoned.

Architecture studios have never had this. The closest equivalent is a sequence of saved Rhino files — v1, v2, v3_final, v3_final_REAL — with no structured relationship between them. The text-based design model, born from accessibility necessity, enables the version-controlled design process that Kalay (2004) argued studios need.

### 3.4 Physical-Digital Fluency

Daniel's primary cognitive interface with spatial organization is touch. He reads floor plans through PIAF swell paper — raised-line tactile drawings produced directly from the design model at 300 DPI, with columns, walls, corridors, room hatches, and Braille labels. He runs his fingers along walls, feels the column grid, traces the corridor from entrance to core. In the other direction, he constructs spatial configurations on a physical pegboard using wire, and a camera digitizes what he built.

This bidirectional flow — digital to physical, physical to digital — was required because Daniel cannot evaluate a design by looking at it. But it realizes the design loop Sass (2024) and Sennett (2008) describe: the hand as a thinking organ, the physical artifact as a cognitive partner, the making as a form of understanding that is different from — not lesser than — visual comprehension.

Sighted students in studio also make physical models. But the models are typically endpoints: a design is completed digitally, then fabricated for presentation. The path back — from physical observation to digital modification — barely exists. Daniel's workflow makes the round trip automatic. He designs in the CLI, prints a tactile plan, evaluates it by touch, identifies something he wants to change, and modifies it through a command. The physical artifact is not a product of the design process; it is an active participant in it.

### 3.5 Mixed-Ability Collaboration

The critical architectural decision — separating the design model from any single viewing modality — was born from a practical problem: Daniel and his sighted classmates needed to work on the same design. Daniel works through text commands and tactile prints. His classmates view the same design in Rhino's viewport. Both are accessing the same authoritative model through different interfaces. Neither interface is primary.

This separation solves a problem that Potluri et al. (2022) identified in software development: mixed-ability collaboration breaks down when one modality is treated as canonical and the other as derivative. If the Rhino viewport were the "real" design and Daniel's CLI were a secondary interface to it, every discrepancy would be resolved in favor of vision, and Daniel's participation would be structurally subordinate. By making the text-based model authoritative and all viewing modalities — CLI, viewport, tactile print — equal projections of it, the tool ecosystem enables collaboration where no one's interface is privileged.

### 3.6 Student as Co-Designer

Daniel is not a test subject. He is a collaborator who shapes the tools weekly. When corridor commands required too many steps, the command structure was simplified. When he needed to understand room areas before partitioning, a new query was added. When verbose output overwhelmed his screen reader, the response format was tightened. His spatial intuitions — honed by years of non-visual navigation — became command structures. His frustrations became bug reports. His workarounds became feature requests.

This is constructionism (Papert 1980) in its deepest form: the student constructing the instrument of his own education. And it enacts Charlton's (1998) disability rights principle — nothing about us without us — not as consultation but as co-design. Daniel's lived experience of blindness is not data we collect; it is expertise we rely on.

## 4. The Tools, Briefly

The six principles are realized through a connected ecosystem. We describe each tool only to the extent needed to show how it embodies the pedagogical commitments above; the technical architecture is secondary to the educational argument.

**The CLI Controller.** A command-line interface where Daniel types architectural commands — setting bay dimensions, activating corridors, placing doors — and receives verbal confirmations through his screen reader. Zero external dependencies. Every command returns a single-line response beginning with OK: or ERROR:. The command vocabulary is architectural, not geometric: students name what they are changing in spatial terms before any geometry is generated. *(Serves: semantic-first reasoning, explicit dialogue.)*

**The Canonical Model Artifact.** A JSON text file containing every design parameter. Human-readable, schema-versioned, diffable. This file *is* the design — not any geometric rendering of it. Evans (1997) argued that architectural drawings are not transparent windows onto buildings but productive instruments that shape what can be designed. The text-based model is a different kind of drawing, one that generates different architectural possibilities. *(Serves: recoverable process, mixed-ability collaboration.)*

**The Viewer.** An IronPython script that watches the model file and rebuilds all geometry in Rhino whenever the file changes. Rhino is a consumer, never a source of truth. If Rhino crashes, nothing is lost — restart it, run the watcher, and everything rebuilds identically from the model file. *(Serves: crash-proof process, mixed-ability collaboration.)*

**The Tactile Pipeline.** Automated rendering from the model file to 300 DPI black-and-white images for PIAF swell paper printing — raised-line drawings with Braille labels that Daniel reads by touch. No Rhino required; renders directly from the semantic model. *(Serves: physical-digital fluency.)*

**The Pegboard.** A physical board where Daniel constructs spatial configurations with wire. An overhead camera digitizes what he builds, closing the loop from physical to digital. *(Serves: physical-digital fluency, the return path.)*

**The AI Integration Layer.** A structured interface that enables conversational queries about the design — "describe the circulation path," "what is the total corridor area," "compare this state to the version I saved yesterday." The AI describes and analyzes; it does not make design decisions. *(Serves: accessibility bridge for studio activities that remain irreducibly visual.)*

**The AI Description Pipeline.** Scene description for physical contexts — site visits via smart glasses, desk crits via viewport analysis. Translates visual information into language Daniel's screen reader can announce. *(Serves: mixed-ability participation in visual studio culture.)*

## 5. What We Learned: Three Pedagogical Discoveries

### 5.1 The Semantic Step Was Always Missing

When Daniel designs, he must articulate spatial relationships in language before geometry exists. He cannot skip this step. Sighted students can — and routinely do. A student in Grasshopper connects nodes and watches geometry appear without ever stating, in words, what the spatial organization is supposed to be.

We have begun asking sighted students to complete the same design tasks in the CLI alongside their visual tools. Preliminary observations suggest that the semantic step — being forced to name what you are designing before you shape it — produces designs with stronger organizational logic and more articulate design rationales. Students who must say "the corridor connects the entrance bay to the service core at the building's midpoint" before any line is drawn develop a spatial argument. Students who draw the corridor first and explain it later often discover, in critique, that they cannot articulate why it is where it is.

This is not a controlled study — it is an observation that warrants one. But the pattern is consistent with Piaget and Inhelder's developmental model: the semantic step, which the CLI enforces and visual CAD allows students to bypass, corresponds to the topological understanding that is supposed to precede metric manipulation.

### 5.2 The Conversation Was Always Silent

Schon's reflective practitioner model assumes that designers notice what the situation "says back." In a visual environment, this means noticing what changed on screen. But noticing is unreliable. Students miss subtle changes. They forget the sequence of moves that led to a state. They cannot explain, in critique, the logic of their process because the process was never recorded.

Daniel's design transcript — the sequence of commands and responses — is a complete record of the design conversation. Every move is documented. Every response is recorded. An instructor can read the transcript and understand not just what the student designed but how they thought about the design.

We did not build the transcript for pedagogical purposes. We built it because Daniel's screen reader needs explicit text output. The pedagogical value was an emergent discovery — a version of the curb cut effect (Pullin 2009) where designing for a specific disability produces tools that turn out to be better for everyone.

### 5.3 The Physical Loop Was Always Broken

Fabrication-centered pedagogy (Sass 2024) values the physical-digital loop. But in practice, the loop is one-directional: digital to physical. Students design in CAD, fabricate models, and bring them to critique. The physical model does not feed back into the digital design because no pathway exists.

Daniel's workflow requires the loop to close. His tactile prints are not presentation artifacts — they are design evaluation tools. He touches the plan, forms judgments about spatial relationships, and modifies the model through CLI commands. The pegboard provides the return path from physical to digital. The loop is complete.

When sighted students observe this workflow — a designer who evaluates by touch and modifies by text — the experience is disorienting. It challenges the assumption that design evaluation requires visual inspection. It demonstrates that spatial judgment operates through the hands as capably as through the eyes. And it models the embodied design loop that fabrication pedagogy advocates, realized in a workflow where the physical artifact is genuinely a thinking medium, not a finished product.

## 6. The Role of AI

This paper's AI contribution requires careful framing. We did not use AI to design architecture. We used an AI-assisted development environment — Claude Code — to build the tool ecosystem that makes Daniel's design participation possible.

A single faculty member cannot build a CLI controller, a JSON schema, a Rhino file watcher, a tactile rendering pipeline, a computer vision system, and an AI description pipeline in one academic year using conventional development methods. The development velocity that AI-assisted coding provides collapsed this from a multi-year funded research project to a system that was deployed in a live graduate studio, iterating on Daniel's feedback weekly.

The distinction matters. Most AI papers at ACADIA 2026 will describe AI systems that generate geometry for designers. Our paper describes an AI system that built tools so a blind designer could generate geometry himself. The AI is in the tool-building loop, not the design loop. Daniel's architectural authorship remains entirely his own.

This positioning is consistent with the project's ethical commitment: Radical Accessible Pedagogy uses AI to expand who can participate in design, not to replace design participation with AI output. The risk identified by Flores-Saviaga et al. (2025) — that AI assistants erode disabled users' agency by being too helpful — is addressed by the CLI's explicit command structure. Every design move is a deliberate action Daniel takes. The AI describes and queries; it never suggests or generates.

## 7. Discussion

### 7.1 Not Accommodation — Revelation

The conventional framing of disability in education is accommodation: identify the student's deficit, provide a workaround, and return the student to the normative workflow with minimal disruption. Radical Accessible Pedagogy rejects this framing. Daniel's blindness is not a deficit to be accommodated. It is a condition that reveals the hidden assumptions of an educational environment that was designed for a specific body — the sighted, mouse-using, screen-watching architect that Hamraie (2017) calls the "normate template."

When we built tools for Daniel, we did not make exceptions to our pedagogy. We operationalized it. The principles we discovered — semantic-first reasoning, explicit dialogue, version-controlled process, embodied making, mixed-ability collaboration — are not accommodations for blindness. They are the principles we already claimed to value, stripped of the visual assumptions that prevented us from practicing them.

### 7.2 The Verification Problem

The computational design field is converging on text-based interfaces to CAD: natural language to geometry (El Hizmi et al. 2024), voice to Grasshopper (Atakan et al. 2025), LLMs mediating design scripting (Rietschel et al. 2024). Every one of these systems assumes the user verifies output visually. What happens when the geometry becomes too complex for visual inspection? When the AI generates hundreds of parametric elements from a single prompt? The verification problem — confirming that generated geometry matches intent — is Daniel's problem today and everyone's problem tomorrow.

Our structured verification system — explicit confirmations, queryable descriptions, automated auditing — was built because Daniel cannot look. But it is the verification infrastructure that text-to-geometry pipelines will eventually need for all users. The blind student's requirements anticipated the field's future needs.

### 7.3 Limitations

This paper reports on one student in one studio. The pedagogical claims — that semantic-first interaction produces richer reasoning, that explicit dialogue makes reflection teachable, that physical-digital fluency deepens understanding — require evaluation with larger populations, including sighted students using the CLI as an alternative or supplement to visual tools.

The tool ecosystem is operational but not complete. The pegboard-to-digital pipeline is a prototype. The AI description system produces variable quality. Sonification — mapping spatial properties to sound — remains unrealized. And the system currently supports floor plan design within the Layout Jig's parametric grammar; extending to more complex architectural programs requires additional development.

## 8. Conclusion

We did not set out to reform architectural pedagogy. We set out to teach one blind student. But the tools we built for Daniel — because he needed semantic interaction, because he needed verbal feedback, because he needed crash-proof files, because he needed physical artifacts he could read — turned out to embody the pedagogy the discipline claims to practice but has never consistently delivered.

Radical Accessible Pedagogy is not about blindness. It is about what blindness makes visible: the gap between the principles we espouse and the tools we use, the silence of our digital feedback systems, the fragility of our design processes, the broken loop between digital and physical, the assumption that spatial knowledge is visual knowledge. Daniel's presence in the studio did not add a problem. It revealed the problems that were already there.

The curb cut effect predicts that designing for the margins improves conditions at the center. If the tools we built for a blind student turn out to produce better pedagogy for all students — and our early observations suggest they do — then the strongest argument for inclusive computational design is not ethical (though it is ethical) or legal (though it is legal) but pedagogical. Designing for blindness makes the teaching better. That is the discovery this paper reports.

---

## References

Atakan, A.O. et al. 2025. "Kakadoo: LLM Enabled Speech Interface for Enhanced Human-Computer Interaction." In *Proceedings of the 43rd eCAADe Conference*, Ankara.

Charlton, J.I. 1998. *Nothing About Us Without Us: Disability Oppression and Empowerment.* Berkeley: University of California Press.

Cuff, D. 1991. *Architecture: The Story of Practice.* Cambridge, MA: MIT Press.

El Hizmi, B. et al. 2024. "LLMto3D: Generating Parametric Objects from Text Prompts." In *Proceedings of ACADIA 2024*, Vol. 1, 157-166.

Evans, R. 1997. *Translations from Drawing to Building and Other Essays.* Cambridge, MA: MIT Press.

Flores-Saviaga, C. et al. 2025. "The Impact of Generative AI Coding Assistants on Developers Who Are Visually Impaired." In *Proceedings of CHI 2025*. ACM.

Giudice, N.A. 2018. "Navigating without Vision: Principles of Blind Spatial Cognition." In *Handbook of Behavioral and Cognitive Geography*. Edward Elgar.

Hamraie, A. 2017. *Building Access: Universal Design and the Politics of Disability.* Minneapolis: University of Minnesota Press.

Heylighen, A. and J. Herssens. 2014. "Designerly Ways of Not Knowing: What Designers Can Learn about Space from People Who Are Blind." *Journal of Urban Design* 19(3): 317-332.

Kalay, Y.E. 2004. *Architecture's New Media: Principles, Theories, and Methods of Computer-Aided Design.* Cambridge, MA: MIT Press.

Loomis, J.M., R.L. Klatzky, and R.G. Golledge. 2001. "Cognitive Mapping and Wayfinding by Adults Without Vision." In *Navigating through Environments*. Springer.

Millar, S. 1994. *Understanding and Representing Space.* Oxford: Oxford University Press.

Oxman, R. 2008. "Digital Architecture as a Challenge for Design Pedagogy: Theory, Knowledge, Models, and Medium." *Design Studies* 29(2): 99-120.

Papert, S. 1980. *Mindstorms: Children, Computers, and Powerful Ideas.* New York: Basic Books.

Piaget, J. and B. Inhelder. 1956. *The Child's Conception of Space.* London: Routledge.

Potluri, V. et al. 2022. "CodeWalk: Facilitating Shared Awareness in Mixed-Ability Collaborative Software Development." In *Proceedings of ASSETS '22*. ACM.

Pullin, G. 2009. *Design Meets Disability.* Cambridge, MA: MIT Press.

Rietschel, M., F. Guo, and K. Steinfeld. 2024. "Mediating Modes of Thought: LLMs for Design Scripting." In *Proceedings of ACADIA 2024*, Calgary.

Sass, L. 2024. ACADIA Teaching Award of Excellence. ACADIA 2024 ("Designing Change"), Calgary.

Schon, D.A. 1983. *The Reflective Practitioner: How Professionals Think in Action.* New York: Basic Books.

Sennett, R. 2008. *The Craftsman.* New Haven: Yale University Press.

Winner, L. 1980. "Do Artifacts Have Politics?" *Daedalus* 109(1): 121-136.
