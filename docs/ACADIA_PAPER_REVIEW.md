# Literature Review: ACADIA & JAE Submissions

**Reviewer:** Claude (automated literature review, second pass)
**Date:** 2026-04-16
**Source:** `docs/ACADIA_BRAINSTORM_REARRANGED.md` (136 sources)
**Purpose:** Identify strongest citations for ACADIA 2026 and JAE, verify recent sources, flag concerns, and surface gaps.

---

## Fresh Thoughts (second-pass editorial notes)

1. **Split the paper now, not later.** The ACADIA and JAE citation sets diverge sharply (technical/computational vs. pedagogical/disciplinary). Drafting one document and fork-and-trim at submission will waste labor. Fork the outline this week.
2. **Lead tier is too long at 10.** ACADIA short papers cite 15-25 total. If Tier 1 has 10 "must-cite" entries, the framing section is already full before any contribution is described. Recommend tightening Tier 1 to 5-6 per venue; demote the rest to Tier 2.
3. **A11yShape and AIDL are the two citations that do the most work.** A11yShape is the direct comparison system; AIDL gives you a blind-AI/blind-human rhetorical pivot that reviewers will remember. Everything else is context. Make sure these two are crisp in the draft.
4. **"Designing While Blind" (Billah) is the problem statement for both venues.** Use it in the first 500 words of both papers. It is the one citation that lets you skip a paragraph of justification.
5. **Verify author lists before any submission deadline.** CADialogue has no author list in the brainstorm; Ant/Grasshopper-MCP/CadQuery are not scholarship. Do not let a reviewer catch these.
6. **Gap list is strong.** Gipe-Lazarou (Virginia Tech) and Liebermann (Routledge 2024) are real holes for the JAE submission. Add both before the JAE draft is circulated.
7. **Reformat recommendation for this file:** numbered tiers with stable IDs so the draft can reference `[T1-3]` instead of re-quoting names. Added in the tables below.

---

## Verification Status

Spot-checked 8 recent (2024-2026) citations. All verified as real and accurately described.

| Citation | Venue | Status |
|---|---|---|
| Siu et al. (2025) A11yShape | ASSETS '25, Denver | [arXiv:2508.03852](https://arxiv.org/abs/2508.03852) |
| Jones et al. (2025) AIDL | Computer Graphics Forum / Pacific Graphics | Confirmed |
| Atakan et al. (2025) Kakadoo | eCAADe 2025, METU Ankara | Confirmed (CumInCAD) |
| Rietschel, Guo & Steinfeld (2024) | ACADIA 2024 | Confirmed |
| Clepper et al. (2025) | CHI 2025, Yokohama | Confirmed |
| Nicholson (2025) | ACSA resource page | Confirmed |
| Flores-Saviaga et al. (2025) | CHI 2025 / Microsoft Research | Confirmed |
| Di Marco (2025) ConvoAI | Architectural Science Review (Taylor & Francis) | Confirmed |

(Accessibility note: this table is short and labeled; it reads cleanly in JAWS/NVDA.)

---

## Flags & Concerns

1. **Ant (2026)** — blog post on rhino3d.com, not peer-reviewed. Label as a commercial product release, not a publication.
2. **Grasshopper MCP Server (2025)** — lobehub.com directory listing. Validates technical feasibility but not citable as scholarship.
3. **CadQuery** — open-source project, not a paper. Cite the GitHub repo for technical context only.
4. **CADialogue (2025)** — no author names in the brainstorm. Confirm authorship before citing.
5. **AIDL rhetorical move** — Jones et al. designed for "blind" AI code generation (no visual feedback loop), not blind humans. The parallel is powerful but must be handled carefully; do not overstate.
6. **Siu et al. (2025) venue** — arXiv preprint 2508.03852 (May 2025 submission, numbering 25-prefix). Confirmed ASSETS 2025, October, Denver.
7. **Older papers add little positioning value** — Nagakura (1990), Nembrini (2009), Garcia (1996) are historical context. Use sparingly or cut.

---

## Top Papers for ACADIA 2026

ACADIA reviewers care about: computational design methods, text-to-geometry, AI+architecture, digital fabrication, and (increasingly) equity. Lead with work they have already seen or reviewed.

### Tier 1 — Must Cite

| ID | Citation | Role |
|---|---|---|
| A1-1 | Rietschel, Guo & Steinfeld (2024) "Mediating Modes of Thought" | Closest pipeline parallel at ACADIA; text→JSON→Grasshopper mirrors CLI→JSON→Rhino |
| A1-2 | El Hizmi et al. (2024) "LLMto3D" | Most directly comparable ACADIA paper; zero accessibility consideration — your paper fills the gap |
| A1-3 | Jones et al. (2025) "AIDL" | Strongest theoretical ally; blind-AI to blind-human pivot |
| A1-4 | Siu et al. (2025) "A11yShape" — [arXiv:2508.03852](https://arxiv.org/abs/2508.03852) | Most directly comparable accessible system; differentiate on scale, tool integration, protocol |
| A1-5 | Cupkova et al. (2023) "AI, Architecture, Accessibility, Data Justice" | ACADIA's own equity call; your paper answers it |
| A1-6 | Atakan et al. (2025) "Kakadoo" | Voice-driven Grasshopper at eCAADe; still requires visual canvas |

Demote to Tier 2 for space: Evans (1997), Karastathi et al. (2024), Billah et al. (2023), Lundgard & Satyanarayan (2022).

### Tier 2 — Should Cite

- Khan et al. (2024) "Text2CAD" — NeurIPS Spotlight
- Carpo (2011, 2017) — notation shapes design thinking
- Siu, Kim et al. (2019) "shapeCAD"
- Clepper et al. (2025) CHI 2025 — BLV tactile creators navigating tradeoffs
- Noel, Boeva & Dortdivanlioglu (2021) — IJAC equity paper
- Rietschel & Steinfeld (2025) IJAC — conversational exploratory design
- Heylighen & Herssens (2014) — designerly blind spots
- Hamraie & Fritsch (2019) — crip technoscience
- Winner (1980) — artifacts have politics
- Gurita & Vatavu (2025) W4A '25 — LLM UIs are not spontaneously accessible
- Evans (1997), Karastathi et al. (2024), Billah et al. (2023), Lundgard & Satyanarayan (2022) (demoted from T1)

### Tier 3 — Use Selectively

Burry (2011); Pallasmaa (1996/2012); Crawford et al. (2024); Seo et al. (2024); Flores-Saviaga et al. (2025); Schon (1983); Maleki & Woodbury (2013).

---

## Top Papers for JAE

JAE reviewers care about: pedagogy, curriculum, studio culture, disability/inclusion, educational theory, and disciplinary self-reflection. The technical system is context; the pedagogical argument is the contribution.

### Tier 1 — Must Cite

| ID | Citation | Role |
|---|---|---|
| J1-1 | Heylighen & Herssens (2014) "Designerly Ways of Not Knowing" | Single most important theoretical paper for JAE framing |
| J1-2 | Heylighen et al. (2021-2024) "How Do Disabled Architects Design?" | Strongest ongoing empirical precedent |
| J1-3 | Schon (1983) The Reflective Practitioner | Design as reflective conversation; CLI makes it explicit |
| J1-4 | Hamraie (2017) Building Access | Normate template concept |
| J1-5 | Nicholson (2025) "Where Are My People?" ([ACSA resource](https://www.acsa-arch.org/resource/where-are-my-people/)) | JAE is ACSA's journal — direct alignment |
| J1-6 | Billah et al. (2023) "Designing While Blind" | Problem statement |

Demote to T2: Gissen (2022), Gissen (2018), Costanza-Chock (2020), Seo et al. (2024).

### Tier 2 — Should Cite

- Gissen (2022) Architecture of Disability; Gissen (2018) "Why are there so few disabled architects?" (Architect's Newspaper)
- Costanza-Chock (2020) Design Justice (open access)
- Seo et al. (2024) "Born-Accessible"
- Pallasmaa (1996/2012) The Eyes of the Skin
- Evans (1997) Translations from Drawing to Building
- Lifchez (1987) Rethinking Architecture
- Mulligan et al. (2018) "Inclusive Design in Architectural Education"
- NAAB (2020) Conditions for Accreditation
- Vermeersch & Heylighen (2012) Carlos Mourao Pereira case study
- Charlton (1998) Nothing About Us Without Us
- Millar (1994, 2008) spatial cognition
- Loomis, Klatzky & Golledge (2001) spatial language
- Clepper et al. (2025) CHI 2025

### Tier 3 — Use Selectively

Hamraie & Fritsch (2019); Winner (1980); Reynolds (2017); Boys (2014); Sennett (2008); Ingold (2013); UT Austin (2023); Shinohara & Wobbrock (2011); Wobbrock et al. (2011).

---

## Overlap — Cite in Both

1. Billah et al. (2023) — the problem statement
2. Heylighen & Herssens (2014) — designerly blind spots
3. Evans (1997) — representation theory
4. Siu et al. (2025) A11yShape — comparison system
5. Clepper et al. (2025) — BLV creator tradeoffs

---

## Deprioritize or Cut

Historical context only — do not strengthen either paper.

- Nagakura (1990); Nembrini et al. (2009); Garcia (1996, 1999)
- Pohl & Hirschberg (2011); Beilharz (2005); Grabowski & Barner (1998); Sjostrom (2002)
- Piaget & Inhelder (1956) — use Millar and Loomis instead for the same point with empirical evidence about blind adults.

---

## Strategic Recommendations

### For ACADIA

- Lead with Cluster 1A (text-to-geometry explosion). Show reviewers their own work, then reveal the blind spot.
- Framing A ("The Accidental Architecture") remains the strongest lead. The verification-gap argument is technically precise and meets reviewers where they are.
- Introduce disability studies selectively (Winner + Hamraie in discussion, not framing). Do not require reviewers to absorb new theoretical vocabulary before the contribution.
- A11yShape is the primary comparison — differentiate clearly on architectural scale, industry-tool integration, screen-reader-native protocol, controller/viewer separation.

### For JAE

- Lead with the pedagogical gap (Nicholson, Gissen, NAAB). JAE cares about who is in the profession and how education shapes that.
- Schon framing (E) may be the strongest JAE lead — the reflective conversation is a pedagogical concept; show how the CLI makes it explicit.
- Use Pallasmaa and Evans more liberally — JAE readers expect them. Theoretical home base.
- "Born-accessible" (Seo) translates well — it is fundamentally about course and tool design.
- Daniel's actual studio workflow is the evidence — JAE wants narrative, specific design sessions, what the student learned. The technical system is context.

---

## Gap Analysis — Papers Missing from the Brainstorm

Searched 2024-2026 across ACADIA, CHI, ASSETS, eCAADe, CVPR, DIS, ACSA, JAE, and Routledge.

### High Priority — Strongly consider adding

**G-1. Gipe-Lazarou — Blind Design Workshop, Virginia Tech (2022-present)**
- Annual 5-day workshops with blind/VI teenagers exploring architecture; ACSA Diversity Achievement Award 2024
- Forthcoming: *Blind Design: Advances in Non-Visual Pedagogy*
- JAE: closest existing pedagogical precedent. His workshops are exposure/awareness; yours is full authorship with industry tools. Cite to differentiate.
- ACADIA: less relevant (no computational design content), but worth acknowledging.
- [Virginia Tech faculty page](https://arch.vt.edu/people/blacksburg-faculty/gipe-andrew.html)

**G-2. Liebermann (2024) — *Architecture's Disability Problem*, Routledge**
- Why mainstream architecture shows little interest in disability despite ADA; three case studies of disabled-led design
- Published June 2024, 238 pages
- JAE: pairs with Gissen (2022) and Nicholson (2025) as a trio documenting the profession's disability gap. Liebermann adds practice; you add education and tools.
- ACADIA: useful in discussion alongside Winner and Hamraie.
- Routledge, ISBN 9780367641146

**G-3. DIS 2025 — "A Framework-Informed Analysis of Accessibility Barriers in Desktop 3D Printing Software"**
- Screen reader operability of 3D printing tasks (positioning, slicing); custom GUI frameworks in slicing software block standard accessibility APIs
- Directly relevant to tactile output pipeline — documents a barrier your system must address
- [DOI: 10.1145/3715668.3736342](https://doi.org/10.1145/3715668.3736342)

### Medium Priority — Cite if space permits

**G-4. Archi-TangiBlock (2024, IEEE Access)**
- Modular block-based tangible CAD for VI users; 1.2% error rate with VI participants
- Parallels the pegboard concept — different approach (modular blocks vs. pegs on grid) to the same problem
- [IEEE Xplore: 10480423](https://ieeexplore.ieee.org/document/10480423)

**G-5. CAD-Llama (CVPR 2025) — Li et al., Fudan University**
- LLM for parametric CAD, code-like representation; outperforms GPT-4 on CAD generation benchmarks
- ACADIA: strengthens the text-to-geometry cluster. Less directly relevant than AIDL or Text2CAD (ML benchmarks, not design workflow).
- [arXiv:2505.04481](https://arxiv.org/abs/2505.04481)

**G-6. DisOrdinary Architecture Project — *Many More Parts than M!* (2024)**
- Led by Jos Boys (already cited as Boys 2014); UK publication reimagining disability access beyond compliance
- JAE: shows Boys' evolution from theory (2014 book) to practice (2024 publication)
- [Free PDF](https://disordinaryarchitecture.co.uk/archive/manymoreparts)

### Lower Priority — Track but do not prioritize

**G-7. "From text to design" framework (2025, Proceedings of the Design Society)**
- LLM agents with function calling for automated CAD generation; another text-to-geometry entry; cluster 1A already well-populated
- Cambridge Core, Proceedings of the Design Society

**G-8. ACADIA 2025 proceedings (Nov 2025, Miami, "Computing for Resilience")**
- Proceedings may contain relevant LLM+CAD or equity papers postdating the brainstorm
- Action: check CumInCAD when fully indexed

---

## Author Action Checklist

- [ ] Fork outline into ACADIA draft and JAE draft this week
- [ ] Tighten each Tier 1 to 5-6 citations; demote the rest
- [ ] Confirm CADialogue authorship before any submission
- [ ] Remove Ant, Grasshopper-MCP, CadQuery from scholarly references; keep in a "commercial/industry context" sidebar only
- [ ] Add Gipe-Lazarou and Liebermann to JAE bibliography
- [ ] Add DIS 2025 3D-printing accessibility paper to both papers' tactile-output sections
- [ ] Decide Framing E (Schon) vs. Framing A (Accidental Architecture) per venue
