# Blindness as Method: What Computational Design Cannot See About Itself

**John Clark**, University of Illinois Urbana-Champaign
**[Collaborator Name]**, [Institution]

---

## Abstract

This paper argues that blindness is not a limitation to be accommodated in computational design education but a methodological lens that produces new knowledge about the discipline's tools, assumptions, and epistemological commitments. We present the Radical Accessibility Project — a tool ecosystem built for Daniel, a blind graduate architecture student at UIUC — and analyze what the process of designing these tools revealed about the hidden structure of visual-first CAD. We identify four knowledge claims that emerged from using blindness as method: (1) that computational design tools encode an epistemology in which spatial knowledge is visual knowledge, structurally excluding non-visual spatial cognition; (2) that the text-to-geometry pipelines currently proliferating in the field all contain an unsolved verification problem that accessibility-first design solves; (3) that the properties tools require for non-visual operation — semantic interaction, explicit feedback, crash-resilient architecture, model-viewer separation — constitute a superior technical paradigm for all users; and (4) that the "curb cut effect" operates at the level of design epistemology, not just design ergonomics. The paper draws on disability studies, philosophy of technology, and cognitive science to frame blindness as a form of disciplinary critique — one that exposes what computational design cannot see about itself precisely because it relies on vision.

**Keywords:** blindness as method, crip technoscience, computational design epistemology, accessible CAD, artifacts and politics, non-visual spatial cognition, verification gap

---

## 1. Introduction: A Methodological Claim

When we set out to build design tools for Daniel — a blind graduate student in architecture at the University of Illinois — we expected to solve an accessibility problem. What we discovered was an epistemological one. Every design decision we made for Daniel's blindness turned out to be a critique of how computational design tools encode assumptions about knowledge, cognition, and the body. The tools we built did not merely include a blind student. They revealed what the field's existing tools structurally exclude, what they assume about how designers think, and what they cannot see about themselves precisely because they were designed by sighted people for sighted people.

This paper advances a methodological argument: blindness, treated not as a deficit to be accommodated but as a primary design constraint, operates as a form of disciplinary critique. It makes visible what is normally invisible — the visual assumptions that permeate computational design from input to feedback to output. It is, in Hamraie and Fritsch's (2019) terms, crip technoscience: disabled experience producing knowledge that non-disabled experience cannot access.

The argument is structured in four parts. We first establish the theoretical frame — how disability studies, philosophy of technology, and cognitive science converge to position blindness as method. We then present four knowledge claims that emerged from building born-accessible CAD tools — claims about epistemology, verification, technical architecture, and the curb cut effect — that could not have been produced by any research program that started with sighted users. We describe the tool ecosystem briefly, as evidence rather than contribution. And we conclude with the implications for a field that is converging on text-based design interfaces without having examined the visual assumptions embedded in the paradigm it is leaving behind or carrying forward.

## 2. Theoretical Frame: Blindness as Epistemic Position

### 2.1 Artifacts Have Politics

Winner (1980) asked whether artifacts have politics — whether designed objects embody social arrangements independent of the intentions of their makers. His answer was yes: the overpasses of Long Island encode racial exclusion; the pneumatic molding machine encodes anti-labor politics. The politics are in the artifact, not in the policy.

Applied to computational design tools, the question becomes: what social arrangements do Rhino, Grasshopper, and Revit encode? The answer is straightforward: they encode the arrangement in which sighted people design buildings and blind people do not. This is not an oversight. It is a structural property of tools whose every feedback loop — viewport rendering, mouse-driven manipulation, visual verification, screen-based output — passes through vision. The tools are not broken for blind users; they were never built for them. The exclusion is architectural, in the precise sense that Winner intended.

Hamraie (2017) extended this analysis through the concept of the "normate template" — the assumed user around whom built environments and tools are designed. In architecture, the normate template is an upright, ambulatory, sighted person. In computational design, it is more specific: a sighted person who uses a mouse, watches a screen, and verifies geometric output through visual inspection. Daniel does none of these things. His exclusion from the tool ecosystem is not a missing feature. It is the normate template made visible.

### 2.2 Crip Technoscience

Hamraie and Fritsch (2019) defined crip technoscience as the practice of disabled people producing knowledge through and about technology — not as test subjects or end users but as knowers and makers. Crip technoscience insists that disabled experience generates epistemic value that non-disabled experience cannot replicate.

Daniel is a crip technoscientist. His experience of blindness is not data we collect about accessibility; it is expertise we rely on for tool design. His spatial reasoning — sequential, landmark-based, language-mediated — is not a limited version of sighted spatial reasoning; it is a different form of spatial cognition that reveals properties of space that visual cognition overlooks (Heylighen and Herssens 2014). His weekly feedback reshapes the tool ecosystem not because we accommodate his needs but because his needs expose design requirements that sighted developers cannot identify from their own experience.

The methodological claim is strong: **some knowledge about computational design tools is only accessible from the epistemic position of blindness.** A sighted researcher can critique visual assumptions in theory. A blind researcher critiques them in practice — by trying to use the tools and discovering, concretely, where they fail and why.

### 2.3 Non-Visual Spatial Cognition

The claim that blindness produces architectural knowledge requires a cognitive foundation. If spatial reasoning were fundamentally visual — if understanding space required seeing it — then blindness would be a genuine limitation, not a methodological lens.

The cognitive science is clear: spatial reasoning does not require vision. Millar (1994, 2008) demonstrated that spatial cognition operates through multiple modalities and that blind individuals develop effective spatial representations when provided with appropriate reference frames and encoding strategies. Loomis, Klatzky, and Golledge (2001) found that spatial representations built from verbal descriptions are functionally equivalent to those built from direct visual experience — people navigate and reason about described spaces with the same accuracy as perceived spaces. Thinus-Blanc and Gaunet (1997) showed that differences in blind spatial performance are attributable to strategy and reference-frame availability, not to fundamental cognitive limitations. Giudice (2018) confirmed that blind spatial cognition is sequential, landmark-based, and language-mediated — different in process from visual cognition but equivalent in outcome.

These findings establish that Daniel's spatial reasoning about architectural floor plans is cognitively valid. But they also do something more: they suggest that the sequential, language-mediated, landmark-based process that Daniel uses might be pedagogically superior for *initial* spatial reasoning in architectural design. Piaget and Inhelder (1956) showed that spatial understanding develops from topological (qualitative relationships) to metric (coordinate-based). Visual CAD drops students directly into metric space. A tool designed for blind spatial cognition starts where spatial understanding starts — with named relationships between things.

## 3. Four Knowledge Claims

### 3.1 Claim One: Computational Design Tools Encode a Visual Epistemology

This is the foundational claim. It is not simply that CAD tools use visual interfaces — obviously they do. The claim is deeper: the tools encode an epistemology in which spatial knowledge is visual knowledge, and this epistemology shapes what designers can think, not just how they work.

Consider the Grasshopper canvas. A student connects nodes to produce geometry. The nodes represent mathematical operations — transformations, divisions, boolean operations. The student sees the geometry update in real time. The feedback is simultaneous, ambient, and visual. What the student does *not* do is name the spatial relationships being created. The corridor is not a "corridor" in Grasshopper; it is a polysurface generated by a loft between two curves. The structural bay is not a "bay"; it is a rectangular grid of points. The semantic content — what the elements *mean* architecturally — exists only in the student's mind. The tool does not require it, record it, or enforce it.

This is an epistemological commitment disguised as an interface choice. The tool says: spatial knowledge is knowledge of geometry. To know a design is to see its shapes. To modify a design is to change its geometry. Meaning — the spatial, programmatic, experiential content — is the designer's private concern, not the tool's business.

When we built tools for Daniel, we were forced to reject this epistemology. Daniel cannot see geometry. He must know the design through its semantic structure — what the elements are, how they relate, what they organize. The tool must carry this semantic content explicitly because there is no viewport to supplement it. Every element has a name, a type, a set of spatial relationships to other elements. Every modification is a statement about architectural intent, not a geometric manipulation.

The discovery: the tool designed for blindness is more semantically rich than the tool designed for vision. The blind user's tool knows what the elements mean. The sighted user's tool knows only what they look like. This is not a minor ergonomic difference. It is an epistemological inversion: the accessible tool carries architectural knowledge that the visual tool discards.

### 3.2 Claim Two: The Verification Gap Is Structural

Between 2022 and 2026, text-based interfaces to CAD became mainstream. Rietschel, Guo, and Steinfeld (2024) built an LLM-to-JSON-to-Grasshopper pipeline. El Hizmi et al. (2024) developed LLMto3D. Khan et al. (2024) demonstrated Text2CAD. Atakan et al. (2025) built a voice-driven Grasshopper plugin. Jones et al. (2025) designed AIDL, a language for LLM-driven CAD that eliminates visual verification for the AI code generator — but not for the human user.

Every one of these systems shares a structural assumption: the human user verifies output by looking at the viewport. Type a prompt, generate geometry, look at the result. The verification step is visual. It is also unscalable. As generative AI produces more geometry from less input, the human's ability to visually verify every element degrades. What happens when an LLM generates 200 parametric objects from a single prompt? The user cannot inspect each one. The verification problem — confirming that generated output matches intent without visual inspection — is unsolved because it was never posed.

We solved it. Not because we were working on verification. Because Daniel cannot look.

Our solution is structural: every operation produces explicit textual confirmation. A `describe` command generates a multi-level spatial narrative — what elements exist, their dimensions, their relationships, their design implications. An `audit` command checks the model against dimensional, accessibility, and structural rules and reports violations in text. A `diff` command compares any two model states and reports what changed. These are not visual inspections translated to text. They are a fundamentally different verification paradigm — queryable, automatable, and exhaustive in ways that visual inspection never is.

The knowledge claim: **the verification problem in text-to-geometry is not a future problem. It is a present problem for blind users that was solved by accessibility-first design.** The solution — structured textual verification — is the architecture that generative design tools will eventually need for everyone. The blind student's requirements anticipated the field's trajectory because the blind student's constraints are the constraints the field is converging toward without realizing it.

### 3.3 Claim Three: The Accessible Architecture Is the Better Architecture

The tool ecosystem we built for Daniel has specific technical properties that were required by accessibility but that constitute a superior paradigm for all users. This is not an abstract argument. It is a concrete comparison.

**Model-viewer separation.** The design model is a text file. Rhino is a disposable viewer that reads the file and renders geometry. If Rhino crashes — and Rhino crashes — nothing is lost. The model on disk is the authoritative representation. In conventional CAD, the model *is* the Rhino file. A crash before saving loses work. A corrupted file loses everything. The accessible architecture is crash-proof by design because a blind user cannot visually confirm crash recovery. The sighted user benefits from the same crash-proofing but never demanded it because they can see the recovery dialog.

**Version-controlled process.** Because the model is a text file, it can be diffed, branched, and version-controlled with standard tools. Two design states can be compared line by line. A student can branch to explore an alternative and merge it back. The entire design history is preserved and navigable. In conventional CAD, "version control" means a folder of numbered files with no structured relationship between them.

**Machine-parseable output.** Every command response follows a strict protocol: `OK:` or `ERROR:` prefix, single line, machine-readable. This was designed for screen readers. It also means every tool response is scriptable, testable, and automatable. No conventional CAD tool has this property because no conventional CAD tool was designed for a user who processes output through software rather than eyes.

**Semantic queryability.** The model can be queried through structured text commands: list all bays, describe all apertures, measure distances between named locations, audit against design rules. This was built because Daniel needs textual access to information sighted users get from a glance. It also means the model is introspectable in ways that geometric models never are — a script can ask "what rooms exist?" and get a structured answer.

Each of these properties was required by blindness. Each is superior to the visual-first alternative. This pattern — accessibility requirements producing better technology for everyone — is the curb cut effect, but it operates at a deeper level than the usual examples suggest.

### 3.4 Claim Four: The Curb Cut Effect Is Epistemological

The standard curb cut narrative (Pullin 2009) is ergonomic: features designed for disabled users — curb cuts, closed captions, voice control — turn out to be convenient for everyone. The argument operates at the level of usability.

Our project suggests the curb cut effect operates at the level of epistemology. Designing for blindness did not just produce more convenient tools. It produced tools that embody a different theory of what it means to know a design — one in which spatial knowledge is semantic, feedback is explicit, process is recoverable, and physical artifacts are cognitive partners, not derivative outputs.

This epistemological curb cut has specific implications for computational design pedagogy. Schon's (1983) reflective practitioner model — the canonical framework for design education — assumes the designer notices the situation's "talk-back." In visual CAD, the talk-back is silent: viewport changes that the student may or may not notice. In the accessible tool, the talk-back is explicit: a verbal response that the screen reader announces and the transcript records. The accessible tool does not just make reflection easier. It makes reflection auditable — and therefore teachable. The instructor can review the student's design conversation, identify moments where the situation talked back and the student responded or failed to respond, and provide feedback on the reflective process itself.

This is not a convenience improvement. It is a different pedagogical possibility — one that exists only because we designed for a user who cannot see silent viewport changes. The curb cut effect, in this case, is not "this is also useful for sighted students." It is: "this reveals a form of pedagogy that was invisible as long as we assumed design feedback was visual."

## 4. The Tool Ecosystem as Evidence

The tools are described here as evidence for the knowledge claims, not as the paper's primary contribution. The contribution is the methodological argument — that blindness produces knowledge about computational design. The tools are what that knowledge looks like when materialized.

The ecosystem consists of seven components: a command-line controller for authoring floor plans through text commands; a JSON canonical model artifact that *is* the design; a Rhino file watcher that renders the model as geometry; a tactile output pipeline for PIAF swell paper prints; a pegboard with computer vision for physical-to-digital input; a Model Context Protocol server for AI agent integration; and an AI description pipeline for translating visual information into language.

The entire ecosystem was built using Claude Code, an AI-assisted development environment, within a single academic year. This is a methodological claim about AI as well: the AI did not generate architecture; it generated the infrastructure that enables a blind student to generate architecture. The development velocity AI-assisted coding provides transforms what was previously a multi-year funded research project into a system responsive enough to iterate on a student's weekly feedback. AI is in the tool-building loop, not the design loop. Daniel's authorship is his own.

The tools are Python 3 with zero external dependencies on the controller side and IronPython 2.7 for the Rhino watcher — two incompatible Python runtimes bridged by a shared text file. This architectural constraint was imposed by Rhino's scripting environment, but it produced the model-viewer separation that turns out to be the system's most valuable property. Constraints — technological, cognitive, perceptual — are not obstacles to good design. They are the conditions under which good design is discovered.

## 5. Implications for the Field

### 5.1 The Text-to-Geometry Convergence

The ACADIA community is moving toward text-based design interfaces. Prompts replace clicks. Language replaces mouse gestures. LLMs mediate between human intent and parametric output. This convergence is presented as a revolution. It is, in one respect: it changes how designers communicate with tools. But in another respect, it preserves the visual epistemology intact. The user types a prompt, the AI generates geometry, and the user *looks at the viewport to verify the result.* The output modality has not changed. The verification assumption has not changed. The normate template — the sighted user watching a screen — has not changed.

Our project arrived at a text-based design interface through a different motivation — not convenience, but necessity. And because necessity demanded a non-visual verification system, we solved a problem the text-to-geometry community has not yet recognized it has. As generative AI produces increasingly complex outputs, the assumption that a human can visually verify everything will break. The structured verification paradigm we built for Daniel — explicit confirmation, queryable description, automated audit — is where the field will eventually arrive. It will arrive there faster if it examines the assumptions blindness makes visible.

### 5.2 Born-Accessible as Design Methodology

Seo et al. (2024) introduced the term "born-accessible" for educational environments designed from the ground up for blind learners. We extend the term to a design methodology: born-accessible development is the practice of taking the most constrained user as the primary case and discovering, through the constraints they impose, design principles that improve the system for all users.

This is stronger than universal design (Mace 1985), which seeks to produce products usable by the widest range of people. Born-accessible development does not seek to serve everyone equally. It seeks to serve the most excluded user first and discovers — through the curb cut effect operating at the epistemological level — that the resulting design is different, not just broader. The semantic richness, the explicit feedback, the crash-proof architecture, the version-controlled process — these are not features that accommodate a wider range of users. They are a different paradigm that emerged from a specific constraint.

### 5.3 Gissen's Challenge

Gissen (2022) argued that disability in architecture must move beyond access — beyond ramps, elevators, and compliance — to the level of architectural knowledge. Disability should not just change who enters the building; it should change what the building is.

We apply this argument to computational design tools. The Radical Accessibility Project does not make Rhino accessible. It replaces the epistemological assumptions that Rhino embodies — visual knowledge, geometric primacy, viewport-based verification — with different assumptions: semantic knowledge, textual primacy, structured verification. The result is not an accessible version of existing tools. It is a different kind of tool that exists because a blind architecture student required it and that reveals, through its differences, what the existing tools assumed and enforced without acknowledgment.

### 5.4 Limitations

Blindness as method is powerful but partial. It illuminates the visual assumptions of CAD tools. It does not illuminate assumptions about manual dexterity (relevant for motor-impaired users), cognitive processing speed (relevant for users with learning disabilities), or sensory processing (relevant for users with sensory integration differences). A comprehensive crip technoscience of computational design would apply multiple disability lenses, each revealing different assumptions.

This paper reports on one student. The epistemological claims are grounded in that student's experience and validated by cognitive science and disability studies. But the pedagogical implications — that semantic-first tools produce better reasoning, that explicit feedback makes reflection teachable, that version-controlled process enables design branching — require broader evaluation with both blind and sighted students.

The tool ecosystem is operational in one domain: parametric floor plan design within the Layout Jig grammar. Extending the methodology to other architectural design domains — massing studies, structural analysis, environmental simulation — is future work that will test whether the knowledge claims generalize.

## 6. Conclusion: What We Cannot See

Every field has blind spots — assumptions so deeply embedded that they are invisible from within. The visual assumptions of computational design are, paradoxically, the hardest to see because seeing is the very faculty they privilege. A discipline built on vision cannot easily perceive the consequences of that dependency. It takes someone who cannot see to show the rest of us what we are not seeing.

Daniel's blindness did not create a problem for our tools. It revealed the problems that were always there: tools that discard semantic content, feedback that is silent and unrecoverable, processes that do not survive their own failures, physical artifacts that are endpoints rather than thinking media. These are not accessibility problems. They are design problems — problems of epistemology, pedagogy, and technical architecture that the field has tolerated because sighted users work around them and sighted designers do not notice them.

Blindness as method does not argue that blind users should design architecture. That argument is made simply by the fact that Daniel does. Blindness as method argues that the epistemic position of blindness — the experience of navigating a world designed for vision — produces knowledge about that world's design that vision itself cannot access. The tool ecosystem we built is evidence. The pedagogical principles it embodies — semantic-first reasoning, explicit reflective dialogue, recoverable process, embodied making — are the curb cut at the epistemological level: discoveries that emerged from the constraint of blindness and that benefit the discipline regardless of who can see.

What computational design cannot see about itself is what blindness reveals. That is both the irony and the contribution of this paper.

---

## References

Atakan, A.O. et al. 2025. "Kakadoo: LLM Enabled Speech Interface for Enhanced Human-Computer Interaction." In *Proceedings of the 43rd eCAADe Conference*, Ankara.

El Hizmi, B. et al. 2024. "LLMto3D: Generating Parametric Objects from Text Prompts." In *Proceedings of ACADIA 2024*, Vol. 1, 157-166.

Giudice, N.A. 2018. "Navigating without Vision: Principles of Blind Spatial Cognition." In *Handbook of Behavioral and Cognitive Geography*. Edward Elgar.

Gissen, D. 2022. *The Architecture of Disability: Buildings, Cities, and Landscapes beyond Access.* Minneapolis: University of Minnesota Press.

Hamraie, A. 2017. *Building Access: Universal Design and the Politics of Disability.* Minneapolis: University of Minnesota Press.

Hamraie, A. and K. Fritsch. 2019. "Crip Technoscience Manifesto." *Catalyst: Feminism, Theory, Technoscience* 5(1).

Heylighen, A. and J. Herssens. 2014. "Designerly Ways of Not Knowing: What Designers Can Learn about Space from People Who Are Blind." *Journal of Urban Design* 19(3): 317-332.

Jay, M. 1993. *Downcast Eyes: The Denigration of Vision in Twentieth-Century French Thought.* Berkeley: University of California Press.

Jones, B.T. et al. 2025. "AIDL: A Solver-Aided Hierarchical Language for LLM-Driven CAD Design." *Computer Graphics Forum*.

Khan, S. et al. 2024. "Text2CAD: Generating Sequential CAD Designs from Beginner-to-Expert Level Text Prompts." In *Proceedings of NeurIPS 2024*.

Loomis, J.M., R.L. Klatzky, and R.G. Golledge. 2001. "Cognitive Mapping and Wayfinding by Adults Without Vision." In *Navigating through Environments*. Springer.

Mace, R.L. 1985. "Universal Design: Barrier Free Environments for Everyone." *Designers West* 33(1).

Millar, S. 1994. *Understanding and Representing Space.* Oxford: Oxford University Press.

Millar, S. 2008. *Space and Sense.* Hove: Psychology Press.

Pallasmaa, J. 2005. *The Eyes of the Skin: Architecture and the Senses.* 2nd ed. Chichester: Wiley.

Piaget, J. and B. Inhelder. 1956. *The Child's Conception of Space.* London: Routledge.

Pullin, G. 2009. *Design Meets Disability.* Cambridge, MA: MIT Press.

Rietschel, M., F. Guo, and K. Steinfeld. 2024. "Mediating Modes of Thought: LLMs for Design Scripting." In *Proceedings of ACADIA 2024*, Calgary.

Schon, D.A. 1983. *The Reflective Practitioner: How Professionals Think in Action.* New York: Basic Books.

Seo, J.Y. et al. 2024. "Designing Born-Accessible Courses in Data Science and Visualization." In *Eurographics / IEEE VGTC Conference on Visualization*.

Thinus-Blanc, C. and F. Gaunet. 1997. "Representation of Space in Blind Persons: Vision as a Spatial Sense?" *Psychological Bulletin* 121(1): 20-42.

Winner, L. 1980. "Do Artifacts Have Politics?" *Daedalus* 109(1): 121-136.
