# ACADIA & CumInCAD Literature Review: Radical Accessibility Project

**Prepared for:** ACADIA 2026 submission
**Last updated:** 2026-02-24
**Project:** Radical Accessibility Project (UIUC School of Architecture)
**PI:** John Clark

---

## Overview

This literature review surveys papers from ACADIA (Association for Computer Aided Design in Architecture) and the broader CumInCAD database (CAADRIA, eCAADe, SIGraDi, CAAD Futures) that are relevant to the Radical Accessibility Project. The project develops tools and workflows that make architectural education fully accessible to blind and low-vision students by treating non-visual interaction as the primary design case. Its core thesis: by designing for blindness first, we create tools that are not only accessible but often superior to their visual-centric counterparts. This is disciplinarily transformative, not assistive -- a critique of architecture's ocularcentrism that produces genuinely novel computational design methods.

Papers are organized by theme. Each entry includes full bibliographic details and a note on relevance to the project's specific concerns: CLI-driven CAD pipelines, tactile fabrication, sonification, AI-assisted description, screen-reader-native workflows, and inclusive design pedagogy.

---

## Theme 1: Accessibility, Disability, and Equity in Computational Design

These papers directly address who gets to participate in computational design and on what terms. They provide the broadest disciplinary framing for the project's critique of architecture's visual bias.

### 1.1 Noel, V.A.A., Boeva, Y., and Dortdivanlioglu, H. (2021). "The Question of Access: Toward an Equitable Future of Computational Design."
- **Venue:** International Journal of Architectural Computing (IJAC), Vol. 19, No. 4, pp. 496-511
- **DOI:** 10.1177/14780771211014925
- **URL:** https://journals.sagepub.com/eprint/ZHJHUQSYMBSYHQNTZNEU/full
- **Summary:** Examines the trope of "access" in digital fabrication, design, and craft, illustrating how it unfolds in these spaces and practices. Argues that an equitable future must build on and create space for multiple bodies, knowledges, and skills, and employ technologies accessible to broad groups of society.
- **Relevance:** Directly frames the Radical Accessibility Project's central argument -- that computational design tools systematically exclude certain bodies and ways of knowing. The project extends Noel et al.'s call for equity by demonstrating what "access" means concretely for a blind architecture student using CLI-driven tools.

### 1.2 Cupkova, D., Wit, A.J., del Campo, M., and Claypool, M. (2023). "AI, Architecture, Accessibility, and Data Justice" (Editorial).
- **Venue:** International Journal of Architectural Computing (IJAC) -- ACADIA Special Issue
- **DOI:** 10.1177/14780771231171939
- **URL:** https://journals.sagepub.com/doi/full/10.1177/14780771231171939
- **Summary:** Editorial for the ACADIA/IJAC special issue examining tensions around technology while developing critical metrics, understanding implicit biases, and probing new methodologies for AI's impact in architecture. Addresses accessibility and data justice as intertwined concerns in architectural computing.
- **Relevance:** The ACADIA community's most direct engagement with accessibility as a computational design concern. The Radical Accessibility Project's use of AI for architectural description and its critique of visual-centric tool design responds directly to this call.

### 1.3 Karastathi, N., Regunathan, S., Doria, D., Walpole, T., and Colletti, M. (2024). "Bridging Pixels and Fabrication: Enhancing Accessibility in CNC Knitting for Architectural Design."
- **Venue:** ACADIA 2024: Designing Change -- Proceedings Volume 1, pp. 241-252 (Vanguard Award Winner)
- **URL:** https://discovery.ucl.ac.uk/id/eprint/10208145/
- **Summary:** Introduces an approach to enhancing accessibility in CNC knitting for architects and designers. Developed "Kniteretta," a Grasshopper plug-in connecting Kniterate (a medium-sized CNC knitting machine) with commonly used design software, simplifying workflows and enabling customizable designs.
- **Relevance:** Demonstrates ACADIA's growing recognition that "accessibility" in computational design means more than theoretical equity -- it means making specific fabrication tools usable by people currently excluded. The Radical Accessibility Project's CLI-to-Rhino pipeline shares the same pattern: creating a bridge layer that translates between an accessible interface and an inaccessible tool.

### 1.4 eCAADe 2022 Conference: "Co-creating the Future: Inclusion in and through Design."
- **Venue:** 40th eCAADe Conference, KU Leuven Technology Campus Ghent, Belgium, September 13-16, 2022
- **Editors:** Pak, B. and Stouffs, R.
- **URL:** https://ecaade.org/prev-conf/archive/ecaade2022/kuleuven.ecaade2022.be/proceedings/index.html
- **Summary:** The entire conference theme was "Inclusion in and through Design," organized by the Altering Practices for Urban Inclusion Research Group. Addressed concerns about the negative impact of digital devices and platforms, including potential exclusion of vulnerable and disadvantaged citizens.
- **Relevance:** Establishes that the eCAADe community recognizes inclusion as a first-order concern in computational design. The Radical Accessibility Project provides a concrete case study of what "inclusion through design" means when the excluded user is a blind architecture student.

---

## Theme 2: Blindness, Haptics, and Non-Visual Spatial Knowledge

These papers explore what designers can learn from blind people's spatial experience and how haptic/tactile interfaces can make architecture accessible beyond vision.

### 2.1 Heylighen, A. and Herssens, J. (2014). "Designerly Ways of Not Knowing: What Designers Can Learn about Space from People Who are Blind."
- **Venue:** Journal of Urban Design, Vol. 19, No. 3, pp. 317-332
- **URL:** https://ideas.repec.org/a/taf/cjudxx/v19y2014i3p317-332.html
- **Summary:** Demonstrates that architects' visual ways of knowing risk favouring visual qualities over non-visual qualities, but also cognition over embodiment in how space is understood and conceived. Argues that designerly ways of knowing are simultaneously designerly ways of "not knowing" -- of disregarding the bodily experience of the built environment. People who are blind appreciate sounds, smells, and haptic qualities that designers may not be attuned to.
- **Relevance:** This is perhaps the single most important theoretical paper for the project. Its argument that designers' visual training creates systematic blind spots directly supports the project's thesis that designing for blindness first reveals architectural knowledge that ocularcentrism obscures. Daniel's feedback on the School Jig tool consistently surfaces spatial relationships that sighted users take for granted.

### 2.2 Herssens, J. and Heylighen, A. (2011). "A Framework of Haptic Design Parameters for Architects: Sensory Paradox Between Content and Representation."
- **Venue:** Computer Aided Architectural Design Futures 2011 (CAAD Futures), Liege, Belgium
- **URL:** https://cumincad.architexturez.net/doc/oai-cumincadworks-id-cf2011-p027
- **Summary:** Defines haptic design parameters as variable characteristics that can be decided upon by designers during the design process, with the value determining the haptic characteristics of the resulting design. Based on research with twenty-two people born blind, identifying how human movement is influenced by movement plane, guiding plane, and resting plane.
- **Relevance:** Directly informs the project's tactile output pipeline (PIAF swell paper, 3D-printed models). The haptic parameters Herssens identifies -- texture, temperature, weight, compliance -- map onto design decisions the project's tools must support. The "sensory paradox between content and representation" mirrors the project's challenge of representing spatial relationships through non-visual media.

### 2.3 Vermeersch, P., Schijlen, J., and Heylighen, A. (2018). "Designing from Disability Experience: Space for Multi-sensoriality."
- **Venue:** Participatory Design Conference (PDC) 2018, Hasselt & Genk, Belgium
- **URL:** https://www.researchgate.net/publication/324593818_Designing_from_disability_experience_Space_for_multi-sensoriality
- **Summary:** Explores how disability experience can inform architectural design processes. Acknowledges perspectives from actual and potential users, user participants in design processes, stakeholders, and various experts, with the goal of producing knowledge applicable in design processes.
- **Relevance:** The participatory design methodology aligns with Daniel's role as co-designer (not just user) of every tool in the project. Vermeersch et al.'s emphasis on disability experience as generative knowledge -- not deficit -- parallels the project's framing of blindness as a design advantage rather than a limitation.

### 2.4 Vermeersch, P. and Heylighen, A. (2012). "Blindness and Multi-sensoriality in Architecture: The Case of Carlos Mourao Pereira."
- **Venue:** Published in research proceedings; indexed in multiple databases
- **URL:** https://www.researchgate.net/publication/237044494_Blindness_and_multi-sensoriality_in_architecture_The_case_of_Carlos_Mourao_Pereira
- **Summary:** Case study of Carlos Mourao Pereira, an architect who lost his sight in 2006 and continues to practice, teach, and conduct research. His practice is centered on multi-sensoriality. After losing his sight, his designs -- such as a sea bathing facility at Lourinha, Portugal -- demonstrate heightened attention to tactile, auditory, and olfactory elements.
- **Relevance:** A direct precedent for the project's thesis that blindness can be generative for architecture, not merely accommodated. Pereira demonstrates that an architect who cannot see can produce richer spatial designs. The project extends this argument from the individual practitioner to the tool ecosystem -- asking what tools look like when designed for a Pereira-like practice from the ground up.

### 2.5 Celani, G., Zattera, V., de Oliveira, M.F., and da Silva, J.V.L. (2013). "'Seeing' with the Hands: Teaching Architecture for the Visually-Impaired with Digitally-Fabricated Scale Models."
- **Venue:** 15th International Conference on Computer Aided Architectural Design Futures (CAAD Futures 2013), Shanghai, China
- **URL:** https://link.springer.com/chapter/10.1007/978-3-642-38974-0_15
- **Summary:** Develops a protocol for making 3D technologies technically and economically available to educators of visually impaired students. Three-dimensional representations are more effective than bidimensional representations for those with congenital blindness, especially during the conceptualization phase. Used Selective Laser Sintering (SLS) to create tactile models for a university library, evaluated by people with different types of visual impairment.
- **Relevance:** Directly relevant to the project's physical-digital round-trip pipeline. Celani et al. address the same problem the project tackles with PIAF swell paper and 3D-printed jigs: how to make architectural representations tangible. The project extends this work by automating the digital-to-tactile translation and closing the loop (tactile input via pegboard digitizes back to geometry).

---

## Theme 3: Sonification of Architectural and Spatial Information

These papers explore using sound as a medium for conveying spatial, structural, and design information -- a key future direction for the Radical Accessibility Project.

### 3.1 Garcia, R. (1996). "Sound Structure: Using Data Sonification to Enhance Building Structures CAI."
- **Venue:** Proceedings of the First Conference on Computer-Aided Architectural Design Research in Asia (CAADRIA 1996), Hong Kong
- **URL:** https://cumincad.architexturez.net/doc/oai-cumincadworks-id-89ca
- **Summary:** Explores how teaching concepts of building structures to architecture and engineering students through computers and multimedia can be enhanced by using appropriate sound parameters. Sound is useful in presenting information such as building structural response to static and dynamic external loading.
- **Relevance:** An early and prescient paper in the CumInCAD database that directly applies sonification to architectural education -- the same domain as the Radical Accessibility Project. The project's planned sonification pipeline (room volume to reverb, wall proximity to tonal shift, ceiling height to pitch) extends Garcia's structural sonification to spatial experience.

### 3.2 Beilharz, K. (2005). "Architecture as the Computer Interface: 4D Gestural Interaction with Socio-Spatial Sonification."
- **Venue:** 23rd eCAADe Conference, Lisbon
- **Summary:** Uses gestural interaction with controller devices to affect source data that produces information sonification in real time. Source information is derived from socio-spatial data about human behaviour in sensate architectural spaces. Proposes a framework for gestural interaction with information sonification, where the purpose is to blur boundaries between computational and spatial interaction and transform building spaces into responsive, intelligent interfaces.
- **Relevance:** Demonstrates that the eCAADe community has explored architecture-as-interface mediated through sound. The Radical Accessibility Project's sonification goals parallel Beilharz's work but with a critical difference: the project's sonification serves a blind user navigating a design they are authoring, not monitoring an existing building.

### 3.3 More, G., Harvey, L., and Burry, M. (2002). "Understanding Spatial Information with Integrated 3D Visual and Aural Design Applications."
- **Venue:** ACADIA 2002: Thresholds, Pomona
- **Summary:** Investigates how aural representations can complement or substitute for visual spatial information in design environments. Explores integrated applications combining 3D visual and aural modalities for spatial understanding.
- **Relevance:** A rare ACADIA paper explicitly investigating aural representation of spatial information for design. Directly anticipates the project's approach of using sound to convey architectural relationships that are normally conveyed visually.

### 3.4 More, G., et al. (2004). "Designing Spatial Sounds for Spatial Information Environments."
- **Venue:** 22nd eCAADe Conference, Copenhagen
- **Summary:** Extends earlier work on spatial sound design for information environments, addressing how sound can be designed to convey spatial architectural information effectively.
- **Relevance:** Provides design principles for the project's planned sonification pipeline, addressing the specific challenge of mapping architectural spatial properties to sound parameters.

### 3.5 Grabowski, N.A. and Barner, K.E. (1998). "Data Visualization Methods for the Blind Using Force Feedback and Sonification."
- **Venue:** SPIE 3524, Telemanipulator and Telepresence Technologies V (indexed in CumInCAD)
- **DOI:** 10.1117/12.333677
- **URL:** https://www.spiedigitallibrary.org/conference-proceedings-of-spie/3524/0000/Data-visualization-methods-for-the-blind-using-force-feedback-and/10.1117/12.333677.short
- **Summary:** Developed methods for adding aural feedback to a haptic force feedback interface, creating a multimodal visualization system. A 2D data set is presented as a polygonal haptic surface with real-time aural feedback as the user explores. Parameters of sound (pitch, spectral content) convey information.
- **Relevance:** Establishes the multimodal paradigm (haptic + auditory) that the project could adopt. The pegboard system already provides haptic input; adding sonification to the audio feedback would create the kind of multimodal interface Grabowski and Barner envision.

---

## Theme 4: Haptic and Tactile Interfaces for Architecture

These papers address the use of touch-based interfaces and tactile representations in architectural design and education.

### 4.1 Koch, V., Luckert, A.J., Schwarz, T., Both, P.v., and Diziol, P. (2012). "Haptic Paintings: Using Rapid Prototyping Technologies to Grant Visually Impaired Persons Access to Paintings, Sculptures, Graphics and Architecture."
- **Venue:** 30th eCAADe Conference (Digital Physicality), Prague, Czech Republic
- **URL:** https://www.blm.ieb.kit.edu/english/536_796.php
- **Summary:** Develops workflows for creating tactile representations of visual art and architecture accessible to visually impaired individuals. Laser-cut layered depth diagrams convey spatial layout while augmenting depth relations; CNC-milled textured reliefs render fine details suitable for the sense of touch.
- **Relevance:** Directly relevant to the project's PIAF swell paper pipeline and tactile precedent library. Koch et al.'s use of rapid prototyping for tactile output parallels the project's use of laser printing + PIAF heating to create raised-line architectural drawings. The project's advantage is automation and integration with the CLI pipeline.

### 4.2 Garcia, R. (1999). "PUSH: Generating Structural Form with Haptic Feedback."
- **Venue:** ACADIA '99, Salt Lake City
- **Summary:** Explores how haptic feedback can be used as a design interface for generating structural form. Designers physically feel forces and structural responses while shaping geometry.
- **Relevance:** An ACADIA paper exploring force-feedback as a design medium -- relevant to the project's future direction of haptic design interfaces. The project's pegboard system is a low-tech version of this concept: physical manipulation that translates to digital geometry.

### 4.3 Sjostrom, C. (2002). "Non-Visual Haptic Interaction Design: Guidelines and Applications."
- **Venue:** PhD Dissertation, Certec, Lund University (indexed in CumInCAD), 216 pages
- **URL:** https://lup.lub.lu.se/search/publication/a38cc004-1b0c-4ae7-bbf0-af227385cf01
- **Summary:** Investigates how blind people's computer usage can be improved by virtual haptics. The three cornerstones: Haptics, HCI, and Blind Users. Develops guidelines for haptic interaction design specific to non-visual use, including investigation of graphical user interface problems for blind people and how haptics can manage them.
- **Relevance:** Provides design guidelines directly applicable to the project. The thesis's finding that haptic interfaces can substitute for visual information in computer interaction validates the project's approach of replacing visual CAD feedback with tactile and auditory alternatives.

### 4.4 Pohl, I.M. and Hirschberg, U. (2011). "Sensitive Voxel: A Reactive Tangible Surface."
- **Venue:** Computer Aided Architectural Design Futures 2011 (CAAD Futures), Liege, Belgium
- **URL:** https://graz.pure.elsevier.com/en/publications/sensitive-voxel
- **Summary:** Presents an interactive folded surface as a prototype for future interactive architectural surfaces, informed by physiological understandings of touch and tactile interaction.
- **Relevance:** Demonstrates the CAAD community's interest in tangible interfaces for architectural interaction. The project's pegboard system occupies a similar design space -- a physical surface that serves as both input and representation.

---

## Theme 5: Text-Based and Scripting Approaches to CAD

These papers explore alternatives to visual-only CAD interaction -- scripting, natural language, and text-based interfaces that are inherently more accessible to screen readers.

### 5.1 Celani, G. and Vaz, C.E.V. (2012). "CAD Scripting and Visual Programming Languages for Implementing Computational Design Concepts: A Comparison from a Pedagogical Point of View."
- **Venue:** International Journal of Architectural Computing (IJAC), Vol. 10, No. 1, pp. 121-137
- **URL:** https://journals.sagepub.com/doi/abs/10.1260/1478-0771.10.1.121
- **Summary:** Compares scripting languages and visual programming languages (e.g., Grasshopper) for teaching computational design to architecture students. Finds that visual programming works well for novices and parametric variation, but scripting languages are fundamental for implementing rule-based generative systems. Scripting is also more accessible to advanced automated workflows.
- **Relevance:** Directly supports the project's decision to use text-based (CLI) interaction rather than Grasshopper's visual canvas. Celani and Vaz find that scripting languages are more powerful for generative systems -- and they are also inherently screen-reader-compatible, which Grasshopper's visual canvas is not. The project proves that the "advanced" scripting approach is also the "accessible" approach.

### 5.2 Maleki, M.M. and Woodbury, R.F. (2013). "Programming in the Model: A New Scripting Interface for Parametric CAD Systems."
- **Venue:** ACADIA 2013: Adaptive Architecture, pp. 183-190. Riverside Architectural Press.
- **URL:** https://summit.sfu.ca/item/14097
- **Summary:** Presents PIM (Programming In the Model), a prototype parametric CAD system with a live interface featuring side-by-side model and script windows, real-time updating, and on-demand dependency representations. Strives to narrow the gap between direct editing and scripting.
- **Relevance:** PIM's live bidirectional link between script and model prefigures the Radical Accessibility Project's CLI-to-Rhino watcher pipeline. The key difference: PIM assumes both windows are visual; the project's architecture separates the text interface (CLI) from the visual output (Rhino) entirely, enabling a blind user to work in the text layer while a sighted collaborator observes the visual layer.

### 5.3 Rietschel, M., Guo, F., and Steinfeld, K. (2024). "Mediating Modes of Thought: LLMs for Design Scripting."
- **Venue:** ACADIA 2024: Designing Change, Calgary
- **URL:** https://arxiv.org/abs/2411.14485
- **Summary:** Explores how Large Language Models can mediate between user intent and algorithms to make design scripting more accessible. System architecture includes LLM agents, an API handling message exchanges, and a Grasshopper plugin parsing generated JSON to the canvas. Users provide text prompts that are sent to the first LLM agent to deduce design intent, then mapped to Grasshopper-specific script and translated to JSON.
- **Relevance:** Extremely relevant. This paper describes a text-prompt-to-JSON-to-Grasshopper pipeline that closely parallels the Radical Accessibility Project's CLI-to-JSON-to-Rhino pipeline. The critical insight: Rietschel et al. built this for convenience; the Radical Accessibility Project built it for necessity. A blind user cannot interact with Grasshopper's visual canvas at all, making text-to-geometry translation not an enhancement but a prerequisite.

### 5.4 Rietschel, M. and Steinfeld, K. (2025). "Intelligent Tools on the Loose: Reasoning Models for Exploratory Computational Design."
- **Venue:** International Journal of Architectural Computing (IJAC)
- **DOI:** 10.1177/14780771251352945
- **URL:** https://journals.sagepub.com/doi/full/10.1177/14780771251352945
- **Summary:** Investigates how reasoning language models can be utilized for early-stage exploratory design, outlining principles to build effective tools with these models.
- **Relevance:** Extends the LLM-for-design-scripting work toward the kind of conversational, exploratory design interaction the project envisions through MCP (Model Context Protocol) -- where Daniel could ask "describe the north elevation" and receive an AI-generated spatial description.

---

## Theme 6: Natural Language and AI-Assisted Architectural Description

These papers explore using natural language processing and AI to bridge between text and geometry -- the core interface challenge of the Radical Accessibility Project.

### 6.1 Atakan, A.O., Kostourou, F., Sandor, V., Seer, S., and Koenig, R. (2025). "Kakadoo: LLM Enabled Speech Interface for Enhanced Human-Computer Interaction."
- **Venue:** 43rd eCAADe Conference, Ankara, September 1-5, 2025
- **URL:** https://papers.cumincad.org/cgi-bin/works/paper/ecaade2025_348
- **Summary:** Presents Kakadoo, a Grasshopper plugin leveraging speech recognition and LLM technology to interpret natural language commands for intuitive model manipulation. Voice-driven design facilitates collaborative urban planning. Evaluation through co-design workshops revealed effectiveness in processing vocal prompts with visual feedback.
- **Relevance:** The most directly relevant recent paper in the CumInCAD database. Kakadoo demonstrates that voice/text-to-geometry interaction is viable in Grasshopper. The Radical Accessibility Project's CLI achieves the same goal through a different architecture (file-watching rather than plugin), with the crucial addition that it is designed specifically for a user who cannot see the visual feedback at all.

### 6.2 CAADRIA 2022 paper: "Rhetoric, Writing, and Anexact Architecture: The Experiment of Natural Language Processing (NLP) and Computer Vision (CV) in Architectural Design."
- **Venue:** CAADRIA 2022: Post-Carbon, Sydney, Vol. 1, pp. 343-352
- **URL:** https://caadria2022.org/rhetoric_writing_and_anexact_architecture_the_experiment_of_natural_language_processing_nlp_and_computer_vision_cv_in_architectural_design/
- **Summary:** Uses GPT-2 to generate architectural descriptions and Attentional GANs to translate text into visual form. Demonstrates AI's ability to do "architectural writing" -- generating coherent spatial descriptions and interrogating shape through language.
- **Relevance:** Demonstrates the possibility of text-to-form translation that the project needs. While this paper works in the direction of text-to-image, the project requires text-to-parametric-geometry (through the CLI-to-JSON pipeline) and geometry-to-text (through AI-assisted description of designs).

### 6.3 Yousif, S. and Vermisso, E. (2022). "Towards AI-Assisted Design Workflows for an Expanded Design Space."
- **Venue:** CAADRIA 2022: Post-Carbon, Sydney, pp. 335-344
- **URL:** https://papers.cumincad.org/cgi-bin/works/paper/caadria2022_503
- **Summary:** Examines integrating AI into design workflows to broaden exploration possibilities. Demonstrates that integrating AI networks into a framework with other computational tools affords a different kind of design exploration. Emphasizes importance of how well different computational methods interconnect and careful dataset curation.
- **Relevance:** The "expanded design space" that AI enables has a specific meaning for the project: it includes design spaces that were previously inaccessible to blind designers. The project's AI critique partner -- which asks Socratic questions about designs rather than just describing them -- extends Yousif and Vermisso's vision of AI as a design collaborator.

---

## Theme 7: Interoperability, Pipelines, and Data Exchange in Computational Design

These papers address the architectural computing infrastructure challenges that the project's CLI-to-JSON-to-Rhino pipeline must solve.

### 7.1 Miller, N. (2010). "[make]SHIFT: Information Exchange and Collaborative Design Workflows."
- **Venue:** ACADIA 2010: LIFE in:formation, New York, pp. 139-144
- **DOI:** https://doi.org/10.52842/conf.acadia.2010.139
- **Summary:** Examines customized design workflows that enhance information exchange across multidisciplinary teams. Demonstrates how non-standard workflows enable collaboration when teams use diverse software platforms. Addresses limitations of proprietary single-model approaches.
- **Relevance:** The project's file-watching pipeline is precisely the kind of "non-standard workflow" Miller describes -- one that enables collaboration between a blind CLI user and a sighted Rhino user through a shared JSON artifact. Miller's insight that proprietary single-model approaches fail in diverse teams applies directly: Rhino's single-model GUI approach fails for a blind user.

### 7.2 Janssen, P. and Chen, K.W. (2011). "Visual Dataflow Modelling: A Comparison of Three Systems."
- **Venue:** Computer Aided Architectural Design Futures 2011 (CAAD Futures), Liege, Belgium
- **Summary:** Compares three visual dataflow systems for parametric design, analyzing their representational and computational characteristics. Examines how visual programming paradigms structure design thinking.
- **Relevance:** By comparing visual dataflow systems, this paper implicitly reveals what is lost when the only interface is visual. The Radical Accessibility Project's text-based alternative to visual dataflow (Grasshopper) must provide equivalent expressive power through sequential, screen-reader-compatible commands -- a constraint that, as the project demonstrates, often produces clearer design logic.

---

## Theme 8: Computational Design Pedagogy and Inclusive Teaching

These papers address how computational design is taught and how pedagogical approaches can be made more inclusive.

### 8.1 Akbar, Z., Ron, G., and Wortmann, T. (2023). "Democratizing the Designer's Toolbox: Adopting Free, Open-Source, and Platform-Agnostic Tools into Computational Design Teaching."
- **Venue:** 41st eCAADe Conference, Graz, Austria, September 20-22, 2023
- **URL:** https://papers.cumincad.org/cgi-bin/works/paper/ecaade2023_311
- **Summary:** Proposes computational design education where students develop their own geometric and logical workflows beyond specific software platforms. Students work directly on coordinates or numerical representations using 3D computer graphics programming rather than learning proprietary 3D modeling software. Promotes democratized design tools through computation.
- **Relevance:** The project's approach is the radical version of what Akbar et al. advocate: not just platform-agnostic, but modality-agnostic. By building on Python stdlib with zero dependencies, the project demonstrates that the most accessible computational design tool is also the most portable and democratic. The paper's emphasis on "coordinates and numerical representations" is exactly how Daniel works through the CLI.

### 8.2 Fricker, P., Kotnik, T., and Borg, K. (2020). "Computational Design Pedagogy for the Cognitive Age."
- **Venue:** 38th eCAADe Conference, TU Berlin, September 16-18, 2020
- **URL:** https://papers.cumincad.org/cgi-bin/works/paper/ecaade2020_255
- **Summary:** Presents an integrative computational design thinking approach requiring the melding of computation, design, and theory as a conceptual framework for architectural education. Emphasizes computational thinking as a way of analyzing interactions across multiple scales.
- **Relevance:** The "cognitive" framing is significant: the project demonstrates that computational design thinking does not require visual cognition. Daniel's command-line interaction with parametric models exemplifies computational design thinking through a purely textual/auditory cognitive mode, challenging assumptions about what "computational design pedagogy" must look like.

### 8.3 Sass, L. (Teaching Award of Excellence, ACADIA 2024).
- **Venue:** ACADIA 2024: Designing Change, Calgary
- **Summary:** Larry Sass (MIT) received the ACADIA Teaching Award of Excellence as a "developer of innovative pedagogical approaches that center digital fabrication and making as an integral part of the design process."
- **Relevance:** The project's emphasis on physical-digital round-trips (pegboard to Rhino, Rhino to PIAF to 3D print) is a fabrication-centered pedagogy that includes a blind student. Sass's recognition by ACADIA validates the pedagogical approach; the project asks what that approach looks like when the student cannot see the screen.

---

## Theme 9: Architecture's Ocularcentrism -- Theoretical Foundations

These works provide the theoretical scaffolding for the project's critique of visual bias in architecture and design tools.

### 9.1 Pallasmaa, J. (1996/2005/2012). *The Eyes of the Skin: Architecture and the Senses.*
- **Venue:** Book, Wiley (multiple editions)
- **ISBN:** 978-1119941286
- **Summary:** Asks why, when there are five senses, has one single sense -- sight -- become so predominant in architectural culture and design. Argues that the suppression of the other four sensory realms has led to the overall impoverishment of the built environment. The most influential text critiquing architecture's ocularcentrism.
- **Relevance:** The foundational theoretical text for the project's framing. Pallasmaa's critique is philosophical; the project makes it operational. By building tools that work without vision, the project demonstrates what Pallasmaa argues: that non-visual architectural knowledge is not merely supplementary but reveals qualities that visual dominance obscures.

### 9.2 Heylighen, A. and Herssens, J. (2014). [See entry 2.1 above]
- **Additional note:** This paper bridges Pallasmaa's philosophical critique and empirical research with blind users. The phrase "designerly ways of not knowing" directly supports the project's claim that architecture's tools encode visual bias as a "way of not knowing" non-visual spatial experience.

---

## Theme 10: Accessible 3D Modeling and CAD for Blind Users

These papers from the broader HCI and accessibility literature (some indexed in CumInCAD) directly address the challenge of making CAD tools usable by blind people.

### 10.1 Siu, A.F., Kim, S., et al. (2019). "shapeCAD: An Accessible 3D Modelling Workflow for the Blind and Visually-Impaired Via 2.5D Shape Displays."
- **Venue:** ASSETS '19 (21st International ACM SIGACCESS Conference on Computers and Accessibility)
- **URL:** https://dl.acm.org/doi/10.1145/3308561.3353782
- **Summary:** 3D models are generated through OpenSCAD, a declarative programming language for 3D modeling, and rendered on a 2.5D shape display (12x24 actuated pins). Blind users leverage the low-resolution output to complement programming of 3D models, haptically explore and modify existing models, and author new models. Validated with five BVI programmers.
- **Relevance:** The most directly comparable system to the Radical Accessibility Project's approach. shapeCAD also uses a text-based programming language (OpenSCAD) for blind 3D modeling, with a separate physical output modality. The project's approach differs in three ways: (1) it uses a domain-specific CLI rather than a general programming language, making it accessible to architecture students without programming expertise; (2) it targets architectural-scale design (floor plans, buildings) rather than object-scale; (3) it integrates with industry-standard Rhino rather than a custom display.

### 10.2 Practical CAD Method for the Visually Impaired (2023).
- **Venue:** Universal Access in Human-Computer Interaction, Springer (LNCS)
- **URL:** https://link.springer.com/chapter/10.1007/978-3-031-35681-0_29
- **Summary:** Presents a practical CAD method for visually impaired users, demonstrated through modeling the Leaning Tower of Pisa. Addresses the challenge that existing CAD software is mostly visually reliant.
- **Relevance:** Confirms that the problem the project addresses -- visual reliance of CAD tools -- is recognized across the HCI and accessibility communities. The project's approach is more radical: rather than adapting existing visual CAD, it builds a non-visual-first interface layer that drives CAD tools as a viewer.

### 10.3 Tactile Architectural Drawings Typology (2022).
- **Authors:** Various
- **Venue:** Sustainability, MDPI, Vol. 14, No. 13, 7847
- **URL:** https://www.mdpi.com/2071-1050/14/13/7847
- **Summary:** Develops a typology of tactile architectural drawings accessible for blind and partially sighted people (typhlographics). Encompasses tactile drawings dedicated to the blind and thematically related to architectural objects and spaces at various scales.
- **Relevance:** Provides a classification framework for the project's tactile output. The PIAF swell paper drawings the project produces are a form of typhlographic output; this typology can inform standards for the project's "unified tactile export" pipeline.

---

## Theme 11: Data Exchange, Automation, and Live-Linking Pipelines

While no CumInCAD paper exactly describes the file-watching pattern used in the Radical Accessibility Project, these papers address related infrastructure challenges.

### 11.1 Nagakura, T. (1990). "Shape Recognition and Transformation: A Script-Based Approach."
- **Venue:** CAAD Futures '89, Cambridge, Massachusetts
- **Summary:** Explores script-based approaches to shape recognition and transformation in CAD environments, demonstrating early work on text-driven geometric operations.
- **Relevance:** An early precedent for text-driven geometry manipulation. The project's CLI commands like `set bay A rotation 30` are descendants of this script-based approach, refined for screen-reader accessibility.

### 11.2 Nembrini, J., Labelle, G., et al. (2009). "Source Studio: Teaching Programming for Architectural Design."
- **Venue:** CAAD Futures 2009
- **Summary:** Presents approaches to teaching programming for architectural design, including framework development for object-oriented geometry.
- **Relevance:** Supports the pedagogical dimension of the project: teaching architecture students to interact with geometry through code rather than visual manipulation.

### 11.3 Navarro Villacampa, A., et al. (2025). "Sensing the Invisible: Architectural Approaches to Sonifying Microbial Life in Icelandic Turf Houses through VR."
- **Venue:** eCAADe 2025, Ankara
- **Summary:** Explores sonification of invisible environmental phenomena (microbial life) within architectural spaces, using VR as a medium.
- **Relevance:** Demonstrates the growing interest in making the invisible audible in architectural contexts. While this paper sonifies microbial data, the project proposes sonifying spatial data (room dimensions, wall proximity, ceiling height) for a blind user's benefit.

---

## Summary Table

| # | Short Citation | Venue | Year | Primary Theme |
|---|---------------|-------|------|---------------|
| 1 | Noel et al., "Question of Access" | IJAC | 2021 | Equity in computational design |
| 2 | Cupkova et al., "AI, Architecture, Accessibility" | IJAC/ACADIA | 2023 | AI and accessibility |
| 3 | Karastathi et al., "Bridging Pixels" | ACADIA | 2024 | Accessible fabrication |
| 4 | eCAADe 2022 Conference Theme | eCAADe | 2022 | Inclusion in design |
| 5 | Heylighen & Herssens, "Designerly Ways" | J. Urban Design | 2014 | Blindness and design knowledge |
| 6 | Herssens & Heylighen, "Haptic Parameters" | CAAD Futures | 2011 | Haptic design |
| 7 | Vermeersch et al., "Disability Experience" | PDC | 2018 | Multi-sensoriality |
| 8 | Vermeersch & Heylighen, "Carlos Pereira" | Research proceedings | 2012 | Blind architect |
| 9 | Celani et al., "Seeing with the Hands" | CAAD Futures | 2013 | Tactile models |
| 10 | Garcia, "Sound Structure" | CAADRIA | 1996 | Sonification |
| 11 | Beilharz, "Architecture as Interface" | eCAADe | 2005 | Spatial sonification |
| 12 | More et al., "Spatial Information" | ACADIA | 2002 | Aural spatial design |
| 13 | More et al., "Designing Spatial Sounds" | eCAADe | 2004 | Sound for spatial info |
| 14 | Grabowski & Barner, "Force Feedback" | SPIE/CumInCAD | 1998 | Haptic + sonification |
| 15 | Koch et al., "Haptic Paintings" | eCAADe | 2012 | Tactile rapid prototyping |
| 16 | Garcia, "PUSH" | ACADIA | 1999 | Haptic form generation |
| 17 | Sjostrom, "Non-Visual Haptic Interaction" | PhD/CumInCAD | 2002 | Haptic design guidelines |
| 18 | Pohl & Hirschberg, "Sensitive Voxel" | CAAD Futures | 2011 | Tangible interfaces |
| 19 | Celani & Vaz, "CAD Scripting vs Visual" | IJAC | 2012 | Text vs visual CAD |
| 20 | Maleki & Woodbury, "Programming in Model" | ACADIA | 2013 | Script-model linking |
| 21 | Rietschel et al., "LLMs for Design Scripting" | ACADIA | 2024 | LLM-to-Grasshopper |
| 22 | Rietschel & Steinfeld, "Intelligent Tools" | IJAC | 2025 | Reasoning models for design |
| 23 | Atakan et al., "Kakadoo" | eCAADe | 2025 | Speech interface for CAD |
| 24 | CAADRIA 2022, "Rhetoric, Writing, Anexact" | CAADRIA | 2022 | NLP for architecture |
| 25 | Yousif & Vermisso, "AI-Assisted Workflows" | CAADRIA | 2022 | AI in design pedagogy |
| 26 | Miller, "[make]SHIFT" | ACADIA | 2010 | Design data exchange |
| 27 | Akbar et al., "Democratizing Toolbox" | eCAADe | 2023 | Open-source design pedagogy |
| 28 | Fricker et al., "Cognitive Age Pedagogy" | eCAADe | 2020 | Computational design teaching |
| 29 | Siu et al., "shapeCAD" | ASSETS | 2019 | Accessible 3D modeling |
| 30 | Pallasmaa, *Eyes of the Skin* | Book | 1996 | Ocularcentrism critique |

---

## NEW ADDITIONS (2021–2026): Deep Dive

The following papers were identified through targeted searches of ACADIA, CumInCAD, CHI, ASSETS, NeurIPS, IEEE VIS, and related venues. They extend the original review with recent work (primarily 2021–2026) across the project's core themes. Papers marked with ⚠ need citation verification before use in a publication.

---

### Theme A: LLM-to-CAD and AI-Driven Geometry Generation

These papers represent the rapidly expanding field of using language models to generate 3D geometry — the same core pattern as the Radical Accessibility Project's CLI-to-JSON-to-Rhino pipeline, but typically without accessibility considerations.

#### A.1 Khan, S., et al. (2024). "Text2CAD: Generating Sequential CAD Designs from Beginner-to-Expert Level Text Prompts."
- **Venue:** NeurIPS 2024 (Spotlight)
- **URL:** https://sadilkhan.github.io/text2cad-project/
- **arXiv:** https://arxiv.org/abs/2409.17106
- **Summary:** First end-to-end transformer-based autoregressive architecture for generating parametric CAD models from natural language prompts. Uses a two-stage annotation pipeline (VLM + LLM) to create ~660K text annotations for ~170K CAD models. Supports prompts from beginner ("two concentric cylinders") to expert level.
- **Relevance:** Demonstrates that natural-language-to-parametric-geometry is now a solved problem at the research level. The Radical Accessibility Project's CLI commands (`set bay A rotation 30`) are a domain-specific version of this pattern. Text2CAD's success validates the approach; the project's contribution is showing that text-to-geometry is not just convenient but *necessary* for a blind designer.

#### A.2 Rietschel, M., et al. "Raven: AI Plugin for Grasshopper."
- **Venue:** ACADIA 2024 / UC Berkeley research; commercial plugin released 2025
- **URL:** https://www.raven.build/
- **Summary:** Novel AI plugin for Grasshopper that uses LLMs to dynamically construct and refine parametric workflows at multiple abstraction levels — from individual node-level customization to high-level workflow orchestration. Users type natural language prompts; Raven generates and connects Grasshopper components automatically.
- **Relevance:** Raven makes Grasshopper's visual canvas text-controllable — but still requires seeing the canvas to verify results. The Radical Accessibility Project's architecture goes further by eliminating the visual dependency entirely: the CLI controller and the Rhino viewer are separate processes, so a blind user never needs to see Grasshopper at all.

#### A.3 "Ant: AI Copilot for Grasshopper" (2026).
- **Venue:** Food4Rhino plugin release, February 2026
- **URL:** https://blog.rhino3d.com/2026/02/ant-your-ai-copilot-for-grasshopper-new.html
- **Summary:** AI plugin that builds, modifies, and explains Grasshopper definitions from natural language. Translates component logic into structured format for LLM processing, then executes LLM instructions directly in the canvas.
- **Relevance:** Further evidence that the architecture community is moving toward text-to-geometry workflows. Like Raven, Ant assumes a sighted user who can inspect visual output. The project demonstrates that the architecture can be split so visual verification is handled by a sighted collaborator (or not needed at all).

#### A.4 Grasshopper MCP Server (2025).
- **Venue:** Open-source tool / MCP ecosystem
- **URL:** https://lobehub.com/mcp/dongwoosuk-rhino-grasshopper-mcp
- **Summary:** An MCP (Model Context Protocol) server that brings AI capabilities directly into Rhino/Grasshopper workflows, enabling AI agents to control parametric design through standardized protocol.
- **Relevance:** Directly relevant to the project's MCP exploration. Validates that the MCP transport layer can work with Rhino/Grasshopper. The project's approach differs by using file-watching as the primary transport (more robust, no server dependency) with MCP as a future conversational layer.

#### A.5 ⚠ Fu, R., et al. (2022). "ShapeCrafter: A Recursive Text-Conditioned 3D Shape Generation." NeurIPS 2022.
- **Summary:** Iteratively refines 3D shapes through sequential text instructions ("make the back taller," "add a wider seat"). Uses recursive conditioning to progressively modify geometry.
- **Relevance:** The iterative text-command paradigm mirrors the CLI's incremental command pattern. Demonstrates that sequential text-based shape modification is viable — the same interaction model the project uses.

#### A.6 ⚠ Ma, Y., et al. (2023/2024). "3D-GPT: Intelligent 3D Modeling with Large Language Models."
- **Summary:** Decomposes 3D modeling tasks into sub-problems handled by LLM agents that generate procedural code (Blender Python scripts). A task dispatch agent assigns modeling, conceptualization, and detailing roles.
- **Relevance:** Very close to the CLI architecture — LLMs generate text-based commands that drive geometry creation through a scripting layer. The agent decomposition parallels the controller/watcher separation.

#### A.7 Wu, S., et al. (2024). "CAD-LLM: Large Language Model for CAD Generation."
- **Venue:** NeurIPS 2023 Workshop / Autodesk Research
- **URL:** https://www.research.autodesk.com/publications/ai-lab-cad-llm/
- **Summary:** Develops generative models for CAD by fine-tuning pre-trained language models on engineering sketches. Achieves strong performance in various CAD generation scenarios by leveraging the sequential nature of CAD operations.
- **Relevance:** Establishes that language model architectures are well-suited to CAD's sequential, parametric nature — the same property that makes CLI-based interaction natural for architectural design.

#### A.8 CADialogue (2025). "A Multimodal LLM-Powered Conversational Assistant for Intuitive Parametric CAD Modeling."
- **Venue:** Computer-Aided Design (ScienceDirect)
- **URL:** https://www.sciencedirect.com/science/article/abs/pii/S0010448525001678
- **Summary:** Enables intuitive parametric CAD modeling through natural language, speech, image inputs, and geometry selection. Conversational interface for iterative design refinement.
- **Relevance:** The conversational paradigm is exactly what the project envisions through MCP — Daniel asking "describe the north elevation" and receiving an AI response. CADialogue assumes multimodal (visual + text) input; the project needs text/speech-only input.

---

### Theme B: Accessible 3D Modeling and Design Tools for Blind Users

These papers directly address the challenge of enabling blind and low-vision users to create and interact with 3D content — the project's core problem space.

#### B.1 Siu, A., et al. (2025). "A11yShape: AI-Assisted 3-D Modeling for Blind and Low-Vision Programmers."
- **Venue:** ASSETS '25 (27th International ACM SIGACCESS Conference on Computers and Accessibility)
- **DOI:** https://doi.org/10.1145/3663547.3746362
- **arXiv:** https://arxiv.org/abs/2508.03852
- **Summary:** Combines OpenSCAD (text-based 3D modeling) with GPT-4o to create an accessible 3D modeling environment. Introduces a four-facet representation: source code, hierarchical model abstraction, AI-generated textual descriptions, and rendered output. Three synchronized panels let blind programmers discover how code changes affect designs. Four blind/low-vision participants successfully completed both guided and free-form 3D modeling tasks (SUS score: 80.6).
- **Relevance:** **The most directly comparable recent system to the Radical Accessibility Project.** A11yShape also uses text-based modeling (OpenSCAD) with AI assistance for blind users. Key differences: (1) A11yShape targets general 3D modeling; the project targets architectural design with domain-specific commands; (2) A11yShape is a single integrated tool; the project's decoupled architecture (CLI + JSON + Rhino) enables a blind user to work independently while a sighted collaborator observes in Rhino; (3) the project's CLI output protocol is specifically designed for screen readers (OK:/ERROR: prefixes), while A11yShape relies on OpenSCAD's generic output.

#### B.2 Crawford, S., et al. (2024). "Co-designing a 3D-Printed Tactile Campus Map With Blind and Low-Vision University Students."
- **Venue:** ASSETS '24 (26th International ACM SIGACCESS Conference)
- **DOI:** https://doi.org/10.1145/3663548.3688537
- **Summary:** Participatory design with BLV university students to create a 3D-printed tactile campus map. During co-design iterations, the participant's screen reader was unable to interpret TinkerCAD's interface, making it impractical for them to manipulate the design directly.
- **Relevance:** Powerfully demonstrates the accessibility failure the project addresses — CAD tools (even "simple" ones like TinkerCAD) are screen-reader-incompatible. The project's CLI-first architecture directly solves this problem. Also validates the co-design methodology the project uses with Daniel.

#### B.3 Shi, L., Zhao, Y., et al. (2020). "Molder: An Accessible Design Tool for Tactile Maps."
- **Venue:** CHI 2020
- **URL:** https://rgonzalezp.github.io/research/2020-04-03-Molder/
- **Summary:** Accessible tool for creating interactive tactile maps. Designers create draft map models and refine them with auditory and high-contrast visual feedback. Addresses the problem that O&M specialists who design tactile materials are often visually impaired themselves and cannot use standard modeling tools.
- **Relevance:** Shares the project's insight that the *creators* of accessible materials are often disabled themselves and need accessible authoring tools. Molder addresses tactile map creation; the project addresses architectural floor plan creation — analogous problems at different scales.

#### B.4 Potluri, V., et al. (2022). "CodeWalk: Facilitating Shared Awareness in Mixed-Ability Collaborative Software Development."
- **Venue:** ASSETS '22 (24th International ACM SIGACCESS Conference)
- **Summary:** Addresses collaborative coding between sighted and blind developers, focusing on shared awareness when one developer uses a screen reader and another uses a visual IDE.
- **Relevance:** The project's controller/viewer separation enables a similar mixed-ability collaboration pattern: Daniel works in the CLI (accessible), a sighted collaborator observes in Rhino (visual). CodeWalk's findings about shared awareness inform how the project might improve collaboration between Daniel and sighted studio peers.

---

### Theme C: Blind Users, AI, and Generative Tools

These papers examine how blind people actually use AI tools — critical context for the project's AI-assisted description pipeline.

#### C.1 Das, M., Adnin, R., et al. (2024). "'I look at it as the king of knowledge': How Blind People Use and Understand Generative AI Tools."
- **Venue:** ASSETS '24
- **DOI:** https://doi.org/10.1145/3663548.3675631
- **URL:** https://maitraye.github.io/files/papers/BLV_GenAI_ASSETS24.pdf
- **Summary:** Interviews with 19 blind individuals on their use of mainstream GenAI tools (ChatGPT, Be My AI). Finds that blind users integrate AI into daily practices but face significant accessibility barriers in the interfaces. Users conceptualize LLMs differently than sighted users.
- **Relevance:** Directly informs how the project's AI critique partner should work. The finding that blind users face accessibility barriers even in AI interfaces validates the project's decision to build a purpose-designed, screen-reader-native CLI rather than relying on existing AI chat interfaces.

#### C.2 MAIDR + AI (2024). "Exploring Multimodal LLM-Based Data Visualization Interpretation by and with Blind and Low-Vision Users."
- **Venue:** ASSETS '24
- **DOI:** https://doi.org/10.1145/3663548.3675660
- **Summary:** Co-designed an LLM extension providing multiple AI responses to blind users' visual queries about data visualizations. Explores how multimodal LLMs can serve as an interpretation layer between visual content and blind users.
- **Relevance:** The "AI as interpretation layer" pattern is exactly what the project needs for describing Rhino viewport content to Daniel. This paper provides evidence that LLM-based interpretation works for visual content accessibility.

#### C.3 Stangl, A., et al. (2021). "Going Beyond One-Size-Fits-All Image Descriptions to Satisfy the Information Wants of People Who are Blind or Have Low Vision."
- **Venue:** ASSETS '21
- **URL:** https://cs.stanford.edu/~merrie/papers/assets2021_scenarios.pdf
- **Summary:** Studies what information blind users want from image descriptions, finding that needs vary by context and purpose. Proposes context-aware descriptions rather than one-size-fits-all approaches.
- **Relevance:** Directly informs how the project's AI vision/description pipeline should generate architectural descriptions for Daniel — different descriptions for design review, spatial navigation, precedent study, and critique sessions.

#### C.4 CHI 2024. "Investigating Use Cases of AI-Powered Scene Description Applications for Blind and Low Vision People."
- **Venue:** CHI 2024
- **DOI:** https://doi.org/10.1145/3613904.3642211
- **Summary:** Examines how blind and low-vision users employ AI scene description tools (like Be My Eyes, Seeing AI) in real-world contexts.
- **Relevance:** The project's Ray-Ban Meta glasses pipeline uses exactly these AI-powered scene description tools. This paper provides evidence on their strengths and limitations in practice.

---

### Theme D: Tactile Graphics, Physical-Digital Pipelines

These papers address the production and use of tactile representations — core to the project's PIAF swell paper pipeline and physical-digital round-trip.

#### D.1 Butler, M., et al. (2023). "TactIcons: Designing 3D Printed Map Icons for People who are Blind or have Low Vision."
- **Venue:** CHI 2023
- **DOI:** https://doi.org/10.1145/3544548.3581359
- **Summary:** Designed and touch-tested over 200 tactile icons for street and park maps with blind and sighted participants. Resulted in 33 instantly recognizable icons and 34 easily learned ones.
- **Relevance:** Provides a design vocabulary for tactile architectural representations. The project's PIAF output for floor plans could adopt similar icon conventions for columns, corridors, voids, and other architectural elements.

#### D.2 Billah, S.M., et al. (2023). "Designing While Blind: Nonvisual Tools and Inclusive Workflows for Tactile Graphic Creation."
- **Venue:** ASSETS '23 (25th International ACM SIGACCESS Conference)
- **DOI:** https://doi.org/10.1145/3597638.3614546
- **Summary:** Formed a Blind-led team of four Blind designers, one sighted designer, and one sighted researcher to design tactile graphics. Found that inaccessible digital tools prevent Blind people from leading the design of media they consume. Contributed recommendations for nonvisual tools and inclusive workflows.
- **Relevance:** **Critically important.** This paper's central argument — that blind designers are excluded from creating the very media they consume — is the exact problem the Radical Accessibility Project solves. The project's CLI-to-PIAF pipeline enables Daniel to *author* tactile architectural drawings, not just receive them. The "Designing While Blind" team's workflow recommendations directly inform the project's tool design.

#### D.3 Holloway, L. & Marriott, K. (2018/2023+). "Accessible Maps for the Blind: Comparing 3D Printed Models with Tactile Graphics."
- **Venue:** CHI 2018; follow-up work through 2025
- **URL:** https://dl.acm.org/doi/10.1145/3173574.3173772
- **Summary:** Controlled study with 16 touch readers comparing 3D printed models with tactile graphics (swell paper). 3D models were preferred, enabled more easily understood icons, facilitated better recall. Analyzed hand movement strategies for systematic scanning.
- **Relevance:** Directly informs the project's choice between 3D printing and PIAF swell paper for different representations. Their finding that 3D models better convey relative height suggests using 3D prints for sectional models and PIAF for plans.

#### D.4 ⚠ FlexiBoard (2024). "The FlexiBoard: Tangible and Tactile Graphics for People with Vision Impairments."
- **Venue:** Multimodal Technologies and Interaction (MDPI), Vol. 8, No. 3
- **URL:** https://www.mdpi.com/2414-4088/8/3/17
- **Summary:** A flexible tangible interface for creating and interacting with tactile graphics, combining physical manipulation with digital feedback.
- **Relevance:** Relevant to the project's pegboard system as an alternative physical input modality.

#### D.5 MIT (2025). "Tactile Vega-Lite: Making Graphs More Accessible to Blind and Low-Vision Readers."
- **Venue:** MIT News / Research paper, March 2025
- **URL:** https://news.mit.edu/2025/making-graphs-more-accessible-blind-low-vision-readers-0325
- **Summary:** Program that takes data from spreadsheets and generates both visual charts and touch-based tactile graphics automatically, using the Vega-Lite visualization grammar.
- **Relevance:** The automatic visual-to-tactile translation pattern is exactly what the project's export pipeline does (state.json → Rhino geometry → tactile PIAF export). Tactile Vega-Lite validates the approach of automatic conversion rather than manual recreation.

---

### Theme E: Accessible Visualization and Natural Language Description

These papers address making visual information accessible through text and natural language — core to the project's screen-reader-native output design.

#### E.1 Lundgard, A. & Satyanarayan, A. (2022). "Accessible Visualization via Natural Language Descriptions: A Four-Level Model of Semantic Content."
- **Venue:** IEEE Transactions on Visualization and Computer Graphics, Vol. 28, No. 1
- **arXiv:** https://arxiv.org/abs/2110.04406
- **Summary:** Introduces a four-level model of semantic content in visualization descriptions: L1 (construction — chart type, axes), L2 (statistics — extremes, correlations), L3 (trends — patterns, comparisons), L4 (context — domain-specific insights). Based on grounded theory analysis of 2,147 sentences.
- **Relevance:** Directly applicable to how the project describes architectural designs to Daniel. The CLI's `show` and `describe` commands could be structured around these four levels: L1 (what elements exist), L2 (dimensions and quantities), L3 (spatial relationships and patterns), L4 (design implications and critique).

#### E.2 ⚠ Sharif, A., et al. (2022). "Understanding Screen-Reader Users' Experiences with Online Data Visualizations." EuroVIS 2022.
- **Summary:** Studies how screen reader users navigate and understand data visualizations, identifying common failure patterns and successful strategies.
- **Relevance:** Informs how the project's visual output from Rhino should be accompanied by structured text descriptions for Daniel.

---

### Theme F: Equity, Inclusion, and Disability in Design Practice and Education

These papers strengthen the theoretical and empirical framing for the project's ACADIA 2026 submission.

#### F.1 Zallio, M. & Clarkson, P.J. (2021). "Inclusion, Diversity, Equity and Accessibility in the Built Environment: A Study of Architectural Design Practice."
- **Venue:** Building and Environment, Vol. 206, 108352
- **DOI:** 10.1016/j.buildenv.2021.108352
- **URL:** https://www.sciencedirect.com/science/article/pii/S0360132321007496
- **Summary:** Ethnographic study of 26 building industry professionals on the adoption of inclusive design. Finds that education and awareness are essential to encourage an inclusive mindset, and recommends holistically mapping user journeys and collecting post-occupancy feedback.
- **Relevance:** Provides empirical evidence that architecture practice systematically excludes disability perspectives. The Radical Accessibility Project's co-design approach with Daniel directly responds to Zallio & Clarkson's call for holistic inclusion.

#### F.2 Zallio, M. & Clarkson, P.J. (2023). "A Study to Depict Challenges and Opportunities Building Industry Professionals Face When Designing Inclusive and Accessible Buildings."
- **Venue:** Architectural Science Review, Vol. 67, pp. 268–279
- **URL:** https://www.tandfonline.com/doi/full/10.1080/00038628.2023.2270983
- **Summary:** Identifies specific challenges professionals face when designing accessibly, including lack of tools, training, and systematic approaches.
- **Relevance:** The project provides exactly the kind of tool-level intervention Zallio & Clarkson identify as missing.

#### F.3 Heylighen, A., et al. (2021–2024). Recent work from Research[x]Design, KU Leuven.
- **URL:** https://rxd.architectuur.kuleuven.be/projects/how-do-disabled-architects-design/
- **Key project:** "How Do Disabled Architects Design?" — examines how architects with disabilities (including vision impairment) approach design differently and what this reveals about architectural knowledge.
- **2021 paper:** Liebergesell, N.P. & Heylighen, A. (2021). "Urban Chandelier: How Experiences of Being Vision Impaired Inform Designing for Attentiveness." *Journal of Interior Design*, Vol. 46, No. 1.
- **2023 paper:** "The Potential of Disability Experience for Heritage" (December 2023).
- **Relevance:** Heylighen's continued work provides the strongest theoretical precedent for the project's thesis. Her research program demonstrates that disability experience generates architectural knowledge that visual-normative practice misses — the same argument the project makes through its tools.

#### F.4 del Campo, M. (2022–2024). AI and Architecture publications.
- **Books:** *Neural Architecture: Design and Artificial Intelligence* (ORO Editions, 2022); *Machine Hallucinations: Architecture and Artificial Intelligence* (AD/Wiley, 2022); *Diffusions in Architecture* (Wiley, 2024); *Artificial Intelligence in Architecture* (AD)
- **Relevance:** Establishes the ACADIA community's deep engagement with AI-architecture integration. Del Campo's work is the context the project's paper enters — but none of his work addresses accessibility. The project's contribution is showing that AI-architecture tools can and must be accessible.

---

### Theme G: Accessible Programming and Screen-Reader-Compatible Development

These papers from HCI address the broader challenge of making programming tools accessible — relevant because the project's CLI is a programming-like environment.

#### G.1 Potluri, V., et al. (2018). "CodeTalk: Improving Programming Environment Accessibility for Visually Impaired Developers."
- **Venue:** CHI 2018 (Honorable Mention)
- **DOI:** https://doi.org/10.1145/3173574.3174192
- **Summary:** Categorizes IDE accessibility difficulties into Discoverability, Glanceability, Navigability, and Alertability. Implements CodeTalk plugin for Visual Studio addressing these categories.
- **Relevance:** The four accessibility categories (DGNA) provide a useful framework for evaluating the project's CLI design. The CLI's OK:/ERROR: prefix convention addresses Glanceability and Alertability; its help system addresses Discoverability; its sequential command structure addresses Navigability.

---

## Updated Summary Table (New Additions Only)

| # | Short Citation | Venue | Year | Primary Theme |
|---|---------------|-------|------|---------------|
| 31 | Khan et al., "Text2CAD" | NeurIPS | 2024 | NL-to-CAD generation |
| 32 | Rietschel et al., "Raven" | ACADIA/Berkeley | 2024 | LLM Grasshopper plugin |
| 33 | "Ant" plugin | Food4Rhino | 2026 | AI Grasshopper copilot |
| 34 | Grasshopper MCP Server | Open source | 2025 | MCP-to-Rhino bridge |
| 35 | Wu et al., "CAD-LLM" | NeurIPS Workshop | 2024 | LLM for CAD generation |
| 36 | CADialogue | Computer-Aided Design | 2025 | Conversational CAD |
| 37 | Siu et al., "A11yShape" | ASSETS | 2025 | Accessible 3D modeling |
| 38 | Crawford et al., "Co-designing Tactile Map" | ASSETS | 2024 | Tactile maps + co-design |
| 39 | Shi et al., "Molder" | CHI | 2020 | Accessible tactile map tool |
| 40 | Potluri et al., "CodeWalk" | ASSETS | 2022 | Mixed-ability collaboration |
| 41 | Das et al., "Blind + GenAI" | ASSETS | 2024 | Blind users + AI tools |
| 42 | MAIDR + AI | ASSETS | 2024 | LLM viz interpretation |
| 43 | Stangl et al., "Image Descriptions" | ASSETS | 2021 | Context-aware descriptions |
| 44 | CHI 2024, "AI Scene Description" | CHI | 2024 | AI scene description apps |
| 45 | Butler et al., "TactIcons" | CHI | 2023 | 3D printed tactile icons |
| 46 | Billah et al., "Designing While Blind" | ASSETS | 2023 | Blind-led tactile design |
| 47 | Holloway & Marriott, "Accessible Maps" | CHI | 2018+ | 3D print vs swell paper |
| 48 | "Tactile Vega-Lite" | MIT | 2025 | Auto visual-to-tactile |
| 49 | Lundgard & Satyanarayan, "4-Level Model" | IEEE VIS | 2022 | NL viz descriptions |
| 50 | Zallio & Clarkson, "IDEA Built Env" | Building & Env | 2021 | Inclusive design practice |
| 51 | Zallio & Clarkson, "Challenges" | Arch Science Rev | 2023 | Inclusive design barriers |
| 52 | Heylighen et al., "Disabled Architects" | KU Leuven/various | 2021+ | Disability experience |
| 53 | del Campo, "Neural Architecture" | Books/ACADIA | 2022+ | AI + architecture context |
| 54 | Potluri et al., "CodeTalk" | CHI | 2018 | Accessible IDE design |
| 55 | Potluri et al., "CodeWalk" | ASSETS | 2022 | Mixed-ability coding |

---

## Key Gaps in the Literature (Updated)

The expanded review (55 papers) reveals that the Radical Accessibility Project occupies a unique intersection. The gaps identified in the original review mostly persist, but with important nuances:

1. **No CumInCAD paper describes a CLI-first, screen-reader-native architectural design tool.** This remains true. Text2CAD (A.1), Raven (A.2), Ant (A.3), and CADialogue (A.8) all build text-to-geometry pipelines but assume sighted verification. A11yShape (B.1) is the closest system — it uses text-based modeling for blind users — but targets general 3D modeling, not architectural design, and is not integrated with industry CAD tools.

2. **The LLM-to-CAD explosion strengthens the project's positioning.** In 2024–2026, text-to-geometry became a mainstream research direction (Text2CAD, CAD-LLM, Raven, Ant, CADialogue, 3D-GPT). The project can now argue: "The architecture community has independently converged on text-to-geometry as the future of design interaction. We arrived at the same architecture by a different route — necessity, not convenience — and our approach has the additional property of being fully accessible."

3. **"Designing While Blind" (D.2) directly validates the project's authorship thesis.** Billah et al. (2023) show that blind people are excluded from *creating* tactile media, not just consuming it. The project's CLI-to-PIAF pipeline is the architectural-design-specific solution to this problem.

4. **Blind users' experiences with GenAI tools (C.1, C.2) reveal interface barriers the project must avoid.** Das et al. (2024) find that even ChatGPT's interface creates accessibility barriers for blind users. The project's screen-reader-native CLI output protocol is validated as necessary, not merely convenient.

5. **The co-design gap persists.** Crawford et al. (B.2) found that TinkerCAD is screen-reader-incompatible during co-design with blind students. The project is still the only system where a blind architecture student co-designs the tools they use *while using them* in a graduate studio.

6. **Sonification for design authoring remains unexplored.** No new papers address sonification as real-time feedback for a blind designer creating new spaces. This remains the project's most novel future direction.

7. **The file-watching pattern as accessibility architecture is still unrecognized.** No paper examines JSON-file-watching as a strategy for decoupling accessible controllers from inaccessible viewers. The MCP server for Grasshopper (A.4) validates the transport-layer concept but uses a different pattern (server vs. file). The project's approach is simpler, more robust, and crash-safe.

8. **Accessibility in the ACADIA/CumInCAD literature remains thin.** Despite 2,500+ papers in CumInCAD from 2021–2025, accessibility/disability content barely registers. The project's ACADIA 2026 paper would be among the first to directly address how a blind student uses computational design tools in a graduate architecture studio.

---

## Recommended Reading Order for ACADIA 2026 Framing (Updated)

For positioning the Radical Accessibility Project within the ACADIA discourse, read in this order:

**Theoretical foundations:**
1. **Pallasmaa (1996)** -- Architecture's ocularcentrism
2. **Heylighen & Herssens (2014)** -- What designers miss; designerly ways of not knowing
3. **Heylighen et al. (2021+)** -- How disabled architects design differently

**Equity and access:**
4. **Noel et al. (2021)** -- The question of access in computational design
5. **Cupkova et al. (2023)** -- ACADIA's engagement with accessibility and AI
6. **Zallio & Clarkson (2021)** -- Inclusion in architectural practice

**Text-based and AI-driven CAD (state of the art):**
7. **Celani & Vaz (2012)** -- Text vs. visual CAD pedagogy
8. **Rietschel et al. (2024)** -- LLMs for design scripting (Raven)
9. **Text2CAD (2024)** -- NL-to-parametric-CAD (NeurIPS)
10. **Atakan et al. (2025)** -- Kakadoo: speech interfaces in CAAD

**Accessible 3D modeling (direct comparators):**
11. **Siu et al. (2019)** -- shapeCAD: the original accessible 3D modeler
12. **Siu et al. (2025)** -- A11yShape: AI-assisted accessible 3D modeling
13. **Crawford et al. (2024)** -- Co-designing with blind students (CAD tools fail)
14. **Billah et al. (2023)** -- Designing While Blind (authorship gap)

**Tactile and multi-sensory:**
15. **Celani et al. (2013)** -- Tactile models for blind learners
16. **Butler et al. (2023)** -- TactIcons: 3D printed tactile vocabulary
17. **Garcia (1996)** -- Sonification: the unexplored channel

**Blind users and AI tools:**
18. **Das et al. (2024)** -- How blind people use generative AI
19. **Stangl et al. (2021)** -- Context-aware image descriptions
20. **Lundgard & Satyanarayan (2022)** -- Four-level model for accessible descriptions

---

## CROSS-DISCIPLINARY FOUNDATIONS (Deep Dive, Round 2)

The papers above are drawn from computational design and HCI conferences — the expected venues for an ACADIA submission. But the Radical Accessibility Project's argument is fundamentally interdisciplinary. It draws on architectural phenomenology, critical disability studies, cognitive science, acoustic ecology, and the politics of technology. The following works provide the deeper theoretical scaffolding that transforms the paper from a tool demo into a disciplinary critique.

---

### Theme H: Architectural Phenomenology — The Sensory Beyond Vision

These works provide the philosophical foundation for arguing that architecture is fundamentally multi-sensory and that visual dominance in design tools represents an impoverishment, not a neutral default.

#### H.1 Pallasmaa, J. (1996/2005/2012). *The Eyes of the Skin: Architecture and the Senses.*
- **Already in original review (9.1).** Remains the foundational text.

#### H.2 Zumthor, P. (2006). *Atmospheres: Architectural Environments — Surrounding Objects.*
- **Publisher:** Birkhäuser
- **Summary:** Zumthor identifies nine generators of architectural atmosphere: The Body of Architecture, Material Compatibility, The Sound of a Space, The Temperature of a Space, Surrounding Objects, Between Composure and Seduction, Tension between Interior and Exterior, Levels of Intimacy, and The Light of Things. Crucially, only one of these nine — Light — is primarily visual. Sound, temperature, material feel, and spatial tension are all non-visual.
- **Relevance:** Zumthor's nine generators provide an operational vocabulary for what the project's tools must capture. The CLI's semantic model (bays, corridors, columns, voids) describes the "Body of Architecture." The planned sonification pipeline could address "The Sound of a Space." The project demonstrates that computational tools can encode Zumthor's multi-sensory architecture, not just its visual projection.

#### H.3 Böhme, G. (2017). *The Aesthetics of Atmospheres.* Ed. Jean-Paul Thibaud.
- **Publisher:** Routledge
- **Summary:** Argues that spatial atmospheres exert tangible emotional effects by appealing directly to the senses. Architecture is experienced through bodily, multi-sensory perception before intellectual comprehension. Develops a "new aesthetics" grounded in embodied experience rather than visual contemplation.
- **Relevance:** Böhme's theory that we experience space sensorially *before* we understand it visually directly supports the project's thesis. If atmosphere precedes vision, then tools that bypass vision and work through text, sound, and touch are not lesser — they may access architectural experience more directly.

#### H.4 Pérez-Gómez, A. (2016). *Attunement: Architectural Meaning after the Crisis of Modern Science.*
- **Publisher:** MIT Press
- **Summary:** Argues that architecture's essential task is attunement between human beings and their environment. Draws on embodied cognition research to argue that the built environment is a constituent part of consciousness. Perception is established as something we *do*, not something that happens to us — proactive, not merely reactive.
- **Relevance:** "Attunement" reframes architecture as an active, embodied relationship — not a picture. This supports the project's argument that Daniel's tactile, auditory, and command-line engagement with architecture is not a workaround for "real" (visual) design but a different — possibly deeper — form of architectural attunement.

#### H.5 Holl, S., Pallasmaa, J., & Pérez-Gómez, A. (1994/2006). *Questions of Perception: Phenomenology of Architecture.*
- **Publisher:** A+U / William Stout
- **Summary:** Three interlocking essays — Holl on "phenomenal zones" (color, light, shadow, time, sound), Pallasmaa on "An Architecture of the Seven Senses," Pérez-Gómez on "The Space of Architecture: Meaning as Presence and Representation." Collectively argues that architecture is a multi-sensory phenomenon irreducible to its visual representation.
- **Relevance:** The canonical collaborative text linking phenomenology and architecture. Pallasmaa's "seven senses" essay directly supports the project's argument that architecture engages senses beyond sight. The project operationalizes this philosophical position through tools.

---

### Theme I: The Phenomenology and Cognition of Blindness

These works address how blind people actually perceive, navigate, and understand space — the empirical foundation for the project's design decisions.

#### I.1 Merleau-Ponty, M. (1945/1962). *Phenomenology of Perception.*
- **Publisher:** Routledge (trans. Colin Smith; later trans. Donald Landes, 2012)
- **Summary:** The foundational phenomenological text on embodied perception. Argues for "the primacy of perception" — that consciousness is fundamentally embodied, not disembodied cognition. Introduces the famous "blind man's cane" example: the cane becomes an extension of the body schema, demonstrating that perception is not limited to biological sense organs.
- **Relevance:** Provides the deepest philosophical foundation for the project. If perception is embodied and extends through tools (the cane), then the CLI is Daniel's "cane" for architectural design — an extension of his body schema into the design model. However, see Reynolds (I.2) for critical corrections.

#### I.2 Reynolds, J.M. (2017). "Merleau-Ponty, World-Creating Blindness, and the Phenomenology of Non-Normate Bodies."
- **Venue:** Chiasmi International, Vol. 19, pp. 419–436
- **URL:** https://philarchive.org/rec/REYMWB
- **Summary:** Critiques Merleau-Ponty's "blind man's cane" example for omitting social dimensions of disability, misconstruing blindness as world-creating, and operating via an able-bodied simulation. Argues that phenomenology must heed "crip phenomenology" — taking the lived experience of disability as its departure point rather than simulating it from a normate perspective.
- **Relevance:** Essential corrective. The project must not romanticize or simulate blindness (a common trap in "designing for empathy" approaches). Reynolds' argument supports the project's methodology: Daniel is a co-designer, not a subject. The tools are built *from* his experience, not *about* it.

#### I.3 Saerberg, S. (2010). "'Just go straight ahead': How Blind and Sighted Pedestrians Negotiate Space."
- **Venue:** The Senses and Society, Vol. 5, No. 3
- **Summary:** Ethnographic study of how blind pedestrians negotiate spatial environments. Draws on Schütz and Merleau-Ponty to show that blindness constitutes a distinct perceptual lifeworld — not a deficit version of sighted experience. Blind pedestrians rely on sequential, route-based spatial knowledge rather than simultaneous, survey-based knowledge.
- **Relevance:** The distinction between sequential/route knowledge and simultaneous/survey knowledge maps directly onto the project's interface design. The CLI's sequential command structure (one command at a time, building up a model incrementally) aligns with how blind people naturally build spatial understanding. Visual CAD's simultaneous display of the entire model is inherently survey-based.

#### I.4 Chen, Q., et al. (2024). "Perception beyond sight: Investigating the cognitive maps of congenitally blind individuals in urban environments."
- **Venue:** ScienceDirect (2024)
- **URL:** https://www.sciencedirect.com/science/article/pii/S2095263524000281
- **Summary:** Studies how congenitally blind individuals construct cognitive maps of cities using touch, hearing, smell, safety sense, and experience. Mental maps consist of five elements: links, reference points, areas, separators, and topography.
- **Relevance:** Provides empirical evidence for how Daniel likely constructs mental models of the architectural designs he creates. The CLI's semantic vocabulary (bays, corridors, columns) maps onto the "reference points" and "areas" that blind cognitive maps prioritize.

#### I.5 Giudice, N.A. (2018). "Navigating without Vision: Principles of Blind Spatial Cognition."
- **Venue:** Handbook of Behavioral and Cognitive Geography (Edward Elgar)
- **Summary:** Reviews research on spatial cognition without vision. Key finding: blind people can and do form accurate spatial representations, but through different processes than sighted people — sequential, landmark-based, and language-mediated rather than simultaneous and visual.
- **Relevance:** The "language-mediated" finding is critical. It means that Daniel's text-based interaction with architecture is not a workaround — it is aligned with how spatial cognition actually works without vision. Language *is* a spatial medium for blind people.

#### I.6 Cattaneo, Z. & Vecchi, T. (2011). *Blind Vision: The Neuroscience of Visual Impairment.*
- **Publisher:** MIT Press
- **Summary:** Comprehensive review of neuroscience research on how blindness affects (and does not affect) spatial cognition. Demonstrates that blind individuals develop robust spatial representations through touch, hearing, and language. Challenges deficit models of blindness.
- **Relevance:** Provides neuroscientific evidence supporting the project's thesis that blindness does not preclude rich spatial reasoning — it merely requires different input modalities. The CLI provides one such modality; the tactile output provides another.

---

### Theme J: Critical Disability Studies and the Politics of Design

These works provide the theoretical framework for arguing that the project is *disciplinarily transformative, not assistive* — that it reveals structural biases in architecture's tool ecosystem.

#### J.1 Hamraie, A. (2017). *Building Access: Universal Design and the Politics of Disability.*
- **Publisher:** University of Minnesota Press
- **URL:** https://www.upress.umn.edu/9781517901646/building-access/
- **Summary:** Blends technoscience studies and design history with critical disability, race, and feminist theories. Traces the co-evolution of accessible design for disabled veterans, a radical disability maker movement, disability rights law, and strategies for diversifying the architecture profession. Introduces "normate template" and "crip technoscience" concepts.
- **Relevance:** The most important critical-theoretical text for the project's framing. Hamraie's "normate template" concept applies directly to CAD tools: Rhino, Grasshopper, and Revit are designed around a normate template that assumes a sighted, mouse-using operator. The project replaces this template with one that assumes a screen-reader-using, keyboard-operating architect.

#### J.2 Hamraie, A. & Fritsch, K. (2019). "Crip Technoscience Manifesto."
- **Venue:** Catalyst: Feminism, Theory, Technoscience, Vol. 5, No. 1
- **URL:** https://catalystjournal.org/index.php/catalyst/article/view/29607
- **Summary:** Defines "crip technoscience" as a field centering the work disabled people do as "knowers and makers." Challenges the imperatives to be typical, productive, and functioning. Argues that too often in architecture and design, disabled people are treated solely as users, not as makers.
- **Relevance:** The Crip Technoscience Manifesto provides the theoretical language for the project's most radical claim: Daniel is not a user of accessibility features — he is a maker of architectural knowledge. The project's tools don't accommodate his blindness; they *leverage* it as a source of design insight. The manifesto's commitment to "interdependence as political technology" also frames the controller/viewer separation: Daniel and his sighted collaborators are interdependent, not in a helper/helped relationship.

#### J.3 Gissen, D. (2022). *The Architecture of Disability: Buildings, Cities, and Landscapes beyond Access.*
- **Publisher:** University of Minnesota Press
- **URL:** https://www.upress.umn.edu/book-division/books/the-architecture-of-disability
- **Summary:** Argues against centering "access" in disability design. Disability should not be relegated to access or accommodation alone. The overwhelming focus on access perpetuates inequalities. Proposes instead that disability experience should be a foundation for architectural form — structuring monuments, nature, urbanization, form, interior environments, and tectonics.
- **Relevance:** Gissen's argument that architecture must go "beyond access" is precisely the project's argument about tools. The project does not merely make Rhino "accessible" (that would be an accommodation). It builds a fundamentally different tool ecosystem where blindness is the primary design case. Gissen is a disabled architect himself — his perspective validates the project's approach.

#### J.4 Boys, J. (2014). *Doing Disability Differently: An Alternative Handbook on Architecture, Dis/ability and Designing for Everyday Life.*
- **Publisher:** Routledge
- **Summary:** Reframes disability as generative and creative — a radical, even avant-garde, approach to architectural education and practice. Asks how disability and ability can help us think more explicitly about habitation. Introduces architects to disability studies and challenges compliance-focused thinking.
- **Relevance:** Boys' framing of disability as "avant-garde" aligns with the project's claim that designing for blindness produces genuinely novel computational design methods. The project can cite Boys to argue that its ACADIA contribution is not a social-good sideshow but a cutting-edge methodological intervention.

#### J.5 Williamson, B. (2019). *Accessible America: A History of Disability and Design.*
- **Publisher:** NYU Press
- **URL:** https://nyupress.org/9781479894093/accessible-america/
- **Summary:** Historical study of how disability advocates harnessed technological design in their quest for access and equality. Shows that access "does not just happen" — when activists, designers, experts, tinkerers, and users address everyday technologies as barriers or as accessible, they define disability as a phenomenon emerging from the material environment.
- **Relevance:** Provides the historical context for the project's work. Williamson's insight that disability emerges from material environments (not bodies) applies directly to CAD tools: the "disability" of a blind architecture student is produced by the tool environment (visual-only CAD), not by the student. The project eliminates the material barrier.

#### J.6 Winner, L. (1980). "Do Artifacts Have Politics?"
- **Venue:** Daedalus, Vol. 109, No. 1, pp. 121–136
- **URL:** https://www.jstor.org/stable/20024652
- **Summary:** The foundational STS (Science and Technology Studies) text arguing that technologies are not politically neutral — they embody and enforce social arrangements. Technologies can be designed to systematically include or exclude specific groups.
- **Relevance:** Winner's argument, applied to the project: Rhino's viewport, Grasshopper's visual canvas, and Revit's click-and-drag interface are not neutral instruments that *happen* to be visual. They are artifacts that *have politics* — they enforce a particular social arrangement in which sighted people design and blind people are excluded. The project builds artifacts with different politics.

#### J.7 Wobbrock, J.O., et al. (2011). "Ability-Based Design: Concept, Principles and Examples."
- **Venue:** ACM Transactions on Accessible Computing, Vol. 3, No. 3
- **DOI:** https://doi.org/10.1145/1952383.1952384
- **Summary:** Proposes shifting the focus of accessible design from disability to ability. Instead of asking "What disability does a person have?" asks "What can a person do?" Offers seven ability-based design principles.
- **Relevance:** The project embodies ability-based design: it asks not "How does Daniel's blindness prevent him from using Rhino?" but "What can Daniel do?" (type, listen, touch, reason spatially through language). The CLI is designed around Daniel's abilities, not his disability.

#### J.8 Ladner, R. (2015). "Design for User Empowerment."
- **Venue:** ACM Interactions, Vol. 22, No. 2
- **DOI:** https://doi.org/10.1145/2723869
- **Summary:** Advocates that users with disabilities should be empowered to solve their own accessibility problems. In its strongest sense, users of technology are empowered to solve their own accessibility problems through self-determination and technical expertise.
- **Relevance:** The project is a case study in Ladner's "design for user empowerment." Daniel is not a passive recipient of accessibility features — he co-designs the tools, tests them in his studio work, and provides feedback that reshapes the CLI. The project empowers rather than accommodates.

---

### Theme K: Sound, Space, and Aural Architecture

These works provide the theoretical foundation for the project's planned sonification pipeline and for understanding architecture as an auditory phenomenon.

#### K.1 Blesser, B. & Salter, L.-R. (2007). *Spaces Speak, Are You Listening? Experiencing Aural Architecture.*
- **Publisher:** MIT Press
- **URL:** https://mitpress.mit.edu/9780262513173/spaces-speak-are-you-listening/
- **Summary:** Defines "aural architecture" — how we experience space through listening. Integrates acoustics, architecture, music, cognitive psychology, and audio engineering. Demonstrates that we navigate rooms in the dark and "hear" the emptiness of a house without furniture. Sound reveals spatial properties that vision alone cannot convey: reverberation time encodes room volume, early reflections encode wall proximity, frequency response encodes material.
- **Relevance:** The single most important text for the project's sonification direction. Blesser & Salter's aural architecture provides the mapping vocabulary: room volume → reverb, wall proximity → early reflections, material → frequency response. The project's planned sonification pipeline can be understood as making Blesser's "aural architecture" computable and designable through the CLI.

#### K.2 Schafer, R.M. (1977/1994). *The Soundscape: Our Sonic Environment and the Tuning of the World.*
- **Publisher:** Destiny Books
- **Summary:** Foundational text in acoustic ecology. Defines "soundscape" as the sum total of all sounds within a defined area — an intimate reflection of social, technological, and natural conditions. Proposes that acoustic design can improve the quality of sonic environments, combining resources from acoustics, architecture, linguistics, music, psychology, and urban planning.
- **Relevance:** Schafer's soundscape concept extends beyond natural environments to architectural spaces. The project's sonification pipeline would create "soundscapes" of Daniel's designs, enabling him to evaluate spatial qualities (openness, enclosure, rhythm, density) through sound — an acoustic ecology of architectural intent.

---

### Theme L: Blind Architects in Practice — Case Studies

These case studies demonstrate that blind architects exist, practice, and produce richer spatial designs — direct precedent for the project's thesis.

#### L.1 Vermeersch, P. & Heylighen, A. (2012). "Blindness and Multi-sensoriality in Architecture: The Case of Carlos Mourao Pereira."
- **Already in original review (2.4).** Remains the primary academic case study.

#### L.2 Chris Downey — Blind Architect, San Francisco.
- **TED Talk:** "Design with the Blind in Mind" (2013)
- **URL:** https://www.ted.com/speakers/chris_downey
- **Key projects:** San Francisco LightHouse for the Blind; Duke Eye Center
- **Summary:** Lost sight in 2008 after 20 years of practice. Rather than leaving architecture, he reinvented his practice around multi-sensory design. Reads architectural plans by touch using a large-format embossing printer that produces raised tactile drawings. Teaches accessibility and universal design at UC Berkeley.
- **Relevance:** Downey is the most prominent blind architect practicing today. His use of embossed tactile plans parallels the project's PIAF swell paper pipeline. His decision to "reinvent his career" rather than leave architecture demonstrates that blindness and architectural practice are compatible — the barrier is tools, not ability. Downey works around inaccessible tools; the project builds accessible ones.

---

### Theme M: Text-Based Parametric Design and Interoperability

These works contextualize the project's CLI within the broader landscape of text-based and script-driven architectural design tools.

#### M.1 Leitão, A., Santos, L., & Lopes, J. (2012). "Programming Languages for Generative Design: A Comparative Study."
- **Venue:** International Journal of Architectural Computing (IJAC), Vol. 10, No. 1
- **Summary:** Compares visual programming languages (VPLs like Grasshopper) with textual programming languages (TPLs) for architectural design. Finds that modern TPLs can be more productive than VPLs for large-scale and complex design tasks. Introduces Rosetta, a multi-language, multi-CAD generative design tool.
- **Relevance:** Provides empirical evidence that text-based interaction is not merely "accessible" but often *superior* for complex parametric tasks. The project can cite Leitão to argue that the CLI's text-based approach is not a compromise for accessibility but a design advantage that the field should adopt more broadly.

#### M.2 CadQuery — Python Parametric CAD Scripting Framework.
- **URL:** https://github.com/CadQuery/cadquery
- **Summary:** Open-source Python library for parametric 3D CAD modeling. Users write short Python scripts that produce CAD models. Uses a fluent API designed for readability. Demonstrates that script-based CAD can be intuitive and productive.
- **Relevance:** Validates the project's Python-stdlib-only approach. CadQuery shows that script-based parametric modeling is a viable paradigm, not a workaround. The project's CLI is domain-specific (architecture) where CadQuery is domain-general (mechanical engineering), but the underlying paradigm is the same.

#### M.3 Gibson, J.J. (1979). *The Ecological Approach to Visual Perception.*
- **Publisher:** Houghton Mifflin (reprinted Psychology Press, 2014)
- **Summary:** Introduces the theory of affordances — that we perceive the environment directly through its action possibilities, not through abstract mental representations. Perception is relational: affordances exist between organism and environment. A chair "affords sitting" not as an abstract property but as a direct perception by a body of certain proportions.
- **Relevance:** Gibson's affordance theory, though titled "Visual Perception," is fundamentally about *action*, not sight. Affordances are perceived through all senses. The CLI's commands ("set bay A rotation 30") are linguistic affordances — they offer specific design actions in a format that affords screen-reader interaction. The project can argue, via Gibson, that the CLI's affordances are richer (more precise, more repeatable, more scriptable) than visual CAD's click-and-drag affordances.

---

## Final Summary Table (All New Additions: Papers 31–80)

| # | Short Citation | Venue/Publisher | Year | Primary Theme |
|---|---------------|-----------------|------|---------------|
| 31–55 | (see earlier table) | | | |
| 56 | Zumthor, *Atmospheres* | Birkhäuser | 2006 | Multi-sensory architecture |
| 57 | Böhme, *Aesthetics of Atmospheres* | Routledge | 2017 | Embodied spatial experience |
| 58 | Pérez-Gómez, *Attunement* | MIT Press | 2016 | Architecture as embodied attunement |
| 59 | Holl/Pallasmaa/Pérez-Gómez, *Questions of Perception* | A+U/Stout | 1994 | Phenomenology of architecture |
| 60 | Merleau-Ponty, *Phenomenology of Perception* | Routledge | 1945 | Embodied perception |
| 61 | Reynolds, "World-Creating Blindness" | Chiasmi International | 2017 | Crip phenomenology |
| 62 | Saerberg, "Blind Pedestrians" | Senses and Society | 2010 | Blind spatial lifeworld |
| 63 | Chen et al., "Perception beyond sight" | ScienceDirect | 2024 | Blind cognitive maps |
| 64 | Cattaneo & Vecchi, *Blind Vision* | MIT Press | 2011 | Neuroscience of blindness |
| 65 | Hamraie, *Building Access* | U Minnesota Press | 2017 | Politics of universal design |
| 66 | Hamraie & Fritsch, "Crip Technoscience Manifesto" | Catalyst | 2019 | Disabled makers |
| 67 | Gissen, *Architecture of Disability* | U Minnesota Press | 2022 | Beyond access |
| 68 | Boys, *Doing Disability Differently* | Routledge | 2014 | Disability as generative |
| 69 | Williamson, *Accessible America* | NYU Press | 2019 | History of disability + design |
| 70 | Winner, "Do Artifacts Have Politics?" | Daedalus | 1980 | Politics of technology |
| 71 | Wobbrock et al., "Ability-Based Design" | ACM TACCESS | 2011 | Ability over disability |
| 72 | Ladner, "Design for User Empowerment" | ACM Interactions | 2015 | User empowerment |
| 73 | Blesser & Salter, *Spaces Speak* | MIT Press | 2007 | Aural architecture |
| 74 | Schafer, *The Soundscape* | Destiny Books | 1977 | Acoustic ecology |
| 75 | Downey, Chris (blind architect) | TED / practice | 2008+ | Blind architect case study |
| 76 | Leitão et al., "Programming Languages" | IJAC | 2012 | Text vs visual CAD |
| 77 | CadQuery | Open source | 2018+ | Python parametric CAD |
| 78 | Gibson, *Ecological Approach* | Psychology Press | 1979 | Affordance theory |
| 79 | Imrie, "Universalism" | Disability & Rehab | 2012 | UD critique |
| 80 | Steinfeld & Maisel, *Universal Design* | Wiley | 2012 | UD framework |

---

## Key Gaps in the Literature (Final Assessment, 80 Papers)

With 80 papers spanning computational design, HCI, architectural phenomenology, critical disability studies, cognitive science, acoustic ecology, and STS, the Radical Accessibility Project's unique contribution becomes sharply defined:

1. **No work bridges architectural phenomenology and computational design tools for blind users.** Pallasmaa, Zumthor, and Böhme critique architecture's visual bias philosophically. Heylighen studies blind spatial experience empirically. The HCI community builds accessible modeling tools. The ACADIA community builds text-to-CAD pipelines. **No one connects all four.** The project is the first to operationalize architectural phenomenology's multi-sensory critique through a functioning, screen-reader-native computational design tool used by a blind architecture student in a graduate studio.

2. **Critical disability studies has not entered the ACADIA/CumInCAD discourse.** Hamraie, Gissen, Boys, and Williamson are well-known in disability studies and architectural theory — but they are virtually absent from computational design literature. The project's ACADIA paper can introduce "crip technoscience" and "artifacts have politics" to a community that has discussed accessibility only in terms of equity (Noel et al.) and data justice (Cupkova et al.), not in terms of structural critique.

3. **The "curb cut" argument is waiting to be made for computational design.** The project's text-based, file-decoupled architecture has properties (auditability, scriptability, crash resilience, version-control friendliness) that benefit *all* users, not just blind users. This is the computational design curb cut effect — and no one has articulated it yet.

4. **Cognitive science of blind spatial reasoning supports the CLI paradigm.** Saerberg, Giudice, Cattaneo & Vecchi, and Chen et al. show that blind spatial cognition is sequential, landmark-based, and language-mediated — exactly the interaction model the CLI provides. This is not a coincidence; it is evidence that the CLI is cognitively aligned with how blind users actually build spatial understanding.

5. **Sonification for architectural design authoring remains a white space.** Blesser and Schafer provide the theory; Garcia (1996) prototyped sonification for structural education. But no one has built a sonification pipeline for a blind designer creating new architectural spaces. The project's planned sonification direction has no direct precedent.

6. **The ACADIA community has AI papers without accessibility, and accessibility papers without AI.** Del Campo, Rietschel, and the Text2CAD community build AI-architecture tools that assume sighted users. Noel, Cupkova, and Karastathi call for equity but don't build AI tools. The project sits in the intersection — a functioning AI-compatible (MCP-ready) architecture tool designed for a blind user.

---

## Recommended Reading Order for ACADIA 2026 Framing (Final, by Argument Layer)

**Layer 1: Architecture's Visual Bias (the problem)**
1. Pallasmaa, *Eyes of the Skin* (1996) — the philosophical critique
2. Zumthor, *Atmospheres* (2006) — 8/9 generators are non-visual
3. Winner, "Do Artifacts Have Politics?" (1980) — tools enforce exclusion
4. Heylighen & Herssens, "Designerly Ways of Not Knowing" (2014) — empirical evidence

**Layer 2: Disability as Generative, Not Deficit (the reframe)**
5. Hamraie, *Building Access* (2017) — politics of universal design
6. Hamraie & Fritsch, "Crip Technoscience Manifesto" (2019) — disabled makers
7. Gissen, *Architecture of Disability* (2022) — beyond access
8. Boys, *Doing Disability Differently* (2014) — disability as avant-garde
9. Reynolds, "World-Creating Blindness" (2017) — crip phenomenology

**Layer 3: Blind Spatial Cognition (the evidence)**
10. Saerberg, "Blind Pedestrians" (2010) — sequential spatial knowledge
11. Cattaneo & Vecchi, *Blind Vision* (2011) — neuroscience of blind spatial reasoning
12. Chen et al., "Perception beyond sight" (2024) — blind cognitive maps

**Layer 4: The Tool Landscape (what exists and what's missing)**
13. Siu et al., "shapeCAD" (2019) — accessible 3D modeling precedent
14. Siu et al., "A11yShape" (2025) — AI-assisted accessible modeling
15. Rietschel et al., "Raven / LLMs for Design Scripting" (2024) — LLM-to-CAD state of art
16. Text2CAD (2024) — NL-to-parametric-CAD
17. Crawford et al., "Co-designing Tactile Map" (2024) — CAD tools fail blind users
18. Billah et al., "Designing While Blind" (2023) — authorship gap

**Layer 5: The Project's Contribution (what this makes possible)**
19. Blesser & Salter, *Spaces Speak* (2007) — aural architecture framework
20. Lundgard & Satyanarayan, "4-Level Model" (2022) — accessible description framework
21. Wobbrock et al., "Ability-Based Design" (2011) — design framework
22. Ladner, "Design for User Empowerment" (2015) — empowerment over accommodation

---

## DEEP FOUNDATIONS (Round 3): Cognitive Science, Ocularcentrism, Design Justice

This final expansion adds four theme clusters that complete the theoretical architecture. Themes N–Q close remaining gaps in cognitive science of haptic/blind spatial development, the philosophical critique of vision's hegemony, disability studies as applied to HCI/technology design, and participatory design / design justice frameworks. These sources provide the deepest evidentiary and ethical foundations for the ACADIA 2026 argument.

---

### Theme N: Cognitive Science of Haptic and Blind Spatial Development

These sources establish the empirical cognitive science behind how blind individuals construct spatial knowledge. They provide hard evidence that spatial understanding does not require vision — a claim the Radical Accessibility Project operationalizes through its CLI-driven, sequential, language-mediated design tools.

#### N.1 Piaget, J. & Inhelder, B. (1956). *The Child's Conception of Space.*
- **Publisher:** Routledge & Kegan Paul (London). Originally published in French, 1948.
- **URL:** https://archive.org/details/childsconception0000piag_e5l4
- **Summary:** Foundational developmental psychology text that includes a chapter on "Perceptual Space, Representational Space, and the Haptic Perception of Shape." Piaget and Inhelder demonstrate that children's earliest spatial understanding is topological (proximity, enclosure, continuity) before becoming projective or Euclidean. Critically, their studies of haptic perception show that children can recognize and classify spatial relationships through touch alone, prior to visual-geometric sophistication. Topology precedes metric geometry in cognitive development.
- **Relevance:** The project's CLI encodes topological and semantic relationships ("bay A is adjacent to bay B," "corridor runs along axis X") before generating precise geometry. This mirrors Piaget and Inhelder's finding that spatial understanding develops from qualitative/topological to quantitative/metric. The CLI's sequential, relationship-first interaction model is not a compromise — it aligns with how spatial cognition actually develops, with or without vision.

#### N.2 Millar, S. (1994). *Understanding and Representing Space: Theory and Evidence from Studies with Blind and Sighted Children.* / Millar, S. (2008). *Space and Sense.*
- **Publisher:** Oxford University Press (1994); Psychology Press / Routledge (2008)
- **URL (1994):** https://global.oup.com/academic/product/understanding-and-representing-space-9780198521426
- **URL (2008):** https://www.routledge.com/Space-and-Sense/Millar/p/book/9780415651882
- **Summary:** Millar's 1994 book challenges the assumption that vision is the primary modality for spatial understanding by examining spatial representation in the total absence of vision, comparing findings from congenitally blind and sighted children. Her 2008 *Space and Sense* extends this work, arguing that spatial processing depends crucially on integrating diverse sensory inputs as reference cues — not on any single modality. She demonstrates that touch and movement can substitute for vision in spatial tasks when appropriate reference frames are provided, and that "visual" illusions found in touch depend on common structural factors, not on vision per se.
- **Relevance:** Millar's central finding — that spatial cognition is modality-independent when adequate reference cues exist — is the cognitive science foundation for the entire project. The CLI provides precisely those reference cues: named bays, labeled axes, numbered dimensions. These are the "external reference frames" that Millar shows enable blind spatial reasoning to match sighted performance. The project's tool design is not accommodating a deficit; it is providing the reference structure that enables full spatial competence.

#### N.3 Hatwell, Y., Streri, A., & Gentaz, E. (Eds.) (2003). *Touching for Knowing: Cognitive Psychology of Haptic Manual Perception.*
- **Publisher:** John Benjamins (Advances in Consciousness Research, Vol. 53)
- **URL:** https://benjamins.com/catalog/aicr.53
- **Summary:** Comprehensive edited volume on the cognitive psychology of haptic (touch-based) perception. Examines exploratory manual behaviors, intramodal haptic abilities, and cross-modal visual-tactual coordination in infants, children, adults, and non-human primates — studying both sighted and blind persons. Key finding: intensive use of touch by blind persons allows them to reach the same levels of spatial knowledge and cognition as sighted peers. Includes chapters on anatomical/neurophysiological bases of tactile perception, Braille reading, raised maps and drawings, sensory substitution displays, and new technologies adapted for blind users.
- **Relevance:** Directly validates the project's physical-digital pipeline. Hatwell et al.'s evidence that haptic perception achieves equivalent spatial cognition to vision supports the project's investment in tactile output (PIAF swell paper, 3D prints) and tactile input (pegboard). The chapter on raised maps and drawings provides an empirical basis for the project's tactile precedent library. The finding that touch reaches "the same levels of knowledge" refutes the deficit model that treats tactile representation as an inferior substitute.

#### N.4 Thinus-Blanc, C. & Gaunet, F. (1997). "Representation of space in blind persons: vision as a spatial sense?"
- **Venue:** Psychological Bulletin, Vol. 121, No. 1, pp. 20–42
- **URL:** https://pubmed.ncbi.nlm.nih.gov/9064698/
- **Summary:** Major review article addressing the fundamental question of whether vision is necessary for spatial representation. Examines why previous studies produced contradictory findings — some showing profound spatial deficits in early blind participants, others finding no deficits. Proposes that the discrepancies stem from differences in spatial strategies rather than fundamental cognitive limitations. Argues that studying strategies (sequential vs. simultaneous, egocentric vs. allocentric) is more productive than asking whether blind people "can" represent space. The answer depends on what strategies and reference frames are available.
- **Relevance:** This paper resolves the apparent contradiction in the blind spatial cognition literature and provides a framework the project can cite directly. The CLI provides exactly the kind of strategy-enabling infrastructure Thinus-Blanc and Gaunet call for: sequential command entry (matching blind users' sequential spatial exploration), explicit naming of landmarks and axes (providing allocentric reference frames), and verbal confirmation of spatial relationships (supporting language-mediated spatial reasoning). The tool design is strategy-aligned, not modality-dependent.

#### N.5 Loomis, J.M., Klatzky, R.L., & Golledge, R.G. (2001). "Cognitive Mapping and Wayfinding by Adults Without Vision."
- **Venue:** Chapter in *Navigating through Environments*, Springer. Multiple related publications 1993–2007.
- **URL:** https://link.springer.com/chapter/10.1007/978-0-585-33485-1_10
- **Summary:** Comprehensive research program investigating how adults without vision develop and use cognitive maps. Key findings: (1) spatial representations derived from spatial language can function equivalently to those derived from direct perception; (2) blind individuals can construct survey-level (bird's-eye-view) spatial knowledge under the right conditions; (3) spatialized audio is more reliable and accurate than language alone for route traversal, but language is sufficient for spatial layout understanding. The team also developed and evaluated personal guidance systems for the visually impaired.
- **Relevance:** The finding that "spatial representations derived from spatial language can function equivalently to those derived from perception" is perhaps the single most powerful piece of evidence for the project's CLI-based approach. Daniel constructs spatial understanding of his designs through textual commands and verbal feedback — exactly the "spatial language" pathway Loomis et al. validate. The project is not a workaround; it leverages a cognitively equivalent pathway to spatial knowledge.

---

### Theme O: Ocularcentrism and the Anti-Visual Tradition

These sources provide the philosophical spine for the project's critique of architecture's visual bias. They establish that the privileging of vision is not natural or inevitable but historical and contestable.

#### O.1 Jay, M. (1993). *Downcast Eyes: The Denigration of Vision in Twentieth-Century French Thought.*
- **Publisher:** University of California Press
- **URL:** https://www.amazon.com/Downcast-Eyes-Denigration-Twentieth-Century-Thought/dp/0520088859
- **Summary:** Monumental intellectual history of the Western critique of vision. Jay traces the tradition of "ocularcentrism" — the privileging of sight as the noblest sense and the primary model for knowledge — from Plato through Descartes to modernity. The book's main subject is the resistance to this visual hegemony in twentieth-century French thought (Bergson, Bataille, Sartre, Merleau-Ponty, Foucault, Derrida, Irigaray). Jay documents how these thinkers challenged vision's supposedly superior access to truth and exposed its complicity with surveillance, spectacle, and domination. He concludes by calling for a plurality of "scopic regimes" rather than defending or abolishing visual primacy.
- **Relevance:** Jay provides the deepest genealogy of the visual bias the project confronts. Architecture's ocularcentrism is not just a practical problem (tools require screens) but an epistemological one (spatial knowledge is assumed to be visual knowledge). Jay's call for a "plurality of scopic regimes" is precisely what the project enacts: not eliminating vision from architecture but demonstrating that spatial design knowledge can be constructed through text, touch, and sound. The ACADIA paper can cite Jay to frame the project's contribution as part of a broader intellectual tradition challenging visual hegemony, not merely as an assistive technology intervention.

---

### Theme P: Disability Studies in HCI and Technology Design

These sources bridge critical disability studies and technology design, providing frameworks for understanding assistive technology not as charitable accommodation but as a site of political and design innovation.

#### P.1 Mankoff, J., Hayes, G.R., & Kasnitz, D. (2010). "Disability Studies as a Source of Critical Inquiry for the Field of Assistive Technology."
- **Venue:** Proceedings of the 12th International ACM SIGACCESS Conference on Computers and Accessibility (ASSETS '10). Received ASSETS Paper Impact Award, 2021.
- **URL:** https://dl.acm.org/doi/10.1145/1878803.1878807
- **Summary:** Argues that disability studies and assistive technology share common goals but rarely engage each other. Reviews key disability studies literature and presents two case studies showing how disability studies perspectives changed the research questions, methods, and outcomes of assistive technology projects. Key insight: disability studies reframes assistive technology from "fixing" individual deficits to questioning the social and technical systems that create disability in the first place.
- **Relevance:** This paper is the bridge between the critical disability studies literature (Hamraie, Gissen, Boys) and the HCI/technology design community that builds the tools. The project enacts exactly the shift Mankoff et al. call for: instead of building assistive overlays on top of visual CAD tools (fixing the individual), it redesigns the tool architecture itself (questioning the system). The CLI-to-JSON-to-Rhino pipeline is not an accommodation — it is a redesign motivated by disability studies' insight that the problem is in the tool, not the user.

#### P.2 Shinohara, K. & Wobbrock, J.O. (2011). "In the Shadow of Misperception: Assistive Technology Use and Social Interactions."
- **Venue:** Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI '11). **Best Paper Award (top 1%).**
- **URL:** https://dl.acm.org/doi/10.1145/1978942.1979044
- **Summary:** Interview study of 20 individuals examining how assistive technology use is affected by social and professional contexts. Found two pervasive misperceptions: (1) that assistive devices can functionally eliminate a disability, and (2) that people with disabilities would be helpless without their devices. Also found that functional access consistently took priority over social self-consciousness, and that assistive devices often marked users as "having disabilities" in social settings. Concludes that accessibility should be built into mainstream technologies rather than relegated to specialized devices.
- **Relevance:** Shinohara and Wobbrock's finding that accessibility should be "built into mainstream technologies" is the design philosophy the project follows. The CLI is not a specialized assistive overlay; it is a mainstream-architecture tool (Python, JSON, Rhino) that happens to be accessible. Daniel uses the same CAD pipeline as any computational designer — just through a different interface. The paper's insight about social stigma also matters: the project's tools don't mark Daniel as "the blind student using special software." He uses the same Rhino, the same file formats, the same output.

#### P.3 Pullin, G. (2009). *Design Meets Disability.*
- **Publisher:** MIT Press
- **URL:** https://mitpress.mit.edu/9780262516747/design-meets-disability/
- **Summary:** Argues that design and disability can inspire each other in ways that transcend mere accommodation. Uses the history of eyeglasses — transformed from medical necessity to fashion statement — as a case study for how disability products can drive design innovation when design culture engages seriously with disability. Interviews leading designers about prosthetics, hearing aids, communication devices, and other assistive technologies. Proposes that the design community's aesthetic and conceptual sophistication, applied to disability, produces objects that are not just functional but culturally meaningful.
- **Relevance:** Pullin's argument that disability drives design innovation — not just in function but in cultural meaning — directly supports the project's thesis. The CLI-to-JSON pipeline was not designed to be elegant; it was designed for a blind user. But it turns out to be more debuggable, more scriptable, more version-controllable, and more crash-resilient than traditional visual CAD workflows. Like Pullin's eyeglasses, the project's tools started as a necessity and became a design contribution. The ACADIA paper can frame this as the computational design equivalent of Pullin's argument.

---

### Theme Q: Participatory Design, Design Justice, and "Nothing About Us Without Us"

These sources provide the ethical and methodological framework for the project's co-design approach with Daniel. They establish that the project's methodology — disabled users as co-designers, not subjects — is not just ethically correct but epistemologically superior.

#### Q.1 Charlton, J.I. (1998). *Nothing About Us Without Us: Disability Oppression and Empowerment.*
- **Publisher:** University of California Press
- **URL:** https://www.jstor.org/stable/10.1525/j.ctt1pnqn9
- **Summary:** The first book in the disability literature to provide a comprehensive theoretical overview of disability oppression, drawing parallels with racism, sexism, and colonialism. The title phrase — "Nothing about us without us" — originated in the disability rights movement and has become the defining principle of participatory disability research and design. Charlton documents how disability policy, technology, and design have historically been controlled by non-disabled people, producing solutions that address the wrong problems or create new forms of dependency. Illuminated by interviews with disability rights activists across the Third World, Europe, and the United States.
- **Relevance:** The project's co-design methodology with Daniel directly enacts Charlton's principle. Daniel is not a test subject; he is a co-designer who shapes tool requirements, evaluates outputs, and identifies spatial relationships that sighted developers miss. Every tool in the project exists because Daniel identified a need — the School Jig was designed for his studio project, the tactile graphics pipeline for his precedent studies, the AI description system for his site visits. This is "nothing about us without us" operationalized as a computational design research method.

#### Q.2 Costanza-Chock, S. (2020). *Design Justice: Community-Led Practices to Build the Worlds We Need.*
- **Publisher:** MIT Press (open access)
- **URL:** https://designjustice.mitpress.mit.edu/
- **Summary:** Rethinks design processes to center people who are normally marginalized by design, using collaborative and creative practices. Argues that design typically assumes users are members of the dominant group (male, white, heterosexual, able-bodied, literate, college-educated) and that this assumption is not neutral but actively exclusionary. Proposes design justice principles: center the voices of those most impacted, prioritize community needs over designer expertise, and recognize that design processes are always political. Made available as open access through MIT Press.
- **Relevance:** Costanza-Chock's design justice framework names what the project does: centering a marginalized user (Daniel) not as a beneficiary but as the primary design authority. The project goes further than Costanza-Chock's framework in one respect — it demonstrates that centering a marginalized user produces tools that are *better for everyone*, not just more equitable. The CLI's crash resilience, scriptability, and version-control friendliness are design justice's curb cut effect made concrete in computational design.

#### Q.3 Levent, N. & Pascual-Leone, A. (Eds.) (2014). *The Multisensory Museum: Cross-Disciplinary Perspectives on Touch, Sound, Smell, Memory, and Space.*
- **Publisher:** Rowman & Littlefield
- **URL:** https://www.amazon.com/Multisensory-Museum-Cross-Disciplinary-Perspectives-Memory/dp/0759123543
- **Summary:** Brings together museum experts and neuroscientists to explore how touch, sound, smell, and memory can create immersive, accessible exhibition experiences. Edited by Nina Levent (executive director of Art Beyond Sight, dedicated to making visual arts accessible to visually impaired people) and Alvaro Pascual-Leone (professor of neurology, Harvard Medical School). Argues that multisensory design is not just an accessibility accommodation but an opportunity to create richer experiences for all visitors. Includes chapters on neuroscience of multisensory perception, curatorial practices, and architectural design for multisensory engagement.
- **Relevance:** The museum context parallels the architecture studio. Like a gallery, the design studio is assumed to be visual — pin-ups, projections, physical models are all primarily visual artifacts. Levent and Pascual-Leone demonstrate that multisensory design enriches experience for everyone, not just visually impaired visitors. The project makes the same argument for architectural design tools: the CLI + tactile output + audio feedback pipeline creates a richer, more information-dense design environment than visual-only CAD workflows.

---

## Final Summary Table (All New Additions: Papers 31–93)

| # | Short Citation | Venue/Publisher | Year | Primary Theme |
|---|---------------|-----------------|------|---------------|
| 31–55 | (see earlier table) | | | |
| 56 | Zumthor, *Atmospheres* | Birkhäuser | 2006 | Multi-sensory architecture |
| 57 | Böhme, *Aesthetics of Atmospheres* | Routledge | 2017 | Embodied spatial experience |
| 58 | Pérez-Gómez, *Attunement* | MIT Press | 2016 | Architecture as embodied attunement |
| 59 | Holl/Pallasmaa/Pérez-Gómez, *Questions of Perception* | A+U/Stout | 1994 | Phenomenology of architecture |
| 60 | Merleau-Ponty, *Phenomenology of Perception* | Routledge | 1945 | Embodied perception |
| 61 | Reynolds, "World-Creating Blindness" | Chiasmi International | 2017 | Crip phenomenology |
| 62 | Saerberg, "Blind Pedestrians" | Senses and Society | 2010 | Blind spatial lifeworld |
| 63 | Chen et al., "Perception beyond sight" | ScienceDirect | 2024 | Blind cognitive maps |
| 64 | Cattaneo & Vecchi, *Blind Vision* | MIT Press | 2011 | Neuroscience of blindness |
| 65 | Hamraie, *Building Access* | U Minnesota Press | 2017 | Politics of universal design |
| 66 | Hamraie & Fritsch, "Crip Technoscience Manifesto" | Catalyst | 2019 | Disabled makers |
| 67 | Gissen, *Architecture of Disability* | U Minnesota Press | 2022 | Beyond access |
| 68 | Boys, *Doing Disability Differently* | Routledge | 2014 | Disability as generative |
| 69 | Williamson, *Accessible America* | NYU Press | 2019 | History of disability + design |
| 70 | Winner, "Do Artifacts Have Politics?" | Daedalus | 1980 | Politics of technology |
| 71 | Wobbrock et al., "Ability-Based Design" | ACM TACCESS | 2011 | Ability over disability |
| 72 | Ladner, "Design for User Empowerment" | ACM Interactions | 2015 | User empowerment |
| 73 | Blesser & Salter, *Spaces Speak* | MIT Press | 2007 | Aural architecture |
| 74 | Schafer, *The Soundscape* | Destiny Books | 1977 | Acoustic ecology |
| 75 | Downey, Chris (blind architect) | TED / practice | 2008+ | Blind architect case study |
| 76 | Leitão et al., "Programming Languages" | IJAC | 2012 | Text vs visual CAD |
| 77 | CadQuery | Open source | 2018+ | Python parametric CAD |
| 78 | Gibson, *Ecological Approach* | Psychology Press | 1979 | Affordance theory |
| 79 | Imrie, "Universalism" | Disability & Rehab | 2012 | UD critique |
| 80 | Steinfeld & Maisel, *Universal Design* | Wiley | 2012 | UD framework |
| 81 | Piaget & Inhelder, *Child's Conception of Space* | Routledge | 1956 | Haptic spatial development |
| 82 | Millar, *Understanding and Representing Space* / *Space and Sense* | OUP / Psychology Press | 1994/2008 | Blind spatial cognition |
| 83 | Hatwell, Streri & Gentaz, *Touching for Knowing* | John Benjamins | 2003 | Haptic cognition |
| 84 | Thinus-Blanc & Gaunet, "Representation of space in blind" | Psychological Bulletin | 1997 | Blind spatial strategies |
| 85 | Loomis, Klatzky & Golledge, "Cognitive Mapping without Vision" | Springer | 2001 | Spatial language equivalence |
| 86 | Jay, *Downcast Eyes* | UC Press | 1993 | Ocularcentrism critique |
| 87 | Mankoff, Hayes & Kasnitz, "Disability Studies for AT" | ASSETS '10 | 2010 | DS + assistive tech |
| 88 | Shinohara & Wobbrock, "Shadow of Misperception" | CHI '11 (Best Paper) | 2011 | AT stigma + mainstream design |
| 89 | Pullin, *Design Meets Disability* | MIT Press | 2009 | Design + disability innovation |
| 90 | Charlton, *Nothing About Us Without Us* | UC Press | 1998 | Disability rights + participation |
| 91 | Costanza-Chock, *Design Justice* | MIT Press | 2020 | Community-led design |
| 92 | Levent & Pascual-Leone, *Multisensory Museum* | Rowman & Littlefield | 2014 | Multisensory design |
| 93 | Giudice, "Navigating without Vision" | Chapter (Springer) | 2018 | Blind spatial principles |

---

## Key Gaps in the Literature (Final Assessment, 93 Papers)

With 93 sources spanning computational design, HCI, architectural phenomenology, critical disability studies, cognitive science, acoustic ecology, STS, design justice, and haptic psychology, the Radical Accessibility Project's unique contribution is now sharply defined against six distinct literatures:

1. **No work bridges architectural phenomenology and computational design tools for blind users.** Pallasmaa, Zumthor, and Böhme critique architecture's visual bias philosophically. Jay traces ocularcentrism's intellectual genealogy. Heylighen studies blind spatial experience empirically. The HCI community builds accessible modeling tools. The ACADIA community builds text-to-CAD pipelines. **No one connects all five.** The project is the first to operationalize architectural phenomenology's multi-sensory critique through a functioning, screen-reader-native computational design tool used by a blind architecture student in a graduate studio.

2. **Cognitive science validates the CLI paradigm, but no one has made the connection.** Millar, Thinus-Blanc & Gaunet, and Loomis et al. demonstrate that spatial cognition is modality-independent when adequate reference frames and strategies are available. Piaget and Inhelder show that spatial understanding begins with topological (qualitative) relationships before becoming metric. The CLI's sequential, semantically-labeled, language-mediated interaction model is exactly the strategy-enabling infrastructure this literature calls for — but no computational design researcher has cited this cognitive science to justify an alternative tool paradigm.

3. **Critical disability studies has not entered the ACADIA/CumInCAD discourse.** Hamraie, Gissen, Boys, Williamson, Mankoff et al., and Costanza-Chock are well-known in disability studies, HCI, and architectural theory — but they are virtually absent from computational design literature. The project's ACADIA paper can introduce "crip technoscience," "design justice," and "do artifacts have politics?" to a community that has discussed accessibility only in terms of equity (Noel et al.) and data justice (Cupkova et al.), not in terms of structural critique.

4. **The "curb cut" argument is waiting to be made for computational design.** Pullin demonstrates that designing for disability drives innovation. Shinohara and Wobbrock show that mainstream integration beats specialized accommodation. Levent and Pascual-Leone prove that multisensory design enriches experience for everyone. The project's text-based, file-decoupled architecture has properties (auditability, scriptability, crash resilience, version-control friendliness) that benefit *all* users. This is the computational design curb cut effect — and no one has articulated it yet.

5. **Sonification for architectural design authoring remains a white space.** Blesser and Schafer provide the theory; Garcia (1996) prototyped sonification for structural education. But no one has built a sonification pipeline for a blind designer creating new architectural spaces. The project's planned sonification direction has no direct precedent.

6. **Participatory design with disabled co-designers in computational architecture is undocumented.** Charlton's "nothing about us without us" is a foundational principle in disability rights. Costanza-Chock extends it to design justice. Vermeersch et al. apply participatory methods with blind users in architectural design. But no ACADIA or CumInCAD paper describes a computational design tool co-designed with a blind architecture student as a research partner (not a user study subject). The project's methodology is itself a contribution.

---

## Recommended Reading Order for ACADIA 2026 Framing (Final, by Argument Layer)

**Layer 1: Architecture's Visual Bias (the problem)**
1. Jay, *Downcast Eyes* (1993) — the deepest genealogy of ocularcentrism
2. Pallasmaa, *Eyes of the Skin* (1996) — the architectural critique
3. Zumthor, *Atmospheres* (2006) — 8/9 generators are non-visual
4. Winner, "Do Artifacts Have Politics?" (1980) — tools enforce exclusion
5. Heylighen & Herssens, "Designerly Ways of Not Knowing" (2014) — empirical evidence

**Layer 2: Disability as Generative, Not Deficit (the reframe)**
6. Hamraie, *Building Access* (2017) — politics of universal design
7. Hamraie & Fritsch, "Crip Technoscience Manifesto" (2019) — disabled makers
8. Gissen, *Architecture of Disability* (2022) — beyond access
9. Boys, *Doing Disability Differently* (2014) — disability as avant-garde
10. Reynolds, "World-Creating Blindness" (2017) — crip phenomenology
11. Pullin, *Design Meets Disability* (2009) — design innovation through disability

**Layer 3: Blind Spatial Cognition (the evidence)**
12. Millar, *Understanding and Representing Space* (1994) / *Space and Sense* (2008) — modality-independent spatial cognition
13. Thinus-Blanc & Gaunet, "Representation of space" (1997) — strategy over modality
14. Loomis, Klatzky & Golledge, "Cognitive Mapping" (2001) — spatial language equivalence
15. Piaget & Inhelder, *Child's Conception of Space* (1956) — topology before metric
16. Saerberg, "Blind Pedestrians" (2010) — sequential spatial knowledge
17. Cattaneo & Vecchi, *Blind Vision* (2011) — neuroscience of blind spatial reasoning
18. Chen et al., "Perception beyond sight" (2024) — blind cognitive maps

**Layer 4: The Tool Landscape (what exists and what's missing)**
19. Siu et al., "shapeCAD" (2019) — accessible 3D modeling precedent
20. Siu et al., "A11yShape" (2025) — AI-assisted accessible modeling
21. Rietschel et al., "Raven / LLMs for Design Scripting" (2024) — LLM-to-CAD state of art
22. Text2CAD (2024) — NL-to-parametric-CAD
23. Crawford et al., "Co-designing Tactile Map" (2024) — CAD tools fail blind users
24. Billah et al., "Designing While Blind" (2023) — authorship gap
25. Mankoff, Hayes & Kasnitz, "Disability Studies for AT" (2010) — reframing assistive tech
26. Shinohara & Wobbrock, "Shadow of Misperception" (2011) — mainstream over specialized

**Layer 5: The Project's Ethical and Methodological Foundation (how we work)**
27. Charlton, *Nothing About Us Without Us* (1998) — participatory principle
28. Costanza-Chock, *Design Justice* (2020) — community-led design
29. Levent & Pascual-Leone, *Multisensory Museum* (2014) — multisensory benefits all

**Layer 6: The Project's Contribution (what this makes possible)**
30. Blesser & Salter, *Spaces Speak* (2007) — aural architecture framework
31. Lundgard & Satyanarayan, "4-Level Model" (2022) — accessible description framework
32. Wobbrock et al., "Ability-Based Design" (2011) — design framework
33. Ladner, "Design for User Empowerment" (2015) — empowerment over accommodation
