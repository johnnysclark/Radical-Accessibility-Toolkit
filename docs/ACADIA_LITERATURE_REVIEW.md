# ACADIA & CumInCAD Literature Review: Radical Accessibility Project

**Prepared for:** ACADIA 2026 submission
**Last updated:** 2026-02-26
**Project:** Radical Accessibility Project (UIUC School of Architecture)
**PI:** John Clark
**Sources:** 136 entries across ACADIA, CumInCAD, CHI, ASSETS, NeurIPS, IEEE VIS, and cross-disciplinary foundations

---

## Overview

This literature review surveys papers from ACADIA (Association for Computer Aided Design in Architecture), the broader CumInCAD database (CAADRIA, eCAADe, SIGraDi, CAAD Futures), HCI/accessibility conferences (CHI, ASSETS), and cross-disciplinary foundations (phenomenology, cognitive science, disability studies, acoustic ecology) relevant to the Radical Accessibility Project. The project develops tools and workflows that make architectural education fully accessible to blind and low-vision students by treating non-visual interaction as the primary design case. Its core thesis: by designing for blindness first, we create tools that are not only accessible but often superior to their visual-centric counterparts. This is disciplinarily transformative, not assistive -- a critique of architecture's ocularcentrism that produces genuinely novel computational design methods.

Papers are organized into eleven thematic sections (A through K). Each entry includes bibliographic details, a summary, and a note on relevance to the project's specific concerns: CLI-driven CAD pipelines, tactile fabrication, sonification, AI-assisted description, screen-reader-native workflows, and inclusive design pedagogy.

---

## Section A: Phenomenology & Ocularcentrism

These works provide the philosophical foundation for arguing that architecture is fundamentally multi-sensory, that visual dominance in design tools represents an impoverishment rather than a neutral default, and that the privileging of vision is historical and contestable.

### A.1 Merleau-Ponty, M. (1945/1962). *Phenomenology of Perception.*
- **Publisher:** Routledge (trans. Colin Smith; later trans. Donald Landes, 2012)
- **Summary:** The foundational phenomenological text on embodied perception. Argues for "the primacy of perception" -- that consciousness is fundamentally embodied, not disembodied cognition. Introduces the famous "blind man's cane" example: the cane becomes an extension of the body schema, demonstrating that perception is not limited to biological sense organs but extends through tools into the world.
- **Relevance:** Provides the deepest philosophical foundation for the project. If perception is embodied and extends through tools (the cane), then the CLI is Daniel's "cane" for architectural design -- an extension of his body schema into the design model. However, see Reynolds (B.12) for critical corrections to Merleau-Ponty's use of blindness.

### A.2 Gibson, J.J. (1979). *The Ecological Approach to Visual Perception.*
- **Publisher:** Houghton Mifflin (reprinted Psychology Press, 2014)
- **Summary:** Introduces the theory of affordances -- that we perceive the environment directly through its action possibilities, not through abstract mental representations. Perception is relational: affordances exist between organism and environment. A chair "affords sitting" not as an abstract property but as a direct perception by a body of certain proportions.
- **Relevance:** Gibson's affordance theory, though titled "Visual Perception," is fundamentally about *action*, not sight. Affordances are perceived through all senses. The CLI's commands ("set bay A rotation 30") are linguistic affordances -- they offer specific design actions in a format that affords screen-reader interaction. The project can argue, via Gibson, that the CLI's affordances are richer (more precise, more repeatable, more scriptable) than visual CAD's click-and-drag affordances.

### A.3 Jay, M. (1993). *Downcast Eyes: The Denigration of Vision in Twentieth-Century French Thought.*
- **Publisher:** University of California Press
- **URL:** https://www.amazon.com/Downcast-Eyes-Denigration-Twentieth-Century-Thought/dp/0520088859
- **Summary:** Monumental intellectual history of the Western critique of vision. Jay traces the tradition of "ocularcentrism" -- the privileging of sight as the noblest sense and the primary model for knowledge -- from Plato through Descartes to modernity. The book's main subject is the resistance to this visual hegemony in twentieth-century French thought (Bergson, Bataille, Sartre, Merleau-Ponty, Foucault, Derrida, Irigaray). Concludes by calling for a plurality of "scopic regimes" rather than defending or abolishing visual primacy.
- **Relevance:** Jay provides the deepest genealogy of the visual bias the project confronts. Architecture's ocularcentrism is not just a practical problem (tools require screens) but an epistemological one (spatial knowledge is assumed to be visual knowledge). Jay's call for a "plurality of scopic regimes" is precisely what the project enacts: not eliminating vision from architecture but demonstrating that spatial design knowledge can be constructed through text, touch, and sound.

### A.4 Holl, S., Pallasmaa, J., & Pérez-Gómez, A. (1994/2006). *Questions of Perception: Phenomenology of Architecture.*
- **Publisher:** A+U / William Stout
- **Summary:** Three interlocking essays -- Holl on "phenomenal zones" (color, light, shadow, time, sound), Pallasmaa on "An Architecture of the Seven Senses," Pérez-Gómez on "The Space of Architecture: Meaning as Presence and Representation." Collectively argues that architecture is a multi-sensory phenomenon irreducible to its visual representation.
- **Relevance:** The canonical collaborative text linking phenomenology and architecture. Pallasmaa's "seven senses" essay directly supports the project's argument that architecture engages senses beyond sight. The project operationalizes this philosophical position through tools.

### A.5 Pallasmaa, J. (1996/2005/2012). *The Eyes of the Skin: Architecture and the Senses.*
- **Publisher:** Wiley (multiple editions)
- **ISBN:** 978-1119941286
- **Summary:** Asks why, when there are five senses, has one single sense -- sight -- become so predominant in architectural culture and design. Argues that the suppression of the other four sensory realms has led to the overall impoverishment of the built environment. The most influential text critiquing architecture's ocularcentrism.
- **Relevance:** The foundational theoretical text for the project's framing. Pallasmaa's critique is philosophical; the project makes it operational. By building tools that work without vision, the project demonstrates what Pallasmaa argues: that non-visual architectural knowledge is not merely supplementary but reveals qualities that visual dominance obscures.

### A.6 Zumthor, P. (2006). *Atmospheres: Architectural Environments — Surrounding Objects.*
- **Publisher:** Birkhäuser
- **Summary:** Identifies nine generators of architectural atmosphere: The Body of Architecture, Material Compatibility, The Sound of a Space, The Temperature of a Space, Surrounding Objects, Between Composure and Seduction, Tension between Interior and Exterior, Levels of Intimacy, and The Light of Things. Crucially, only one of these nine -- Light -- is primarily visual.
- **Relevance:** Zumthor's nine generators provide an operational vocabulary for what the project's tools must capture. The CLI's semantic model (bays, corridors, columns, voids) describes the "Body of Architecture." The planned sonification pipeline could address "The Sound of a Space." The project demonstrates that computational tools can encode Zumthor's multi-sensory architecture, not just its visual projection.

### A.7 Pérez-Gómez, A. (2016). *Attunement: Architectural Meaning after the Crisis of Modern Science.*
- **Publisher:** MIT Press
- **Summary:** Argues that architecture's essential task is attunement between human beings and their environment. Draws on embodied cognition research to argue that the built environment is a constituent part of consciousness. Perception is established as something we *do*, not something that happens to us -- proactive, not merely reactive.
- **Relevance:** "Attunement" reframes architecture as an active, embodied relationship -- not a picture. This supports the project's argument that Daniel's tactile, auditory, and command-line engagement with architecture is not a workaround for "real" (visual) design but a different -- possibly deeper -- form of architectural attunement.

### A.8 Böhme, G. (2017). *The Aesthetics of Atmospheres.* Ed. Jean-Paul Thibaud.
- **Publisher:** Routledge
- **Summary:** Argues that spatial atmospheres exert tangible emotional effects by appealing directly to the senses. Architecture is experienced through bodily, multi-sensory perception before intellectual comprehension. Develops a "new aesthetics" grounded in embodied experience rather than visual contemplation.
- **Relevance:** Böhme's theory that we experience space sensorially *before* we understand it visually directly supports the project's thesis. If atmosphere precedes vision, then tools that bypass vision and work through text, sound, and touch are not lesser -- they may access architectural experience more directly.

### A.9 Schön, D.A. (1983). *The Reflective Practitioner: How Professionals Think in Action.*
- **Publisher:** Basic Books
- **Summary:** Argues that professional practice -- including design -- is a "reflective conversation with the situation." Designers do not apply rules to problems; they engage in a back-and-forth dialogue where each action reveals new qualities of the situation, which in turn suggest new actions. Introduces the concepts of "reflection-in-action" (thinking while doing) and "knowing-in-action" (the tacit knowledge embedded in skilled performance).
- **Relevance:** The CLI is a conversation medium. Each command is a "move" in a reflective dialogue; each OK:/ERROR: response is the "situation talking back." Schön's framework reframes the CLI not as a limited interface but as a design conversation -- and arguably a *better* one than visual CAD, where the situation's "talk back" is a silent visual change that the designer must notice. The CLI's verbal feedback makes the reflective conversation explicit and auditable.

### A.10 Varela, F.J., Thompson, E., & Rosch, E. (1991). *The Embodied Mind: Cognitive Science and Human Experience.*
- **Publisher:** MIT Press (revised edition 2016)
- **Summary:** The foundational text of enactivism. Argues that cognition is not the internal manipulation of abstract representations but "enaction" -- the bringing forth of domains of significance through embodied action in a coupled organism-environment system. Draws on Merleau-Ponty's phenomenology, Buddhist mindfulness, and autopoietic biology. The key claim: mind is inseparable from bodily engagement with the world.
- **Relevance:** Extends Merleau-Ponty's phenomenology into cognitive science. If cognition is enacted through embodied engagement rather than detached representation, then Daniel's CLI-mediated engagement with architectural models is not a substitute for "real" (visual) design -- it is a different enactment of spatial cognition, equally valid and potentially revealing of different architectural qualities. The CLI is not a representation of architecture; it is an enactive medium through which architecture is brought forth.

### A.11 Clark, A. & Chalmers, D.J. (1998). "The Extended Mind."
- **Venue:** Analysis, Vol. 58, No. 1, pp. 7-19
- **URL:** https://www.jstor.org/stable/3328150
- **Summary:** The landmark paper arguing that cognitive processes do not stop at the skull. When an external tool (notebook, calculator, software) plays the same functional role as an internal cognitive process, it is part of the mind. Otto's notebook, which he consults for directions because his biological memory is impaired, is functionally equivalent to Inga's biological memory -- both constitute "beliefs" that guide action.
- **Relevance:** The CLI is Daniel's extended mind for architectural design. Where a sighted designer's cognitive process extends through their eyes into the viewport, Daniel's extends through the CLI into the JSON state model. Clark and Chalmers' criterion -- that the external resource must be reliably available, automatically endorsed, and easily accessible -- is met by the CLI's deterministic, always-available, screen-reader-native interface. The state.json file is Daniel's architectural memory, and the CLI is the cognitive process that accesses it.

### A.12 Sennett, R. (2008). *The Craftsman.*
- **Publisher:** Yale University Press
- **Summary:** Explores the intelligence of the hand and the relationship between making and thinking. Argues that craftsmanship -- the desire to do a job well for its own sake -- depends on a continuous dialogue between concrete practices and thinking. The hand is not a dumb executor of the mind's plans; it is an organ of cognition. Skilled practice involves a rhythm of problem-solving and problem-finding where tacit knowledge (what the body knows) guides explicit reasoning.
- **Relevance:** Sennett's "dialogue between hand and head" maps onto the CLI's command-response loop. Daniel's hands on the keyboard and braille display are his primary cognitive interface with architecture. The CLI's text-in, text-out pattern creates exactly the rhythmic dialogue Sennett describes: type a command (make a move), receive feedback (feel the result), adjust (next move). The project demonstrates that the craftsman's "intelligent hand" need not be a drawing hand.

### A.13 Ingold, T. (2013). *Making: Anthropology, Archaeology, Art and Architecture.*
- **Publisher:** Routledge
- **Summary:** Argues that making is a process of growth, not of imposing form on matter. The maker does not execute a preconceived design; they "correspond" with materials, following flows of material and adjusting in real time. Challenges the hylomorphic model (form imposed on passive matter) and proposes that knowledge is generated through the act of making, not applied to it.
- **Relevance:** Ingold's critique of the hylomorphic model (design as mental image imposed on material) applies to visual CAD's assumption that the designer conceives a form mentally and then draws it. The CLI's incremental, command-by-command workflow embodies Ingold's alternative: knowledge generated through the process of making. Daniel does not conceive a floor plan and then type it in; he discovers the plan through the act of commanding and receiving feedback. The CLI is a medium of correspondence, not imposition.

---

## Section B: Blindness & Non-Visual Spatial Cognition

These works address how blind people perceive, navigate, and understand space -- the empirical and cognitive-science foundation for the project's design decisions. Includes haptic spatial development, blind spatial cognition research, and case studies of blind architects in practice.

### B.1 Piaget, J. & Inhelder, B. (1956). *The Child's Conception of Space.*
- **Publisher:** Routledge & Kegan Paul (London). Originally published in French, 1948.
- **URL:** https://archive.org/details/childsconception0000piag_e5l4
- **Summary:** Foundational developmental psychology text that includes a chapter on "Perceptual Space, Representational Space, and the Haptic Perception of Shape." Piaget and Inhelder demonstrate that children's earliest spatial understanding is topological (proximity, enclosure, continuity) before becoming projective or Euclidean. Their studies of haptic perception show that children can recognize and classify spatial relationships through touch alone, prior to visual-geometric sophistication.
- **Relevance:** The project's CLI encodes topological and semantic relationships ("bay A is adjacent to bay B," "corridor runs along axis X") before generating precise geometry. This mirrors Piaget and Inhelder's finding that spatial understanding develops from qualitative/topological to quantitative/metric. The CLI's sequential, relationship-first interaction model aligns with how spatial cognition actually develops, with or without vision.

### B.2 Millar, S. (1994). *Understanding and Representing Space.* / Millar, S. (2008). *Space and Sense.*
- **Publisher:** Oxford University Press (1994); Psychology Press / Routledge (2008)
- **URL (1994):** https://global.oup.com/academic/product/understanding-and-representing-space-9780198521426
- **URL (2008):** https://www.routledge.com/Space-and-Sense/Millar/p/book/9780415651882
- **Summary:** Millar's 1994 book challenges the assumption that vision is the primary modality for spatial understanding by examining spatial representation in the total absence of vision, comparing findings from congenitally blind and sighted children. Her 2008 *Space and Sense* extends this, arguing that spatial processing depends crucially on integrating diverse sensory inputs as reference cues -- not on any single modality. She demonstrates that touch and movement can substitute for vision when appropriate reference frames are provided.
- **Relevance:** Millar's central finding -- that spatial cognition is modality-independent when adequate reference cues exist -- is the cognitive science foundation for the entire project. The CLI provides precisely those reference cues: named bays, labeled axes, numbered dimensions. These are the "external reference frames" that Millar shows enable blind spatial reasoning to match sighted performance. The project is not accommodating a deficit; it is providing the reference structure that enables full spatial competence.

### B.3 Thinus-Blanc, C. & Gaunet, F. (1997). "Representation of space in blind persons: vision as a spatial sense?"
- **Venue:** Psychological Bulletin, Vol. 121, No. 1, pp. 20–42
- **URL:** https://pubmed.ncbi.nlm.nih.gov/9064698/
- **Summary:** Major review article addressing whether vision is necessary for spatial representation. Examines why previous studies produced contradictory findings -- some showing profound spatial deficits in early blind participants, others finding none. Proposes that the discrepancies stem from differences in spatial strategies rather than fundamental cognitive limitations. Argues that studying strategies (sequential vs. simultaneous, egocentric vs. allocentric) is more productive than asking whether blind people "can" represent space.
- **Relevance:** This paper resolves the apparent contradiction in the blind spatial cognition literature. The CLI provides exactly the kind of strategy-enabling infrastructure Thinus-Blanc and Gaunet call for: sequential command entry (matching blind users' sequential spatial exploration), explicit naming of landmarks and axes (providing allocentric reference frames), and verbal confirmation of spatial relationships (supporting language-mediated spatial reasoning). The tool design is strategy-aligned, not modality-dependent.

### B.4 Loomis, J.M., Klatzky, R.L., & Golledge, R.G. (2001). "Cognitive Mapping and Wayfinding by Adults Without Vision."
- **Venue:** Chapter in *Navigating through Environments*, Springer. Multiple related publications 1993–2007.
- **URL:** https://link.springer.com/chapter/10.1007/978-0-585-33485-1_10
- **Summary:** Comprehensive research program investigating how adults without vision develop and use cognitive maps. Key findings: (1) spatial representations derived from spatial language can function equivalently to those derived from direct perception; (2) blind individuals can construct survey-level (bird's-eye-view) spatial knowledge under the right conditions; (3) spatialized audio is more reliable and accurate than language alone for route traversal, but language is sufficient for spatial layout understanding.
- **Relevance:** The finding that "spatial representations derived from spatial language can function equivalently to those derived from perception" is perhaps the single most powerful piece of evidence for the project's CLI-based approach. Daniel constructs spatial understanding of his designs through textual commands and verbal feedback -- exactly the "spatial language" pathway Loomis et al. validate.

### B.5 Hatwell, Y., Streri, A., & Gentaz, E. (Eds.) (2003). *Touching for Knowing: Cognitive Psychology of Haptic Manual Perception.*
- **Publisher:** John Benjamins (Advances in Consciousness Research, Vol. 53)
- **URL:** https://benjamins.com/catalog/aicr.53
- **Summary:** Comprehensive edited volume on the cognitive psychology of haptic perception. Examines exploratory manual behaviors, intramodal haptic abilities, and cross-modal visual-tactual coordination in infants, children, adults, and non-human primates. Key finding: intensive use of touch by blind persons allows them to reach the same levels of spatial knowledge and cognition as sighted peers. Includes chapters on Braille reading, raised maps and drawings, and sensory substitution displays.
- **Relevance:** Directly validates the project's physical-digital pipeline. Hatwell et al.'s evidence that haptic perception achieves equivalent spatial cognition to vision supports the project's investment in tactile output (PIAF swell paper, 3D prints) and tactile input (pegboard). The finding that touch reaches "the same levels of knowledge" refutes the deficit model that treats tactile representation as inferior.

### B.6 Saerberg, S. (2010). "'Just go straight ahead': How Blind and Sighted Pedestrians Negotiate Space."
- **Venue:** The Senses and Society, Vol. 5, No. 3
- **Summary:** Ethnographic study of how blind pedestrians negotiate spatial environments. Draws on Schütz and Merleau-Ponty to show that blindness constitutes a distinct perceptual lifeworld -- not a deficit version of sighted experience. Blind pedestrians rely on sequential, route-based spatial knowledge rather than simultaneous, survey-based knowledge.
- **Relevance:** The distinction between sequential/route knowledge and simultaneous/survey knowledge maps directly onto the project's interface design. The CLI's sequential command structure (one command at a time, building up a model incrementally) aligns with how blind people naturally build spatial understanding. Visual CAD's simultaneous display of the entire model is inherently survey-based.

### B.7 Cattaneo, Z. & Vecchi, T. (2011). *Blind Vision: The Neuroscience of Visual Impairment.*
- **Publisher:** MIT Press
- **Summary:** Comprehensive review of neuroscience research on how blindness affects (and does not affect) spatial cognition. Demonstrates that blind individuals develop robust spatial representations through touch, hearing, and language. Challenges deficit models of blindness.
- **Relevance:** Provides neuroscientific evidence supporting the project's thesis that blindness does not preclude rich spatial reasoning -- it merely requires different input modalities. The CLI provides one such modality; the tactile output provides another.

### B.8 Herssens, J. and Heylighen, A. (2011). "A Framework of Haptic Design Parameters for Architects: Sensory Paradox Between Content and Representation."
- **Venue:** Computer Aided Architectural Design Futures 2011 (CAAD Futures), Liege, Belgium
- **URL:** https://cumincad.architexturez.net/doc/oai-cumincadworks-id-cf2011-p027
- **Summary:** Defines haptic design parameters as variable characteristics that can be decided upon by designers during the design process. Based on research with twenty-two people born blind, identifying how human movement is influenced by movement plane, guiding plane, and resting plane. The haptic parameters include texture, temperature, weight, and compliance.
- **Relevance:** Directly informs the project's tactile output pipeline (PIAF swell paper, 3D-printed models). The "sensory paradox between content and representation" mirrors the project's challenge of representing spatial relationships through non-visual media.

### B.9 Vermeersch, P. and Heylighen, A. (2012). "Blindness and Multi-sensoriality in Architecture: The Case of Carlos Mourao Pereira."
- **Venue:** Published in research proceedings; indexed in multiple databases
- **URL:** https://www.researchgate.net/publication/237044494_Blindness_and_multi-sensoriality_in_architecture_The_case_of_Carlos_Mourao_Pereira
- **Summary:** Case study of Carlos Mourao Pereira, an architect who lost his sight in 2006 and continues to practice, teach, and conduct research. His practice is centered on multi-sensoriality. After losing his sight, his designs demonstrate heightened attention to tactile, auditory, and olfactory elements.
- **Relevance:** A direct precedent for the project's thesis that blindness can be generative for architecture. Pereira demonstrates that an architect who cannot see can produce richer spatial designs. The project extends this argument from the individual practitioner to the tool ecosystem.

### B.10 Celani, G., Zattera, V., de Oliveira, M.F., and da Silva, J.V.L. (2013). "'Seeing' with the Hands: Teaching Architecture for the Visually-Impaired with Digitally-Fabricated Scale Models."
- **Venue:** CAAD Futures 2013, Shanghai, China
- **URL:** https://link.springer.com/chapter/10.1007/978-3-642-38974-0_15
- **Summary:** Develops a protocol for making 3D technologies available to educators of visually impaired students. Three-dimensional representations are more effective than bidimensional for those with congenital blindness, especially during conceptualization. Used Selective Laser Sintering (SLS) to create tactile models evaluated by people with various visual impairments.
- **Relevance:** Directly relevant to the project's physical-digital round-trip pipeline. The project extends this work by automating the digital-to-tactile translation and closing the loop (tactile input via pegboard digitizes back to geometry).

### B.11 Heylighen, A. and Herssens, J. (2014). "Designerly Ways of Not Knowing: What Designers Can Learn about Space from People Who are Blind."
- **Venue:** Journal of Urban Design, Vol. 19, No. 3, pp. 317-332
- **URL:** https://ideas.repec.org/a/taf/cjudxx/v19y2014i3p317-332.html
- **Summary:** Demonstrates that architects' visual ways of knowing risk favouring visual qualities over non-visual qualities, but also cognition over embodiment. Argues that designerly ways of knowing are simultaneously designerly ways of "not knowing" -- of disregarding the bodily experience of the built environment. People who are blind appreciate sounds, smells, and haptic qualities that designers may not be attuned to.
- **Relevance:** Perhaps the single most important theoretical paper for the project. Its argument that designers' visual training creates systematic blind spots directly supports the project's thesis that designing for blindness first reveals architectural knowledge that ocularcentrism obscures.

### B.12 Reynolds, J.M. (2017). "Merleau-Ponty, World-Creating Blindness, and the Phenomenology of Non-Normate Bodies."
- **Venue:** Chiasmi International, Vol. 19, pp. 419–436
- **URL:** https://philarchive.org/rec/REYMWB
- **Summary:** Critiques Merleau-Ponty's "blind man's cane" example for omitting social dimensions of disability, misconstruing blindness as world-creating, and operating via an able-bodied simulation. Argues that phenomenology must heed "crip phenomenology" -- taking the lived experience of disability as its departure point rather than simulating it from a normate perspective.
- **Relevance:** Essential corrective. The project must not romanticize or simulate blindness. Reynolds' argument supports the project's methodology: Daniel is a co-designer, not a subject. The tools are built *from* his experience, not *about* it.

### B.13 Giudice, N.A. (2018). "Navigating without Vision: Principles of Blind Spatial Cognition."
- **Venue:** Handbook of Behavioral and Cognitive Geography (Edward Elgar)
- **Summary:** Reviews research on spatial cognition without vision. Key finding: blind people can and do form accurate spatial representations, but through different processes -- sequential, landmark-based, and language-mediated rather than simultaneous and visual.
- **Relevance:** The "language-mediated" finding is critical. Daniel's text-based interaction with architecture is not a workaround -- it is aligned with how spatial cognition actually works without vision. Language *is* a spatial medium for blind people.

### B.14 Vermeersch, P., Schijlen, J., and Heylighen, A. (2018). "Designing from Disability Experience: Space for Multi-sensoriality."
- **Venue:** Participatory Design Conference (PDC) 2018, Hasselt & Genk, Belgium
- **URL:** https://www.researchgate.net/publication/324593818_Designing_from_disability_experience_Space_for_multi-sensoriality
- **Summary:** Explores how disability experience can inform architectural design processes. Emphasizes disability experience as generative knowledge -- not deficit -- with the goal of producing knowledge applicable in design processes.
- **Relevance:** The participatory design methodology aligns with Daniel's role as co-designer (not just user) of every tool in the project. Vermeersch et al.'s framing of blindness as a design advantage parallels the project's framing.

### B.15 Chen, Q., et al. (2024). "Perception beyond sight: Investigating the cognitive maps of congenitally blind individuals in urban environments."
- **Venue:** ScienceDirect (2024)
- **URL:** https://www.sciencedirect.com/science/article/pii/S2095263524000281
- **Summary:** Studies how congenitally blind individuals construct cognitive maps of cities using touch, hearing, smell, safety sense, and experience. Mental maps consist of five elements: links, reference points, areas, separators, and topography.
- **Relevance:** Provides empirical evidence for how Daniel likely constructs mental models of his designs. The CLI's semantic vocabulary (bays, corridors, columns) maps onto the "reference points" and "areas" that blind cognitive maps prioritize.

### B.16 Downey, Chris — Blind Architect, San Francisco.
- **TED Talk:** "Design with the Blind in Mind" (2013)
- **URL:** https://www.ted.com/speakers/chris_downey
- **Key projects:** San Francisco LightHouse for the Blind; Duke Eye Center
- **Summary:** Lost sight in 2008 after 20 years of practice. Rather than leaving architecture, he reinvented his practice around multi-sensory design. Reads architectural plans by touch using a large-format embossing printer that produces raised tactile drawings. Teaches accessibility and universal design at UC Berkeley.
- **Relevance:** The most prominent blind architect practicing today. His use of embossed tactile plans parallels the project's PIAF swell paper pipeline. Downey works around inaccessible tools; the project builds accessible ones from the ground up.

---

## Section C: Critical Disability Studies & Design Justice

These works provide the theoretical framework for arguing that the project is *disciplinarily transformative, not assistive* -- that it reveals structural biases in architecture's tool ecosystem. Includes disability politics, crip technoscience, participatory design principles, ability-based design, and universal design critiques.

### C.1 Winner, L. (1980). "Do Artifacts Have Politics?"
- **Venue:** Daedalus, Vol. 109, No. 1, pp. 121–136
- **URL:** https://www.jstor.org/stable/20024652
- **Summary:** The foundational STS text arguing that technologies are not politically neutral -- they embody and enforce social arrangements. Technologies can be designed to systematically include or exclude specific groups.
- **Relevance:** Winner's argument, applied to the project: Rhino's viewport, Grasshopper's visual canvas, and Revit's click-and-drag interface are not neutral instruments that *happen* to be visual. They are artifacts that *have politics* -- they enforce a social arrangement in which sighted people design and blind people are excluded. The project builds artifacts with different politics.

### C.2 Charlton, J.I. (1998). *Nothing About Us Without Us: Disability Oppression and Empowerment.*
- **Publisher:** University of California Press
- **URL:** https://www.jstor.org/stable/10.1525/j.ctt1pnqn9
- **Summary:** The first book in the disability literature to provide a comprehensive theoretical overview of disability oppression, drawing parallels with racism, sexism, and colonialism. The title phrase originated in the disability rights movement and has become the defining principle of participatory disability research and design.
- **Relevance:** The project's co-design methodology with Daniel directly enacts Charlton's principle. Daniel is not a test subject; he is a co-designer who shapes tool requirements, evaluates outputs, and identifies spatial relationships that sighted developers miss. Every tool exists because Daniel identified a need.

### C.3 Pullin, G. (2009). *Design Meets Disability.*
- **Publisher:** MIT Press
- **URL:** https://mitpress.mit.edu/9780262516747/design-meets-disability/
- **Summary:** Argues that design and disability can inspire each other in ways that transcend mere accommodation. Uses the history of eyeglasses -- transformed from medical necessity to fashion statement -- as a case study for how disability products can drive design innovation when design culture engages seriously with disability.
- **Relevance:** The CLI-to-JSON pipeline was designed for a blind user. But it turns out to be more debuggable, more scriptable, more version-controllable, and more crash-resilient than traditional visual CAD workflows. Like Pullin's eyeglasses, the project's tools started as a necessity and became a design contribution.

### C.4 Mankoff, J., Hayes, G.R., & Kasnitz, D. (2010). "Disability Studies as a Source of Critical Inquiry for the Field of Assistive Technology."
- **Venue:** ASSETS '10. Received ASSETS Paper Impact Award, 2021.
- **URL:** https://dl.acm.org/doi/10.1145/1878803.1878807
- **Summary:** Argues that disability studies and assistive technology share common goals but rarely engage each other. Key insight: disability studies reframes assistive technology from "fixing" individual deficits to questioning the social and technical systems that create disability in the first place.
- **Relevance:** The project enacts exactly the shift Mankoff et al. call for: instead of building assistive overlays on top of visual CAD tools (fixing the individual), it redesigns the tool architecture itself (questioning the system). The CLI-to-JSON-to-Rhino pipeline is not an accommodation -- it is a redesign motivated by disability studies' insight that the problem is in the tool, not the user.

### C.5 Shinohara, K. & Wobbrock, J.O. (2011). "In the Shadow of Misperception: Assistive Technology Use and Social Interactions."
- **Venue:** CHI '11. **Best Paper Award (top 1%).**
- **URL:** https://dl.acm.org/doi/10.1145/1978942.1979044
- **Summary:** Interview study of 20 individuals examining how assistive technology use is affected by social and professional contexts. Found that functional access took priority over self-consciousness, and that assistive devices often marked users as "having disabilities." Concludes that accessibility should be built into mainstream technologies rather than relegated to specialized devices.
- **Relevance:** The CLI is not a specialized assistive overlay; it is a mainstream-architecture tool (Python, JSON, Rhino) that happens to be accessible. Daniel uses the same CAD pipeline as any computational designer -- just through a different interface. The project's tools don't mark him as "the blind student using special software."

### C.6 Wobbrock, J.O., et al. (2011). "Ability-Based Design: Concept, Principles and Examples."
- **Venue:** ACM Transactions on Accessible Computing, Vol. 3, No. 3
- **DOI:** https://doi.org/10.1145/1952383.1952384
- **Summary:** Proposes shifting the focus of accessible design from disability to ability. Instead of asking "What disability does a person have?" asks "What can a person do?" Offers seven ability-based design principles.
- **Relevance:** The project embodies ability-based design: it asks not "How does Daniel's blindness prevent him from using Rhino?" but "What can Daniel do?" (type, listen, touch, reason spatially through language). The CLI is designed around Daniel's abilities, not his disability.

### C.7 Imrie, R. (2012). "Universalism, Universal Design and Equitable Access to the Built Environment."
- **Venue:** Disability & Rehabilitation, Vol. 34, No. 10
- **Summary:** Critically evaluates universal design's philosophical foundations and practical limitations. Questions whether universalism adequately addresses the diversity of disabled people's needs and experiences.
- **Relevance:** The project's approach is more specific than universal design -- it designs for a particular user (Daniel) in a particular context (graduate architecture studio) and then discovers that the resulting tools have broader value. This "design for one, extend to many" approach may be more productive than abstract universalism.

### C.8 Steinfeld, E. & Maisel, J. (2012). *Universal Design: Creating Inclusive Environments.*
- **Publisher:** Wiley
- **Summary:** Updated framework for universal design with eight goals: body fit, comfort, awareness, understanding, wellness, social integration, personalization, and cultural appropriateness.
- **Relevance:** Provides a checklist against which to evaluate the project's tools. The CLI scores well on understanding (clear text feedback), personalization (configurable state), and awareness (OK:/ERROR: protocol), but could improve on social integration (collaboration features for mixed-ability teams).

### C.9 Boys, J. (2014). *Doing Disability Differently: An Alternative Handbook on Architecture, Dis/ability and Designing for Everyday Life.*
- **Publisher:** Routledge
- **Summary:** Reframes disability as generative and creative -- a radical, even avant-garde, approach to architectural education and practice. Challenges compliance-focused thinking and asks how disability and ability can help us think more explicitly about habitation.
- **Relevance:** Boys' framing of disability as "avant-garde" aligns with the project's claim that designing for blindness produces genuinely novel computational design methods. The project can cite Boys to argue that its ACADIA contribution is not a social-good sideshow but a cutting-edge methodological intervention.

### C.10 Levent, N. & Pascual-Leone, A. (Eds.) (2014). *The Multisensory Museum.*
- **Publisher:** Rowman & Littlefield
- **URL:** https://www.amazon.com/Multisensory-Museum-Cross-Disciplinary-Perspectives-Memory/dp/0759123543
- **Summary:** Brings together museum experts and neuroscientists to explore how touch, sound, smell, and memory can create immersive, accessible exhibition experiences. Argues that multisensory design is not just an accessibility accommodation but an opportunity to create richer experiences for all visitors.
- **Relevance:** The museum context parallels the architecture studio. Levent and Pascual-Leone demonstrate that multisensory design enriches experience for everyone. The project makes the same argument for architectural design tools.

### C.11 Ladner, R. (2015). "Design for User Empowerment."
- **Venue:** ACM Interactions, Vol. 22, No. 2
- **DOI:** https://doi.org/10.1145/2723869
- **Summary:** Advocates that users with disabilities should be empowered to solve their own accessibility problems through self-determination and technical expertise.
- **Relevance:** Daniel is not a passive recipient of accessibility features -- he co-designs the tools, tests them in studio, and provides feedback that reshapes the CLI. The project empowers rather than accommodates.

### C.12 Hamraie, A. (2017). *Building Access: Universal Design and the Politics of Disability.*
- **Publisher:** University of Minnesota Press
- **URL:** https://www.upress.umn.edu/9781517901646/building-access/
- **Summary:** Blends technoscience studies and design history with critical disability, race, and feminist theories. Introduces "normate template" and "crip technoscience" concepts. Traces the co-evolution of accessible design for disabled veterans, a radical disability maker movement, and disability rights law.
- **Relevance:** The most important critical-theoretical text for the project's framing. Hamraie's "normate template" concept applies directly to CAD tools: Rhino, Grasshopper, and Revit are designed around a normate template that assumes a sighted, mouse-using operator. The project replaces this template with one that assumes a screen-reader-using, keyboard-operating architect.

### C.13 Hamraie, A. & Fritsch, K. (2019). "Crip Technoscience Manifesto."
- **Venue:** Catalyst: Feminism, Theory, Technoscience, Vol. 5, No. 1
- **URL:** https://catalystjournal.org/index.php/catalyst/article/view/29607
- **Summary:** Defines "crip technoscience" as a field centering the work disabled people do as "knowers and makers." Challenges imperatives to be typical, productive, and functioning. Argues that disabled people are treated solely as users, not as makers.
- **Relevance:** Daniel is not a user of accessibility features -- he is a maker of architectural knowledge. The project's tools don't accommodate his blindness; they *leverage* it as a source of design insight. The manifesto's commitment to "interdependence as political technology" also frames the controller/viewer separation.

### C.14 Williamson, B. (2019). *Accessible America: A History of Disability and Design.*
- **Publisher:** NYU Press
- **URL:** https://nyupress.org/9781479894093/accessible-america/
- **Summary:** Historical study of how disability advocates harnessed technological design for access and equality. Shows that access "does not just happen" and that disability is a phenomenon emerging from the material environment, not from bodies.
- **Relevance:** Williamson's insight that disability emerges from material environments applies directly to CAD tools: the "disability" of a blind architecture student is produced by the tool environment (visual-only CAD), not by the student. The project eliminates the material barrier.

### C.15 Costanza-Chock, S. (2020). *Design Justice: Community-Led Practices to Build the Worlds We Need.*
- **Publisher:** MIT Press (open access)
- **URL:** https://designjustice.mitpress.mit.edu/
- **Summary:** Rethinks design processes to center people normally marginalized by design. Argues that design typically assumes users are members of the dominant group and that this assumption is actively exclusionary. Proposes design justice principles: center voices of those most impacted, prioritize community needs, recognize that design processes are always political.
- **Relevance:** The project goes further than Costanza-Chock's framework -- it demonstrates that centering a marginalized user produces tools that are *better for everyone*, not just more equitable. The CLI's crash resilience, scriptability, and version-control friendliness are design justice's curb cut effect made concrete.

### C.16 Gissen, D. (2022). *The Architecture of Disability: Buildings, Cities, and Landscapes beyond Access.*
- **Publisher:** University of Minnesota Press
- **URL:** https://www.upress.umn.edu/book-division/books/the-architecture-of-disability
- **Summary:** Argues against centering "access" in disability design. Disability should not be relegated to access or accommodation alone. Proposes that disability experience should be a foundation for architectural form.
- **Relevance:** Gissen's argument that architecture must go "beyond access" is precisely the project's argument about tools. The project does not merely make Rhino "accessible" (that would be accommodation). It builds a fundamentally different tool ecosystem where blindness is the primary design case.

### C.17 Lifchez, R. (1987). *Rethinking Architecture: Design Students and Physically Disabled People.*
- **Publisher:** University of California Press
- **URL:** https://www.degruyter.com/document/doi/10.1525/9780520326934/html
- **Summary:** Documents an experiment in architectural education at UC Berkeley where approximately 30 disabled individuals (using wheelchairs, letter-boards, walkers, white canes, hearing aids) participated as co-designers in an architecture studio. Lifchez recounts his shift from learning about disabled people through state agencies to direct involvement with Berkeley's politically and socially active disabled community. Argues that disability and access must be integral to design education rather than supplementary topics.
- **Relevance:** The foundational text for disability-inclusive architectural pedagogy, written nearly 40 years ago. Lifchez's approach -- bringing disabled people into the studio as participants, not subjects -- directly prefigures the project's co-design methodology. The key difference: Lifchez's participants were consumers and critics of design; Daniel is the primary author. Chris Downey now holds the inaugural Lifchez Professor of Practice position at UC Berkeley, directly extending this legacy.

### C.18 Gissen, D. (2018). "Why are there so few disabled architects and architecture students?"
- **Venue:** The Architect's Newspaper, June 15, 2018
- **URL:** https://www.archpaper.com/2018/06/disability-education-of-architects/
- **Summary:** Identifies three structural barriers excluding disabled people from architecture: (1) physically inaccessible facilities at elite schools, (2) a curriculum romanticizing physically demanding site visits that embeds an "athletic aesthetic," and (3) inaccessible construction sites where internships occur. Argues that "multiple generations of architect leaders with disabilities have been lost."
- **Relevance:** Documents the systemic exclusion that makes a blind architecture student like Daniel so rare. The barriers Gissen identifies extend to tools: inaccessible CAD software is a fourth structural barrier his article does not name, and it is the one the project directly addresses.

### C.19 Mulligan, K., Calder, A., & Mulligan, H. (2018). "Inclusive design in architectural practice: Experiential learning of disability in architectural education."
- **Venue:** Disability and Health Journal, Vol. 11, No. 2, pp. 237-242
- **URL:** https://pubmed.ncbi.nlm.nih.gov/28882468/
- **Summary:** Qualitative study of 24 architecture students' perceptions of inclusive design after an experiential learning module. Three themes: inclusive design is perceived as challenging, students value direct contact with disability perspectives, and genuine attitude changes occur. Concludes that experiential learning with positive examples must be embedded in architectural education.
- **Relevance:** Documents the current state: disability is taught as a topic to design *for*, not a perspective to design *from*. The project inverts this by positioning Daniel as co-designer, producing exactly the experiential shift Mulligan et al. call for but going further -- the blind student reshapes the tools, not just the curriculum.

### C.20 Nicholson, K.A. (2025). "Where Are My People? Disability in Architecture."
- **Venue:** ACSA (Association of Collegiate Schools of Architecture)
- **URL:** https://www.acsa-arch.org/resource/where-are-my-people-disability-in-architecture/
- **Summary:** Part of ACSA's research series examining marginalized populations in architecture. Investigates the presence and absence of disabled people as students, practitioners, and leaders. Advisory board includes Great Plains ADA Center and multiple university partners.
- **Relevance:** The most recent and directly relevant institutional survey of disability in architectural education. Provides the institutional context for why the project is necessary: the profession has not systematically addressed the inclusion of disabled practitioners, let alone developed tools for their use.

---

## Section D: Equity & Inclusion in Computational Design

These papers directly address who gets to participate in computational design and on what terms, from within the ACADIA/CumInCAD community and allied architectural research.

### D.1 Noel, V.A.A., Boeva, Y., and Dortdivanlioglu, H. (2021). "The Question of Access: Toward an Equitable Future of Computational Design."
- **Venue:** IJAC, Vol. 19, No. 4, pp. 496-511
- **DOI:** 10.1177/14780771211014925
- **URL:** https://journals.sagepub.com/eprint/ZHJHUQSYMBSYHQNTZNEU/full
- **Summary:** Examines the trope of "access" in digital fabrication, design, and craft. Argues that an equitable future must build on and create space for multiple bodies, knowledges, and skills, and employ technologies accessible to broad groups of society.
- **Relevance:** Directly frames the project's central argument -- that computational design tools systematically exclude certain bodies and ways of knowing. The project extends Noel et al.'s call for equity by demonstrating what "access" means concretely for a blind architecture student using CLI-driven tools.

### D.2 Zallio, M. & Clarkson, P.J. (2021). "Inclusion, Diversity, Equity and Accessibility in the Built Environment."
- **Venue:** Building and Environment, Vol. 206, 108352
- **DOI:** 10.1016/j.buildenv.2021.108352
- **Summary:** Ethnographic study of 26 building industry professionals on the adoption of inclusive design. Finds that education and awareness are essential, and recommends holistically mapping user journeys and collecting post-occupancy feedback.
- **Relevance:** Provides empirical evidence that architecture practice systematically excludes disability perspectives. The project's co-design approach with Daniel directly responds to Zallio & Clarkson's call for holistic inclusion.

### D.3 eCAADe 2022 Conference: "Co-creating the Future: Inclusion in and through Design."
- **Venue:** 40th eCAADe Conference, KU Leuven Technology Campus Ghent, Belgium
- **Editors:** Pak, B. and Stouffs, R.
- **URL:** https://ecaade.org/prev-conf/archive/ecaade2022/kuleuven.ecaade2022.be/proceedings/index.html
- **Summary:** Entire conference themed around "Inclusion in and through Design." Addressed the negative impact of digital devices and platforms, including exclusion of vulnerable citizens.
- **Relevance:** Establishes that the eCAADe community recognizes inclusion as a first-order concern. The project provides a concrete case study of what "inclusion through design" means when the excluded user is a blind architecture student.

### D.4 Heylighen, A., et al. (2021–2024). Recent work from Research[x]Design, KU Leuven.
- **URL:** https://rxd.architectuur.kuleuven.be/projects/how-do-disabled-architects-design/
- **Key project:** "How Do Disabled Architects Design?" -- examines how architects with disabilities approach design differently and what this reveals about architectural knowledge.
- **Summary:** Heylighen's continued research demonstrates that disability experience generates architectural knowledge that visual-normative practice misses.
- **Relevance:** The strongest ongoing theoretical precedent for the project's thesis. Her research program and the project make the same argument through different methods -- she through empirical study, the project through tool-building.

### D.5 Cupkova, D., Wit, A.J., del Campo, M., and Claypool, M. (2023). "AI, Architecture, Accessibility, and Data Justice" (Editorial).
- **Venue:** IJAC -- ACADIA Special Issue
- **DOI:** 10.1177/14780771231171939
- **Summary:** Editorial examining tensions around technology, developing critical metrics, understanding implicit biases, and probing new methodologies for AI's impact in architecture. Addresses accessibility and data justice as intertwined concerns.
- **Relevance:** The ACADIA community's most direct engagement with accessibility as a computational design concern. The project's use of AI for architectural description responds directly to this call.

### D.6 Zallio, M. & Clarkson, P.J. (2023). "Challenges Designing Inclusive and Accessible Buildings."
- **Venue:** Architectural Science Review, Vol. 67, pp. 268–279
- **Summary:** Identifies specific challenges professionals face when designing accessibly, including lack of tools, training, and systematic approaches.
- **Relevance:** The project provides exactly the kind of tool-level intervention Zallio & Clarkson identify as missing.

### D.7 Karastathi, N., et al. (2024). "Bridging Pixels and Fabrication: Enhancing Accessibility in CNC Knitting for Architectural Design."
- **Venue:** ACADIA 2024 (Vanguard Award Winner)
- **URL:** https://discovery.ucl.ac.uk/id/eprint/10208145/
- **Summary:** Developed "Kniteretta," a Grasshopper plug-in connecting Kniterate with commonly used design software, simplifying workflows and enabling customizable designs.
- **Relevance:** ACADIA's growing recognition that "accessibility" means making specific tools usable by people currently excluded. The project's CLI-to-Rhino pipeline shares the same pattern: a bridge layer translating between an accessible interface and an inaccessible tool.

### D.8 del Campo, M. (2022–2024). AI and Architecture publications.
- **Books:** *Neural Architecture* (ORO, 2022); *Machine Hallucinations* (AD/Wiley, 2022); *Diffusions in Architecture* (Wiley, 2024)
- **Summary:** Establishes the ACADIA community's deep engagement with AI-architecture integration.
- **Relevance:** Context: none of del Campo's work addresses accessibility. The project's contribution is showing that AI-architecture tools can and must be accessible.

---

## Section E: Sonification & Aural Architecture

These works explore using sound as a medium for conveying spatial, structural, and design information -- a key future direction for the project.

### E.1 Schafer, R.M. (1977/1994). *The Soundscape: Our Sonic Environment and the Tuning of the World.*
- **Publisher:** Destiny Books
- **Summary:** Foundational text in acoustic ecology. Defines "soundscape" as the sum total of all sounds within a defined area. Proposes that acoustic design can improve sonic environments, combining resources from acoustics, architecture, linguistics, music, psychology, and urban planning.
- **Relevance:** Schafer's soundscape concept extends to architectural spaces. The project's sonification pipeline would create "soundscapes" of Daniel's designs, enabling him to evaluate spatial qualities (openness, enclosure, rhythm, density) through sound.

### E.2 Garcia, R. (1996). "Sound Structure: Using Data Sonification to Enhance Building Structures CAI."
- **Venue:** CAADRIA 1996, Hong Kong
- **URL:** https://cumincad.architexturez.net/doc/oai-cumincadworks-id-89ca
- **Summary:** Explores how teaching building structures through computers can be enhanced by sound parameters. Sound presents information such as structural response to static and dynamic loading.
- **Relevance:** An early and prescient paper applying sonification to architectural education. The project's planned sonification pipeline extends Garcia's structural sonification to spatial experience.

### E.3 Grabowski, N.A. and Barner, K.E. (1998). "Data Visualization Methods for the Blind Using Force Feedback and Sonification."
- **Venue:** SPIE 3524 (indexed in CumInCAD)
- **DOI:** 10.1117/12.333677
- **Summary:** Methods for adding aural feedback to a haptic force feedback interface, creating a multimodal visualization system. Sound pitch and spectral content convey information as users explore haptic surfaces.
- **Relevance:** Establishes the multimodal paradigm (haptic + auditory) that the project could adopt. The pegboard system already provides haptic input; adding sonification would create the kind of multimodal interface Grabowski and Barner envision.

### E.4 More, G., Harvey, L., and Burry, M. (2002). "Understanding Spatial Information with Integrated 3D Visual and Aural Design Applications."
- **Venue:** ACADIA 2002: Thresholds, Pomona
- **Summary:** Investigates how aural representations can complement or substitute for visual spatial information in design environments.
- **Relevance:** A rare ACADIA paper explicitly investigating aural representation of spatial information for design. Directly anticipates the project's approach.

### E.5 More, G., et al. (2004). "Designing Spatial Sounds for Spatial Information Environments."
- **Venue:** 22nd eCAADe Conference, Copenhagen
- **Summary:** Extends earlier work on spatial sound design, addressing how sound can convey spatial architectural information effectively.
- **Relevance:** Provides design principles for the project's planned sonification pipeline.

### E.6 Beilharz, K. (2005). "Architecture as the Computer Interface: 4D Gestural Interaction with Socio-Spatial Sonification."
- **Venue:** 23rd eCAADe Conference, Lisbon
- **Summary:** Gestural interaction producing real-time information sonification derived from socio-spatial data. Blurs boundaries between computational and spatial interaction.
- **Relevance:** The project's sonification goals parallel Beilharz's work but with a critical difference: the project's sonification serves a blind user navigating a design they are authoring, not monitoring an existing building.

### E.7 Blesser, B. & Salter, L.-R. (2007). *Spaces Speak, Are You Listening? Experiencing Aural Architecture.*
- **Publisher:** MIT Press
- **URL:** https://mitpress.mit.edu/9780262513173/spaces-speak-are-you-listening/
- **Summary:** Defines "aural architecture" -- how we experience space through listening. We navigate rooms in the dark and "hear" emptiness. Sound reveals spatial properties: reverberation time encodes room volume, early reflections encode wall proximity, frequency response encodes material.
- **Relevance:** The single most important text for the project's sonification direction. Blesser & Salter's aural architecture provides the mapping vocabulary the project's planned sonification pipeline needs.

### E.8 Navarro Villacampa, A., et al. (2025). "Sensing the Invisible: Architectural Approaches to Sonifying Microbial Life in Icelandic Turf Houses through VR."
- **Venue:** eCAADe 2025, Ankara
- **Summary:** Sonification of invisible environmental phenomena (microbial life) within architectural spaces.
- **Relevance:** Demonstrates growing interest in making the invisible audible in architectural contexts. The project proposes sonifying spatial data for a blind user's benefit.

---

## Section F: Haptic & Tactile Interfaces, Graphics & Fabrication

These papers address touch-based interfaces, tactile maps, swell paper, 3D-printed representations, and the production of tactile architectural media.

### F.1 Garcia, R. (1999). "PUSH: Generating Structural Form with Haptic Feedback."
- **Venue:** ACADIA '99, Salt Lake City
- **Summary:** Haptic feedback as a design interface for generating structural form. Designers physically feel forces and structural responses.
- **Relevance:** The project's pegboard system is a low-tech version of this concept: physical manipulation that translates to digital geometry.

### F.2 Sjostrom, C. (2002). "Non-Visual Haptic Interaction Design: Guidelines and Applications."
- **Venue:** PhD Dissertation, Certec, Lund University (indexed in CumInCAD)
- **URL:** https://lup.lub.lu.se/search/publication/a38cc004-1b0c-4ae7-bbf0-af227385cf01
- **Summary:** Investigates improving blind people's computer usage through virtual haptics. Develops guidelines for haptic interaction design specific to non-visual use.
- **Relevance:** Provides design guidelines directly applicable to the project. The thesis validates the project's approach of replacing visual CAD feedback with tactile and auditory alternatives.

### F.3 Pohl, I.M. and Hirschberg, U. (2011). "Sensitive Voxel: A Reactive Tangible Surface."
- **Venue:** CAAD Futures 2011, Liege, Belgium
- **Summary:** An interactive folded surface as a prototype for future interactive architectural surfaces, informed by physiological understandings of touch.
- **Relevance:** The project's pegboard system occupies a similar design space -- a physical surface serving as both input and representation.

### F.4 Koch, V., et al. (2012). "Haptic Paintings: Using Rapid Prototyping Technologies to Grant Visually Impaired Persons Access."
- **Venue:** 30th eCAADe Conference, Prague
- **URL:** https://www.blm.ieb.kit.edu/english/536_796.php
- **Summary:** Workflows for creating tactile representations of visual art and architecture. Laser-cut layered depth diagrams and CNC-milled textured reliefs for the sense of touch.
- **Relevance:** Directly relevant to the project's PIAF swell paper pipeline and tactile precedent library. The project's advantage is automation and integration with the CLI pipeline.

### F.5 Holloway, L. & Marriott, K. (2018). "Accessible Maps for the Blind: Comparing 3D Printed Models with Tactile Graphics."
- **Venue:** CHI 2018
- **URL:** https://dl.acm.org/doi/10.1145/3173574.3173772
- **Summary:** Controlled study with 16 touch readers comparing 3D printed models with tactile graphics (swell paper). 3D models were preferred, enabled more easily understood icons, facilitated better recall.
- **Relevance:** Directly informs the project's choice between 3D printing and PIAF swell paper. Their finding that 3D models better convey height suggests using 3D prints for sections and PIAF for plans.

### F.6 Tactile Architectural Drawings Typology (2022).
- **Venue:** Sustainability, MDPI, Vol. 14, No. 13, 7847
- **URL:** https://www.mdpi.com/2071-1050/14/13/7847
- **Summary:** Develops a typology of tactile architectural drawings accessible for blind and partially sighted people (typhlographics).
- **Relevance:** Provides a classification framework for the project's tactile output. The PIAF swell paper drawings the project produces are a form of typhlographic output.

### F.7 Butler, M., et al. (2023). "TactIcons: Designing 3D Printed Map Icons for People who are Blind or have Low Vision."
- **Venue:** CHI 2023
- **DOI:** https://doi.org/10.1145/3544548.3581359
- **Summary:** Designed and touch-tested over 200 tactile icons with blind and sighted participants. Resulted in 33 instantly recognizable and 34 easily learned icons.
- **Relevance:** Provides a design vocabulary for tactile architectural representations. The project's PIAF output could adopt similar icon conventions for columns, corridors, voids.

### F.8 FlexiBoard (2024). "Tangible and Tactile Graphics for People with Vision Impairments."
- **Venue:** Multimodal Technologies and Interaction (MDPI), Vol. 8, No. 3
- **Summary:** A flexible tangible interface for creating and interacting with tactile graphics.
- **Relevance:** Relevant to the project's pegboard system as an alternative physical input modality.

### F.9 MIT (2025). "Tactile Vega-Lite: Making Graphs More Accessible to Blind and Low-Vision Readers."
- **Venue:** MIT News / Research paper, March 2025
- **URL:** https://news.mit.edu/2025/making-graphs-more-accessible-blind-low-vision-readers-0325
- **Summary:** Program that takes spreadsheet data and generates both visual charts and tactile graphics automatically, using the Vega-Lite visualization grammar.
- **Relevance:** The automatic visual-to-tactile translation pattern is exactly what the project's export pipeline does (state.json to Rhino geometry to tactile PIAF export). Validates automatic conversion over manual recreation.

### F.10 Miele, J.A., Landau, S., & Gilden, D. (2006). "Talking TMAP: Automated Generation of Audio-Tactile Maps Using Smith-Kettlewell's TMAP Software."
- **Venue:** British Journal of Visual Impairment, Vol. 24, No. 2
- **URL:** https://journals.sagepub.com/doi/abs/10.1177/0264619606064436
- **Summary:** Describes the Tactile Map Automated Production (TMAP) system from Smith-Kettlewell Eye Research Institute -- a web application combining GIS data with braille embosser technology to produce tactile street maps on demand. The "Talking TMAP" extension adds audio-tactile capability via touch tablet: tapping map elements triggers spoken labels and sounds. Different levels of information are accessed through repeated tapping.
- **Relevance:** TMAP demonstrates that automated, on-demand tactile media production is feasible and transformative. A follow-up study (Biggs et al., 2022) found that access to TMAP increased blind users' map usage from less than one per year to dozens. The multi-layer information architecture (tap once for name, tap again for detail) parallels the CLI's `show` vs. `describe` commands. Miele's work also influenced shapeCAD, connecting tactile mapping to accessible 3D modeling.

### F.11 Brulé, E. & Bailly, G. (2021). "'Beyond 3D printers': Understanding Long-Term Digital Fabrication Practices for the Education of Visually Impaired or Blind Youth."
- **Venue:** CHI 2021
- **URL:** https://dl.acm.org/doi/10.1145/3411764.3445403
- **Summary:** Reports on a French organization's six-year experience (2013-2019) using digital fabrication for blind education. Traces how professionals defined how digital fabrication could and should be used. Argues for moving "beyond 3D printers" to hybrid approaches supported by laser cutters, documentation processes, and production at regional or national scale.
- **Relevance:** Provides longitudinal evidence that digital fabrication for blind education requires institutional infrastructure, not just individual tools. The shift from single-technology to hybrid approaches (laser cutters, swell paper, 3D prints) parallels the project's multi-output strategy. The emphasis on documentation and scalable production is relevant as the project considers dissemination beyond Daniel's individual use.

---

## Section G: Text-Based & Scripting Approaches to CAD

These papers explore alternatives to visual-only CAD interaction -- scripting, text-based interfaces, and programming environments that are inherently more accessible to screen readers.

### G.1 Nagakura, T. (1990). "Shape Recognition and Transformation: A Script-Based Approach."
- **Venue:** CAAD Futures '89, Cambridge, Massachusetts
- **Summary:** Script-based approaches to shape recognition and transformation in CAD environments, demonstrating early text-driven geometric operations.
- **Relevance:** An early precedent for text-driven geometry manipulation. The project's CLI commands like `set bay A rotation 30` are descendants of this script-based approach, refined for screen-reader accessibility.

### G.2 Nembrini, J., Labelle, G., et al. (2009). "Source Studio: Teaching Programming for Architectural Design."
- **Venue:** CAAD Futures 2009
- **Summary:** Approaches to teaching programming for architectural design, including framework development for object-oriented geometry.
- **Relevance:** Supports the pedagogical dimension: teaching architecture students to interact with geometry through code rather than visual manipulation.

### G.3 Celani, G. and Vaz, C.E.V. (2012). "CAD Scripting and Visual Programming Languages for Implementing Computational Design Concepts: A Comparison."
- **Venue:** IJAC, Vol. 10, No. 1, pp. 121-137
- **URL:** https://journals.sagepub.com/doi/abs/10.1260/1478-0771.10.1.121
- **Summary:** Compares scripting languages and visual programming languages (e.g., Grasshopper) for teaching computational design. Finds that scripting languages are fundamental for rule-based generative systems and more accessible to advanced automated workflows.
- **Relevance:** Directly supports the project's decision to use text-based (CLI) interaction rather than Grasshopper's visual canvas. The "advanced" scripting approach is also the "accessible" approach.

### G.4 Leitão, A., Santos, L., & Lopes, J. (2012). "Programming Languages for Generative Design: A Comparative Study."
- **Venue:** IJAC, Vol. 10, No. 1
- **Summary:** Compares visual programming languages with textual programming languages for architectural design. Finds that modern TPLs can be more productive than VPLs for large-scale and complex design tasks. Introduces Rosetta, a multi-language, multi-CAD generative design tool.
- **Relevance:** Empirical evidence that text-based interaction is not merely "accessible" but often *superior* for complex parametric tasks. The CLI's text-based approach is a design advantage the field should adopt more broadly.

### G.5 Maleki, M.M. and Woodbury, R.F. (2013). "Programming in the Model: A New Scripting Interface for Parametric CAD Systems."
- **Venue:** ACADIA 2013, pp. 183-190
- **URL:** https://summit.sfu.ca/item/14097
- **Summary:** PIM (Programming In the Model), a prototype with a live interface featuring side-by-side model and script windows with real-time updating.
- **Relevance:** PIM's bidirectional link between script and model prefigures the CLI-to-Rhino watcher pipeline. The key difference: PIM assumes both windows are visual; the project separates the text interface from the visual output entirely.

### G.6 CadQuery — Python Parametric CAD Scripting Framework.
- **URL:** https://github.com/CadQuery/cadquery
- **Summary:** Open-source Python library for parametric 3D CAD modeling. Users write Python scripts that produce CAD models using a fluent API designed for readability.
- **Relevance:** Validates the project's Python-stdlib-only approach. Script-based parametric modeling is a viable paradigm, not a workaround.

### G.7 Rietschel, M., Guo, F., and Steinfeld, K. (2024). "Mediating Modes of Thought: LLMs for Design Scripting."
- **Venue:** ACADIA 2024, Calgary
- **URL:** https://arxiv.org/abs/2411.14485
- **Summary:** LLMs mediate between user intent and algorithms. System includes LLM agents, an API, and a Grasshopper plugin parsing generated JSON. Users provide text prompts; LLM deduces design intent, maps to Grasshopper script, translates to JSON.
- **Relevance:** Extremely relevant. Describes a text-prompt-to-JSON-to-Grasshopper pipeline that closely parallels the project's CLI-to-JSON-to-Rhino pipeline. Critical insight: Rietschel et al. built this for convenience; the project built it for necessity.

### G.8 Rietschel, M. and Steinfeld, K. (2025). "Intelligent Tools on the Loose: Reasoning Models for Exploratory Computational Design."
- **Venue:** IJAC
- **DOI:** 10.1177/14780771251352945
- **Summary:** How reasoning language models can be utilized for early-stage exploratory design.
- **Relevance:** Extends toward the conversational, exploratory design interaction the project envisions through MCP -- where Daniel could ask "describe the north elevation" and receive an AI-generated spatial description.

### G.9 Xue, S. & Yen, J. (2009). "Natural Voice-Enabled CAD: Modeling via Natural Discourse."
- **Venue:** Computer-Aided Design and Applications, Vol. 6, No. 1, pp. 125-136
- **URL:** https://www.cad-journal.net/files/vol_6/CAD_6(1)_2009_125-136.pdf
- **Summary:** Proposes a CAD system accepting free-form natural language voice commands rather than fixed vocabularies. Uses "Verb-based CAD Semantic Search" with Phrase Identification and Targeted Word Distilling to parse natural discourse into executable CAD operations. Users say "draw me a circle that has a radius of 2.5 inches" rather than memorizing shortcut commands.
- **Relevance:** Foundational work on natural-language-first CAD interaction, directly parallel to the CLI approach. The system's core insight -- that CAD commands should accept natural discourse rather than requiring memorized vocabularies -- validates the project's principle that text/speech-based interfaces can be primary, not accommodative.

### G.10 Desolda, G., Esposito, A., Müller, F., & Feger, S. (2023). "Digital Modeling for Everyone: Exploring How Novices Approach Voice-Based 3D Modeling."
- **Venue:** CHI 2023
- **URL:** https://dl.acm.org/doi/10.1145/3544548.3581100
- **Summary:** Examines how novices approach 3D modeling through voice commands. Finds that users naturally structure voice commands hierarchically (creating objects, then modifying properties) and prefer spatial/relational descriptions over absolute coordinates. Users struggled most with specifying precise spatial relationships verbally.
- **Relevance:** Empirical evidence for how people naturally talk about 3D geometry. The finding that users prefer relational descriptions ("next to," "on top of") over coordinates validates the CLI's semantic approach (`set bay A rotation 30` rather than coordinate input). The precision challenge they identify is exactly what the CLI's structured command vocabulary solves -- constrained, unambiguous commands that avoid the imprecision of freeform speech.

---

## Section H: LLM-to-CAD, AI & Natural Language for Design

These papers represent the rapidly expanding field of using language models to generate 3D geometry -- the same core pattern as the project's CLI-to-JSON-to-Rhino pipeline, but typically without accessibility considerations.

### H.1 CAADRIA 2022. "Rhetoric, Writing, and Anexact Architecture: NLP and CV in Architectural Design."
- **Venue:** CAADRIA 2022, Sydney, Vol. 1, pp. 343-352
- **Summary:** Uses GPT-2 to generate architectural descriptions and Attentional GANs to translate text into visual form. Demonstrates AI's ability to do "architectural writing."
- **Relevance:** Demonstrates text-to-form translation. The project requires text-to-parametric-geometry (CLI-to-JSON) and geometry-to-text (AI-assisted description).

### H.2 Fu, R., et al. (2022). "ShapeCrafter: A Recursive Text-Conditioned 3D Shape Generation." NeurIPS 2022.
- **Summary:** Iteratively refines 3D shapes through sequential text instructions ("make the back taller," "add a wider seat"). Uses recursive conditioning to progressively modify geometry.
- **Relevance:** The iterative text-command paradigm mirrors the CLI's incremental command pattern.

### H.3 Yousif, S. and Vermisso, E. (2022). "Towards AI-Assisted Design Workflows for an Expanded Design Space."
- **Venue:** CAADRIA 2022, Sydney
- **URL:** https://papers.cumincad.org/cgi-bin/works/paper/caadria2022_503
- **Summary:** Integrating AI into design workflows to broaden exploration. Emphasizes how computational methods interconnect.
- **Relevance:** The "expanded design space" AI enables includes spaces previously inaccessible to blind designers. The project's AI critique partner extends this vision.

### H.4 Ma, Y., et al. (2023/2024). "3D-GPT: Intelligent 3D Modeling with Large Language Models."
- **Summary:** Decomposes 3D modeling tasks into sub-problems handled by LLM agents that generate procedural code (Blender Python scripts).
- **Relevance:** Very close to the CLI architecture -- LLMs generate text-based commands that drive geometry creation. The agent decomposition parallels the controller/watcher separation.

### H.5 Khan, S., et al. (2024). "Text2CAD: Generating Sequential CAD Designs from Beginner-to-Expert Level Text Prompts."
- **Venue:** NeurIPS 2024 (Spotlight)
- **URL:** https://sadilkhan.github.io/text2cad-project/
- **arXiv:** https://arxiv.org/abs/2409.17106
- **Summary:** First end-to-end transformer-based autoregressive architecture for generating parametric CAD models from natural language. ~660K text annotations for ~170K CAD models. Supports beginner to expert prompts.
- **Relevance:** Demonstrates that NL-to-parametric-geometry is a solved research problem. The project's CLI commands are a domain-specific version. Text2CAD validates the approach; the project shows it is *necessary* for a blind designer.

### H.6 Rietschel, M., et al. (2024). "Raven: AI Plugin for Grasshopper."
- **Venue:** ACADIA 2024 / UC Berkeley; commercial plugin 2025
- **URL:** https://www.raven.build/
- **Summary:** AI plugin for Grasshopper that uses LLMs to construct and refine parametric workflows from natural language prompts at multiple abstraction levels.
- **Relevance:** Makes Grasshopper text-controllable but still requires seeing the canvas. The project eliminates the visual dependency entirely.

### H.7 Wu, S., et al. (2024). "CAD-LLM: Large Language Model for CAD Generation."
- **Venue:** NeurIPS 2023 Workshop / Autodesk Research
- **URL:** https://www.research.autodesk.com/publications/ai-lab-cad-llm/
- **Summary:** Fine-tuning language models on engineering sketches. Leverages the sequential nature of CAD operations.
- **Relevance:** Establishes that language model architectures are well-suited to CAD's sequential, parametric nature -- the same property that makes CLI-based interaction natural.

### H.8 Atakan, A.O., et al. (2025). "Kakadoo: LLM Enabled Speech Interface for Enhanced Human-Computer Interaction."
- **Venue:** 43rd eCAADe Conference, Ankara
- **URL:** https://papers.cumincad.org/cgi-bin/works/paper/ecaade2025_348
- **Summary:** Grasshopper plugin leveraging speech recognition and LLM technology for natural language model manipulation. Voice-driven design for collaborative urban planning.
- **Relevance:** The most directly relevant recent CumInCAD paper. Kakadoo demonstrates voice/text-to-geometry is viable. The project's CLI achieves the same goal but for a user who cannot see the visual feedback at all.

### H.9 CADialogue (2025). "A Multimodal LLM-Powered Conversational Assistant for Intuitive Parametric CAD Modeling."
- **Venue:** Computer-Aided Design (ScienceDirect)
- **URL:** https://www.sciencedirect.com/science/article/abs/pii/S0010448525001678
- **Summary:** Conversational parametric CAD through natural language, speech, image inputs, and geometry selection.
- **Relevance:** The conversational paradigm is what the project envisions through MCP. CADialogue assumes multimodal (visual + text) input; the project needs text/speech-only.

### H.10 Grasshopper MCP Server (2025).
- **URL:** https://lobehub.com/mcp-dongwoosuk-rhino-grasshopper-mcp
- **Summary:** MCP server bringing AI capabilities directly into Rhino/Grasshopper workflows.
- **Relevance:** Validates that MCP transport works with Rhino/Grasshopper. The project uses file-watching as primary transport with MCP as future conversational layer.

### H.11 Ant (2026). "AI Copilot for Grasshopper."
- **Venue:** Food4Rhino plugin release, February 2026
- **URL:** https://blog.rhino3d.com/2026/02/ant-your-ai-copilot-for-grasshopper-new.html
- **Summary:** Builds, modifies, and explains Grasshopper definitions from natural language. Translates component logic for LLM processing.
- **Relevance:** Further evidence the community is moving toward text-to-geometry workflows. Like Raven, assumes sighted verification.

### H.12 El Hizmi, B., Shkolnik, A., Austern, G., & Sterman, Y. (2024). "LLMto3D: Generating Parametric Objects from Text Prompts."
- **Venue:** ACADIA 2024: Designing Change, Vol. 1, pp. 157-166
- **URL:** https://cdml-lab.github.io/LLMto3D/
- **Summary:** Multi-agent LLM pipeline translating natural language descriptions into parametric 3D objects. The first agent deconstructs textual prompts into design elements describing geometry and spatial relations. Unlike image-based 3D generation (NeRF, Gaussian Splatting), produces parametric CAD models that are printable, manufacturable, and dimensionally accurate.
- **Relevance:** The closest published work to the project's text-to-geometry ambition from within ACADIA. The multi-agent decomposition pattern (text prompt to semantic elements to parametric geometry) maps onto a potential CLI workflow. The gap: zero consideration of accessibility or non-visual verification. Published at the same venue the project targets.

### H.13 Jones, B.T., Hahnlein, F., Zhang, Z., Ahmad, M., Kim, V., & Schulz, A. (2025). "AIDL: A Solver-Aided Hierarchical Language for LLM-Driven CAD Design."
- **Venue:** Computer Graphics Forum (Pacific Graphics 2025). MIT CSAIL / U. Washington.
- **URL:** https://arxiv.org/abs/2502.09819
- **Summary:** Domain-specific language designed for LLMs to generate CAD geometry. Key insight: traditional CAD languages (OpenSCAD) assume a human verifying output visually; AIDL is designed for "blind" AI code generation. Features implicit geometry referencing (no precise coordinates needed), declarative constraints solved by external solvers, and hierarchical structure. GPT-4 with AIDL outperforms GPT-4 with OpenSCAD in few-shot prompting despite never having seen AIDL before.
- **Relevance:** Exceptionally relevant. AIDL's design philosophy -- that CAD languages should not require spatial reasoning or visual verification from the code author -- maps directly onto the project's thesis. The hierarchical, constraint-based approach (declare relationships, let solvers handle coordinates) is exactly the semantic-over-geometric principle in the project's architecture. A CLI speaking in AIDL-like terms ("column at intersection of bay A and corridor B") rather than coordinates is both LLM-friendly and blind-user-friendly. The strongest theoretical ally for the project's approach from the ML/graphics community.

### H.14 Di Marco, G. (2025). "Agentic, Multimodal LLM for Conversational Architectural Design."
- **Venue:** Architectural Science Review (published online November 2025)
- **URL:** https://www.tandfonline.com/doi/full/10.1080/00038628.2025.2586655
- **Summary:** Proposes ConvoAI, an agentic multimodal LLM integrating behavioral modes and self-iteration for conversational design. Validated in a six-week studio with 11 master's students. Three engagement patterns emerged: Design Partner (problem-space redefinition), Concept Clarifier (visualization + dialogue), Design Assistant (workflow acceleration).
- **Relevance:** New entrant in conversational AI for architecture. The "Design Partner" mode -- AI reframing design problems through dialogue -- is most relevant to the project's MCP direction. A conversational agent helping Daniel explore design alternatives through text dialogue rather than visual manipulation. The behavioral modes concept (different AI personas for different design phases) could inform how the project structures its MCP integration.

---

## Section I: Accessible Tools, Modeling & Visualization for Blind Users

These papers directly address enabling blind and low-vision users to create, interact with, and understand visual content -- the project's core problem space.

### I.1 Potluri, V., et al. (2018). "CodeTalk: Improving Programming Environment Accessibility for Visually Impaired Developers."
- **Venue:** CHI 2018 (Honorable Mention)
- **DOI:** https://doi.org/10.1145/3173574.3174192
- **Summary:** Categorizes IDE accessibility difficulties into Discoverability, Glanceability, Navigability, and Alertability (DGNA). Implements CodeTalk plugin for Visual Studio.
- **Relevance:** The DGNA framework evaluates the project's CLI design. The OK:/ERROR: prefix convention addresses Glanceability and Alertability; the help system addresses Discoverability; sequential command structure addresses Navigability.

### I.2 Siu, A.F., Kim, S., et al. (2019). "shapeCAD: An Accessible 3D Modelling Workflow for the Blind and Visually-Impaired Via 2.5D Shape Displays."
- **Venue:** ASSETS '19
- **URL:** https://dl.acm.org/doi/10.1145/3308561.3353782
- **Summary:** 3D models generated through OpenSCAD (declarative programming language) and rendered on a 2.5D shape display (12x24 actuated pins). Blind users leverage low-resolution output to complement programming of 3D models.
- **Relevance:** The most directly comparable system. shapeCAD also uses text-based programming for blind 3D modeling. The project differs: (1) domain-specific CLI rather than general programming language; (2) architectural-scale design; (3) integrates with industry-standard Rhino.

### I.3 Shi, L., Zhao, Y., et al. (2020). "Molder: An Accessible Design Tool for Tactile Maps."
- **Venue:** CHI 2020
- **URL:** https://rgonzalezp.github.io/research/2020-04-03-Molder/
- **Summary:** Accessible tool for creating tactile maps. Addresses the problem that O&M specialists who design tactile materials are often visually impaired themselves.
- **Relevance:** Shares the project's insight that the *creators* of accessible materials are often disabled and need accessible authoring tools. Molder and the project address analogous problems at different scales.

### I.4 Stangl, A., et al. (2021). "Going Beyond One-Size-Fits-All Image Descriptions."
- **Venue:** ASSETS '21
- **URL:** https://cs.stanford.edu/~merrie/papers/assets2021_scenarios.pdf
- **Summary:** Studies what information blind users want from image descriptions, finding needs vary by context and purpose.
- **Relevance:** Directly informs how the project's AI description pipeline should generate architectural descriptions for Daniel -- different for design review, spatial navigation, precedent study, and critique.

### I.5 Lundgard, A. & Satyanarayan, A. (2022). "Accessible Visualization via Natural Language Descriptions: A Four-Level Model of Semantic Content."
- **Venue:** IEEE Transactions on Visualization and Computer Graphics, Vol. 28, No. 1
- **arXiv:** https://arxiv.org/abs/2110.04406
- **Summary:** Four-level model: L1 (construction -- chart type, axes), L2 (statistics -- extremes, correlations), L3 (trends -- patterns), L4 (context -- domain insights). Based on 2,147 sentences.
- **Relevance:** The CLI's `show` and `describe` commands could be structured around these four levels: L1 (what elements exist), L2 (dimensions), L3 (spatial relationships), L4 (design implications).

### I.6 Potluri, V., et al. (2022). "CodeWalk: Facilitating Shared Awareness in Mixed-Ability Collaborative Software Development."
- **Venue:** ASSETS '22
- **Summary:** Addresses collaborative coding between sighted and blind developers, focusing on shared awareness.
- **Relevance:** The project's controller/viewer separation enables a similar mixed-ability collaboration: Daniel works in the CLI (accessible), a sighted collaborator observes in Rhino (visual).

### I.7 Sharif, A., et al. (2022). "Understanding Screen-Reader Users' Experiences with Online Data Visualizations." EuroVIS 2022.
- **Summary:** Studies how screen reader users navigate and understand data visualizations, identifying common failure patterns.
- **Relevance:** Informs how the project's visual output from Rhino should be accompanied by structured text descriptions.

### I.8 Practical CAD Method for the Visually Impaired (2023).
- **Venue:** Universal Access in Human-Computer Interaction, Springer (LNCS)
- **URL:** https://link.springer.com/chapter/10.1007/978-3-031-35681-0_29
- **Summary:** A practical CAD method for visually impaired users. Addresses the challenge that existing CAD software is mostly visually reliant.
- **Relevance:** Confirms the problem the project addresses is recognized across the HCI and accessibility communities. The project's approach is more radical: building a non-visual-first interface layer.

### I.9 Billah, S.M., et al. (2023). "Designing While Blind: Nonvisual Tools and Inclusive Workflows for Tactile Graphic Creation."
- **Venue:** ASSETS '23
- **DOI:** https://doi.org/10.1145/3597638.3614546
- **Summary:** Blind-led team of four Blind designers, one sighted designer, and one sighted researcher designing tactile graphics. Found that inaccessible digital tools prevent Blind people from leading the design of media they consume.
- **Relevance:** **Critically important.** The central argument -- that blind designers are excluded from creating the very media they consume -- is the exact problem the project solves. The CLI-to-PIAF pipeline enables Daniel to *author* tactile architectural drawings, not just receive them.

### I.10 Crawford, S., et al. (2024). "Co-designing a 3D-Printed Tactile Campus Map With Blind and Low-Vision University Students."
- **Venue:** ASSETS '24
- **DOI:** https://doi.org/10.1145/3663548.3688537
- **Summary:** Participatory design with BLV students. During co-design, the participant's screen reader was unable to interpret TinkerCAD's interface.
- **Relevance:** Powerfully demonstrates the accessibility failure the project addresses -- even "simple" CAD tools are screen-reader-incompatible. The project's CLI-first architecture directly solves this.

### I.11 Das, M., Adnin, R., et al. (2024). "'I look at it as the king of knowledge': How Blind People Use and Understand Generative AI Tools."
- **Venue:** ASSETS '24
- **URL:** https://maitraye.github.io/files/papers/BLV_GenAI_ASSETS24.pdf
- **Summary:** Interviews with 19 blind individuals on their use of GenAI tools. Blind users face significant accessibility barriers even in AI interfaces.
- **Relevance:** Validates the project's decision to build a purpose-designed, screen-reader-native CLI rather than relying on existing AI chat interfaces.

### I.12 MAIDR + AI (2024). "Exploring Multimodal LLM-Based Data Visualization Interpretation by and with Blind and Low-Vision Users."
- **Venue:** ASSETS '24
- **DOI:** https://doi.org/10.1145/3663548.3675660
- **Summary:** Co-designed an LLM extension providing multiple AI responses to blind users' visual queries about data visualizations.
- **Relevance:** The "AI as interpretation layer" pattern is what the project needs for describing Rhino viewport content to Daniel.

### I.13 CHI 2024. "Investigating Use Cases of AI-Powered Scene Description Applications for Blind and Low Vision People."
- **Venue:** CHI 2024
- **DOI:** https://doi.org/10.1145/3613904.3642211
- **Summary:** Examines how BLV users employ AI scene description tools (Be My Eyes, Seeing AI) in real-world contexts.
- **Relevance:** The project's Ray-Ban Meta glasses pipeline uses exactly these AI-powered scene description tools.

### I.14 Siu, A., et al. (2025). "A11yShape: AI-Assisted 3-D Modeling for Blind and Low-Vision Programmers."
- **Venue:** ASSETS '25
- **DOI:** https://doi.org/10.1145/3663547.3746362
- **arXiv:** https://arxiv.org/abs/2508.03852
- **Summary:** Combines OpenSCAD with GPT-4o for accessible 3D modeling. Four-facet representation: source code, hierarchical model abstraction, AI-generated textual descriptions, and rendered output. Four BLV participants completed modeling tasks (SUS: 80.6).
- **Relevance:** **The most directly comparable recent system.** Key differences: (1) A11yShape targets general 3D modeling; the project targets architectural design; (2) A11yShape is integrated; the project's decoupled architecture enables independent blind/sighted collaboration; (3) the project's CLI output protocol is screen-reader-specific (OK:/ERROR:).

### I.15 Madugalla, A., Marriott, K., Marinai, S., Capobianco, S., & Goncu, C. (2020). "Creating Accessible Online Floor Plans for Visually Impaired Readers."
- **Venue:** ACM Transactions on Accessible Computing (TACCESS), Vol. 13, No. 4, Article 15
- **URL:** https://dl.acm.org/doi/10.1145/3410446
- **Summary:** Generic model for providing blind readers with access to online floor plans. Supports semi-automatic transcription of architectural drawings into three output formats: text-only descriptions, tactile graphics, and touchscreen displays with audio feedback. Formative user study determined what information blind users need from floor plans; second study evaluated outputs.
- **Relevance:** Directly addresses the gap the project fills. Blind users cannot access conventional architectural floor plans. The multi-modal output approach (text, tactile, audio) aligns with the project's strategy. The finding that users want both overview and detailed room-by-room information validates the CLI's `show` and `describe` command patterns.

### I.16 Clepper, G., McDonnell, E.J., Findlater, L., & Peek, N. (2025). "'What Would I Want to Make? Probably Everything': Practices and Speculations of Blind and Low Vision Tactile Graphics Creators."
- **Venue:** CHI 2025
- **URL:** https://dl.acm.org/doi/10.1145/3706598.3714173
- **Summary:** Interviews 14 blind and low-vision adults who both use and create tactile graphics. Finds that tactile graphics are intensely valued but access and fluency are compounding challenges. BLV makers constantly navigate tradeoffs between accessible low-fidelity craft materials and less accessible high-fidelity equipment. Centers BLV people as *creators*, not just consumers.
- **Relevance:** Extremely high. Provides the closest published parallel to Daniel's position as a blind person creating design artifacts. The tradeoff between accessible low-fidelity tools and inaccessible high-fidelity tools is exactly the problem the project solves: making high-fidelity CAD (Rhino) operable through an accessible interface (CLI). Cite as evidence that the project addresses a documented, underserved need.

### I.17 Flores-Saviaga, C., Hanrahan, B.V., Imteyaz, K., Clarke, S., & Savage, S. (2025). "The Impact of Generative AI Coding Assistants on Developers Who Are Visually Impaired."
- **Venue:** CHI 2025
- **URL:** https://arxiv.org/abs/2503.16491
- **Summary:** Studies 10 visually impaired developers using GitHub Copilot through an Activity Theory framework. Finds that AI assistants are beneficial but exacerbate accessibility barriers: excessive suggestion volume, difficult context-switching between AI-generated and user-authored code, and a desire for "AI timeouts." A longitudinal follow-up found participants shifted from Agent mode (AI does everything) to Ask mode (AI answers questions).
- **Relevance:** Directly relevant as a cautionary tale for integrating AI into the CLI. The project must avoid the "suggestion flood" problem. The CLI's explicit command-response model (type command, get OK/ERROR) is better suited to screen readers than inline suggestions. The finding that blind programmers preferred Ask mode validates the project's philosophy: the CLI remains the primary control surface, and AI features should be consultative rather than autonomous.

### I.18 Seo, J.Y., et al. (2024). "Designing Born-Accessible Courses in Data Science and Visualization."
- **Venue:** Eurographics / IEEE VGTC Conference on Visualization; arXiv:2403.02568
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC11872190/
- **Summary:** Presents a "born-accessible" approach to teaching data science -- courses designed from the ground up for blind learners, taught by blind instructors, rather than retrofitting accessibility. Nine blind learners participated in a two-week summer course. JooYoung Seo is at UIUC.
- **Relevance:** The "born-accessible" concept is the pedagogical parallel to the project's "accessibility-first" design principle. The project's CLI tools are "born-accessible CAD" -- designed for blindness from the start, not accommodated after the fact. Seo's course design methodology could inform the project's approach to teaching architecture students to use the tools. As a UIUC colleague, Seo represents a natural collaboration target.

### I.19 Gurita, A.-E. & Vatavu, R.-D. (2025). "When LLM-Generated Code Perpetuates User Interface Accessibility Barriers, How Can We Break the Cycle?"
- **Venue:** 22nd International Web for All Conference (W4A '25), Sydney
- **URL:** https://dl.acm.org/doi/10.1145/3744257.3744266
- **Summary:** Tests whether accessibility-oriented prompting affects WCAG compliance in LLM-generated UIs. Surprisingly, UIs generated with accessibility-oriented prompts had a slightly higher violation rate (17.32%) vs. accessibility-agnostic prompts (15.93%), though they performed better on key criteria (focus visibility, info & relationships).
- **Relevance:** Relevant to the project's MCP/AI integration. If an AI agent generates interface elements, accessibility cannot be assumed -- it must be enforced by system architecture. Validates the project's approach of baking accessibility into the CLI output protocol (OK:/ERROR: prefixes, labeled lines) rather than relying on AI to generate accessible output spontaneously.

---

## Section J: Pipelines, Interoperability & Pedagogy

These papers address data exchange infrastructure, computational design teaching, and pipeline challenges relevant to the project's CLI-to-JSON-to-Rhino architecture.

### J.1 Miller, N. (2010). "[make]SHIFT: Information Exchange and Collaborative Design Workflows."
- **Venue:** ACADIA 2010, New York, pp. 139-144
- **DOI:** https://doi.org/10.52842/conf.acadia.2010.139
- **Summary:** Customized design workflows for information exchange across multidisciplinary teams. Non-standard workflows enable collaboration when teams use diverse software.
- **Relevance:** The project's file-watching pipeline is the kind of "non-standard workflow" Miller describes -- enabling collaboration between a blind CLI user and a sighted Rhino user through a shared JSON artifact.

### J.2 Janssen, P. and Chen, K.W. (2011). "Visual Dataflow Modelling: A Comparison of Three Systems."
- **Venue:** CAAD Futures 2011, Liege, Belgium
- **Summary:** Compares three visual dataflow systems for parametric design, analyzing representational and computational characteristics.
- **Relevance:** By comparing visual dataflow systems, this paper implicitly reveals what is lost when the only interface is visual. The project's text-based alternative must provide equivalent expressive power through sequential, screen-reader-compatible commands.

### J.3 Fricker, P., Kotnik, T., and Borg, K. (2020). "Computational Design Pedagogy for the Cognitive Age."
- **Venue:** 38th eCAADe Conference, TU Berlin
- **URL:** https://papers.cumincad.org/cgi-bin/works/paper/ecaade2020_255
- **Summary:** Integrative computational design thinking requiring the melding of computation, design, and theory. Emphasizes computational thinking as analysis across multiple scales.
- **Relevance:** The project demonstrates that computational design thinking does not require visual cognition. Daniel's CLI interaction exemplifies computational design thinking through a purely textual/auditory cognitive mode.

### J.4 Akbar, Z., Ron, G., and Wortmann, T. (2023). "Democratizing the Designer's Toolbox."
- **Venue:** 41st eCAADe Conference, Graz
- **URL:** https://papers.cumincad.org/cgi-bin/works/paper/ecaade2023_311
- **Summary:** Computational design education where students develop workflows beyond specific software platforms, working directly on coordinates and numerical representations.
- **Relevance:** The project is the radical version: not just platform-agnostic but modality-agnostic. By building on Python stdlib with zero dependencies, the most accessible computational design tool is also the most portable and democratic.

### J.5 Sass, L. (2024). ACADIA Teaching Award of Excellence.
- **Venue:** ACADIA 2024 ("Designing Change"), Calgary
- **URL:** https://www.archpaper.com/2025/02/acadia-2024-research-innovation-computational-design/
- **Summary:** Larry Sass (MIT Department of Architecture) received the ACADIA Teaching Award of Excellence for his innovative pedagogical approaches that center digital fabrication and making as an integral part of the design process. Sass founded the MIT Design Fabrication Group and has taught digital fabrication and design computing since 2002, developing curricula where students move fluidly between computational representation and physical production.
- **Relevance:** Sass's pedagogy — centering fabrication as a design method, not just an output step — parallels the project's approach to physical-digital round-tripping. Where Sass treats fabrication as integral to design thinking, the project treats tactile output (PIAF, 3D prints, pegboard) as integral to spatial cognition. The Teaching Award recognizing this fabrication-first pedagogy suggests ACADIA values the same design-through-making ethos that underpins the project's tactile pipeline.

### J.6 UT Austin School of Architecture (2023). "If buildings were invisible, what of architecture would remain?"
- **Venue:** Graduate design studio, University of Texas at Austin, Spring 2023
- **URL:** https://soa.utexas.edu/news/if-buildings-were-invisible-what-architecture-would-remain
- **Summary:** Graduate studio tasking students with designing a new building for the Texas School for the Blind and Visually Impaired (TSBVI). Students researched universal design strategies for wayfinding, placemaking, and wellness. Studio collaborated with TSBVI staff who hosted campus visits and led cane training. Final reviews included Chris Downey as critic.
- **Relevance:** One of very few documented cases of an architecture studio directly engaging with blindness as a design condition. However, the blind experience remains the *subject* being designed for, not a tool-level transformation -- students used conventional visual tools. This contrasts with the project, where the blind student is authoring geometry through a CLI rather than being a user whose needs are interpreted by sighted designers.

### J.7 NAAB (2020). *Conditions for Accreditation, 2020 Edition.*
- **Venue:** National Architectural Accrediting Board (regulatory document, revised 2023)
- **URL:** https://www.naab.org/accreditation/accreditation-criteria
- **Summary:** Includes "Equity, Diversity, and Inclusion" as a shared value. Condition 5.5 addresses Social Equity, requiring programs to "describe the resources and procedures in place to provide adaptive environments" for students with different needs. Student Performance Criterion PC.8 requires students to understand how design affects diverse users. However, no specific guidance on making design tools, critique formats, or fabrication processes accessible.
- **Relevance:** NAAB standards address disability in building design (PC.8) and student support (5.5), but are vague about *how* programs accommodate disabled students in studio-based learning. No guidance on accessible CAD tools or alternative critique formats. This gap means accommodating a blind architecture student falls entirely on individual programs -- exactly the situation the project addresses by providing tools.

---

## Section K: Architectural Representation & the Politics of Design Media

These works theorize how representational media (drawings, software, algorithms) actively shape what can be designed and who can design it. They provide the argument that changing the medium of architectural interaction is not an accommodation but an epistemological intervention.

### K.1 Evans, R. (1997). *Translations from Drawing to Building and Other Essays.*
- **Publisher:** MIT Press / AA Publications
- **URL:** https://mitpress.mit.edu/9780262550277/translations-from-drawing-to-building-and-other-essays/
- **Summary:** The definitive text arguing that architectural drawings are not transparent windows onto design intent but active, opaque media that shape, filter, and transform design. The "translation" from drawing to building is productive, not reproductive: it generates surplus meaning, creative possibilities, and "mistakes" that would not exist without the specific characteristics of the representational medium. Every drawing convention -- plan, section, elevation, axonometric, perspective -- carries assumptions about spatial experience and bodily occupation that privilege certain outcomes and suppress others.
- **Relevance:** Provides the single strongest theoretical foundation for the project's core claim. If the architectural drawing is an active agent that shapes what can be designed, then the CLI is equally active. The project's text commands, JSON state files, and screen-reader output are not impoverished substitutes for drawings -- they are a different representational medium that will generate different architectural possibilities, different "translations," different surplus meanings. Evans transforms the project from an accessibility accommodation into an epistemological proposition: changing the medium of architectural representation changes what architecture can be.

### K.2 Lynn, G. (1999). *Animate Form.*
- **Publisher:** Princeton Architectural Press
- **Summary:** The canonical text of the first digital turn's visual-computational paradigm. Used high-end animation software (Maya, 3D Studio) to generate architecture through topological geometries and time-based techniques. Introduced vocabulary -- blobs, hypersurfaces, polysurfaces -- for biomorphic shapes generated through force fields and motion. The accompanying CD-ROM exemplified interactive visual design exploration.
- **Relevance:** Lynn demonstrates how a specific tool (animation software) generated an entire architectural vocabulary and sensibility -- smooth, curving forms that could not have been conceived without that particular medium. This is strong evidence for the thesis that tools shape design thinking. The CD-ROM, a visual-interactive medium, exemplifies the ocularcentrism the project critiques. The project's non-visual alternative represents a fundamentally different response to the same question of how computation reshapes architecture.

### K.3 Kolarevic, B., ed. (2003). *Architecture in the Digital Age: Design and Manufacturing.*
- **Publisher:** Spon Press / Taylor & Francis
- **URL:** https://www.taylorfrancis.com/books/edit/10.4324/9780203634561/architecture-digital-age-branko-kolarevic
- **Summary:** Compiles contributions on how digital technologies radically change the conception, design, and production of buildings. Organized around digital morphogenesis, digital production, building information modeling, and performance-based design. Documents the moment when digital fabrication collapsed the distance between design file and built artifact -- the "file-to-factory" paradigm.
- **Relevance:** The "file-to-factory" concept maps directly onto the project's "JSON-to-Rhino" pipeline, where a canonical data file drives downstream realization. The book's emphasis on associative and parametric design aligns with storing design intent semantically rather than geometrically. The critical difference: Kolarevic's contributors universally assume visual-interactive workflows; the project demonstrates the same file-to-factory logic works through text-only interfaces.

### K.4 Allen, S. (2009). *Practice: Architecture, Technique and Representation.* 2nd ed.
- **Publisher:** Routledge
- **URL:** https://www.routledge.com/Practice-Architecture-Technique-and-Representation/Allen/p/book/9780415776257
- **Summary:** Argues that architectural concepts emerge through the materials and procedures of practice -- drawing conventions, notational systems, construction logics -- not from outside the discipline. His essay "Mapping the Unmappable: On Notation" directly addresses how notational systems structure design thinking. "Field Conditions" proposes bottom-up organizational logics rather than top-down compositional hierarchies.
- **Relevance:** If concepts emerge from representational practices, then a CLI-first workflow generates different architectural thinking. The project's command vocabulary (`set bay A rotation 30`, `corridor A width 8`) constitutes a notational system that, by Allen's logic, produces its own kind of architectural intelligence. The "Field Conditions" emphasis on bottom-up design also resonates with the project's semantic, component-based approach.

### K.5 Picon, A. (2010). *Digital Culture in Architecture.*
- **Publisher:** Birkhäuser
- **URL:** https://birkhauser.com/en/book/9783034602594
- **Summary:** Treats digital tools not as mere software applications but as a *culture* -- a way of thinking, communicating, and organizing practice that reshapes the entire architectural enterprise. Examines the influence of digital culture on architecture, urban design, and product design, arguing that digital simulation leads to increasingly strategic, scenario-based approaches.
- **Relevance:** If CAD software constitutes a culture, then that culture's assumptions about interaction (visual, mouse-driven) are cultural commitments, not neutral technical choices. The project's CLI culture -- text-based, command-driven, screen-reader-native -- constitutes an alternative digital culture in architecture, with its own norms, aesthetics, and modes of design thinking.

### K.6 Carpo, M. (2011). *The Alphabet and the Algorithm.*
- **Publisher:** MIT Press (Writing Architecture Series)
- **URL:** https://mitpress.mit.edu/9780262515801/the-alphabet-and-the-algorithm/
- **Summary:** Traces two pivotal moments of "identicality": Alberti's invention of architectural design (building as identical copy of drawing) and industrial mass production. Argues the digital age ends identicality -- everything digital is inherently variable. Charts the rise and fall of the identical, comparing postindustrial digital craftsmanship to pre-industrial hand-making. Proposes a new agenda for variable objects, generic authorship, and participatory design.
- **Relevance:** Carpo's core thesis -- that the representational medium (alphabetic notation vs. algorithmic computation) fundamentally structures what can be designed and who can author it -- directly supports the project. If Alberti's system of identical-copy design privileged the eye and the drawing, then CLI-driven text-based parametric tools represent a genuinely different paradigm of authorship. The project's JSON state (variable, non-identical) aligns with the digital variability Carpo describes.

### K.7 Carpo, M. (2017). *The Second Digital Turn: Design Beyond Intelligence.*
- **Publisher:** MIT Press (Writing Architecture Series)
- **URL:** https://mitpress.mit.edu/9780262534024/the-second-digital-turn/
- **Summary:** Distinguishes two digital turns. The first (1990s CAD/CAM) changed ways of making -- smooth, curving forms. The second changes ways of thinking: tools are now driven by big data, machine learning, and computational search rather than parametric optimization. Designers employ simulation and aggregation to discover forms, bypassing conventional deductive reasoning.
- **Relevance:** The "second digital turn" framework theorizes the project's AI-assisted workflows (Claude API, conversational agents) as part of a broader disciplinary shift. If the first turn privileged visual-spatial manipulation, the second turn's emphasis on search, data, and machine thinking opens space for non-visual interfaces. A blind user working through text and AI dialogue may be a more advanced instantiation of the second digital turn than a sighted user dragging sliders in Grasshopper.

### K.8 Burry, M. (2011). *Scripting Cultures: Architectural Design and Programming.*
- **Publisher:** Wiley
- **URL:** https://onlinelibrary.wiley.com/doi/book/10.1002/9781118670538
- **Summary:** Argues that scripting -- writing code to customize, extend, or bypass standard CAD software -- constitutes a genuine design method, not merely a technical skill. Treats scripting as both a practical challenge and a cultural/theoretical phenomenon. Demonstrates through case studies (including the Sagrada Familia) that programming enables designers to work around constraints embedded in commercial software.
- **Relevance:** Burry's central argument -- that scripting lets designers escape constraints embedded in standard tools -- is the theoretical backbone of the project. Commercial CAD embeds assumptions about visual interaction; the project's Python CLI is exactly the "scripting culture" Burry describes: a bespoke tool bypassing Rhino's GUI. His emphasis on scripting as cultural practice (not just workaround) elevates the project from "accessibility accommodation" to "design methodology."

### K.9 Easterling, K. (2014). *Extrastatecraft: The Power of Infrastructure Space.*
- **Publisher:** Verso
- **URL:** https://www.versobooks.com/products/30-extrastatecraft
- **Summary:** Argues that infrastructure is not merely pipes and wires but the hidden rules structuring spaces of everyday life -- free trade zones, smart cities, suburbs, broadband networks, and international standards. Infrastructure space operates as an "operating system" governed by protocols and spatial products beyond traditional governance. Understanding infrastructure as active political medium opens new techniques for resistance.
- **Relevance:** The "infrastructure space" of architectural education -- Rhino's GUI, Grasshopper's canvas, the assumption that design happens on a screen -- constitutes hidden rules that include and exclude. When built around visual interaction, this infrastructure structurally excludes blind designers as thoroughly as any physical barrier. The project's file-watching architecture (CLI to JSON to Rhino watcher) builds alternative infrastructure space for design -- new protocols encoding different assumptions about who can be a designer.

### K.10 Deamer, P. (2015/2020). *The Architect as Worker* (2015) / *Architecture and Labor* (2020).
- **Publisher:** Bloomsbury Academic (2015); Routledge (2020)
- **URL:** https://www.routledge.com/Architecture-and-Labor/Deamer/p/book/9780367343507
- **Summary:** Examines the architecture profession through the lens of labor. Argues that tools are not neutral instruments but structures of labor determining who works, how they work, and whose contributions are valued. Analyzes the "schizophrenic" split between parametric tools (young, avant-garde) and BIM (old, managerial), demonstrating how tool categories create hierarchies among architectural workers. Addresses CAD/CAM's transformation of labor organization. Deamer is founding member of the Architecture Lobby.
- **Relevance:** Screen-based CAD tools constitute a labor structure that renders certain kinds of design work (visual-spatial manipulation) legible and valued while making other kinds (semantic, text-based, tactile) invisible. The project's CLI tools are, in Deamer's terms, a reorganization of architectural labor that makes a blind designer's work visible and authoritative. Her framework shows that the project is not just making tools accessible but restructuring the conditions of architectural production.

---

## Summary Table

| # | Citation | Year | Venue | S |
|---|---------|------|-------|---|
| 1 | Merleau-Ponty, *Phenomenology of Perception* | 1945 | Routledge | A |
| 2 | Gibson, *Ecological Approach to Visual Perception* | 1979 | Psychology Press | A |
| 3 | Jay, *Downcast Eyes* | 1993 | UC Press | A |
| 4 | Holl, Pallasmaa & Pérez-Gómez, *Questions of Perception* | 1994 | A+U / Stout | A |
| 5 | Pallasmaa, *Eyes of the Skin* | 1996 | Wiley | A |
| 6 | Zumthor, *Atmospheres* | 2006 | Birkhäuser | A |
| 7 | Pérez-Gómez, *Attunement* | 2016 | MIT Press | A |
| 8 | Böhme, *Aesthetics of Atmospheres* | 2017 | Routledge | A |
| 9 | Schön, *The Reflective Practitioner* | 1983 | Basic Books | A |
| 10 | Varela, Thompson & Rosch, *The Embodied Mind* | 1991 | MIT Press | A |
| 11 | Clark & Chalmers, "The Extended Mind" | 1998 | Analysis | A |
| 12 | Sennett, *The Craftsman* | 2008 | Yale UP | A |
| 13 | Ingold, *Making* | 2013 | Routledge | A |
| 14 | Piaget & Inhelder, *Child's Conception of Space* | 1956 | Routledge | B |
| 15 | Millar, *Understanding and Representing Space* / *Space and Sense* | 1994/2008 | OUP / Psychology Press | B |
| 16 | Thinus-Blanc & Gaunet, "Representation of space in blind" | 1997 | Psychological Bulletin | B |
| 17 | Loomis, Klatzky & Golledge, "Cognitive Mapping without Vision" | 2001 | Springer | B |
| 18 | Hatwell, Streri & Gentaz, *Touching for Knowing* | 2003 | John Benjamins | B |
| 19 | Saerberg, "Blind Pedestrians" | 2010 | Senses and Society | B |
| 20 | Cattaneo & Vecchi, *Blind Vision* | 2011 | MIT Press | B |
| 21 | Herssens & Heylighen, "Haptic Design Parameters" | 2011 | CAAD Futures | B |
| 22 | Vermeersch & Heylighen, "Carlos Mourao Pereira" | 2012 | Research proceedings | B |
| 23 | Celani et al., "'Seeing' with the Hands" | 2013 | CAAD Futures | B |
| 24 | Heylighen & Herssens, "Designerly Ways of Not Knowing" | 2014 | J. Urban Design | B |
| 25 | Reynolds, "World-Creating Blindness" | 2017 | Chiasmi International | B |
| 26 | Giudice, "Navigating without Vision" | 2018 | Springer | B |
| 27 | Vermeersch et al., "Designing from Disability Experience" | 2018 | PDC | B |
| 28 | Chen et al., "Perception beyond sight" | 2024 | ScienceDirect | B |
| 29 | Downey, Chris (blind architect) | 2008+ | TED / Practice | B |
| 30 | Winner, "Do Artifacts Have Politics?" | 1980 | Daedalus | C |
| 31 | Charlton, *Nothing About Us Without Us* | 1998 | UC Press | C |
| 32 | Pullin, *Design Meets Disability* | 2009 | MIT Press | C |
| 33 | Mankoff et al., "Disability Studies for AT" | 2010 | ASSETS | C |
| 34 | Shinohara & Wobbrock, "Shadow of Misperception" | 2011 | CHI (Best Paper) | C |
| 35 | Wobbrock et al., "Ability-Based Design" | 2011 | ACM TACCESS | C |
| 36 | Imrie, "Universalism" | 2012 | Disability & Rehab | C |
| 37 | Steinfeld & Maisel, *Universal Design* | 2012 | Wiley | C |
| 38 | Boys, *Doing Disability Differently* | 2014 | Routledge | C |
| 39 | Levent & Pascual-Leone, *Multisensory Museum* | 2014 | Rowman & Littlefield | C |
| 40 | Ladner, "Design for User Empowerment" | 2015 | ACM Interactions | C |
| 41 | Hamraie, *Building Access* | 2017 | U Minnesota Press | C |
| 42 | Hamraie & Fritsch, "Crip Technoscience Manifesto" | 2019 | Catalyst | C |
| 43 | Williamson, *Accessible America* | 2019 | NYU Press | C |
| 44 | Costanza-Chock, *Design Justice* | 2020 | MIT Press | C |
| 45 | Gissen, *Architecture of Disability* | 2022 | U Minnesota Press | C |
| 46 | Lifchez, *Rethinking Architecture* | 1987 | UC Press | C |
| 47 | Gissen, "Why so few disabled architects?" | 2018 | Architect's Newspaper | C |
| 48 | Mulligan et al., "Inclusive Design Pedagogy" | 2018 | Disability & Health J | C |
| 49 | Nicholson, "Where Are My People?" | 2025 | ACSA | C |
| 50 | Noel et al., "Question of Access" | 2021 | IJAC | D |
| 51 | Zallio & Clarkson, "Inclusion in Built Environment" | 2021 | Building & Env | D |
| 52 | eCAADe 2022, "Co-creating the Future" | 2022 | eCAADe | D |
| 53 | Heylighen et al., "How Do Disabled Architects Design?" | 2021+ | KU Leuven | D |
| 54 | Cupkova et al., "AI, Architecture, Accessibility" | 2023 | IJAC / ACADIA | D |
| 55 | Zallio & Clarkson, "Challenges" | 2023 | Arch Science Rev | D |
| 56 | Karastathi et al., "Bridging Pixels and Fabrication" | 2024 | ACADIA | D |
| 57 | del Campo, AI + Architecture | 2022+ | Books / ACADIA | D |
| 58 | Schafer, *The Soundscape* | 1977 | Destiny Books | E |
| 59 | Garcia, "Sound Structure" | 1996 | CAADRIA | E |
| 60 | Grabowski & Barner, "Force Feedback + Sonification" | 1998 | SPIE / CumInCAD | E |
| 61 | More et al., "Understanding Spatial Information" | 2002 | ACADIA | E |
| 62 | More et al., "Designing Spatial Sounds" | 2004 | eCAADe | E |
| 63 | Beilharz, "Architecture as Computer Interface" | 2005 | eCAADe | E |
| 64 | Blesser & Salter, *Spaces Speak* | 2007 | MIT Press | E |
| 65 | Navarro Villacampa et al., "Sensing the Invisible" | 2025 | eCAADe | E |
| 66 | Garcia, "PUSH" | 1999 | ACADIA | F |
| 67 | Sjostrom, "Non-Visual Haptic Interaction" | 2002 | PhD / CumInCAD | F |
| 68 | Pohl & Hirschberg, "Sensitive Voxel" | 2011 | CAAD Futures | F |
| 69 | Koch et al., "Haptic Paintings" | 2012 | eCAADe | F |
| 70 | Holloway & Marriott, "Accessible Maps" | 2018 | CHI | F |
| 71 | Tactile Architectural Drawings Typology | 2022 | Sustainability / MDPI | F |
| 72 | Butler et al., "TactIcons" | 2023 | CHI | F |
| 73 | FlexiBoard | 2024 | MDPI | F |
| 74 | MIT, "Tactile Vega-Lite" | 2025 | MIT | F |
| 75 | Miele et al., "Talking TMAP" | 2006 | British J. Visual Impairment | F |
| 76 | Brulé & Bailly, "Beyond 3D Printers" | 2021 | CHI | F |
| 77 | Nagakura, "Shape Recognition" | 1990 | CAAD Futures | G |
| 78 | Nembrini et al., "Source Studio" | 2009 | CAAD Futures | G |
| 79 | Celani & Vaz, "CAD Scripting vs Visual" | 2012 | IJAC | G |
| 80 | Leitão et al., "Programming Languages" | 2012 | IJAC | G |
| 81 | Maleki & Woodbury, "Programming in the Model" | 2013 | ACADIA | G |
| 82 | CadQuery | 2018+ | Open source | G |
| 83 | Rietschel et al., "LLMs for Design Scripting" | 2024 | ACADIA | G |
| 84 | Rietschel & Steinfeld, "Intelligent Tools" | 2025 | IJAC | G |
| 85 | Xue & Yen, "Voice-Enabled CAD" | 2009 | CAD Applications | G |
| 86 | Desolda et al., "Voice-Based 3D Modeling" | 2023 | CHI | G |
| 87 | CAADRIA 2022, "Rhetoric, Writing, Anexact Architecture" | 2022 | CAADRIA | H |
| 88 | Fu et al., "ShapeCrafter" | 2022 | NeurIPS | H |
| 89 | Yousif & Vermisso, "AI-Assisted Design Workflows" | 2022 | CAADRIA | H |
| 90 | Ma et al., "3D-GPT" | 2023 | arXiv | H |
| 91 | Khan et al., "Text2CAD" | 2024 | NeurIPS (Spotlight) | H |
| 92 | Rietschel et al., "Raven" | 2024 | ACADIA / Berkeley | H |
| 93 | Wu et al., "CAD-LLM" | 2024 | NeurIPS Workshop | H |
| 94 | Atakan et al., "Kakadoo" | 2025 | eCAADe | H |
| 95 | CADialogue | 2025 | Computer-Aided Design | H |
| 96 | Grasshopper MCP Server | 2025 | Open source | H |
| 97 | Ant, "AI Copilot for Grasshopper" | 2026 | Food4Rhino | H |
| 98 | El Hizmi et al., "LLMto3D" | 2024 | ACADIA | H |
| 99 | Jones et al., "AIDL" | 2025 | Computer Graphics Forum | H |
| 100 | Di Marco, "ConvoAI" | 2025 | Arch Science Rev | H |
| 101 | Potluri et al., "CodeTalk" | 2018 | CHI | I |
| 102 | Siu et al., "shapeCAD" | 2019 | ASSETS | I |
| 103 | Shi et al., "Molder" | 2020 | CHI | I |
| 104 | Stangl et al., "Image Descriptions" | 2021 | ASSETS | I |
| 105 | Lundgard & Satyanarayan, "4-Level Model" | 2022 | IEEE VIS | I |
| 106 | Potluri et al., "CodeWalk" | 2022 | ASSETS | I |
| 107 | Sharif et al., "Screen-Reader Users + Viz" | 2022 | EuroVIS | I |
| 108 | Practical CAD for VI | 2023 | Springer LNCS | I |
| 109 | Billah et al., "Designing While Blind" | 2023 | ASSETS | I |
| 110 | Crawford et al., "Co-designing Tactile Map" | 2024 | ASSETS | I |
| 111 | Das et al., "Blind + GenAI" | 2024 | ASSETS | I |
| 112 | MAIDR + AI | 2024 | ASSETS | I |
| 113 | CHI 2024, "AI Scene Description" | 2024 | CHI | I |
| 114 | Siu et al., "A11yShape" | 2025 | ASSETS | I |
| 115 | Madugalla et al., "Accessible Online Floor Plans" | 2020 | ACM TACCESS | I |
| 116 | Clepper et al., "What Would I Want to Make?" | 2025 | CHI | I |
| 117 | Flores-Saviaga et al., "GenAI Coding + BLV" | 2025 | CHI | I |
| 118 | Seo et al., "Born-Accessible Courses" | 2024 | EuroVIS / IEEE | I |
| 119 | Gurita & Vatavu, "LLM Code Perpetuates Barriers" | 2025 | W4A | I |
| 120 | Miller, "[make]SHIFT" | 2010 | ACADIA | J |
| 121 | Janssen & Chen, "Visual Dataflow Modelling" | 2011 | CAAD Futures | J |
| 122 | Fricker et al., "Computational Design Pedagogy" | 2020 | eCAADe | J |
| 123 | Akbar et al., "Democratizing the Toolbox" | 2023 | eCAADe | J |
| 124 | Sass, ACADIA Teaching Award | 2024 | ACADIA | J |
| 125 | UT Austin, "If buildings were invisible" | 2023 | UT Austin SOA | J |
| 126 | NAAB, *Conditions for Accreditation* | 2020 | NAAB | J |
| 127 | Evans, *Translations from Drawing to Building* | 1997 | MIT Press | K |
| 128 | Lynn, *Animate Form* | 1999 | Princeton Arch Press | K |
| 129 | Kolarevic, *Architecture in the Digital Age* | 2003 | Spon Press | K |
| 130 | Allen, *Practice* | 2009 | Routledge | K |
| 131 | Picon, *Digital Culture in Architecture* | 2010 | Birkhäuser | K |
| 132 | Carpo, *The Alphabet and the Algorithm* | 2011 | MIT Press | K |
| 133 | Carpo, *The Second Digital Turn* | 2017 | MIT Press | K |
| 134 | Burry, *Scripting Cultures* | 2011 | Wiley | K |
| 135 | Easterling, *Extrastatecraft* | 2014 | Verso | K |
| 136 | Deamer, *Architect as Worker* / *Architecture and Labor* | 2015/2020 | Bloomsbury / Routledge | K |

---

## Assessment

### What the 136 sources establish

The Radical Accessibility Project sits at an intersection that no existing work occupies. Six literatures converge on the project but none connects them:

**1. No work bridges architectural phenomenology and computational design tools for blind users.**

Pallasmaa (A.5), Zumthor (A.6), Böhme (A.8), and Jay (A.3) critique architecture's visual bias philosophically. Varela et al. (A.10) and Clark & Chalmers (A.11) extend this into enactivist cognitive science. Evans (K.1) proves that representational media are never neutral; Carpo (K.6, K.7) traces how notation systems structure design thinking across epochs. Heylighen (B.11) studies blind spatial experience empirically. The HCI community builds accessible modeling tools -- shapeCAD (I.2), A11yShape (I.14), Molder (I.3). The ACADIA community builds text-to-CAD pipelines -- Text2CAD (H.5), Raven (H.6), Kakadoo (H.8), LLMto3D (H.12), AIDL (H.13). No one connects all four. The project is the first to operationalize architectural phenomenology's multi-sensory critique through a functioning, screen-reader-native computational design tool used by a blind architecture student in a graduate studio.

**2. Cognitive science validates the CLI paradigm, but no computational design researcher has made the connection.**

Millar (B.2) demonstrates that spatial cognition is modality-independent when adequate reference frames are available. Thinus-Blanc & Gaunet (B.3) show that discrepancies in blind spatial cognition research stem from strategy differences, not fundamental limitations -- spatial performance depends on what strategies and reference frames are provided. Loomis, Klatzky & Golledge (B.4) find that spatial representations derived from spatial language can function equivalently to those derived from direct perception. Piaget & Inhelder (B.1) show spatial understanding develops topologically (qualitative relationships first) before becoming metric. Saerberg (B.6) and Giudice (B.13) confirm blind spatial cognition is sequential, landmark-based, and language-mediated.

The CLI's sequential, semantically-labeled, language-mediated interaction model is exactly the strategy-enabling infrastructure this literature calls for -- but no computational design researcher has cited this cognitive science to justify an alternative tool paradigm. The project can make this connection explicit: the CLI is not a compromise, it is cognitively aligned with how blind users actually construct spatial knowledge. Schön's reflective practitioner framework (A.9) adds further support: the CLI's command-response loop is a "reflective conversation with the situation" where verbal feedback makes the design dialogue explicit.

**3. Critical disability studies has not entered the ACADIA/CumInCAD discourse.**

Hamraie (C.12, C.13), Gissen (C.16, C.18), Boys (C.9), Williamson (C.14), Mankoff et al. (C.4), and Costanza-Chock (C.15) are well-established in disability studies, HCI, and architectural theory -- but they are virtually absent from computational design literature. Winner's "Do Artifacts Have Politics?" (C.1) is among the most cited STS papers ever written, yet the ACADIA community has not applied it to its own tools. Lifchez's pioneering work at Berkeley (C.17, 1987) and ACSA's own "Where Are My People?" report (C.20, 2025) confirm that disabled architects remain systemically absent from the profession. The project's ACADIA paper can introduce "crip technoscience," "design justice," and "do artifacts have politics?" to a community that has discussed accessibility only in terms of equity (Noel, D.1) and data justice (Cupkova, D.5), not structural critique.

Rhino's viewport, Grasshopper's visual canvas, and Revit's click-and-drag interface are not neutral instruments that happen to be visual. They are artifacts that have politics -- they enforce a social arrangement in which sighted people design and blind people are excluded. The project builds artifacts with different politics.

**4. The "curb cut" argument is waiting to be made for computational design.**

Pullin (C.3) demonstrates that designing for disability drives innovation beyond accommodation. Shinohara & Wobbrock (C.5) show that mainstream integration beats specialized assistive technology. Levent & Pascual-Leone (C.10) prove that multisensory design enriches experience for everyone. The project's text-based, file-decoupled architecture has properties -- auditability, scriptability, crash resilience, version-control friendliness, zero-dependency portability -- that benefit all users, not just blind users. The CLI-to-JSON-to-Rhino pipeline was designed for a blind user. It turns out to be more debuggable, more automatable, and more resilient than traditional visual CAD workflows. This is the computational design curb cut effect -- and no one has articulated it yet.

**5. Sonification for architectural design authoring remains a white space.**

Blesser & Salter (E.7) define aural architecture and map spatial properties to sound parameters (room volume to reverb, wall proximity to early reflections, material to frequency response). Schafer (E.1) provides the foundational acoustic ecology framework. Garcia (E.2) prototyped sonification for structural education in 1996. But no one has built a sonification pipeline for a blind designer creating new architectural spaces -- real-time auditory feedback as design decisions change the spatial model. The project's planned sonification direction has no direct precedent.

**6. Participatory design with disabled co-designers in computational architecture is undocumented.**

Charlton's "nothing about us without us" (C.2) is the foundational principle. Costanza-Chock (C.15) extends it to design justice. Vermeersch et al. (B.14) apply participatory methods with blind users in architectural design. But no ACADIA or CumInCAD paper describes a computational design tool co-designed with a blind architecture student as a research partner -- not a user study subject recruited for evaluation, but a collaborator who shapes tool requirements, evaluates outputs, identifies spatial relationships sighted developers miss, and uses the tools in graduate studio work. Daniel is not a test subject; he is a co-designer. Every tool exists because he identified a need. The project's methodology is itself a contribution.

### The LLM-to-CAD explosion strengthens positioning

Between 2022 and 2026, text-to-geometry became a mainstream research direction: Text2CAD (H.5), CAD-LLM (H.7), Raven (H.6), Ant (H.11), CADialogue (H.9), 3D-GPT (H.4), ShapeCrafter (H.2), Kakadoo (H.8), LLMto3D (H.12), AIDL (H.13), ConvoAI (H.14). The architecture community has independently converged on text-to-geometry as the future of design interaction. AIDL (H.13) is particularly striking: MIT CSAIL designed a CAD language explicitly for "blind" AI code generation -- eliminating the need for visual verification of spatial output. The project arrived at the same architecture by a different route -- necessity, not convenience. The ACADIA paper can argue: we built this because a blind user cannot interact with Grasshopper's visual canvas at all; the fact that the field is now building the same pipeline for everyone validates both the approach and the broader claim that designing for exclusion reveals better design patterns.

### "Designing While Blind" validates the authorship thesis

Billah et al. (I.9) demonstrate that blind people are excluded from creating the very tactile media they consume. Crawford et al. (I.10) found that TinkerCAD is screen-reader-incompatible during co-design with blind students. Das et al. (I.11) show that even ChatGPT creates accessibility barriers for blind users. The project is the only system where a blind architecture student co-designs the tools he uses while using them in a graduate studio. The authorship gap -- blind people as consumers of design, never authors -- is what the project closes.

### What remains unexplored

**7. Architectural representation theory validates the CLI as an epistemological intervention, not an accommodation.**

Evans (K.1) proved in 1997 that the architectural drawing is not transparent but an active agent that shapes what can be designed. Carpo (K.6, K.7) traced how notation systems structure design thinking across epochs. Allen (K.4) showed that concepts emerge from representational practices. Burry (K.8) demonstrated that scripting lets designers escape the constraints embedded in commercial software. Deamer (K.10) revealed that tools are structures of labor that determine whose work is visible and valued. Easterling (K.9) theorized infrastructure as a political medium. The project can now make the strongest possible theoretical claim: the CLI is not an accessibility workaround; it is, by Evans' logic, a different representational medium that will generate different architectural possibilities and different "translations." Changing the medium changes what architecture can be.

**8. "Born-accessible" is emerging as a design paradigm distinct from retrofitted accessibility.**

Seo's "born-accessible" courses (I.18) -- designed from the ground up for blind learners -- demonstrate that accessibility-first design produces fundamentally different and often superior outcomes compared to retrofitted accessibility. Clepper et al. (I.16) document how blind tactile graphics creators are trapped between accessible low-fidelity tools and inaccessible high-fidelity ones. Flores-Saviaga et al. (I.17) show that even AI coding assistants exacerbate accessibility barriers through suggestion overload. Gurita & Vatavu (I.19) found that LLM-generated interfaces do not spontaneously produce accessible code. Together, these findings validate the project's architecture: accessibility must be structural (baked into the CLI protocol), not emergent (hoped for from AI output).

Even with 136 sources, several areas lack published work:

- **File-watching as accessibility architecture.** No paper examines JSON file-watching as a strategy for decoupling accessible controllers from inaccessible viewers. The MCP server for Grasshopper (H.10) validates the transport-layer concept but uses a different pattern. The project's approach is simpler, more robust, and crash-safe.
- **Accessibility in ACADIA/CumInCAD remains thin.** Despite 2,500+ CumInCAD papers from 2021–2025, accessibility/disability content barely registers. The project's paper would be among the first to directly address how a blind student uses computational design tools in a graduate architecture studio.
- **AI + accessibility in architecture.** del Campo (D.8), Rietschel (G.7, G.8, H.6), and the Text2CAD community build AI-architecture tools that assume sighted users. Noel (D.1) and Cupkova (D.5) call for equity but don't build AI tools. The project sits in the intersection -- a functioning, MCP-ready architecture tool designed for a blind user.

---

## Recommended Reading Order for ACADIA 2026 Framing

**Layer 1 -- Architecture's Visual Bias (the problem):**
Jay (A.3), Pallasmaa (A.5), Zumthor (A.6), Winner (C.1), Heylighen & Herssens (B.11), Evans (K.1)

**Layer 2 -- Disability as Generative, Not Deficit (the reframe):**
Hamraie (C.12), Hamraie & Fritsch (C.13), Gissen (C.16), Boys (C.9), Reynolds (B.12), Pullin (C.3), Lifchez (C.17)

**Layer 3 -- Embodied Cognition and Representation Theory (the theoretical foundation):**
Merleau-Ponty (A.1), Varela et al. (A.10), Clark & Chalmers (A.11), Schön (A.9), Carpo (K.6, K.7), Burry (K.8), Allen (K.4), Deamer (K.10)

**Layer 4 -- Blind Spatial Cognition (the evidence):**
Millar (B.2), Thinus-Blanc & Gaunet (B.3), Loomis et al. (B.4), Piaget & Inhelder (B.1), Saerberg (B.6), Cattaneo & Vecchi (B.7), Chen et al. (B.15)

**Layer 5 -- The Tool Landscape (what exists and what's missing):**
shapeCAD (I.2), A11yShape (I.14), Rietschel/Raven (G.7, H.6), Text2CAD (H.5), AIDL (H.13), LLMto3D (H.12), Crawford (I.10), Billah (I.9), Clepper et al. (I.16), Flores-Saviaga (I.17)

**Layer 6 -- Ethics and Method (how we work):**
Charlton (C.2), Costanza-Chock (C.15), Seo (I.18), Nicholson/ACSA (C.20), NAAB (J.7)

**Layer 7 -- The Project's Contribution (what this makes possible):**
Blesser & Salter (E.7), Lundgard & Satyanarayan (I.5), Wobbrock/Ability-Based Design (C.6), Ladner (C.11), Sennett (A.12), Ingold (A.13)
