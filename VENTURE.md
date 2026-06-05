# Venture: A Deeper Exploration of RAP as a Company

A second-pass synthesis. The first pass (`STARTUP_PITCH.md`) was a working strategy document — what an investor or co-founder would need to decide. This one goes further: thirteen parallel research agents, each chasing an angle the first round either compressed or didn't touch. Founder archetype. Five-year product. Brand and movement. Pre-mortem. Agent-infrastructure platform. New-pedagogy thesis. Disability movement politics. M&A game theory. Adjacent creative disciplines. Multimodal/XR future. Hardware partner ecosystem. Non-startup organizational alternatives. Underground wildcards.

The agents disagreed about details. They converged, with surprising force, on a few claims this document treats as load-bearing:

1. RAP is not "accessibility software for blind architects." It is the first AEC codebase whose architecture (semantic state, deterministic mutations, multi-modal IO) was forced into the shape that AI-native CAD and post-screen design will require by 2030 — and accessibility is the reason it got there first. *Accessibility is the moat, not the market.*
2. The right organizational shape is **not a Delaware C-corp on day one.** It is a 24-month fiscally-sponsored open-source project that earns its way into a **Mozilla-style hybrid** — a 501(c)(3) foundation that wholly owns a Public Benefit Corporation subsidiary. This shape preserves academic incentives, protects the mission structurally rather than contractually, and defers the venture question until adoption signal is real.
3. The right founder team is not "John + Hugh + Daniel" alone. It is **Configuration C**: a recruited technical co-founder (CTO from the Hypar/Forma/Autodesk-Generative diaspora or the CMU HCII accessibility lineage), a named disability-movement Executive Director who fronts the company publicly, John as Chief Architect of Inclusion, Hugh staying UIUC-side as Chief Research, and Daniel as paid co-founder with named board seat and 10x-voting mission-class shares. The DynaVox/Be-My-Eyes/UpCodes triad, modernized.
4. The right name for the company is probably not "RAP." The strongest candidate the agents surfaced is **Plumb** — one syllable, architecture-native, screen-reader-friendly, brandable as a verb. Keep "Radical Accessibility Project" as the research and pedagogy arm at UIUC; the venture is Plumb. Mozilla/Firefox split, OpenAI/ChatGPT split.
5. The pre-mortem's honest forecast: **~7% probability of a venture-scale exit, ~25% Dancing-Dots-style profitable niche, ~30% dignified shutdown, ~38% outright failure.** The mission survives in roughly 10–15% of paths. These numbers are not reasons not to do it. They are reasons to do it correctly — which is to say, with the structural commitments below, not the ones that intuition would generate.

This document is long. It earns its length only if the founders are seriously considering this. If you're skimming, skip to §III (the three founding commitments), §IV (the wedge), §XIII (the 12-month plan), and §XIV (the 90-day kill test). Everything else is the case.

---

## I. The thesis, sharpened

The first pass argued that RAP could become a company because the technical architecture is right. The deeper read is that the technical architecture is right *because of three converging pressures the AEC industry has not yet absorbed*, and RAP is positioned at the exact intersection.

**Pressure 1 — The AI agent revolution arrives in CAD.** Cursor reached $2B ARR and a $50–60B valuation by being the AI-native IDE. Hypar, Zoo.dev, Adam, Backflip, and Autodesk Forma's own AI Assistant are charging the same hill in AEC. None has Cursor's traction yet. The technical reason is structural: Cursor wrapped a *text editor*, not Photoshop, because LLMs need closed feedback loops — small mutation, terse confirmation, deterministic next step. CAD has no equivalent surface. Wrapping Revit with an LLM is wrapping a black box with a stochastic agent. RAP, alone in AEC, has editor-grade observability: semantic IDs (`bay A`), deterministic mutations, `OK:` / `ERROR:` single-line confirmations, a JSON state file you can diff and merge like Git. Anthropic shipped Claude Code voice mode in March 2026; the missing piece between voice-and-design is not the model. It's the substrate. RAP is the substrate.

**Pressure 2 — Multi-modal output stops being a research dream.** APH Monarch shipped v1.4 in February 2026 — multi-line refreshable braille plus a 10×32 dynamic tactile graphics array, JAWS/NVDA compatible, with a published SDK and TIME's Best Invention of 2025. Dot Pad X added a 300-cell tactile graphics surface with a developer SDK. Be My Eyes integrated with Ray-Ban Meta glasses in late 2024 and added hands-free brand support calls in March 2026. Apple shipped Vision Pro accessibility features in May 2026 including eye-tracked wheelchair control. Steam Audio (Valve, free, production-grade) renders binaural spatial audio. The 2028 demo — designer wears Ray-Ban Meta, talks to Claude, model updates, partner sees Rhino viewport, blind colleague feels Monarch refresh, AirPods render binaural walkthrough, contractor on site sees AR overlay — is buildable in twelve months from pieces that all exist today. The CAD tool that wins 2030 is the one whose state is **modality-agnostic**. RAP is structurally there.

**Pressure 3 — Architecture education is publicly in crisis.** In March 2025 RAND released *Building Impact*, commissioned by AIA, NCARB, and ACSA — the first independent audit of architectural education in a generation. Its verdict: only half of students felt prepared in technical skills, debt is unmanageable, the academy-practice gap is structural. In November 2025 Harriet Harriss (former Pratt dean) published a *Dezeen* essay arguing "the prevailing approach to architecture education must be allowed to die." The studio crit is being publicly indicted in *Azure* and *Common Edge*. ChatGPT has made every visual deliverable epistemically suspect. The discipline knows it's broken and does not know what to replace it with. RAP — whose state.json is auditable, diff-able, version-controlled like code — is structurally the answer. *git blame the design.* It is the first design pedagogy where AI-assisted iteration is a feature rather than a leak: instructors require students to use Claude to draft commands and grade the dialogue and the diffs, not the artifact. This is much more than a marketing angle. It is a curriculum thesis that no architecture school in the world is currently equipped to write — and the only academic team that could write it sits at UIUC.

The three pressures converge on a single sentence: **the post-visual, post-GUI, AI-native AEC tool — the one a blind architect, a sighted senior, a voice-controlled paraplegic designer, and a Claude agent can all use the same way — has the same architecture as the tool a blind student forced into existence at UIUC three years ago.** The company that productizes that head start, with the right structural commitments to the original community, can be a category-defining infrastructure player by 2030. The same codebase can also be a beloved profitable niche. The founders, the cap table, and the org shape decide which.

---

## II. The shape (the most important reframe)

The single most important contribution of this round of agents is to **reject the Delaware C-corp default.** John, Hugh, and Daniel are academic researchers and a graduate student. Optimizing for a 10× venture return in 7 years contradicts the actual mission and misaligns with who the founders are. The non-startup alternatives agent's recommendation, which the disability-movement, pedagogy, and pre-mortem agents independently support: **a sequenced two-step.**

**Step 1 (months 0–24): Fiscally-sponsored open-source project.** Operate under an existing 501(c)(3)'s tax umbrella (the Open Source Initiative, NTEN, or a similar mission-aligned sponsor; fee 5–10%). No incorporation paperwork. Immediate grant eligibility for ED/IES SBIR (June 29, 2026 — still the immediate forcing function on the calendar), NIDILRR SBIR, NSF DARE, Microsoft AI for Accessibility, Ford/Mellon Disability Futures Fellowships, AIA Upjohn. Daniel pursues a Disability Futures Fellowship in his own name. John holds the NIDILRR PI role. Hugh writes the NSF DARE proposal. The "startup question" is deferred for 24 months. The decision criterion is paid adoption: if you have 5–10 paying institutional pilots and AEC vendors are asking for licenses by month 24, you incorporate. If you don't, you stay academic and the open-source code becomes infrastructure for whoever comes next. Both outcomes preserve the work.

**Step 2 (years 2–5): Mozilla-style hybrid.** A **Radical Accessibility Foundation** (501(c)(3) — owns open-source code, advocacy, fellowships, the pedagogy curriculum, the Bein Fellowship, the certification mark) wholly owns **Plumb, PBC** (Delaware Public Benefit Corporation — sells hosted Layout Jig, tactile services, AEC compliance products, Monarch content packs). Foundation ownership of the PBC is the structural commitment that prevents acquisition under hostile terms; the foundation can fire the PBC's CEO if mission drift occurs. John stays at UIUC, Hugh becomes Foundation president. Daniel chooses: run the PBC or stay academic with a board seat. Ethan, Isaac, Laura become early PBC engineers or Foundation fellows depending on appetite.

This shape is structurally what Mozilla, Wikimedia, Signal Foundation, and several leading open-infrastructure organizations use. The Foundation pays no dividends and has no shareholders; the corporation has no public equity. Mission is owned, not contracted.

**Configuration C — the founder team, in detail.** From the founder-archetype agent's analysis of twelve real comparable companies (ViewPlus, Be My Eyes, Aira, Hypar, UpCodes, Procore, Cursor, Fable, Tobii/DynaVox, Vispero, 2Gether-International):

- **Technical co-founder (CTO).** Recruit by month 4. Profile: shipped a CAD-adjacent or geometry-heavy SaaS to production, has CAD or AI-agent experience, can mentor accessibility-aware engineering practice. Hunting grounds: ex-Autodesk Generative Design / Forma / Tandem alumni (the Project Refinery / Fractal diaspora), ex-Bentley iTwin engineers, ex-Hypar / Snaptrude / Spacemaker / Higharc / Testfit engineers, Anthropic / OpenAI / Cursor / Zoo.dev ex-engineers, NSF/NIDILRR-funded PhD alums in HCI accessibility (CMU HCII, UW DUB, Maryland HCIL — Jeffrey Bigham's diaspora at CMU is a literal goldmine), and the 2Gether-International alumni network for disabled CTO candidates. 14% equity, 4-year vest, full acceleration on change of control.
- **Executive Director / public face.** Named accessibility-movement figure who fronts the company publicly. Recruit from the 2GI alumni or the Matt Ater / Haben Girma-tier roster. 12% equity. This is the hire that prevents the "two sighted UIUC faculty with a blind student" reading.
- **John — Chief Architect of Inclusion.** Research direction, university channel, NIDILRR PI continuity, NAAB/ACSA distribution. 9% equity. Stays UIUC-affiliated; takes leave only if Configuration C transitions to Configuration B (operator-led venture path).
- **Hugh — Chief Research.** UIUC-side; runs the institute work; co-PI on grants. 5% equity.
- **Daniel — co-founder and Head of User Research.** Salaried, with a named board seat ("Lived Experience Director") and a paid advisory cohort. **9% common equity plus 2% mission-class supervoting shares with 10× voting rights on enumerated triggers**: WCAG/Section 508 conformance reductions, sale to acquirer without published accessibility roadmap, discontinuation of free/subsidized tier for blind users. Successor selection rights held by Daniel plus an external committee (NFB, AFB, 2GI representative) so the seat survives him stepping back.

Equity rounds out with employee pool (14%), advisor pool (3%), seed (~25%), and unallocated reserve. Seed VC enters only at month 7–9, ideally led by Building Ventures (Hypar precedent) or Brick & Mortar with Adaptation Ventures and Disability:IN co-investing. Cap-table transparency at launch is non-negotiable.

**Five concrete advisor names to recruit before incorporation:**

1. **Chris Downey** (Architecture for the Blind). Blind architect, UC Berkeley universal-design teaching, California Commission on Disability Access. The single most credible AEC + lived-experience advisor on the continent.
2. **Haben Girma.** First deafblind Harvard Law grad, advises Apple/Microsoft/Acquia. Legal-accessibility + community legitimacy.
3. **Matt Ater (Vispero SVP).** Blind executive, JAWS-ecosystem credibility, enterprise customer access, "nothing about us without us" pedigree.
4. **Anthony Hauck or Ian Keough (Hypar).** Ex-Autodesk Revit / Dynamo / Generative Design leads now running text-to-BIM. Either anchors AEC-software credibility for VCs.
5. **Diego Mariscal (founder, 2Gether-International).** Gateway to disabled-founder capital ecosystem and movement-aligned funds.

---

## III. The three non-negotiable founding commitments

The disability-movement-politics agent named these as the operational floor. Without them, the question is not whether the company fails on community grounds but how publicly. With them, the company has the standing to make the case that it is the first sighted-faculty-founded accessibility company that built the structural answer in before the first dollar of revenue. **Encode these in the Foundation's certificate of incorporation and the PBC's operating agreement — not the website.**

**Commitment 1 — Blind-led governance with teeth.** Daniel as equal-equity co-founder with formal product/brand veto. ≥50% disabled board seats. A paid advisory council of 8–12 disabled designers and architects spanning braille users, low-vision, late-blinded, deafblind, mobility-plus-blind, and disability-justice constituencies, with named decision categories where their vote is binding (pricing, marketing creative, NFB partnership terms, acquisition terms). Breaking this costs: NFB resolution within twelve months and accessiBe-tier reputational death.

**Commitment 2 — Free forever for blind individual users; institutions pay.** Codified in the certificate of incorporation as a structural commitment, not a marketing promise. Be My Eyes is the precedent and the proof it is venture-fundable. Charge universities, schools for the blind, government agencies, AEC firms. Never gate functionality on a disabled individual's ability to pay. Breaking this costs: immediate ACB/AFB op-ed, NFB resolution, blind user migration to any open-source fork the day the price wall appears.

**Commitment 3 — Open core, open format, open exit.** Controller and state-format AGPL-licensed (or equivalent copyleft); schema versioned and published as a portable spec; written commitment that user data and macros are portable and never proprietary-locked. Commercial value lives in hosted services, integrations, support, training, and the Monarch/PIAF/voice content pipelines — not in hostage-taking the file format. This aligns with the right-to-access movement and NV Access's lineage. Users always have an escape valve. Breaking this costs: loss of academic disability-studies coalition, loss of open-source credibility, permanent "trojan horse" reputation that no PR campaign reverses.

These three commitments do not guarantee success. They are the floor. Everything else hangs off them.

---

## IV. The wedge: still TACT, but framed within Monarch + Anthropic

The first pass picked TACT (image-and-state-to-tactile-PDF) as the v1 SKU at $4,800/yr to DRES offices. That call holds — but the deeper read is that TACT is not just a wedge product. It is the entry point into two strategic relationships that determine the company's ceiling.

**Strategic relationship 1 — APH and the Monarch content engine.** APH (American Printing House for the Blind) controls the federal quota program — a Congressional appropriation of roughly $38–45M per year, distributed per capita to state schools for the blind based on the January census of legally blind students. APH and HumanWare jointly built Monarch (v1.4 shipped February 2026, multi-line refreshable braille plus dynamic tactile graphics, TIME Best Invention 2025). APH has explicitly opened a Monarch SDK and welcomes third-party apps (Desmos KeyMath, PBS Cyberchase, Monarch Chess are existing precedents). APH is mission-aligned (nonprofit, congressional charter), not adversarial.

The play: **become the canonical CAD content engine for Monarch.** A Monarch-native "Layout Jig Viewer" app that streams state.json to the 10×32 dynamic tactile array, plus a content pipeline that pushes RAP-authored architectural and STEM tactile content into APH's Tactile Graphics Image Library. Deal structure: zero-royalty app, paid content authoring services, revenue share on Federal Quota orders for premium content packs, 70/30 split to RAP for premium and 50/50 for Federal-Quota-distributed content. Two-year term, mutual MFN, no exclusivity outside Monarch. One APH catalog listing reaches all 50 state outreach programs by default.

**Strategic relationship 2 — Anthropic and the MCP standards play.** Anthropic launched a formal Claude Partner Network in late 2025 with featured slots for MCP integrations (Asana, Box, Canva, Figma already inside Claude's chat UI). RAP already runs MCP servers — it is one of the only MCP servers built for accessibility rather than productivity. The pitch is a single sentence: *RAP is the canonical accessibility MCP example.* Featured slot in Anthropic's MCP gallery, joint blog post, inclusion in the Partner Hub. Costs Anthropic nothing. Gives RAP credibility with every Claude Enterprise sales conversation that touches accessibility — and, by transitivity, every AEC firm exploring AI in 2026–2028.

**Pricing and packaging refinement.** The DRES tier remains $4,800/yr (engineered to sit below the typical discretionary-approval ceiling). Add: **TACT Pro at $12K/yr** (full state-to-PIAF + Monarch viewer + Layout Jig CLI / MCP access). **University site license at $25–50K/yr** (multi-school, LMS integration, instructor tools). **AEC firm seat license at $1,500–3,000/seat/yr** introduced year 3 once the Revit/Rhino plugin ships. **Federal/state government via GSA Schedule (year 2)** — multi-site bundles in the $50–250K range.

**First 10 customers — refined and named.** UIUC DRES, Illinois School for the Visually Impaired, Perkins School for the Blind, California School for the Blind, Texas School for the Blind and Visually Impaired, MIT Disability and Access Services, Stanford Office of Accessible Education, Gallaudet TIP/IDEA program (deafblind track), APH (channel partnership), RNIB UK (international beachhead). Tier-2 same year: Lighthouse Guild, SF LightHouse, Carroll Center, CNIB, Vision Australia, Cooper Union, Pratt, Cornell AAP, the Big Ten Academic Alliance accessibility working group (14 peer R1s simultaneously).

---

## V. The five-year product (where the architecture compounds)

The product roadmap agent argued that the **Year-5 product shape is not a SaaS app or a desktop CAD tool but a substrate**: a CLI core, a hosted multi-tenant state service, and a plugin marketplace. The text-first controller stays as source of truth; viewers (Rhino, Revit, Forma, browser-WebGL, tactile printer, screen reader, voice agent, Vision Pro, Ray-Ban Meta) are peers consuming the same state stream. GitHub for buildings, with first-class agent and accessibility APIs.

**Year-by-year, condensed:**

- **Year 1 — TACT Productized.** Hosted conversion endpoint, DRES dashboard, Canvas/Blackboard LTI plugin, batch course-pack conversion, audit logs, Grade 1/2/UEB Math Braille. SOC2 Type I. Monarch app shipped. Anthropic Partner Hub listing. Goal: 20+ DRES contracts.
- **Year 2 — Layout Jig Studio.** Hosted state service with versioning, named branches, diff/merge of state.json. Web viewer with screen-reader-native interaction. First AEC firm pilots (Perkins&Will accessibility group, Gensler, HOK accessibility consultants). Revit read-only import. APH partnership signed. State VR vendor listings in CA / NY / IL / TX / MA.
- **Year 3 — Compliance Cloud + Revit Plugin.** ADA / Section 508 / EAA / IBC accessibility audit engine. Revit and Forma bidirectional sync. Audit reports as separate billable SKU. Federal GSA / DOE procurement cleared. Monarch viewer first-class. *Killer demo at ACADIA 2029: a blind architect designs a 40,000-sf elementary school from scratch in 25 minutes using voice + a refreshable braille display, with live ADA narration, generative layout options, a tactile printout handed to the audience, and IFC exported to Revit on the projector.*
- **Year 4 — Agent Platform & Marketplace.** Public MCP gateway, third-party plugins (precedent libraries, code-checkers, fabrication vendors), revenue share. Hardware partners ship "RAP Inside" labels (APH, ViewPlus, Bambu). Voice-first design agent GA. Adjacent verticals enter: scientific data sonification (NASA Chandra precedent — *A Universe of Sound* study with n=3,184 empirically proved sighted users get the same gains as blind ones) and GIS / cartography (Esri partnership; Kadaster precedent).
- **Year 5 — AI-Native AEC Operating Layer.** Multi-user semantic CRDT — *Git for buildings, not Google Docs for buildings* — branches and approvals, not cursor presence. Generative layout under live compliance constraints. Hardware-agnostic tactile/audio/haptic output. Urban-scale state graphs. *The killer 2028 demo lands at AIA: one model, five senses — voice in, JSON state mutates, Rhino viewport renders, Monarch refreshes the floor plan, AirPods render the binaural walkthrough, refreshable braille confirms the corridor width, contractor on site sees AR overlay via Ray-Ban Meta linked to the same state.json. One mutation, five outputs.*

**Year-1 engineering priority stack** (the things the team works on, ranked, with one-line justifications):

1. **Hosted TACT API + DRES dashboard.** The SKU that pays salaries.
2. **State store v2 (event-sourced, Postgres snapshots).** Every later product depends on this.
3. **SOC2 Type I + auth/SSO.** Gates every enterprise sale after Q3.
4. **Canvas/Blackboard LTI for TACT.** Distribution wedge into ~4,000 US campuses.
5. **Rust controller core (compatibility-preserving).** Kills the Python perf ceiling before it bites.
6. **Public MCP gateway (rate-limited free tier).** Seeds the agent ecosystem early.
7. **Monarch viewer app.** The APH partnership's deliverable.
8. **Steam Audio binaural walkthrough renderer.** The "hear your design" surface; weeks of work, years of moat.
9. **Compliance engine v0 (ADA wheelchair clearances + door widths).** Proves the year-3 SKU.
10. **Web viewer with screen-reader-native interaction.** Kills the "is RAP real outside a CLI?" objection from AEC buyers.

**Architectural decisions that compound vs. liabilities to refactor.**

Compound into moats: semantic state.json, deterministic CLI + replay, MCP surface, crash-only viewer discipline, accessibility-first IO discipline.

Refactor for enterprise: Python-stdlib-only controller → Rust or Go core by year 3 for parallel evaluation and predictable performance on million-element states; single-tenant state.json → log-structured event store; IronPython 2.7 Rhino watcher → RhinoCommon C# or Compute by year 2; synchronous MCP → streaming protocol by year 3.

---

## VI. Mission protection, structurally

Ben & Jerry's sold to Unilever in 2000 for $326M with an independent mission-protection board contract. Magnum Ice Cream dissolved it by January 2026. *Contractual mission covenants fail under sufficient acquirer pressure.* Patagonia's structure — a Purpose Trust holding 2% voting stock with an independent Protector and the rest held by the Holdfast Collective — has held for 30 years. The lesson is unambiguous: **mission protection must be structural (charter, ownership, voting), not contractual (agreements that can be litigated or bought out).**

The full mission-protection stack the agents converged on:

- **Delaware Public Benefit Corporation** for the operating company. Stronger than B-Corp (which is a certification, not a charter form). Anthropic, Patagonia, Kickstarter precedent.
- **501(c)(3) Foundation holding 100% of the PBC's voting stock.** Mozilla model. Foundation board is independent of PBC operating leadership and can replace it.
- **Dual-class shares with mission-class supervoting rights.** Daniel's 2% mission-class shares carry 10× voting on enumerated triggers (accessibility regression, sale to non-accessibility-aligned acquirer, discontinuation of free tier for individuals).
- **Disability Community Advisory Board with charter-level veto rights** on pricing, marketing creative, partnership terms with NFB/ACB/AFB, acquisition terms, and any retirement of accessibility features. ≥50% blind/low-vision members; spans braille/non-braille, totally-blind/low-vision, congenitally/late-blinded constituencies. Paid professional honoraria, not unpaid advisory.
- **B-Corp certification** as a public signal.
- **UIUC tech-transfer license with accessibility-conformance covenant.** If the PBC drops below WCAG 2.2 AA or Section 508 conformance, IP rights revert to UIUC. Powerful, underused; UIUC's OTM is structurally amenable.
- **Open-source core + state.json schema under Linux Foundation governance** by year 3. Makes the *protocol* a public asset that even an acquirer cannot shelve.

The acquisition negotiation, when it happens, then becomes: not "will the acquirer respect the mission" (they won't, on a long enough timescale) but "can the acquirer break the open-source schema, the Foundation's ownership of the PBC, the supervoting mission-class shares, or the UIUC reversion covenant" (no, no, no, and no). Price gets maximized by running a banked process; mission gets preserved by the structure being too expensive to dismantle.

---

## VII. The pedagogy thesis (institute as load-bearing wall)

The most under-monetized intellectual asset RAP currently holds is not the software. It is the **pedagogy**. The new-pedagogy agent argued, persuasively, that the Foundation arm of the Mozilla hybrid should not be a generic open-source steward. It should be a **Radical Accessibility Institute** at UIUC — funded by NSF DARE, NIDILRR RERC, Mellon, Ford, and corporate consortium memberships in the MIT Media Lab mold ($150K/yr per member × 10 members = $1.5M/yr unrestricted, hires 4 faculty FTE + 8 grad students + 2 staff engineers).

**Why the Institute is load-bearing.** The 2025 RAND *Building Impact* report, commissioned by AIA / NCARB / ACSA, gave the architecture profession permission to admit that pedagogy is broken. NCARB's 2025 *Accessibility and the Impact of Disabilities on Architectural Licensure* survey found 50% of disabled candidates faced major barriers vs. 41% of non-disabled. Harriet Harriss is returning to Pratt faculty in 2026 explicitly to do independent research on what should replace the studio. The window to write the next NAAB *Conditions for Accreditation* (next revision cycle 2027–2028, per NAAB's published cadence) is open *now*. Whoever writes the de facto standard for "accessible architecture education infrastructure" — the curriculum kit, the textbook, the certification mark — owns the discipline's standards conversation for the next twenty years. RAP is the only academic team with the infrastructure (Layout Jig + TACT + Daniel as co-author) to write it.

**What the Institute publishes** (in order of strategic leverage):

1. **An open educational resource (OER) curriculum kit** under CC-BY. The 16-week first-year studio syllabus. Adoption is the wedge; the kit is free.
2. **A peer-reviewed companion textbook with MIT Press or Routledge.** Architecture's two main academic houses. The textbook is what helps adopting faculty earn tenure — and faculty adopt what helps them get promoted. This is the deepest distribution channel that exists.
3. **The annual *State of Accessible AEC* report card.** Public scorecard rating every major AEC tool (Revit, Rhino, AutoCAD, ArchiCAD, Vectorworks) against a defined accessibility rubric. Adversarial, citable, the artifact journalists call about every year.
4. **The Bein Fellowship** — paid year-long residency for one disabled architecture student per cohort, with a public output requirement. Credentialing path. Pipeline.
5. **An open spec — the Semantic CAD Schema (state.json) under Linux Foundation governance.** The Anthropic-MCP play formalized.
6. **A small invitation-curated annual conference at UIUC ("RADCON," ~200 people, mixed disabled and non-disabled, mixed software and architecture).** Year 3 onward.
7. **A book — *The Inclusive Default*** — co-authored by Daniel and the founders, Princeton Architectural Press or MIT Press. Year 2–3. The artifact that gets the company taken seriously by deans.

**The "AI proof" angle is real.** Architecture studios are in crisis because ChatGPT generates plausible-looking student work. RAP's semantic state file is *more* auditable than visual deliverables — every command issued, every change made, every iteration. Instructors require students to use Claude to help draft commands and grade the dialogue and the diffs, not the artifact. RAP shows the receipts. This frame alone should command attention from every NAAB-accredited program with an academic-integrity policy under stress (which is to say, all of them).

**Five most likely first adopters of the curriculum.** Cooper Union (Nader Tehrani — most publicly committed to pedagogical reform); MIT Architecture Computation Group (Terry Knight, Takehiko Nagakura — academic ancestors of this work); SCI-Arc MS in Design Theory and Pedagogy; Pratt (Harriet Harriss); UIUC itself (home turf, in-state policy advantage). Don't skip UIUC because it's home — anchor school plus four marquee co-developers is the right launch.

---

## VIII. Adjacent verticals (GIS and sonification by Year 4)

The first-pass synthesis recommended ignoring most adjacent disciplines. The deeper read is more selective. From the creative-disciplines agent:

**Expand into, by Year 4:**

1. **Scientific data sonification.** NASA Chandra's *A Universe of Sound* study (n=3,184 participants) empirically proved that the "post-visual is better for everyone" thesis holds: sighted users got the *same* learning gains as blind/low-vision users from sonified astronomy data. SoniPy, Astronify, Strauss, Sonecules, Highcharts Sonification Studio exist but are fragmented academic projects. A deterministic semantic-state authoring tool for scientific charts with multi-modal output is greenfield. Buyer: NSF, NIH, university accessibility offices, scientific publishers. Founder fit: architecture → chart authoring is geometrically natural.
2. **GIS / cartography (tactile + sonified maps).** Esri Press published *Tactile Mapping: Cartography for People with Visual Impairments* in 2023; the Netherlands' Kadaster won the 2023 Esri Making A Difference Award for tactile-map workflows. Esri has a public accessibility program. RAP-paradigm GIS = "semantic state = GeoJSON, viewer = ArcGIS/QGIS, exports = tactile PDF + sonified flyover + braille legend." Esri is a partner candidate, not a competitor. Buyer: government, transit agencies, schools for the blind, urban planning.

**Skip entirely.** Mechanical/sculpture CAD (A11yShape + OpenSCAD/CadQuery already won this lane; the U-Mich team has a multi-year head start). Visual fine arts and animation (non-semantic artifacts; paradigm doesn't port). Fashion patterning (no Daniel-equivalent surfaced; CLO3D entrenched).

**Partner, don't build.** Dancing Dots (music notation — 30-year incumbent with the niche locked); Kinetic Light (choreography — Alice Sheppard and Laurel Lawson built Audimance and own the audience); AbleGamers (game accessibility — community-owned).

**The repeatable pattern is the deepest insight.** Each successful disability-tech company has a disabled founder/co-designer (WeWALK, Be My Eyes, NV Access, Bricks for the Blind / Matthew Shifrin, Architecture for the Blind / Chris Downey). RAP's expansion model is: **find a Daniel-equivalent per vertical.** For sonification, a blind astrophysicist or chemist (Wanda Diaz-Merced is the obvious name). For GIS, a blind cartographer (the Netherlands Kadaster team has named contributors). For theatre lighting, the search is open. The pattern isn't "expand the product"; it is "form the partnership that gives the new vertical lived-experience legitimacy from day one."

---

## IX. The MCP standards play

Of every angle the thirteen agents explored, **this one is the single highest-leverage move** the company can make in the next 90 days. It costs almost nothing and forecloses nothing. It earns the company the right to define a category.

**The play:** Ship a public draft of a **CAD-MCP spec v0.1** — a proposed standard for how LLMs drive CAD tools — plus a conformance benchmark. Open-source both under Linux Foundation governance. Run Claude 4.x and GPT-5 against three tools (Rhino-via-RAP, raw Rhino, raw Revit) and publish the numbers: *Claude completes 73% of architectural design tasks via wrapper, 94% via CAD-MCP.* Numbers move markets.

**Why this works.**

- MCP was donated to the Linux Foundation's Agentic AI Foundation in December 2025. The protocol layer is now governance-neutral. The application-layer standards are unwritten and up for grabs. Owning the AEC standard is worth more than the SaaS.
- The narrative makes Anthropic want to feature RAP (canonical accessibility MCP example). Featured slot in Anthropic's Partner Hub is distribution-equivalent to a Series A round of marketing budget.
- It forces Autodesk into a public response. They either adopt the spec (giving RAP standards leadership) or ship a competing spec (giving RAP the David-vs-Goliath narrative the press will love). Bentley quietly adopts because they always lose standards wars and know it. BricsCAD, Vectorworks, FreeCAD, Onshape adopt because they need any edge against Autodesk. The IFC.js / Speckle / BlenderBIM open-source AEC community is the natural first home — Speckle is already a "semantic CAD interchange" company and a natural co-author.
- It positions RAP as Anthropic's, APH's, *and* Speckle's natural partner. Three independent partners maintaining the business without a sale.
- Distribution leverage scales. CAD-MCP becomes the thing Hypar and Zoo.dev have to interoperate with, not the thing they compete against. Standards are how small players neutralize big players.

**What ships in the first six months:**

1. CAD-MCP spec v0.1 — open, with reference semantic schema for AEC.
2. Conformance test suite — "is your CAD tool agent-driveable?" — Claude + GPT-5 driven.
3. Reference SDK in Python and TypeScript.
4. Three reference implementations: Rhino (have), FreeCAD (open source, easy), one paid pilot from BricsCAD / Vectorworks / Onshape.
5. Public leaderboard.
6. Hosted MCP gateway so vendors don't have to run their own.

**This is the move that opens the venture-scale ceiling without abandoning the wedge.** The TACT/DRES revenue pays the rent. The protocol owns the future. Do both — but ship the spec *first*, because narrative leadership in a forming category is a one-time prize and the window closes in 2027.

---

## X. The M&A endgame (years 5–7)

Autodesk acquired Spacemaker — 115 employees, Series A, ~$25M raised — for **$240M in late 2020**, four years after founding. Their pattern is consistent: 13 design-construction investments in three years pre-Spacemaker, ongoing AI tuck-ins thereafter (Payapps, Aether at $131M in May 2024). Nemetschek bought GoCanvas in 2024 at **~11.5× 2023 ARR** — the public benchmark for AEC SaaS pricing. Bentley paid **$1.05B for Seequent in 2021** and acquired Cesium in 2024 to build the iTwin platform. Vector Capital's Vispero rolled up Freedom Scientific + Optelec + TPGi + Enhanced Vision at PE multiples (4–7× revenue) for profitable, channel-leverageable assets.

**The most likely exit, with probability and price:**

- **Autodesk acquisition in year 6 (2030–2031) at $200–300M on $10–14M ARR, ~20–25× ARR.** Strategic premium driven by Spacemaker precedent and AI-CAD competitive urgency. Probability ~40%.
- **Nemetschek at $130–180M (~12× ARR).** Roll-up logic, disciplined multiple. Probability ~25%.
- **Vispero at $40–80M (5–8×).** PE-style, accessibility-vertical consolidation. Probability ~15%.
- **Merger with HumanWare creating a $200–400M combined entity.** Most coherent strategic option. Probability ~10%.
- **Stay private (Dancing Dots ceiling, $5–10M ARR, profitable forever).** Probability ~25%. Not mutually exclusive with the rest — this is what happens if no exit clears.
- **IPO.** Probability ~2%. Procore needed $400M ARR and 38% growth to clear the bar. RAP is structurally a strategic acquisition candidate, not an IPO candidate.

**The single move that maximizes optionality:** become Anthropic's reference MCP-CAD implementation, APH/HumanWare's reference content pipeline, *and* keep the state.json schema open-source under Linux Foundation governance — all simultaneously. This creates three independent buyers (Autodesk, Vispero, Bentley) competing for a non-shelvable asset, *and* three sustaining partners (Anthropic, APH, Microsoft) keeping the business alive without sale. Costs nothing. Forecloses nothing.

**The acquisition negotiation playbook** (years 5–7):

1. Run a banked process with Qatalyst or FT Partners.
2. Force Autodesk vs. Bentley vs. Nemetschek vs. Vispero to bid against a credible IPO/merger-with-HumanWare alternative.
3. Insist on, in writing, in the merger agreement:
   - Named-product survival with 7-year minimum.
   - Accessibility non-regression covenant with $5M annual budget floor.
   - Reversion-to-open-source trigger if the product is sunset.
   - Disability Community Advisory Board preserved post-close, with same charter veto rights.
   - Earnouts tied to *user accessibility metrics*, not just revenue.
4. Accept ~15% lower headline price for ironclad covenants. The Foundation's 100% ownership of the PBC's voting stock means the Foundation board has standing to enforce these terms post-close.

The mission survives only if the protocol is open and the covenants are structural. Price is maximized only if three credible buyers and one credible non-sale alternative exist simultaneously at the table.

---

## XI. The pre-mortem (the autopsy you should read before signing anything)

It is January 2031. The company is dead. The pre-mortem agent's autopsy, condensed:

**The five most likely failure modes, ranked:**

1. **TAM ceiling — the Dancing Dots trap.** Most likely. The mission was achieved perfectly; ARR stalled at $1.8–3M because the buyer set was always small (60–150 DRES offices plus ~70 schools-for-the-blind, plus a long tail of slow-procurement institutions). Series A term sheets evaporate at this multiple. Year 2029.
2. **Incumbent crush.** Hypar or Autodesk Forma adds a screen-reader layer + JSON state + braille labels in a quarterly release. RAP's wedge collapses overnight. Year 2027–2028.
3. **SBIR-grant trap.** The team wins ED/IES Phase I and NIDILRR Phase II, builds for grant deliverables instead of customers, arrives in 2029 with great research and no commercial traction. Year 2028–2029.
4. **Regulatory rollback.** A 2027 DOJ rulemaking guts the Title II web/mobile rule entirely; the "forced buyer" thesis dies. Year 2027.
5. **Founder fracture or loss of community legitimacy.** Daniel departs over equity, direction, or burnout; NFB endorses a competitor or stays silent; moral authority evaporates. Year 2028–2029.

**The two-year warning-sign dashboard** (any one → re-evaluate; any two → call the question):

- Fewer than 8 paying DRES customers by month 18.
- ACV trending below $25K.
- Fewer than 3 reference customers willing to do a 15-minute sales call.
- Sales cycle median >9 months.
- Hypar / Autodesk / Forma mentions "accessibility" in any release notes (start an 18-month countdown).
- Engineering hours on grant deliverables >40%.
- Daniel's public hours on RAP <5/week by month 12.
- Lead engineer recruiter outreach >2/month.
- NFB convention demo gets <50 attendees.
- Any IES/NIDILRR grant deadline extended or rolled back federally.

**Honest probabilistic forecast:**

- P(reaches $1M ARR by month 30): ~30%.
- P(reaches $10M ARR by year 5): ~6–8%.
- P(meaningful exit / acquisition year 5–7): ~15–20% (acqui-hire is the median).
- P(mission preserved at exit or Series B): ~10–15%.

Net: ~7% venture-scale win, ~25% Dancing-Dots lifestyle, ~30% dignified shutdown or acqui-hire, ~38% outright failure with founder burnout. **The 13–15% probability of mission-preserved success is the number that should drive structural decisions.** Configuration C + Mozilla-hybrid + the three founding commitments + the MCP standards play, taken together, are the moves that move that probability from ~7% to ~13–15%. None of them, individually, is sufficient. All of them, together, are the only path.

**Exit-without-failing options** (in priority order, if you have to wind down):

1. Open-source-foundation transfer to Linux Foundation or APH Foundation. Founders take board seats. Cleanest mission-preserving exit.
2. License sale to APH or HumanWare. $2–8M. Team rolls in for 2 years.
3. Acqui-hire by Autodesk Foundation or Adobe accessibility team. Founders get jobs; IP gets buried or open-sourced.
4. Wind-down with grants intact. Spend down NIDILRR on a final research deliverable, publish everything, return remaining capital.
5. Convert to 501(c)(3). Restructure as a nonprofit hosted at UIUC. Caps the upside; preserves the work.

**The single steelman against attempting this venture, in 200 words:**

The accessibility-CAD vertical does not have a $100M ARR outcome in it. The buyer set is structurally small (≤200 institutions in the US, ≤1,000 globally), the budgets are statutory not strategic, the procurement cycles are 9–18 months, the regulatory tailwind just stalled under a hostile administration, and the most likely incumbent response is a 6-month feature ship from Hypar or Autodesk that nullifies the wedge. The non-dilutive grant path that looks like RAP's friend is its enemy: it will let the team avoid the brutal customer-discovery work for three years and arrive at Series A unable to tell a venture story. The blind-architect TAM is real but rounding-error small. The AEC-compliance TAM is real but already owned by Level Access, Deque, and AudioEye, who will not let a CAD upstart take it. The work matters — but mattering is not the same as being venture-fundable. The same outcomes (Daniel-class users served, IP preserved, research advanced) are achievable through a UIUC research center plus an APH partnership, with zero equity dilution and zero founder-conflict risk. *Starting a company is the worst vehicle for this mission.* This is the case the founders should be able to answer in writing, not in conversation, before signing the first founder agreement.

---

## XII. Three wildcards the standard analyses won't surface

The wildcards agent ran the most expansive pass and produced three under-considered moves that deserve real engineering, marketing, and capital allocation. None is a substitute for the core strategy. All three amplify it.

**Wildcard A — The traveling "famous buildings you can touch" exhibit.** Smithsonian Affiliate exhibits charge $80–250K hosting fees plus shipping. *Bodies: The Exhibition* grossed $200M+ over a decade. A 12-stop circuit of tactile reproductions of canonical buildings (Farnsworth, Villa Savoye, Fallingwater, the Pantheon, the Salk Institute) at $150K/stop nets $1.8M over 18 months, plus catalogues, plus permanent collection sales of leftover models, plus museum relationships that route into adjacent education funding. The exhibit's centerpiece is a public RAP terminal where any visitor — sighted or not — types or speaks a command and a tactile printout of their own building emerges. The printouts are the marketing visitors carry home. Build it once at UIUC; let museums fund the tour. Cooper Hewitt's *Access+Ability* and *The Senses: Design Beyond Vision* prove the audience exists.

**Wildcard B — The structured-negotiation remediation channel.** Lainey Feingold has spent 25 years building a cleaner version of accessibility-litigation GTM — structured negotiations that produce binding settlements *with* defendant cooperation. Walmart, Bank of America, Major League Baseball settled under her process. RAP slots into those agreements as the technical remediation tool, billed to the defendant as part of the settlement, blessed by plaintiff counsel. The lawyer relationships are the moat — maybe 20 people in the US do this work, they all know each other, and once two or three reference RAP in consent decrees, you become the default. The disability-movement-politics implications are clean: this is the *cooperative* channel, not the drive-by-Title-III channel. $50–100M ARR ceiling. Nobody in the SaaS-for-architecture space is even thinking about it because it requires legal-domain relationships, not product-led growth.

**Wildcard C — The Champaign-Urbana biennale.** A blind-led architecture biennale, hosted at UIUC every odd-numbered year, where every commissioned pavilion must be navigable by a blind visitor without sighted assistance. Tactile catalogues. Audio-described openings. Pavilions by Foster, BIG, MAD, Adjaye plus emerging blind designers. State of Illinois underwrites $5M as economic development. Daniel curates the inaugural edition. The biennale becomes the *de facto* certification body for accessible architecture. RAP is the technical backbone, but the biennale is the moat: once it exists, no competing platform can credibly claim "the standard" because the standard literally meets in Champaign every two years. Costs $5–8M for year one. Breakeven by year three on sponsorships, ticket sales, and pavilion fees. *It sounds insane until you remember that the Venice Biennale was started in 1895 by a city of 175,000 that wasn't yet on most international itineraries.* Categories beat products on long timescales. If RAP succeeds purely as software, a bigger player will eventually undercut it. If RAP creates the biennial gathering where the entire discipline of accessible architecture meets, it owns the discipline's standards conversation — and software dominance follows from standards dominance.

These three are not equally fundable in year 1. The exhibit (A) is buildable by year 2 with a $300K NEH or Mellon planning grant. The structured-negotiation channel (B) requires one full-time business-development hire with legal-domain relationships, year 3–4. The biennale (C) is a year-4 launch contingent on a $5M State of Illinois economic-development commitment that John could plausibly secure given Tammy Duckworth's office and the existing UIUC institutional infrastructure.

---

## XIII. The 12-month plan, revised

A quarter-by-quarter that integrates the second-round insights.

**Q1 (months 1–3) — Foundation, fiscal sponsorship, partnership, and the spec.**

- Find a fiscal sponsor (Open Source Initiative, NTEN, or equivalent). Sign a 5–10% sponsorship agreement. No incorporation yet.
- Bring Daniel on as paid co-founder (sponsor-payable contractor). Equity offer in writing, contingent on later incorporation.
- Begin UIUC OTM IP-licensing conversation with the accessibility-conformance reversion covenant.
- **Ship the CAD-MCP spec v0.1 publicly.** Plus conformance benchmark. Plus the Claude/GPT-5 leaderboard against Rhino-via-RAP, raw Rhino, raw Revit. This is the single most leveraged move.
- Submit ED/IES SBIR Phase I (June 29, 2026 deadline — the immediate forcing function).
- Submit NIDILRR SBIR Phase I.
- Submit Microsoft AI for Accessibility (next deadline).
- Pursue Daniel's nomination for the Ford / Mellon Disability Futures Fellowship.
- Land 3 free design-partner pilots: UIUC DRES, Illinois School for the Visually Impaired, Perkins.

**Q2 (months 4–6) — Conferences, CTO recruit, advisor board.**

- Conference presence: CSUN 2027 booth (co-present with Daniel), submit to ASSETS 2027 and ACADIA 2027 papers, plan AECTech 2027 talk.
- **CTO recruit closes by month 4.** Hunt in the Hypar/Forma/Snaptrude diaspora and at CMU HCII's accessibility group.
- Recruit named advisory board: Downey, Girma, Ater, Hauck/Keough, Mariscal. Closed by month 5.
- Open Anthropic Partner Hub conversation. Co-author the "MCP for accessibility" blog post.
- Open APH Monarch app conversation.
- Convert 2 of 3 pilots to paid contracts (sponsor-payable, $4.8K each). Or paid-pilot model under the sponsor's umbrella.
- Apply to 2Gether-International Venture Labs accelerator to credential disability-led status.
- Apply to YC W27 batch (if Configuration C is locked).

**Q3 (months 7–9) — Repeatable sales motion, sales engineer hire.**

- Hire one part-time sales engineer (ex-DRES staffer with assistive-tech background). They exist, they're cheap, they speak the buyer's language.
- Get listed on state VR vendor catalogs in CA / NY / IL / TX / MA.
- File the Section 508 VPAT.
- Begin GSA Schedule path via a reseller partner (12-month timeline).
- 8 paid institutions closed by month 9.
- Sign APH Monarch app developer agreement; ship first Monarch viewer build.
- Sign Anthropic featured-partner status.
- Publish first State of Accessible AEC report card.
- ED/IES Phase I and NIDILRR Phase I awards in hand (if granted; if not, regroup).

**Q4 (months 10–12) — Decision quarter.**

- 20 paid institutions / pilots; ARR-equivalent ~$100–150K.
- Launch Pro tier (Layout Jig + state-to-PIAF + Monarch viewer) at $12K/yr. Convert 3 design partners.
- Publish Year-1 Impact Report.
- Submit NSF SBIR / IES Phase II using Phase I results.
- Begin the Mozilla-hybrid incorporation work (Foundation 501(c)(3) application + PBC Delaware filing).
- **Capital decision.** Three paths: (1) continue fiscally-sponsored through year 2 on grants alone; (2) incorporate the Mozilla hybrid and raise a $2–4M seed from Building Ventures / Brick & Mortar with Adaptation Ventures + Disability:IN co-investing; (3) consolidate as a UIUC research center with corporate consortium funding, defer the company question to year 3.

The 12-month plan is structured so that all three Q4 capital paths remain open through month 12. Optionality is the asset.

---

## XIV. The 90-day kill test (before any incorporation)

The pre-mortem agent named this and it deserves its own section because it is the cheapest, fastest, most honest test of whether the venture should exist.

**Within 90 days of public outreach, secure five paid pilots at $10K+ each — actual purchase orders, not letters of support — with five distinct DRES offices or schools for the blind.**

If you can close five paid pilots in 90 days with a charismatic blind co-founder, an existing working prototype, IES grant credibility, and UIUC institutional backing — that's the proof the TAM and the GTM both exist. Founders, prospective hires, and board candidates can all watch this run before anyone signs anything.

If you cannot close five paid pilots in 90 days with all of those advantages, you will not close fifty in year two for Series A. Fold the work back into UIUC as a research program, transfer the IP to APH for the Monarch content engine, publish everything, and walk away with dignity. The dignified non-start is a real option and is better than the four-year founder burnout that the optimism scenario hides.

This kill criterion belongs at the top of the 12-month plan, before any of it. If month 3 fails this test, the rest of the plan is theater.

---

## XV. The pitch — three versions

**The pitch for an investor (90 seconds, by phone).**

> Architecture software was built for people who could see. When a blind student enrolled in our program, every CAD tool, every drawing review, every studio crit was inaccessible. So we built the opposite: a text-first design platform where the model is a JSON file, every command produces a single-line confirmation, every change can be undone, and the output flows to a screen reader, a braille display, a swell-paper sheet, a 3D-printed model, a binaural walkthrough — interchangeably. Building for a blind designer forced us into the exact architecture an AI agent needs to operate a CAD tool. Semantic handles instead of coordinates. Deterministic mutations instead of GUI state. Auditable history instead of viewport context. We are the most AI-agent-ready CAD codebase in AEC. Our wedge is the tactile graphics pipeline for university disability offices and schools for the blind — a $200M institutional market with no entrenched software vendor. Our ceiling is the AI-native AEC design tool of the 2030s, the way Cursor became the AI-native IDE of the 2020s. Accessibility is our moat, not our market. We are organized as a Mozilla-style hybrid — a 501(c)(3) foundation owning a PBC subsidiary — to make mission protection structural rather than contractual. Our team is two UIUC architecture faculty, the blind graduate student we co-designed it with, a CTO from the Hypar/Forma diaspora, a working open-source codebase with 70+ MCP functions, an open CAD-MCP standard we just published with Anthropic, and twenty paid institutions before we incorporated.

**The pitch for the disability community (the email you send to a skeptical NFB community member).**

> You're right to be skeptical. Most accessibility products are built about disabled people, not with them. Plumb's co-founder Daniel Bein is a blind architect; he and the team built the tool together over three years at UIUC. The cap table is public. Daniel holds mission-class shares with 10× voting on accessibility regression, sale to a non-accessibility-aligned acquirer, or discontinuation of the free tier for blind users. Individual blind users will never pay. Institutions do. The roadmap is public. The schema is open under the Linux Foundation. If after trying it you still think we got it wrong, tell us where, on the record, and we'll publish the criticism alongside our response. We're not selling you a feeling. We're selling you a tool. We'd rather earn the endorsement than ask for it.

**The pitch for the founder team (the document you put in front of each other before signing anything).**

> We can do this honestly. The shape is a 24-month fiscally-sponsored project that earns its way into a Mozilla-style hybrid. The founder team is Daniel as paid co-founder with mission veto, a recruited CTO, a recruited Executive Director, John as Chief Architect of Inclusion, Hugh as Chief Research. The three founding commitments — blind-led governance with teeth, free forever for blind individuals, open core / open format / open exit — go into the certificate of incorporation, not the marketing site. The wedge is TACT and the Monarch content engine. The standards play is the CAD-MCP spec. The pedagogy thesis is the Foundation's load-bearing wall. The honest probabilistic forecast is ~13–15% mission-preserved success, ~25% Dancing-Dots ceiling, ~30% dignified shutdown, ~30% outright failure. We do not pretend the higher number. We design for the lower numbers. The 90-day kill test runs first. If we cannot close five paid pilots in 90 days, we publish the work and walk away with dignity. If we can, we incorporate.

---

## XVI. Open questions for John

What only you can decide. Not answerable from the repo, not answerable from this document.

1. **Founder commitment level.** Side project that benefits from a commercial layer, or a venture that warrants reshaping your faculty role? The 24-month fiscal sponsorship buys you 24 months to defer this. The answer at month 24 determines almost everything else.
2. **Daniel.** Are you willing to put him on the cap table at full co-founder equity (9% common + 2% mission-class) before incorporation, with named board seat and 10× voting on enumerated triggers? This is the disability-movement-politics floor.
3. **Hugh.** Co-founder of the PBC, president of the Foundation, both, neither?
4. **The name.** Is "Plumb" right? Other top candidates the brand agent surfaced were Semantic (best thesis name) and Bay (best community name). The Mozilla-precedent move is to keep "Radical Accessibility Project" as the Foundation / research arm and use a new name for the PBC.
5. **UIUC IP.** Standard faculty-startup license terms, or something more bespoke (the accessibility-conformance reversion covenant)?
6. **Capital appetite.** Bootstrap on grants and revenue (Dancing-Dots / ViewPlus / NV Access shape), or accept seed capital and chase the AI-native CAD ceiling? Both are reachable from the same codebase. The choice constrains hiring, board, and exit.
7. **Geographic posture.** Stay in Champaign-Urbana (cheap, talent thin, UIUC adjacency), open an SF/NYC node (expensive, talent rich, VC adjacency), or distributed (cheaper, harder culture)?
8. **The reframe.** Are you willing to lead externally with "AI-native CAD that happens to be the only accessible one" while internally protecting the original mission with the structural commitments? This is the move that opens the venture-scale ceiling and the move that risks community trust if done badly.
9. **The Institute.** Are you willing to commit 5–10 years of academic effort to writing the curriculum, the textbook, the certification mark, and the NAAB language? This is the most under-monetized intellectual asset you currently hold.
10. **The 90-day kill test.** Are you willing to commit, in writing, to walking away if you cannot close five paid pilots in 90 days?

---

## XVII. What to do this week

1. Read the ED/IES SBIR Phase I solicitation. Decide. June 29 deadline. The fiscal-sponsorship structure makes this submittable.
2. Call the UIUC Office of Technology Management. Begin the IP-assignment conversation with the accessibility-conformance reversion covenant on the table.
3. Have the Daniel conversation. Equity offer in writing — 9% common plus 2% mission-class supervoting plus named board seat plus paid contract under the fiscal sponsor. Get a signed letter of intent before anything public.
4. Identify a fiscal sponsor (Open Source Initiative, NTEN, or a UIUC-adjacent 501(c)(3) the IDEA Center at Cornell or the Center for Independent Living of Central Illinois could refer). Two-week setup.
5. **Publish the CAD-MCP spec v0.1.** Even a draft. Even rough. The narrative leadership of a forming category is a one-time prize.
6. Reach out to one peer at MIT Disability and Access Services or Perkins for a 30-minute conversation. Validate the $4,800 / $12K pricing.
7. Reach out to one architecture dean at a peer R1 (Cornell AAP, RISD, Pratt — Tehrani at Cooper for the killer call). Validate the $25K curriculum site-license.
8. Reach out to one APH staffer (suggest the Monarch Student Pilot Project lead). Open the channel.
9. Reach out to Anthropic's MCP / partner-hub team. The pitch is one sentence.
10. Begin the CTO search. Two weeks of outreach to the Hypar/Forma/Snaptrude diaspora and the CMU HCII alumni list.

---

## Appendix: the thirteen agents

This document synthesized output from thirteen parallel research agents. Each ran with web access, formed an independent view, and produced decision-grade notes ranging from 700 to 2,000 words. Their convergences and disagreements drove the recommendations above. Brief summaries, for the record:

1. **Founder archetype & team architecture.** Mapped 12 comparable founder patterns. Recommended Configuration C (technical CTO + accessibility-movement Executive Director + John as Chief Architect of Inclusion + Hugh UIUC-side + Daniel as paid co-founder with 9% common + 2% mission-class supervoting). Named five concrete advisors to recruit by name.
2. **Five-year product roadmap.** Recommended substrate-not-app shape: CLI core + hosted multi-tenant state + plugin marketplace. Year-by-year evolution with the killer 2028 AIA demo. Ten priority-ranked Year-1 engineering tasks.
3. **Brand, narrative, movement.** Proposed renaming the venture **Plumb** (keeping RAP as the research / pedagogy arm at UIUC). Patagonia × Linear brand archetype. Recommended the "Post-Visual Design" / "Inclusive Default" movement positioning. Identified the single Year-1 brand move: a live, on-stage demo of Daniel designing a building without a mouse or screen.
4. **Pre-mortem.** Five failure modes ranked. Two-year warning-sign dashboard. Honest probabilistic forecast (~7% venture-scale, ~25% Dancing-Dots, ~30% dignified shutdown, ~38% failure). The 90-day kill test before incorporating.
5. **Agent-infrastructure platform.** Recommended publishing CAD-MCP spec v0.1 and conformance benchmark within 30 days. The single highest-leverage near-term move.
6. **New-pedagogy thesis.** Recommended the Institute as load-bearing wall of the Mozilla-hybrid Foundation. RAP as the studio-pedagogy revolution and the AI-cheating solution. Named five most-likely curriculum first adopters (Cooper Union, MIT, SCI-Arc, Pratt, UIUC). Identified the 2027–2028 NAAB Conditions revision cycle as the window for writing the de facto standard.
7. **Disability movement politics.** Named the three non-negotiable founding commitments: blind-led governance with teeth, free forever for blind individuals, open core / open format / open exit. Mapped NFB, ACB, AFB, AAPD, DREDF politics. Stella Young red lines. The single most important Year-1 move: pre-incorporation equity for Daniel with public cap-table transparency.
8. **M&A game theory.** Recommended Autodesk acquisition at year 6, $200–300M, on $10–14M ARR. Standards-leadership as acquisition-resistance lever. Banked-process negotiation playbook with structural covenants.
9. **Adjacent creative disciplines.** Recommended GIS / cartography and scientific data sonification as Year-4 verticals. The "find a Daniel-equivalent per vertical" repeatable pattern. NASA Chandra's n=3,184 sonification study as empirical proof that "post-visual is better for everyone" generalizes.
10. **Multimodal / XR / spatial computing.** The buildable-in-12-months "One model, five senses" AIA 2028 demo. 18-month roadmap integrating Claude voice mode (already shipped March 2026), Steam Audio binaural walkthrough, Monarch and Dot Pad X tactile renderers, Ray-Ban Meta via Be My Eyes partnership, and Trimble SiteVision accessibility overlay.
11. **Hardware partner ecosystem.** Three Year-1 partners: APH (Monarch app + Federal Quota catalog listing — the anchor), Anthropic (Claude Partner Network MCP featured slot — zero cost, maximum credibility), Bambu Lab (informal MakerWorld profile family — consumer reach). Hardware-agnostic at the schema layer.
12. **Non-startup organizational alternatives.** Recommended the sequenced two-step: months 0–24 as a fiscally-sponsored open-source project; years 2–5 spin into Mozilla-style hybrid (501(c)(3) parent owning PBC subsidiary). Preserves academic incentives. Defers the startup question until adoption signal is real.
13. **Underground wildcards.** Three under-considered moves: traveling "famous buildings you can touch" exhibit ($1.5–2M over 18 months, Cooper Hewitt precedent); structured-negotiation remediation channel (Lainey Feingold–style cooperative compliance, $50–100M ARR ceiling, requires legal-domain hire); Champaign-Urbana accessibility architecture biennale ($5–8M year-one, breakeven year three, category-defining infrastructure that beats any product strategy on long timescales).

The agents disagreed about which path to lead with. The disagreement itself is the most important data in this document: there is no obviously right answer. There is only the answer the founders are equipped to execute. This synthesis recommends the path that preserves the most optionality, encodes the strongest structural mission protection, and matches who the founders actually are. Whether they take it is, properly, their decision.
