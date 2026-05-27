# Pitch Variants

A lookup table. One thesis sentence, eight tailored title-and-opener pairs.

When sending a cold email or building a cover letter, pick the variant whose audience matches the funder, paste the opener as the first line, then attach a customized version of `CAPABILITY_SUMMARY.md` (or `ONE_PAGER.md` for short outreach). The shared body of the prospectus stays the same; only the opening shifts.

---

## The thesis

The Radical Accessibility Project replaces architecture's visual viewport as the sole source of truth with a sense-agnostic design state that can render into visual, tactile, linguistic, and computational forms.

Every variant below is a translation of this one sentence into the language of a specific funder community.

---

## Variants

### Federal research (NSF CISE/IIS, NIDILRR Development, IES)

**Title.** AI-Ready Accessible Design Education: A Multimodal Harness for Non-Visual CAD Authorship

**Opener.** The Radical Accessibility Project develops and evaluates an AI-mediated accessibility harness that lets blind and low-vision students author, inspect, revise, and critique CAD-based design work through a sense-agnostic design state and multimodal renderers.

### Assistive technology (NIDILRR DRRP, APH, Perkins Howe)

**Title.** AI-Driven Assistive Technology for Non-Visual Spatial Design Authorship

**Opener.** The Radical Accessibility Project is an assistive technology system that increases independence and participation for blind and low-vision learners in visually dominated design, CAD, and digital-fabrication workflows.

### AI companies (Anthropic, OpenAI, Google, Microsoft)

**Title.** Auditable Agentic CAD for Accessibility

**Opener.** The Radical Accessibility Project uses agentic coding as a screen-reader-accessible tool-use interface for CAD, grounding every action in inspectable state, logs, and tactile or linguistic verification.

### CAD vendors (Autodesk, McNeel, Onshape, Trimble, Bentley)

**Title.** Beyond the Viewport: Sense-Agnostic Design State for Accessible Design-and-Make Workflows

**Opener.** The Radical Accessibility Project prototypes a future design-software paradigm in which visual, tactile, linguistic, and computational interfaces all render from the same auditable model state.

### Humanities and disability studies (Mellon, NEH, Ford, Critical Design Lab)

**Title.** Architecture Beyond Sighted Studio Culture

**Opener.** The Radical Accessibility Project uses disability-forward pedagogy and AI-mediated authorship to challenge the visual epistemology of architectural education.

### Architecture discipline (Graham Foundation, AIA, ACSA, Architectural League)

**Title.** The End of the Viewport as Source of Truth

**Opener.** The Radical Accessibility Project develops tactile, linguistic, and AI-mediated architectural representation as a critical practice of non-visual authorship.

### Education research (Spencer, IES, NSF EDU / IUSE)

**Title.** Multimodal Studio Pedagogy for AI-Era Design Education

**Opener.** The Radical Accessibility Project develops and studies a studio pedagogy in which design state is explicit, critique is multimodal, and AI-scaffolded verification is available to every student — designed for blind learners, evaluated for all of them.

### Hardware partners (APH, Dot Inc., ViewPlus, Bambu Lab, Quantum RLV)

**Title.** A Design-Software Pipeline for {hardware}

**Opener.** The Radical Accessibility Project renders architectural design state directly into tactile output on {hardware}, demonstrating an end-to-end CAD-to-touch workflow for blind and low-vision design students.

---

## Pairing notes

Each variant pairs naturally with one or two modules from `MODULES.md`:

| Variant | Lead module(s) |
|---|---|
| Federal research | RAP Core + RAP Describe |
| Assistive technology | RAP Touch + RAP Core |
| AI companies | RAP Core + RAP Describe |
| CAD vendors | RAP Core |
| Humanities and disability studies | RAP Describe + RAP Studio |
| Architecture discipline | RAP Touch + RAP Studio |
| Education research | RAP Studio + RAP Core |
| Hardware partners | RAP Touch + RAP Desk |

---

## What goes into every version, regardless

The shared prospectus body — drawn from `CAPABILITY_SUMMARY.md` — covers: what's built, the five constitutive properties from the paper (sense-agnostic state, renderer parity, multiple authoring channels, LLM skill scaffolding, auditability), team, status, deliverables. The opener changes; the substance underneath does not.

## Reviewer objections

When the variant lands a meeting, the next thing to prepare for is objections. See `FAQ.md` for our answers to the six anticipated reviewer concerns: "this is only one student," "this depends on proprietary LLMs," "architecture is too niche," "LLMs hallucinate," "how do you measure success," "how do you handle privacy."
