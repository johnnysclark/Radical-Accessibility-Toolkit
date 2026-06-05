# The Radical Accessibility Project as a Startup

A working strategy document. Not a pitch deck — the source material a pitch deck would be built from. Written for John, by an assistant that read the repo end-to-end and ran six parallel research agents (market sizing, competitive landscape, business models, GTM wedge, adjacent markets, regulatory tailwinds) before forming an opinion.

The agents disagreed on details but converged on one core claim: **RAP is not "accessibility software for blind architects." It is the first AEC tool whose architecture was forced into the shape that AI-native CAD will require by 2030 — and accessibility is the reason it got there first.** That reframe is the only one that supports a venture-scale business. Everything else here is the consequence.

---

## 1. The thesis in one paragraph

Architecture software was built on the assumption that the user can see. Every design decision downstream of that assumption — viewport-as-truth, mouse-driven manipulation, modal dialogs, undocumented intermediate state, ambient cursor context — is a constraint masquerading as a feature. When Daniel Bein could not use any of it, the project was forced to build the opposite: a JSON file as the canonical model, deterministic mutations with single-line confirmations, semantic addressing (`bay A`, not coordinates), an auditable undo stack, and any-modality IO. Those are not accessibility features. They are the exact properties an LLM agent needs to operate a CAD tool — semantic handles to address, deterministic outputs to verify, text to read, text to write. RAP, by accident of its constraint, is the most AI-agent-ready CAD codebase that currently exists. The startup is the company that productizes that architectural head start, with accessibility as the original wedge and the moat.

---

## 2. The market we'd actually be in

We ran the numbers across five segments. One is a non-market; one is a real-but-niche revenue floor; three are venture-scale ceilings.

| Segment | TAM | SAM (US) | RAP 5-yr SOM | Verdict |
|---|---|---|---|---|
| Blind designers (direct license) | ~$10M | ~$1M | <$500K | Non-market. Cause, not company. |
| Tactile graphics production (institutional) | ~$1.5B | $200–300M | $5–20M | Real floor. Bootstrap-viable. |
| AEC architectural software | $6B → $10–19B by 2032 | ~$1.5B | $50–150M | Long bet. Realistic if positioned as AI-native CAD. |
| AEC accessibility compliance (Section 508/ADA Title II) | ~$400M | ~$100M | $5–20M | Forced-buyer regulatory tailwind. |
| K-12 / publisher tactile content authoring | $4–5B textbook market, <1% accessible | ~$30M addressable | $10–30M | Adjacent license/API play. |

Two specific numbers worth holding in mind:

- **Daniel is a unicorn, not a market.** US architecture has 33,558 students in NAAB-accredited programs; blind/VI architecture students at any time are 20–80. A pure "tool for blind architects" priced at $5K/yr tops out at <$500K TAM. That is moral proof. It is not a business.
- **Adam (YC W25) raised $4.1M seed for text-to-CAD. Zoo.dev is Sequoia-backed. Cursor is $2B ARR at $50–60B valuation in three years.** The "text-first AI-native design tool" thesis is now venture-validated. The question is whether RAP's architectural head start translates before incumbents catch up.

The blind-designer market is the proof. The tactile-production market pays the bills. The AEC compliance market is the wedge into AEC firms. The AI-native CAD market is the ceiling.

---

## 3. The competitive landscape and the white space

Two years ago the right competitive frame was "nobody." That is no longer true. The frame in 2026 is **"three categories converging, none combined."**

**Category A — Text-first / AI-native CAD for sighted users.** Zoo.dev (Sequoia), Hypar 2.0 (text-to-BIM at AEC scale), Adam (YC W25, text-to-3D copilot), CADAM (open-source NL→OpenSCAD), MakeIt3D, Veras/EvolveLab (rendering, not authoring). All product/mechanical-CAD focused except Hypar. None have a tactile output path. None co-designed with disabled users.

**Category B — Accessible CAD research.** A11yShape (University of Michigan, ASSETS 2025) is the closest active analog — GPT-4o over OpenSCAD with hierarchical model navigation, participatory design with a blind co-author. Product-scale, no architecture, no tactile pipeline. Stanford's shapeCAD prototype, Quorum (Stefik, UNLV) for accessible programming. All research-stage.

**Category C — Tactile graphics hardware and content.** ViewPlus (Tiger embossers, IVEO), HumanWare/APH **Monarch** (the platform shift — multi-line braille + dynamic tactile graphics, v1.4 Feb 2026), BrailleBlaster (APH/open-source), TactileView, PIAF/Swell. All convert finished images. None take a design model as input.

**Category D — AEC compliance / code-checking.** UpCodes (800k AEC users, AI plan review June 2026, $11M codes), dodda.ai ADA Compliance Checker (Revit plugin), icheck CBC, Solibri. All check geometry against codes. None help a disabled designer author the geometry.

**The white space — and RAP's defensible position — is the intersection of all four:**

> **AEC-scale, model-as-canonical-state, AI-driven, with tactile output as a first-class render target, co-designed with a blind architect.**

Nobody combines these. A sighted competitor can copy the text interface in a quarter. They cannot fake the multi-year design language built with Daniel, the tactile pipeline, the round-trip from PIAF/Monarch back into the semantic model, or the procurement legitimacy that comes from a blind architect being the named co-designer.

**The most likely competitor vector:** Zoo.dev or Hypar ships a screen-reader mode and a JSON export. Probability: high within 18 months. Defense: own the tactile/physical loop and the AEC-compliance-by-construction story before that lands.

**The most likely acquirer / partner:** APH or HumanWare for the Monarch content engine (license `tact render` as their tactile-design pipeline). UpCodes for the audit pivot (RAP's semantic state is machine-checkable by construction, which their geometry-first checkers are not).

---

## 4. The wedge: ship TACT first, not the Layout Jig

Out of everything RAP does, the smallest, sharpest v1 SKU is **TACT — the image-and-state-to-tactile-PDF pipeline**. Not the whole Layout Jig. Not the MCP stack. Not voice control.

Why TACT and not the Layout Jig:

1. **TACT solves a daily-pain problem with money already allocated.** Every R1 university DRES office and every school for the blind has an alt-media coordinator or TVI who currently hand-traces architectural diagrams in TactileView at 30–90 minutes per figure. They have backlog. They have an SLA they miss. They have a PIAF machine ($2–3K, already installed). TACT collapses 60 minutes of human labor into 30 seconds.
2. **TACT requires zero behavior change from the buyer.** No Rhino, no CAD literacy, no studio adoption. A staffer drags in a PDF and gets a tactile-ready file back.
3. **TACT has no entrenched competitor.** TactileView ships a drawing app; nobody ships an automated converter with OCR + RainbowTact patterns + Grade 2 Braille + density management. APH consulting is the closest substitute and it's a service, not a tool.
4. **TACT is the camel's nose for the Layout Jig.** Once the alt-media coordinator depends on TACT for image conversion, the architecture school's accessibility lead (an entirely different cost center, often the dean's office) becomes warm for the Layout Jig at a higher price point in year 2.

**Pricing:** $4,800/yr site license, unlimited seats, unlimited conversions. **This number is engineered.** It sits below the ~$5K discretionary-approval ceiling at most R1 DRES offices, which means it skips the procurement process and lands on a P-card. That's the magic number for fast higher-ed accessibility sales.

**Add-on:** $12K/yr Pro tier unlocking `tact render state.json` and the Layout Jig CLI/MCP for studio integration. Sell once they're hooked.

---

## 5. The first 10 customers, by name

The list the founders should already have a spreadsheet for, with named human contacts at each:

1. **UIUC DRES** — home turf, Daniel is the user, John is faculty. Free pilot → paid renewal in year 2 from a different cost center.
2. **Illinois School for the Visually Impaired (Jacksonville, IL)** — in-state credibility, NLS-adjacent.
3. **Perkins School for the Blind (Watertown, MA)** — runs the Perkins Tactile Graphics Library. The credibility anchor in the K-12 blind-ed market. If Perkins references you, every state school listens.
4. **California School for the Blind (Fremont)** — largest state school, CDE budget.
5. **Texas School for the Blind and Visually Impaired (Austin)** — large transcription staff, federal pass-through funding.
6. **MIT Disability and Access Services** — peer R1, STEM-heavy diagram load, halo effect.
7. **Stanford OAE / SAE** — peer R1, design-school adjacency (d.school).
8. **Gallaudet TIP/IDEA program (deafblind track)** — wedge into deafblind, differentiates from competitors who can't serve this population.
9. **APH (American Printing House)** — *not a customer, a channel.* License TACT as a backend for their TactileView pipeline. APH controls the federal quota program (~$38M/yr in materials distribution).
10. **RNIB UK** — international beachhead. Centralized procurement, real budget line, CSUN/AAATE relationships, opens EMEA.

**Tier-2 in the same 12 months:** Lighthouse Guild (NYC), San Francisco LightHouse, Carroll Center (MA), CNIB (Canada), Vision Australia, Cooper Union, Pratt, Cornell AAP, Big Ten Academic Alliance accessibility working group (14 peer R1s simultaneously).

**Who NOT to sell to in year 1:**

- **Blind individuals directly.** Market too small. Willingness-to-pay near zero (correctly — people don't pay to access their own profession). Optically fraught.
- **AEC firms (SOM, Gensler, HOK).** No budget line. Long bespoke cycles. Wait until year 3+ when there's a Revit plugin with a compliance hook.
- **State VR agencies (year 1).** Listing on Cal-ATSD, TX TWC, GA GVRA is year-2 work; the application process takes 6–9 months and you need a VPAT and a price book first.

---

## 6. The business model: open-core SaaS on grant-funded R&D rails

The honest reading of the five business model archetypes we considered:

**Primary: vertical SaaS for AEC accessibility (Path 2 from the strategy analysis).** Free CLI/MCP open source for individuals and academics. Paid hosted/managed/SLA'd version for institutions. Paid Revit/Rhino plugin for AEC firms as the year-3 expansion. $4,800/yr DRES tier → $12K/yr Pro tier → $30–200K ACV firm tier. Comparable cost structure to vertical SaaS (75–85% gross margin). VC-backable seed if the founders want that path.

**Wedge: EdTech to architecture schools and DRES (Path 3).** $15–50K/yr site licenses, sold via Big Ten accessibility working group and ACSA. Lower ceiling ($2–5M ARR — there are ~150 NAAB-accredited US programs) but matches founder distribution exactly. This is what de-risks Path 2.

**Capital structure: non-dilutive grants for R&D, contracts for cashflow, optional seed when ready.** This is the **ViewPlus playbook** — founded 1996, first SBIR 2003, then 15 SBIR awards (9 Phase I + 6 Phase II) built Tiger and IVEO into a commercial product. The model exists. It works. It produces a profitable $20–60M company, not a $1B exit, but it preserves the mission.

**What we ruled out:**

- **Pure tactile graphics service bureau.** Real demand (Touch Graphics has been at it for 20+ years sub-$10M), but service businesses don't compound and hiring tactile illustrators is the bottleneck. RAP's IP becomes incidental. Use as a fallback only.
- **Cursor-for-CAD direct play (Path 4).** The architecture is right, the timing is right, the comps are real ($2B ARR Cursor at $50–60B). **But this is a founder-mismatch trap for academic founders.** The path requires a YC-grade hacker CTO and a venture-experienced CEO, and abandoning accessibility as the lead story risks both mission drift and a head-on collision with $100M-funded competitors. Pursue only if an A-grade technical co-founder appears unsolicited. **Posture as the long-term reframe, not the v1.**
- **Hardware / "The Desk" bundle (Path 5).** Hardware ops are brutal. Tactile Inc and Graphiti killed multiple startups in adjacent categories. Stay software-only, hardware-agnostic, integrate with everyone — including OEM partnerships with APH (Monarch) and ViewPlus (IVEO).
- **Pure non-profit / foundation.** Lower ceiling than the open-core SaaS. Right shape if the mission is the only goal — wrong shape if a $50M outcome is possible.

---

## 7. The five-year shape

```
Year 1 — TACT as wedge SKU
  Q1: incorporate, productize, 3 free pilots, NIDILRR + IES SBIR Phase I submissions
  Q2: CSUN 2027 booth, ASSETS + ACADIA papers, 2 of 3 pilots paid
  Q3: sales engineer hire, GSA Schedule path, APH partnership conversation
  Q4: 20 paid institutions ($96–120K ARR), Pro tier launch, raise decision
  ARR: $100–250K   Non-dilutive grants: $400K–$1M

Year 2 — Layout Jig site licenses + state VR channel
  20 → 70 paid institutions. Layout Jig + MCP at $12K/yr.
  State VR vendor listings (CA, NY, IL, TX, MA) for per-seat purchases.
  SBIR Phase II ($1–1.7M). APH partnership signs (TactileView/Monarch backend).
  ARR: $750K–$1.5M

Year 3 — Revit/Rhino compliance plugin (AEC firms)
  Forced-buyer regulatory tailwind: Title II compliance deadline (April 2027/2028 in US),
  EAA enforcement biting in EU. Plugin tier $30–200K ACV.
  ARR: $3–6M

Year 4 — Reframe externally as AI-native CAD
  Same product, different lede. "The CAD tool an AI agent can drive natively —
  because it was built for designers who couldn't see the screen."
  Open the Layout Jig MCP as a third-party platform.
  ARR: $8–15M

Year 5 — Acquisition window or Series A
  Acquirer set: Autodesk, Nemetschek, Bentley, Trimble (vertical SaaS roll-up),
  or APH/Vispero (assistive-tech consolidation), or PE roll-up (Bluebeam pattern).
  Realistic exit: $50–250M at $10M ARR. Or raise A and bet on the Cursor-for-CAD ceiling.
  ARR: $15–30M
```

This is the open-core SaaS shape with grant rails — explicitly **not** the Cursor-for-CAD shape, which would be `Year 1 raise $5M seed, Year 3 raise $30M A, Year 5 either $1B+ or zero`. Both shapes start from the same codebase. The founder team determines which one is reachable.

---

## 8. The tailwinds — regulatory, funding, institutional

**Immediate forcing functions (next 90 days):**

- **ED/IES SBIR — deadline June 29, 2026.** Up to $1.25M total ($250K Phase IA/IB → $1M Phase II). Explicit Special Education Tech track. RAP fits cleanly: tactile/braille STEM tooling for blind students. **High likelihood of award.** This is the single most actionable funding deadline on the horizon. Source: [ies.ed.gov](https://ies.ed.gov/funding/research/programs/small-business-innovation-research-sbir/solicitation-information).
- **Microsoft AI for Accessibility — January 13, 2026 next deadline reported.** Equity-free Azure credits plus cash. Apply concurrent with IES.
- **NIDILRR SBIR.** Phase I ~$100K / 6 mo, Phase II up to $575K / 24 mo. Search Grants.gov for "BISA" / "BISB." Annual competition. ViewPlus walked this path 15 times.

**Medium-term policy tailwinds (12–24 months):**

- **DOJ Title II Web/Mobile Rule.** April 2024 rule required state/local governments (including public universities and planning departments) to make ICT WCAG 2.1 AA compliant. **April 2026 Interim Final Rule extended the compliance dates to April 2027 (large jurisdictions) and April 2028 (small).** Real risk: same IFR signaled potential substantive changes via NPRM. Mitigation: do not bet the business on federal enforcement; build for EU + state-level demand which is durable regardless. Sources: [federalregister.gov](https://www.federalregister.gov/documents/2026/04/20/2026-07663/extension-of-compliance-dates-for-nondiscrimination-on-the-basis-of-disability-accessibility-of-web), [ada.gov](https://www.ada.gov/resources/2024-03-08-web-rule/).
- **European Accessibility Act — enforcing since June 28, 2025.** Penalties up to €3M. Covers ICT including design tooling sold into EU public sectors. Nordic, German, Dutch markets will enforce first. RAP can sell into EU architecture schools and public planning departments under EAA pressure regardless of US politics.
- **NAAB 2020 Conditions for Accreditation (rev. March 2026).** Architecture programs must teach accessibility. RAP is curriculum infrastructure for that requirement, not a charity ask. Distribute via ACSA (Association of Collegiate Schools of Architecture).
- **NCARB disability-in-licensure report (2024).** Profession is opening a conversation about ARE accommodations and architect licensure for disabled candidates. RAP rides the same wave.

**Capital tailwinds specific to disability tech:**

- **2Gether-International.** Disability-founder accelerator. Portfolio includes XR Navigation (digital maps for blind users). Mentorship + Google for Startups support. Direct fit.
- **Enable Ventures.** Disability-tech VC. Specific 2026 fund size not confirmed but partnered with 2GI.
- **Ford + Mellon Disability Futures Fellows.** $50K individual fellowships, architecture eligible.
- **AIA Upjohn Research Initiative** ($15–30K) and **Latrobe Prize** ($150K biennial). Small but high-prestige.

**Posture across all of this:** non-dilutive grants fund the R&D, VR contracts + university site licenses fund the burn, EU and state-level deals hedge against US federal regression, and seed/Series A happen only after SBIR Phase II is awarded and 3+ VR contracts are signed.

---

## 9. The risks, named

**Founder-fit risk (highest).** Path 2 (vertical SaaS) requires hiring a head of sales by year 2 and an enterprise CTO by year 3. Academic founders typically lack both. Mitigation: bring on Daniel as paid co-founder/equity (not advisor), recruit an ex-Vispero or ex-Autodesk-vertical-SaaS operator as employee #4.

**Mission drift risk.** Every business model option except service bureau requires expanding beyond blind architects. The risk is that AEC enterprise revenue or AI-CAD pivots pull resources away from Daniel-style users, and the original mission rots. Mitigation: tithe — minimum 20% of engineering effort permanently allocated to accessibility features, regardless of revenue mix. State this in the corporate documents.

**Incumbent competitive risk.** Zoo.dev or Hypar ships a screen-reader mode within 12–18 months and competes for the text-CAD-with-AI story. Mitigation: own the tactile/physical loop (which they will not build) and the AEC-compliance-by-construction angle (which UpCodes will not build). Defend the moat that is hardest to copy: lived-experience design language + co-designed legitimacy + tactile pipeline.

**Federal regulatory rollback risk.** April 2026 IFR signal is real; an administration hostile to accessibility enforcement is a non-zero scenario. Mitigation already named: EU + state-level + private-sector demand do not vanish with federal regression.

**Daniel-as-prop risk.** The blindness community will torpedo a sighted-founder accessibility company on a listserv in 48 hours if they smell tokenism. Mitigation: Daniel is a paid co-founder or equity partner with named role and decision authority. Co-author the ASSETS paper. Co-present at NFB National Convention. Pay him.

**IP assignment risk.** UIUC owns the work product unless explicitly assigned. The faculty-startup IP process at Illinois is well-trodden but takes 4–8 months. Start it now if there's any seriousness to the venture.

**The Dancing Dots ceiling.** The honest contrarian read is that RAP becomes the architecture equivalent of Dancing Dots / Lime Lighter — 25 years of profitable, beloved niche software, NFB endorsement, $2–10M ARR, no VC pressure, mission preserved. This is a great outcome. It is also a cap. Founders should decide which they want: the beloved niche floor or the AI-native CAD ceiling. The codebase supports both; the team and the cap table determine which is reachable.

---

## 10. The 12-month plan

**Q1 (months 1–3) — Productize**

- Incorporate (Delaware C-corp). Start UIUC IP assignment process.
- Bring Daniel on as paid co-founder or equity-holding advisor with named role.
- Ship hosted TACT (web upload + API + CLI). Produce VPAT. Write FERPA + data-handling one-pager.
- Land 3 free design-partner pilots: UIUC DRES, Illinois School for the Visually Impaired, Perkins.
- Submit **ED/IES SBIR Phase I before June 29, 2026.** Submit Microsoft AI for Accessibility (Jan 13 deadline if not missed). Submit NIDILRR SBIR cycle.

**Q2 (months 4–6) — Conference circuit + first paid contracts**

- CSUN 2027 booth (new-exhibitor discount, ~$3–5K). Co-present with Daniel.
- Submit ASSETS 2027 paper and ACADIA 2027 paper in parallel.
- Convert 2 of 3 pilots to paid ($4.8K each).
- Cold-outbound to 30 top R1 DRES offices + 15 schools for the blind, warm-introduced via Big Ten Academic Alliance.
- Apply to 2Gether-International accelerator.

**Q3 (months 7–9) — Repeatable motion**

- Hire one part-time sales engineer (ex-DRES staffer with assistive-tech background — they exist, they're cheap, and they speak the buyer's language).
- File Section 508 VPAT.
- Begin GSA Schedule path via reseller partner (12-month timeline).
- 8 paid institutions closed.
- APH partnership conversation: license TACT as TactileView/Monarch backend, revenue share.

**Q4 (months 10–12) — Expand and decide**

- 20 paid institutions ($96–120K ARR).
- Launch Pro tier (Layout Jig + state-to-PIAF) at $12K/yr. Convert 3 design-partners.
- Publish Year 1 Impact Report: diagrams produced, hours saved per coordinator, named customer quotes.
- Submit NSF SBIR Phase II (using IES Phase I results) — up to $1.7M / 24 mo.
- **Capital decision:** bootstrap to profitability on grants + ARR (Dancing Dots path), or raise $1.5–2M seed from Enable Ventures / 2GI alumni / disability-friendly LPs (vertical SaaS path).

---

## 11. The pitch, one page

This is the pitch the founders should be able to deliver in 90 seconds, on a phone, to a peer architect or a disability-tech investor.

> Architecture software was built for people who can see. When a blind student enrolled in our program, every CAD tool, every drawing review, every studio crit was inaccessible. So we built the opposite: a text-first design platform where the model is a JSON file, every command produces a single-line confirmation, every change can be undone, and the output flows to a screen reader, a braille display, a PIAF swell sheet, or a 3D-printed tactile model — interchangeably.
>
> The surprising part: building for a blind designer forced us into the exact software architecture that AI agents need to operate a CAD tool. Semantic handles instead of coordinates. Deterministic mutations instead of GUI state. Auditable history instead of viewport context. We are, by accident of constraint, the most AI-agent-ready CAD codebase in AEC.
>
> Our wedge is tactile graphics production for university disability offices and schools for the blind — a $200M institutional market, urgent pain, no entrenched software vendor. Our ceiling is the AI-native AEC design tool of the 2030s, the way Cursor became the AI-native IDE of the 2020s.
>
> Accessibility is our moat, not our market. We are funded today by ED/IES and NIDILRR SBIR grants; our revenue customers are R1 university DRES offices at $4,800/yr, expanding to architecture schools at $12K/yr and AEC firms at $30–200K/yr. ADA Title II, Section 508, and the European Accessibility Act mean our buyers are legally required to procure what we sell.
>
> The team is two UIUC architecture faculty, the blind graduate student we built it with, a working open-source codebase with 58 MCP functions, and a 12-month plan to twenty paid institutions and an SBIR Phase II.

---

## 12. Open questions for John

Before this becomes a real venture, these are the calls only the founders can make. They are not answerable from the repo.

1. **Founder commitment.** Is this a side project that benefits from a commercial layer, or a venture that warrants leaving (or reshaping) faculty roles? The answer determines almost everything else.
2. **Daniel's role.** Co-founder with equity? Advisor with equity? Paid contractor? The blindness community will read this directly from the cap table.
3. **Hugh's role.** Co-founder? Board? Academic partner?
4. **UIUC IP.** What's the assignment posture — clean spinout under faculty-startup terms, or licensed back from UIUC?
5. **Capital appetite.** Bootstrap on grants and revenue (Dancing Dots / ViewPlus shape), or raise venture and chase the AI-CAD ceiling? Both are defensible from the same codebase. The choice constrains hiring, board, mission protection, and exit options.
6. **Geographic posture.** Stay in Champaign-Urbana (cheap, talent thin, UIUC adjacency), or open an SF/NYC node (expensive, talent rich, VC adjacency)?
7. **Mission protection.** Are you willing to write into the corporate documents a permanent commitment to accessibility R&D (e.g., 20% engineering tithe regardless of revenue mix)? This is what prevents drift in years 4–7 and what makes the disability community trust the venture.
8. **The reframe.** Are you willing to lead externally with "AI-native CAD that happens to be the only accessible one" while internally protecting the original mission? This is the move that opens the venture-scale ceiling, but it is the move that risks the existing community's trust if done badly.

---

## 13. What to do this week

Not next quarter. This week.

- Read the ED/IES SBIR Phase I solicitation. June 29 deadline. Decide whether to submit.
- Call the UIUC Office of Technology Management. Start the IP assignment conversation.
- Have the Daniel conversation. Equity offer in writing.
- Reach out to one peer at MIT DAS or Perkins for a 30-minute conversation about what they'd pay for an automated image-to-tactile pipeline. Validate the $4,800 number.
- Reach out to one architecture dean at a peer R1 (Cornell AAP, RISD, Pratt) and ask whether they'd license the Layout Jig for studio accessibility at $15K/yr. Validate.
- File a placeholder Delaware C-corp or LLC. $300, an afternoon. Don't capitalize it yet. Just reserve the entity.
- Read three of the agent reports linked above end to end. Form your own opinion. This document is a synthesis, not a verdict.

---

## Appendix: the agents we ran

Six parallel research agents fed this synthesis. Each ran with web access and produced its own decision-grade notes. Their full reports are not in this document but are available on request. Their summaries:

1. **Market sizing & customer segments.** Confirmed that blind-only TAM is too small (<$10M) for venture, that tactile graphics is real ($1.5B global / $200–300M US institutional), and that the AI-native CAD reframe is the only path to a $50M+ company. Cited NAAB enrollment, Revit/Rhino pricing, NLS contract sizes, NIDILRR SBIR ceilings, and Adam/Zoo.dev funding rounds.
2. **Competitive landscape.** Mapped Zoo.dev, Hypar, Adam, CADAM, A11yShape, Quorum, ViewPlus, APH Monarch, BrailleBlaster, TactileView, UpCodes, dodda.ai, icheck, Fable, 2Gether-International. Concluded the defensible white space is AEC-scale text-CAD + tactile output as first-class + co-designed-with-blind-architect provenance. Flagged that Zoo or Hypar shipping a screen-reader mode is the biggest threat.
3. **Business model options.** Compared five archetypes (service bureau, vertical SaaS, EdTech, Cursor-for-CAD, hardware bundle). Recommended vertical SaaS for AEC accessibility (Path 2) primary, EdTech (Path 3) as the wedge, with the AI-native-CAD reframe held as a year-4 option contingent on technical co-founder hire.
4. **GTM wedge strategy.** Recommended TACT as the v1 SKU, $4,800/yr site license below DRES discretionary threshold, beachhead = alt-media coordinators at R1 DRES + schools for the blind. Named 10 specific first customers. Mapped a quarter-by-quarter 12-month plan that ends in 20 paid institutions and an SBIR Phase II submission.
5. **Adjacent markets and generalization.** Ranked disability adjacencies (low-vision biggest, aging architects underrated), discipline adjacencies (landscape + planning + GIS yes, MechE / electrical / fashion no), and steelmanned the contrarian "Dancing Dots ceiling" case. Concluded that the AI-native CAD reframe is the venture-scale path but requires a different founder team.
6. **Regulatory & funding tailwinds.** Identified ED/IES SBIR (June 29, 2026 deadline), NIDILRR SBIR, NSF AccessComputing distribution, EU Accessibility Act (enforcing June 2025), state VR procurement channels, and the ViewPlus 15-SBIR template. Flagged federal regulatory rollback risk and recommended hedging via EU + state-level demand.

The agents disagreed about which path to lead with (one wanted AI-native CAD direct; one wanted Dancing Dots niche; the rest wanted the vertical SaaS path that's recommended above). The disagreement is the most important data point in this document: there is no obviously right answer. There is only the answer the founders are equipped to execute.
