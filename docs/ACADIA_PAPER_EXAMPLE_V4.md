# The Model Is Not the Viewport: Architectural Notation After Vision

**John Clark**, University of Illinois Urbana-Champaign
**[Collaborator Name]**, [Institution]

---

## Abstract

Robin Evans proved that architectural drawings are not transparent representations of buildings but productive instruments that shape what can be designed. Mario Carpo argued that the shift from identical drawing to algorithmic notation transforms the relationship between representation and production. This paper extends their arguments into a domain neither anticipated: what happens to architectural notation when the designer cannot see the drawing? We present the Canonical Model Artifact (CMA) — a structured JSON text file that serves as the authoritative architectural representation in a tool ecosystem built for Daniel, a blind graduate architecture student at UIUC. The CMA is not a drawing in any conventional sense. It is a semantic notation: a structured text that names bays, corridors, walls, rooms, and their relationships without rendering them visually. It is read by screen readers, queried through typed commands, diffed through version control, and rendered into multiple modalities — Rhino viewport, tactile swell paper, Braille labels, spoken description — none of which is primary. We argue that the CMA constitutes a new kind of architectural notation, one that is post-visual not by ideology but by necessity, and that this notation produces specific architectural possibilities that viewport-based representation forecloses. The paper examines what representation theory means when the drawing is a text file, what design cognition looks like when the primary medium is language, and what the field's convergence on text-to-geometry interfaces might learn from a notation system that was born without vision.

**Keywords:** architectural notation, representation theory, canonical model artifact, post-visual drawing, Robin Evans, Mario Carpo, blind architecture, text-based CAD

---

## 1. Introduction: The Drawing That Is Not a Drawing

Architectural representation has a problem it has not noticed. The discipline's most sophisticated theoretical framework — Evans's (1997) argument that drawings are not passive records but active instruments that shape what can be designed — has been developed entirely within the domain of visual media. Evans analyzed orthographic projection, axonometric drawing, and perspective. Carpo (2011) extended the analysis to algorithmic notation and parametric scripts. Oxman (2006) mapped the shift from representation-of to representation-for in digital design. In every case, the representation is something to be looked at — a visual artifact addressed to a seeing eye.

What happens to representation theory when the designer cannot look?

This paper presents the Canonical Model Artifact — a JSON text file that serves as the authoritative representation of an architectural design in a tool ecosystem built for Daniel, a blind graduate student in architecture at UIUC. The CMA is not drawn, rendered, or displayed. It is typed, queried, read aloud by a screen reader, explored through Braille, and rendered into multiple output modalities — none of which is the "real" drawing. The CMA is the drawing. And it is a text file.

This is not an accommodation story. It is a representation theory story. The CMA exists because Daniel cannot see a viewport. But its properties — semantic structure, modality independence, version controllability, queryability — constitute a kind of architectural notation that Evans's framework predicts but that no one has built from visual-first premises. It took a blind student to produce the notation that representation theory implies.

## 2. Representation Theory: From Evans to the Viewport

### 2.1 Evans: Drawings as Productive Instruments

Evans's (1997) central argument in *Translations from Drawing to Building* is that architectural drawings do not passively represent buildings. They actively produce them. The drawing is not a window through which the architect sees the future building; it is an instrument that shapes what the building can be. Different drawing systems — plan, section, perspective, axonometric — produce different architectural possibilities because each system foregrounds certain spatial relationships and suppresses others.

The plan foregrounds horizontal organization and suppresses vertical experience. The section foregrounds enclosure and suppresses circulation. The perspective foregrounds the view from a fixed point and suppresses the spatial structure that generates the view. The architect who works in plan thinks different thoughts than the architect who works in section — not because they choose to but because the drawing system constrains what can be thought.

Evans's argument has been deeply influential. But it has been applied almost exclusively to visual media. The drawing systems Evans analyzed are all things to look at. The spatial relationships they foreground and suppress are all relationships visible from a particular vantage point. The theory assumes a seeing eye.

### 2.2 Carpo: From Identical to Differential

Carpo (2011) identified a shift in architectural notation from the identical — the repeatable drawing, the printed plan, the engraved elevation — to the differential: the parametric script, the algorithm, the code that specifies not a single design but a family of possible designs. In Carpo's account, the shift from drawing to script changes the architect's relationship to the design: instead of specifying a form, the architect specifies the rules that generate forms.

This shift is relevant to our argument because it moves architectural notation from the visual (a drawing of a building) toward the textual (a script that generates buildings). But Carpo's scripts still produce visual output. The parametric model is evaluated in the viewport. The script is the notation; the viewport is the reading. The eye remains the final arbiter.

### 2.3 The Viewport as Unmarked Assumption

In the digital design stack — Rhino, Grasshopper, Revit, and their descendants — the viewport has become the unmarked assumption of architectural representation. "Unmarked" in the linguistic sense: it is the default condition that goes without saying. No computational design paper justifies the viewport. No tutorial explains why the primary feedback mechanism is visual. The viewport is simply there, the ground on which everything else stands.

But the viewport is not neutral. It is a representational system with the same productive properties Evans identified in the plan and section. The viewport foregrounds geometric form and suppresses semantic content. A wall in the Rhino viewport is a polysurface with vertices, edges, and faces. It is not "the north wall of the circulation corridor connecting the entrance bay to the service core." The semantic content — what the element *is* in architectural terms — exists only in the designer's mind. The viewport does not record it, require it, or enforce it.

The viewport also foregrounds the current state and suppresses process. You see what the design looks like now. You do not see how it got there, what alternatives were considered, or which decisions were revised. The viewport is a snapshot, not a history.

These are representational choices. They produce specific architectural possibilities and foreclose others. And they are invisible precisely because the viewport is unmarked — because no one questions the assumption that the primary medium of architectural representation is a geometric image displayed on a screen.

## 3. The Canonical Model Artifact: A Post-Visual Notation

### 3.1 What the CMA Is

The Canonical Model Artifact is a JSON text file. It contains structured data describing every element of an architectural floor plan: site dimensions, bay configurations (grid type, column spacing, origin, rotation), wall properties (enabled, thickness), corridor settings (axis, position, width, loading type), apertures (doors, windows, portals with position, size, hinge, swing), room names, hatch patterns, Braille labels, style parameters, and metadata.

A representative fragment:

```
"A": {
  "grid_type": "rectangular",
  "origin": [0, 0],
  "rotation_deg": 30,
  "num_bays_x": 6,
  "num_bays_y": 3,
  "spacing_x": [24, 24, 24, 24, 24, 24],
  "spacing_y": [24, 24, 24],
  "walls": { "enabled": true, "thickness": 0.5 },
  "corridor": { "enabled": true, "axis": "y", "position": 2, "width": 8 }
}
```

This is not a drawing. It is a structured description. It names spatial entities ("bay A"), specifies their properties (six-by-three grid, 24-foot spacing, rotated 30 degrees), and declares their relationships (the corridor runs along the y-axis at gridline 2). No geometry is present. No visual form is specified. The CMA describes what the design *is* — semantically, organizationally, architecturally — without showing what it *looks like*.

### 3.2 How the CMA Is Read

Daniel reads the CMA through multiple modalities, none of which is visual:

**Text commands.** He types `describe` and receives a multi-paragraph narrative of the design's spatial organization — what bays exist, how they are positioned relative to each other, what corridors connect them, how many rooms are named. He types `list bays` and receives a structured summary of each bay's properties. He types `audit` and receives a report of dimensional violations, accessibility non-compliance, and structural issues.

**Screen reader.** Every command produces a single-line confirmation that his NVDA screen reader announces: "OK: Bay A rotation set to 30 degrees." The design conversation is literally spoken — the screen reader is the voice of the notation system.

**Braille display.** Daniel can read the JSON file directly on his refreshable Braille display, parsing the structured text character by character. The two-space indentation, stable key names, and consistent formatting were designed for this kind of sequential reading.

**Tactile print.** The CMA renders to 300 DPI black-and-white tactile graphics for PIAF swell paper — raised-line drawings with columns as dots, walls as thick lines, corridors as dashed centerlines, room hatches as patterns, and labels in Braille. Daniel reads these with his hands.

**Spoken description.** Through the AI integration layer, Daniel can request natural language descriptions at multiple levels of detail: what elements exist, their dimensions, their spatial relationships, and their design implications.

No modality is primary. The CMA is the authoritative representation. Every reading — text command, screen reader, Braille, tactile print, spoken description, and also the Rhino viewport that sighted collaborators use — is a projection of the same underlying notation. Evans argued that different drawing systems produce different architectural thoughts. The CMA produces multiple simultaneous readings, each foregrounding different spatial relationships, and the designer moves between them.

### 3.3 How the CMA Is Written

Daniel authors the CMA through typed commands: `set bay A bays 6 3` (establish a grid), `set bay A rotation 30` (orient it), `corridor A on` (activate circulation), `add aperture A d1 door y 0 4 3 7` (place a door). Each command names what is being changed in architectural terms. The command vocabulary is semantic — bays, corridors, walls, apertures, rooms — not geometric. Points, lines, and surfaces do not appear.

This is Evans's productive instrument operating in a different register. The plan drawing produces architectural thoughts organized by horizontal projection. The CMA produces architectural thoughts organized by semantic structure — by what things are called, how they relate, and what they organize. A designer working in the CMA thinks: "Bay A is a 6x3 structural grid, oriented 30 degrees, with a corridor along the second transverse axis." A designer working in Rhino's viewport thinks: "These lines form a rotated rectangle with subdivisions." The same design, different cognitive engagements — exactly the phenomenon Evans documented for plan versus section.

## 4. What the CMA Foregrounds and Suppresses

Every notation system has this double action: it makes some things visible (or in this case, sayable) and renders others invisible (or unsayable). The CMA is no exception.

### 4.1 What the CMA Foregrounds

**Organizational logic.** The CMA's vocabulary is architectural: bays, corridors, rooms. Working in this notation means working at the level of spatial organization before geometric form. The designer must decide that there is a corridor, that it connects specific bays, that it runs in a specific direction, before any line is drawn anywhere. This organizational logic is foregrounded because the notation requires it — there is no way to draw a line without first declaring what it is part of.

**Spatial relationships.** The CMA specifies relationships explicitly: bay A is at origin [0,0], bay B is at [120, 0], the corridor connects them along the x-axis. These relationships are declared, not inferred from visual proximity. In a viewport, two bays that happen to be near each other might or might not be related — the designer knows, but the drawing does not. In the CMA, relationships are structural.

**Design process.** Because the CMA is a text file, every version can be saved, diffed, and compared. The process of design — which decisions were made first, which were revised, which alternatives were explored — is preserved in the sequence of file states. The notation records history. A viewport does not.

**Multi-modal accessibility.** The CMA can be projected into any modality: visual geometry, tactile graphics, spoken language, Braille text. No projection is privileged. This is a representational property that no visual notation has: the ability to serve multiple sensory modalities without designating any as primary.

### 4.2 What the CMA Suppresses

**Geometric subtlety.** The CMA's parametric grammar is constrained. It describes rectilinear and radial column grids, straight corridors, and orthogonal rooms. Freeform curves, complex surfaces, and non-orthogonal intersections are outside its current vocabulary. The notation cannot say what it has no words for — a limitation Evans would recognize from his analysis of how orthographic projection suppresses the spatial qualities that perspective reveals.

**Visual composition.** The CMA does not represent how the design looks. It represents what the design is. The aesthetic dimension of visual composition — proportions visible from a vantage point, the play of light and shadow, the graphic qualities of a rendered plan — is absent because the notation is addressed to understanding, not to seeing.

**Ambient spatial quality.** The phenomenological experience of space — the qualities Pallasmaa (2005) and Zumthor (2006) describe, the feel of enclosure, the sense of threshold, the drama of arrival — is outside the CMA's semantic register. The notation is organizational, not experiential. This is a real limitation, though one shared by most computational design representations.

These suppressions are not failures. They are the costs of what the notation foregrounds. Every drawing system makes this trade. The plan suppresses section; the perspective suppresses structure; the CMA suppresses visual form to foreground semantic organization. The question is whether the trade is worth it.

## 5. The Productive Properties of Post-Visual Notation

### 5.1 Enforced Semantic Engagement

Piaget and Inhelder (1956) demonstrated that spatial understanding develops from topological (qualitative relationships) to metric (coordinate-based). Visual CAD drops students into metric space immediately — clicking points at specific coordinates. The CMA drops students into semantic space — naming bays and corridors and specifying their relationships — before any coordinates are relevant.

This is a productive property of the notation. Students working in the CMA must articulate the organizational logic of their design before they see (or touch, or hear) its geometric consequences. The notation forces the articulation. The cognitive science (Millar 1994; Loomis et al. 2001; Giudice 2018) confirms that this sequential, language-mediated approach to spatial reasoning is not merely how blind people must work — it is how spatial cognition builds from foundations.

### 5.2 Auditable Design Conversation

Schon (1983) described design as a reflective conversation with the situation. In visual CAD, the situation talks back through silent viewport changes. In the CMA ecosystem, the situation talks back through explicit text: "OK: Bay A rotation set to 30 degrees. READY:" The conversation is literal and recorded. Every command and every response is a transcript entry.

Evans noted that architectural drawings produce design knowledge through the act of translation — from concept to drawing, from drawing to building. The CMA adds a translation that Evans did not consider: from typed command to textual response. The designer types an intention ("set bay A rotation 30"), the notation system translates it into state change, and the system reports back what happened. This translation loop is auditable in ways that the visual loop (move the mouse, see the geometry change) is not.

### 5.3 Notation as Collaboration Medium

The CMA's modality independence enables a form of collaboration that visual notation structurally prevents. Daniel works through text commands and tactile prints. His sighted classmate views the same model in Rhino's viewport. Both are reading the same notation through different projections. Neither projection is authoritative.

Evans argued that different drawing systems produce incommensurable architectural thoughts — plan-thinking and section-thinking are genuinely different cognitive modes. The CMA suggests a different possibility: a single notation that supports commensurable readings across different sensory modalities. The text reading and the visual reading and the tactile reading are all valid interpretations of the same semantic structure. This is not a property any visual notation possesses, because visual notation presupposes a shared sensory modality.

### 5.4 Version-Controlled Notation

Because the CMA is a text file, it is diffable. Two design states can be compared line by line: "rotation changed from 30 to 45 degrees; door d1 moved from gridline 2 to gridline 3; room C2 renamed from 'storage' to 'seminar.'" The notation records not just what the design is but what changed between any two states.

No visual notation has this property. Two Rhino files cannot be meaningfully compared without opening them side by side and visually scanning for differences. Two CMAs can be compared computationally, automatically, exhaustively. The notation system that was designed for a blind user — who cannot visually compare two viewports — turns out to be the first architectural notation that supports computational design history.

## 6. The Text-to-Geometry Field and Its Missing Theory

The ACADIA community is converging on text-based design interfaces. Rietschel, Guo, and Steinfeld (2024) translate natural language to Grasshopper. El Hizmi et al. (2024) generate parametric objects from text prompts. Khan et al. (2024) produce CAD sequences from language. Atakan et al. (2025) enable voice-driven design. These systems share a direction: from text to geometry, from language to form.

But they lack a theory of the notation they are creating. None of these papers engages with Evans or Carpo. None asks what the text prompt *is* as a representational instrument — what it foregrounds, what it suppresses, what architectural thoughts it makes possible and impossible. The text prompt is treated as a transparent instruction, not a productive medium. The viewport remains the unmarked assumption: the user types, the system generates, and the user *looks.*

The CMA offers this field a missing theoretical foundation. It demonstrates what a text-based architectural notation looks like when it is taken seriously as a representational system — not as a convenience layer over visual output but as an autonomous notation with its own productive properties. The CMA's semantic vocabulary, its explicit feedback loop, its version controllability, and its modality independence are properties of a notation system that was *designed* as text, not properties of a visual system that accepts text input.

The text-to-geometry community is building text-to-visual pipelines. The CMA is a text-to-semantics notation that can project into any modality, including visual. The difference is not cosmetic. It is the difference between treating text as input and treating text as the drawing itself.

## 7. AI-Assisted Development: Building the Notation

The CMA and its surrounding tool ecosystem — CLI controller, Rhino file watcher, tactile rendering pipeline, AI description system, MCP integration server — were built by a single researcher using Claude Code as the primary development environment. The development velocity AI-assisted coding provides was essential: the system iterates on a blind student's weekly feedback, adding new query commands, refining output formatting, and extending the parametric grammar in response to studio needs.

The AI role is precise and limited. Claude Code writes the code that implements the notation system. It does not author designs within that system. Daniel's architectural decisions — where to place the corridor, how to orient the bay, which rooms to name — remain his own. The AI built the instrument; the student plays it. This distinction — AI in the tool-building loop, not the design loop — is the project's AI contribution, and it is a deliberately modest one. In a field where AI papers compete to demonstrate the most impressive geometry generation, we argue that the most consequential AI contribution is not a new form but a new notation — built at AI-assisted development speed, deployed for a student the field had excluded.

## 8. Discussion

### 8.1 Evans Without Vision

Evans did not anticipate the CMA. His analysis was rooted in visual media — the productive properties of plan, section, axonometric, perspective. But his theoretical framework — that drawings are instruments that shape what can be designed, that different drawing systems produce different architectural thoughts — extends naturally to non-visual notation.

The CMA is, in Evans's terms, a translation system. It translates between typed commands (intent) and structured text (state) and multiple output modalities (readings). Each translation produces knowledge. The designer who types `set bay A rotation 30` and hears "OK: Bay A rotation set to 30 degrees" has completed a design move through an entirely linguistic translation — intent to command to confirmation. The spatial knowledge produced by this translation is different from the knowledge produced by dragging a rectangle in a viewport. It is semantic rather than geometric, explicit rather than ambient, recorded rather than ephemeral.

### 8.2 Carpo After the Screen

Carpo's (2011) distinction between identical and differential notation — between the fixed drawing and the parametric script — maps onto the CMA in unexpected ways. The CMA is differential: it specifies parameters (bay spacing, corridor width, rotation angle) that generate families of possible configurations. But unlike Carpo's parametric scripts, the CMA is human-readable in its native form. A Grasshopper definition is opaque without the visual canvas. The CMA is legible to anyone who can read structured text — including screen readers and Braille displays. The notation is differential *and* accessible, a combination Carpo's framework does not address because it assumes the screen as the primary reading surface.

### 8.3 Limitations

The CMA's parametric grammar is constrained to floor plan elements within a column-grid organizational logic. It cannot currently represent freeform geometry, complex roof structures, or multi-story spatial relationships. These are real limitations of the notation's vocabulary, not fundamental limitations of the approach. Extending the semantic grammar is future work.

The representation theory argument is developed through one project. A stronger case would compare multiple post-visual notation systems — including aural notations (Blesser and Salter 2007), haptic notations, and other text-based approaches — to identify which productive properties are specific to the CMA and which generalize to non-visual notation as a category.

The claim that the CMA produces "better" spatial reasoning than viewport-based representation requires empirical evaluation. We have observational evidence from Daniel's studio work and from sighted students experimenting with the CLI. Controlled comparisons are planned but not yet complete.

## 9. Conclusion: The Drawing After Vision

Evans taught us that drawings are not windows. They are instruments. Each drawing system — plan, section, perspective, parametric script — is an instrument with its own productive properties, its own cognitive affordances, and its own architectural consequences.

The CMA is a new instrument. It was built for a blind student, out of necessity. But its properties — semantic structure, explicit feedback, modality independence, version controllability — are not accommodations. They are the productive properties of a notation system that takes text seriously as the primary architectural medium, not as a convenience layer over visual output.

The field is moving toward text-based design interfaces. Prompts are replacing clicks. Language is replacing mouse gestures. But the theory of this shift — what text *is* as a representational instrument, what it foregrounds and suppresses, what architectural thoughts it makes possible — remains unwritten. The text-to-geometry community treats text as input. The CMA treats text as the drawing itself.

Evans proved that the plan and the section produce different architectures. We argue that the CMA — the post-visual notation, the text-based drawing, the semantic model that precedes all geometric projection — produces different architectures too. And the architectures it produces are organized by semantic logic rather than visual form, documented by auditable process rather than ephemeral viewport, and accessible to any sensory modality rather than vision alone.

The architectural drawing after vision is not a drawing without content. It is a drawing with different content — and the content it carries, the organizational logic it enforces, and the design cognition it supports turn out to be what architectural education has needed all along.

---

## References

Atakan, A.O. et al. 2025. "Kakadoo: LLM Enabled Speech Interface for Enhanced Human-Computer Interaction." In *Proceedings of the 43rd eCAADe Conference*, Ankara.

Blesser, B. and L.-R. Salter. 2007. *Spaces Speak, Are You Listening? Experiencing Aural Architecture.* Cambridge, MA: MIT Press.

Carpo, M. 2011. *The Alphabet and the Algorithm.* Cambridge, MA: MIT Press.

El Hizmi, B. et al. 2024. "LLMto3D: Generating Parametric Objects from Text Prompts." In *Proceedings of ACADIA 2024*, Vol. 1, 157-166.

Evans, R. 1997. *Translations from Drawing to Building and Other Essays.* Cambridge, MA: MIT Press.

Giudice, N.A. 2018. "Navigating without Vision: Principles of Blind Spatial Cognition." In *Handbook of Behavioral and Cognitive Geography*. Edward Elgar.

Khan, S. et al. 2024. "Text2CAD: Generating Sequential CAD Designs from Beginner-to-Expert Level Text Prompts." In *Proceedings of NeurIPS 2024*.

Loomis, J.M., R.L. Klatzky, and R.G. Golledge. 2001. "Cognitive Mapping and Wayfinding by Adults Without Vision." In *Navigating through Environments*. Springer.

Millar, S. 1994. *Understanding and Representing Space.* Oxford: Oxford University Press.

Oxman, R. 2006. "Theory and Design in the First Digital Age." *Design Studies* 27(3): 229-265.

Pallasmaa, J. 2005. *The Eyes of the Skin: Architecture and the Senses.* 2nd ed. Chichester: Wiley.

Piaget, J. and B. Inhelder. 1956. *The Child's Conception of Space.* London: Routledge.

Rietschel, M., F. Guo, and K. Steinfeld. 2024. "Mediating Modes of Thought: LLMs for Design Scripting." In *Proceedings of ACADIA 2024*, Calgary.

Schon, D.A. 1983. *The Reflective Practitioner: How Professionals Think in Action.* New York: Basic Books.

Zumthor, P. 2006. *Atmospheres: Architectural Environments — Surrounding Objects.* Basel: Birkhauser.
