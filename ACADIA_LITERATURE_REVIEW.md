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
