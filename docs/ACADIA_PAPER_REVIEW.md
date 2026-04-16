# Review: ACADIA Brainstorm Rearranged — Most Relevant Papers for ACADIA & JAE

**Reviewer:** Claude (automated literature review)
**Date:** 2026-04-16
**Source document:** `docs/ACADIA_BRAINSTORM_REARRANGED.md`
**Purpose:** Identify the most relevant papers from the 136-source literature review for ACADIA 2026 and JAE submissions, verify recent citations, flag concerns, and identify gaps.

---

## Verification Status

Spot-checked 8 of the most critical recent (2024-2026) citations against live web sources. All verified as real and accurately described:

- Siu et al. (2025) A11yShape -- confirmed ASSETS '25, Denver
- Jones et al. (2025) AIDL -- confirmed Computer Graphics Forum / Pacific Graphics
- Atakan et al. (2025) Kakadoo -- confirmed eCAADe 2025, METU Ankara
- Rietschel, Guo & Steinfeld (2024) -- confirmed ACADIA 2024
- Clepper et al. (2025) -- confirmed CHI 2025, Yokohama
- Nicholson (2025) -- confirmed ACSA resource page
- Flores-Saviaga et al. (2025) -- confirmed CHI 2025, also Microsoft Research
- Di Marco (2025) ConvoAI -- confirmed Architectural Science Review, Taylor & Francis

---

## Flags & Concerns

1. **Ant (2026)** is a blog post on rhino3d.com, not a peer-reviewed paper. Fine as contextual evidence of industry trends but should not be treated as a key citation. Label it as a commercial product release, not a publication.

2. **Grasshopper MCP Server (2025)** is a lobehub.com directory listing. Same -- validates technical feasibility but not citable as scholarship.

3. **CadQuery** is an open-source project, not a paper. Cite the GitHub repo if needed for technical context but don't list it among scholarly references.

4. **CADialogue (2025)** -- the document gives no author names. Confirm the full author list before citing. The ScienceDirect link is to Computer-Aided Design journal.

5. **AIDL rhetorical move** -- The document correctly notes that Jones et al. designed for "blind" AI code generation (meaning the AI can't see geometry), not blind humans. This is a powerful rhetorical point but handle with care: don't overstate the parallel. The paper's "blind" is about removing visual feedback from the generation loop, not about human disability.

6. **Siu et al. (2025) venue** -- The document lists it as "ASSETS '25" but the DOI resolves to ASSETS 2025 proceedings. The arXiv preprint date is May 2025 (2508.03852 -- note the "25" prefix indicates 2025). Confirmed presented October 2025 in Denver.

7. **Some older papers add little positioning value** -- Nagakura (1990), Nembrini (2009), Garcia (1996) are historical context only. They don't strengthen the argument for either venue. Use sparingly or cut.

---

## Top Papers for ACADIA 2026

ACADIA reviewers care about: computational design methods, text-to-geometry, AI+architecture, digital fabrication, and (increasingly) equity. Lead with work they've already seen or reviewed.

### Tier 1 -- Must Cite (10 papers that position the contribution)

1. **Rietschel, Guo & Steinfeld (2024)** "Mediating Modes of Thought" -- Closest pipeline parallel at ACADIA. Text-prompt to JSON to Grasshopper mirrors CLI to JSON to Rhino. Built for convenience; you built for necessity.

2. **El Hizmi et al. (2024)** "LLMto3D" -- Most directly comparable ACADIA paper. Multi-agent LLM to parametric 3D. Zero accessibility consideration -- your paper fills the gap.

3. **Jones et al. (2025)** "AIDL" -- Strongest theoretical ally from ML/graphics. Hierarchical, constraint-based, designed for code generation without visual verification. The "blind AI" to blind human rhetorical move.

4. **Siu et al. (2025)** "A11yShape" -- Most directly comparable accessible system. OpenSCAD + GPT-4o. Key differentiators: yours is architectural-scale, industry-tool-integrated, screen-reader-native output protocol.

5. **Cupkova et al. (2023)** "AI, Architecture, Accessibility, Data Justice" -- ACADIA's own equity call. Your paper answers it with a working system. IJAC Special Issue -- reviewers will know this.

6. **Atakan et al. (2025)** "Kakadoo" -- Voice-driven Grasshopper at eCAADe. Most directly relevant recent CumInCAD paper for voice/text-to-geometry. Still requires visual canvas -- you don't.

7. **Evans (1997)** Translations from Drawing to Building -- Theoretical backbone. Drawings are active agents; the CLI is a different representational agent that shapes different designs.

8. **Karastathi et al. (2024)** "Bridging Pixels and Fabrication" -- ACADIA 2024 Vanguard Award Winner on accessibility. Shows ACADIA recognizes this work. Bridge-layer pattern parallels yours.

9. **Billah et al. (2023)** "Designing While Blind" -- The problem statement from ASSETS. Blind people can't author tactile media they consume; your system enables exactly this for architecture.

10. **Lundgard & Satyanarayan (2022)** "Accessible Visualization via NL Descriptions" -- Four-level description model (L1-L4). Framework for structuring your describe output. IEEE VIS -- cross-disciplinary credibility.

### Tier 2 -- Should Cite (10 papers that strengthen the argument)

11. **Khan et al. (2024)** "Text2CAD" -- NeurIPS Spotlight. NL-to-parametric-geometry is solved; your contribution is showing it's necessary for blind designers.

12. **Carpo (2011, 2017)** Alphabet & Algorithm, Second Digital Turn -- Notation systems structure design thinking. The CLI is a new notation. Pairs with Evans.

13. **Siu, Kim et al. (2019)** "shapeCAD" -- Prior art for accessible 3D modeling. Your system differs: domain-specific, architectural-scale, Rhino-integrated.

14. **Clepper et al. (2025)** CHI 2025 -- BLV tactile graphics creators navigating accessible-but-low-fidelity vs. inaccessible-but-high-fidelity. Your system resolves this tradeoff.

15. **Noel, Boeva & Dortdivanlioglu (2021)** "The Question of Access" -- IJAC equity paper. Defines what "access" means in computational design; your CLI is the concrete answer.

16. **Rietschel & Steinfeld (2025)** IJAC -- Extends toward conversational, exploratory design. The conversational pattern you envision through MCP.

17. **Heylighen & Herssens (2014)** "Designerly Ways of Not Knowing" -- Architects' visual training creates systematic blind spots. Most important theoretical paper for the pedagogy dimension.

18. **Hamraie & Fritsch (2019)** "Crip Technoscience Manifesto" -- Introduces disability studies framework to ACADIA. Daniel as maker, not user. Use selectively -- define terms for the audience.

19. **Winner (1980)** "Do Artifacts Have Politics?" -- Widely known in STS. Rhino/Grasshopper enforce sighted operation. Your system builds artifacts with different politics.

20. **Gurita & Vatavu (2025)** W4A '25 -- LLM-generated interfaces don't spontaneously produce accessible code. Accessibility must be structural. Validates your born-accessible approach.

### Tier 3 -- Use Selectively (cite only where argument demands)

- **Burry (2011)** -- scripting escapes embedded constraints; the CLI is exactly this
- **Pallasmaa (1996/2012)** -- ocularcentrism critique; one paragraph max at ACADIA
- **Crawford et al. (2024)** -- screen reader failing TinkerCAD; powerful anecdote
- **Seo et al. (2024)** -- "born-accessible" concept; if using Framing C
- **Flores-Saviaga et al. (2025)** -- AI assistants exacerbate barriers; validates CLI model
- **Schon (1983)** -- if using Framing E (reflective conversation)
- **Maleki & Woodbury (2013)** -- bidirectional script/model link; historical CumInCAD precedent

---

## Top Papers for JAE

JAE reviewers care about: pedagogy, curriculum, studio culture, disability/inclusion, educational theory, and disciplinary self-reflection. The technical system is context; the pedagogical argument is the contribution.

### Tier 1 -- Must Cite (10 papers)

1. **Heylighen & Herssens (2014)** "Designerly Ways of Not Knowing" -- Architects' visual training creates blind spots. The single most important theoretical paper for JAE framing.

2. **Heylighen et al. (2021-2024)** "How Do Disabled Architects Design?" -- Strongest ongoing empirical precedent. She argues through study; you argue through tool-building. Complementary.

3. **Schon (1983)** The Reflective Practitioner -- Design as reflective conversation. The CLI makes the conversation explicit and auditable. JAE readers know Schon.

4. **Hamraie (2017)** Building Access -- "Normate template" concept. Rhino designed around sighted operator. Your project replaces this template.

5. **Gissen (2022)** The Architecture of Disability -- Beyond access. You don't make Rhino "accessible" -- you build a different ecosystem.

6. **Gissen (2018)** "Why are there so few disabled architects?" -- Names the structural barrier (inaccessible CAD) that your project addresses. Architect's Newspaper -- widely read.

7. **Nicholson (2025)** "Where Are My People?" ACSA -- The profession hasn't addressed inclusion of disabled practitioners. ACSA resource -- JAE is ACSA's journal. Direct alignment.

8. **Billah et al. (2023)** "Designing While Blind" -- Blind people excluded from authoring design. The problem your studio addresses.

9. **Costanza-Chock (2020)** Design Justice -- Center voices of those most impacted. Open access -- reviewers can read it. The CLI demonstrates the principle.

10. **Seo et al. (2024)** "Born-Accessible" -- "Born-accessible" courses designed from the ground up. Your system is born-accessible CAD. Pedagogical parallel. UIUC colleague.

### Tier 2 -- Should Cite (10 papers)

11. **Pallasmaa (1996/2012)** The Eyes of the Skin -- Canonical ocularcentrism critique. JAE readers know this well. Your project operationalizes it.

12. **Evans (1997)** Translations from Drawing to Building -- Representation shapes design. The CLI is a different representational medium.

13. **Lifchez (1987)** Rethinking Architecture -- Foundational disability-inclusive pedagogy. Daniel extends: not consumer but primary author.

14. **Mulligan et al. (2018)** "Inclusive Design in Architectural Education" -- Disability taught as subject for, not perspective from. Your project inverts this.

15. **NAAB (2020)** Conditions for Accreditation -- Silent on accessible design tools. Exposes institutional gap.

16. **Vermeersch & Heylighen (2012)** Carlos Mourao Pereira -- Blind architect case study. Individual precedent for tool-level argument.

17. **Charlton (1998)** Nothing About Us Without Us -- Daniel shapes requirements, evaluates outputs. Co-designer, not subject.

18. **Millar (1994, 2008)** spatial cognition -- Spatial cognition is modality-independent. The CLI provides adequate reference frames.

19. **Loomis, Klatzky & Golledge (2001)** -- Spatial language representations equivalent to perceptual ones. Strongest evidence for the CLI approach.

20. **Clepper et al. (2025)** CHI 2025 -- BLV creators navigating tool tradeoffs. Closest parallel to Daniel's situation.

### Tier 3 -- Use Selectively

- **Hamraie & Fritsch (2019)** -- crip technoscience; JAE audience may be more receptive than ACADIA
- **Winner (1980)** -- artifacts have politics; one paragraph
- **Reynolds (2017)** -- crip phenomenology; Daniel as co-designer, not subject
- **Boys (2014)** -- disability as avant-garde
- **Sennett (2008)** -- the craftsman; hand-head dialogue via keyboard and braille
- **Ingold (2013)** -- knowledge through making; CLI as medium of correspondence
- **UT Austin (2023)** -- studio designing for blind school; contrast: your student is blind and authoring geometry
- **Shinohara & Wobbrock (2011)** -- accessibility built into mainstream tech
- **Wobbrock et al. (2011)** -- ability-based design; "what can Daniel do?"

---

## Papers That Overlap Both Venues (cite in both)

These papers are central regardless of venue:

1. **Billah et al. (2023)** -- the problem statement
2. **Heylighen & Herssens (2014)** -- designerly blind spots
3. **Evans (1997)** -- representation theory
4. **Siu et al. (2025)** A11yShape -- comparison system
5. **Clepper et al. (2025)** -- BLV creator tradeoffs

---

## Papers to Deprioritize or Cut

These add historical context but don't strengthen either paper:

- **Nagakura (1990)** -- too old, minimal positioning value
- **Nembrini et al. (2009)** -- teaching programming; tangential
- **Garcia (1996, 1999)** -- early sonification/haptic; only if writing the sonification future-work section
- **Pohl & Hirschberg (2011)** -- reactive tangible surface; peripheral
- **Beilharz (2005)** -- gestural sonification; peripheral
- **Grabowski & Barner (1998)** -- multimodal haptic+auditory; peripheral
- **Sjostrom (2002)** -- haptic interaction PhD; peripheral unless discussing pegboard in depth
- **Piaget & Inhelder (1956)** -- spatial cognition development; foundational but old. Use Millar and Loomis instead for the same point with empirical evidence about blind adults.

---

## Strategic Recommendations

### For ACADIA
- Lead with Cluster 1A (text-to-geometry explosion). This is where the audience lives. Show them their own work, then reveal the blind spot.
- Framing A ("The Accidental Architecture") remains the strongest lead for ACADIA. The verification-gap argument is technically precise and meets reviewers where they are.
- Introduce disability studies selectively (Winner + Hamraie in discussion, not in framing). Don't require reviewers to absorb a new theoretical vocabulary before they see the technical contribution.
- A11yShape is your primary comparison -- differentiate clearly: architectural domain, industry-tool integration, screen-reader-native protocol, controller/viewer separation.

### For JAE
- Lead with the pedagogical gap (Nicholson, Gissen, NAAB). JAE readers care about who is in the profession and how education shapes that.
- The Schon framing (E) may be the strongest lead for JAE -- the reflective conversation is a pedagogical concept, and showing how the CLI makes it explicit is a contribution to how we understand studio.
- Use Pallasmaa and Evans more liberally -- JAE readers know and expect these. They're the theoretical home base.
- The "born-accessible" concept (Seo) translates well to JAE because it's fundamentally about course and tool design.
- Daniel's actual studio workflow is the evidence -- JAE wants narrative, specific design sessions, what the student learned. The technical system is context.

---

## Gap Analysis: Papers Missing from the Brainstorm Document

Searched for recent (2024-2026) work across ACADIA, CHI, ASSETS, eCAADe, CVPR, DIS, ACSA, JAE, and Routledge. Here are sources not in the 136-source brainstorm that are potentially relevant:

### High Priority -- Strongly consider adding

**1. Gipe-Lazarou -- Blind Design Workshop, Virginia Tech (2022-present)**
- Annual 5-day workshops with blind/VI teenagers exploring architecture
- Won ACSA Diversity Achievement Award 2024
- Forthcoming: "Blind Design: Advances in Non-Visual Pedagogy"
- Why it matters for JAE: The closest existing pedagogical precedent. His workshops are for blind teenagers exploring architecture; your project has a blind graduate student authoring parametric models. Cite to differentiate: his work is exposure/awareness; yours is full authorship with industry tools.
- Why it matters for ACADIA: Less relevant (no computational design content), but worth acknowledging as the most active blind+architecture pedagogy program.
- Source: https://arch.vt.edu/people/blacksburg-faculty/gipe-andrew.html

**2. Liebermann (2024) -- Architecture's Disability Problem, Routledge**
- Explores why mainstream architecture shows little interest in disability despite ADA
- Three case studies of design processes driven by disabled people
- Published June 2024, 238 pages
- Why it matters for JAE: Pairs with Gissen (2022) and Nicholson (2025) to form a trio documenting the profession's disability gap. Liebermann focuses on practice; your paper adds education and tools.
- Why it matters for ACADIA: Less central, but useful in the discussion section alongside Winner and Hamraie.
- Source: Routledge, ISBN 9780367641146

**3. DIS 2025 -- "A Framework-Informed Analysis of Accessibility Barriers in Desktop 3D Printing Software"**
- Evaluated screen reader operability of core 3D printing tasks (model positioning, slicing)
- Found custom GUI frameworks in slicing software block standard accessibility APIs
- Why it matters: Directly relevant to your tactile output pipeline. If the 3D printer's slicing software is inaccessible, Daniel can't independently print. Documents a barrier your system must address.
- Source: https://dl.acm.org/doi/10.1145/3715668.3736342

### Medium Priority -- Worth citing if space permits

**4. Archi-TangiBlock (2024, IEEE Access)**
- Modular block-based tangible CAD tool for visually impaired users
- Blocks represent architectural landmarks; panel for plugging in modules; computer interface
- 1.2% error rate with VI participants
- Why it matters: Parallels the pegboard concept. Different approach (modular blocks vs. pegs on grid) to the same problem (tangible input for blind spatial authoring). Cite to position the pegboard within a broader trend.
- Source: https://ieeexplore.ieee.org/document/10480423

**5. CAD-Llama (CVPR 2025) -- Li et al., Fudan University**
- LLM for parametric CAD, code-like representation, CVPR 2025
- Outperforms GPT-4 on CAD generation benchmarks
- Why it matters for ACADIA: Strengthens the text-to-geometry cluster (1A) -- another major venue (CVPR) publishing LLM-to-CAD work. Less directly relevant than AIDL or Text2CAD since it's ML benchmarks, not design workflow.
- Source: https://arxiv.org/abs/2505.04481

**6. DisOrdinary Architecture Project -- "Many More Parts than M!" (2024)**
- Led by Jos Boys (already cited as Boys 2014 in brainstorm)
- UK publication reimagining disability access beyond compliance
- Free PDF available
- Why it matters for JAE: Boys' newer applied work. Shows the evolution from theory (2014 book) to practice (2024 publication). Less relevant for ACADIA.
- Source: https://disordinaryarchitecture.co.uk/archive/manymoreparts

### Lower Priority -- Track but don't prioritize

**7. "From text to design" framework (2025, Proceedings of the Design Society)**
- LLM agents with function calling for automated CAD generation
- Another text-to-geometry entry; adds breadth to cluster 1A but already well-populated
- Source: Cambridge Core, Proceedings of the Design Society

**8. ACADIA 2025 proceedings (Nov 2025, Miami)**
- Theme: "Computing for Resilience"
- Proceedings may contain relevant LLM+CAD or equity papers that postdate the March 2026 brainstorm
- Action: Check CumInCAD when proceedings are fully indexed
