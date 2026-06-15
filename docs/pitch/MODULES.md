# Pitchable Modules

The Radical Accessibility Project is one project, but it pitches better as five.

Different funders fund different parts of the world. NSF cares about the research infrastructure; Mellon cares about the pedagogy and disability humanities; APH cares about the tactile output pipeline; Anthropic cares about the agentic harness; UIUC's own teaching-innovation office cares about the workstation that can be replicated in other classrooms. A monolithic "fund our toolkit" pitch makes every reviewer wonder why the parts they don't care about are in scope.

Decompose into five modules. Each gets its own pitch sentence, its own funder list, and its own 12-month deliverable. The modules share infrastructure but stand alone as fundable units.

---

## RAP Core — research infrastructure

**What it is.** The Controller, the State JSON, the Watcher, the audit logs. The sense-agnostic design state and the agentic harness wrapping it. See the ACADIA 2026 paper, §4.2.

**One-sentence pitch.** A sense-agnostic design-state layer for AI-mediated, non-visual CAD authorship.

**Best-fit funders.**
- NSF CISE/IIS Human-Centered Computing
- NIDILRR Field-Initiated Projects (Development track)
- Anthropic / Google / OpenAI — credits + expertise
- Autodesk Research, McNeel & Associates — technical partnership

**12-month deliverable.** Published reference implementation, schema documentation, evaluation protocols, harness-pattern paper at ASSETS or CHI.

---

## RAP Touch — tactile renderer pipeline

**What it is.** PIAF swell-paper pipeline, 3D-printed tactile models, embossed Braille labels, the in-house tactile graphic standards (density management, abbreviation keys, BANA-compliant label sizing). See the ACADIA paper, §4.3.

**One-sentence pitch.** A tactile renderer system for architectural drawings, models, and critique.

**Best-fit funders.**
- NIDILRR DRRP (Disability and Rehabilitation Research Projects)
- APH — Monarch partnership
- Dot Inc. — Dot Pad developer collaboration
- ViewPlus, Quantum RLV (PIAF maker) — product partnerships
- Perkins School for the Blind — Howe Innovation Center
- Lavelle Fund for the Blind

**12-month deliverable.** Open tactile-output standards documentation, multi-institutional pilot of the rendering pipeline, joint paper with DAISY Consortium or BANA on tactile-graphics conventions.

---

## RAP Describe — linguistic renderer

**What it is.** The Macro/Meso/Micro alt-text generator, the LLM querier over canonical state, the description-as-authorship workflow. See the ACADIA paper, §4.4.

**One-sentence pitch.** A domain-specific linguistic renderer for architecture and spatial media.

**Best-fit funders.**
- Mellon Foundation — Architecture, Urbanism & Humanities
- NEH Digital Humanities Advancement Grants
- Anthropic / Google / OpenAI — credits + expertise
- Schmidt Sciences — HAVI (Humanities + AI)

**12-month deliverable.** Open alt-text dataset for architectural images, evaluation against sighted-baseline descriptions, querier benchmark suite, public dataset release.

---

## RAP Desk — accessible workstation

**What it is.** The physical configuration described in §4.3 of the paper: CLI host, PIAF printer, consumer 3D printer, scanner, ergonomic analog tools — co-located, fixed-position, reproducible across classrooms.

**One-sentence pitch.** A reproducible accessible design workstation for architecture and design schools.

**Best-fit funders.**
- UIUC internal — equipment grants, course-development funds, CITL, the FAA Dean's office
- APH — Quota fund equipment routing
- Bambu Lab, Prusa Research, Formlabs — education-program sponsorship
- Microsoft AI for Accessibility (if rebrand allows)
- Logitech adaptive-input partnerships
- Freedom Scientific / Vispero — JAWS site licenses for partner institutions

**12-month deliverable.** Bill of materials and reproducibility guide, deployment at two partner institutions, public case study with hardware-vendor co-branding.

---

## RAP Studio — pedagogy and curriculum

**What it is.** The adaptive studio practice from §5 of the paper: multimodal critique, communication protocols ("using your words"), faculty training, student assessment, the four-semester curriculum that surrounds the harness.

**One-sentence pitch.** A multimodal studio pedagogy model for access-first architectural education.

**Best-fit funders.**
- Spencer Foundation — Research-Practice Partnerships or Large Research Grants
- NSF EDU / IUSE (Improving Undergraduate STEM Education)
- IES Special Education Research — Development & Innovation
- NEA Design grants
- ACSA Course Development Prize
- NCARB Award for Curricular Innovation
- AIA Upjohn Research Initiative

**12-month deliverable.** Studio syllabus and instructor guide, four-semester case study published in a peer-reviewed education venue, faculty workshop curriculum.

---

## How modules combine

A single application usually targets one module. But several combinations make sense:

- **Core + Describe** to an AI company. The agentic harness and the linguistic renderer are the parts that exercise their product surfaces.
- **Touch + Desk** to a hardware partner (APH, Dot Inc., Bambu). The tactile pipeline and the workstation are the parts that sell their hardware.
- **Studio + Core** to NSF EDU. The pedagogy is the visible deliverable; the Core is the infrastructure that makes it work.
- **Describe + Studio** to Mellon. The linguistic renderer is the disability-humanities artifact; the Studio is the practice it changes.

A federal consortium proposal (NSF INCLUDES Alliance, Horizon Europe) can plausibly fund all five modules at once — but only after several smaller funders have validated individual modules. Don't lead with the consortium ask.

---

## How not to use this

The modules are a **pitching frame**, not an engineering refactor. The code stays one project. Don't split the repository or rename directories to match these labels. The team works on one system; the pitch presents it as five lenses.
