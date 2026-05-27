# IDEAS — NEH DHAG Brainstorm

Working notes for the proposal. Not a draft. Captures framing decisions, scope hypotheses, risks, and the open questions the team needs to answer before drafting prose.

## Why DHAG, why now

DHAG funds digital humanities projects that contribute critical infrastructure for scholarly research, teaching, and public programming in the humanities. The Radical Accessibility Project sits at this hinge in three concrete ways:

1. **Architecture as a humanities discipline.** Architecture is studied historically, theoretically, and culturally as much as it is practiced technically. Its pedagogy — design studio, pin-up critique, hand-drafting traditions, the typology of the architectural drawing itself — is a humanities tradition. The ACADIA 2026 paper's Section 3.2 (Hamraie 2017, Boys 2014, the DisOrdinary Architecture Project, Schön 1987) names this lineage. The proposal makes the case that the discipline's ocularcentrism is a humanities problem and not just an engineering one.

2. **Digital humanities methodology as accessibility infrastructure.** The Accessibility Harness is a configuration pattern, not a tool. Its primitives — a sense-agnostic JSON state, multiple renderers, LLM-mediated authoring, auditable logs — are characteristically DH primitives. We are not proposing a single accessible CAD product; we are proposing a methodological move (canonical textual state + parallel renderers + LLM scaffolding) that any humanities discipline confronting an ocularcentric tool stack could adopt.

3. **Accessibility as explicit DHAG priority.** Recent DHAG guidance foregrounds accessibility and usability as evaluation criteria, and reviewers are explicitly directed to favor teams that include members of target audiences. Daniel Bein is co-designer, not test subject. This is the unusual structural alignment we should make impossible to miss in the Overview and Significance sections.

## What shifts from ACADIA voice to NEH voice

The ACADIA paper's voice is already much closer to NEH than the Anthropic pitch was. Shifts to make:

- **From "we built" to "the field needs and we contribute."** ACADIA narrative is comfortable describing the artifact in the first person. NEH narrative should foreground the field-level problem and position the project as a contribution to digital humanities infrastructure.
- **From "candidate hypotheses" framing to "Tier II will test."** The paper's Section 5 honestly labels its claims as candidate hypotheses drawn from a single case. That humility is correct, and we keep it. But the proposal must pair each candidate hypothesis with a concrete Tier II activity that begins to test it.
- **From single venue (ACADIA conference) to multi-channel dissemination.** ACADIA is one publication; the NEH proposal must describe open-source code release, standards documentation, a studio-adoption guide, talks/workshops at DH venues, and partner-institution pilots.
- **Drop competitive/vendor framing entirely.** The Anthropic pitch's "deepest deployment" and "only viable platform" framing must not enter the NEH narrative. The methodology is substrate-agnostic; we use Claude because of MCP and Claude Code's harness pattern, but the *pattern* (Section 4.5 of the ACADIA paper) is what the proposal contributes.
- **Foreground student training.** NEH cares about humanities pedagogy and the training of future scholars. The undergraduate and graduate research assistants are not just labor; they are humanities-students-being-trained-in-DH-methods. Name them and their contributions in the Staff section.

## Tier II scope hypothesis (working draft)

A two-to-three year Tier II project at the $75K–$150K level should plausibly cover:

1. **Refine the Harness for a second and third BLV student.** The single-case basis is the principal weakness of the current evidence. The first year adds two additional BLV student users — at UIUC and at one partner architecture school — and documents what about the configuration carries over and what required adaptation.
2. **Formalize the in-house tactile-graphic standards.** Internal standards already govern the PIAF and 3D-print outputs. Formalize them as a public specification with worked examples (Macro/Meso/Micro alt-text, raised-line conventions, scale and abbreviation conventions, Braille labeling rules).
3. **Open-source the code.** The ACADIA paper commits to release on acceptance under an open-source license. The Tier II project budgets the technical-debt cleanup, documentation, packaging, and continuous-integration work that a credible release requires.
4. **Studio-adoption guide.** A short publication aimed at architecture faculty at other institutions: how to set up The Desk, how to onboard a BLV student to the Harness, what to expect, what we got wrong the first time. This is the public-humanities deliverable.
5. **Structured evaluation.** Studio observation, structured interviews with the BLV students and their sighted peers and faculty, and a published reflection. Not a controlled study — the population is too small and the context too rich — but a rigorous qualitative documentation of transferability.
6. **Dissemination across DH and architecture venues.** ACADIA, ASSETS, a DH-venue talk (DH conference, ODH-sponsored workshop), and a journal-length write-up.

This list is the input to the Work Plan. Budget categories follow from it: stipends for the BLV students and the research assistants, travel for partner-site visits and conference presentations, materials and supplies for tactile media at the partner site, publication costs, modest software/hosting for the open-source release, indirect costs per UIUC's federally negotiated rate.

## Risks and known weaknesses

To name in the proposal rather than hide:

- **Single-case evidence base.** Mitigated by the Tier II activity to add two additional BLV students. NEH reviewers respect honest naming of evidence limits; the alternative (overclaiming generalizability from one student) reads worse.
- **LLM vendor dependence.** The current Harness is built around Claude (via Claude Code and MCP). Mitigation: the *pattern* — canonical textual state, parallel renderers, LLM-mediated authoring, auditable logs — is substrate-agnostic; an MCP-compatible alternative model would slot in without restructuring. Name this explicitly in Significance.
- **Tactile-graphic standardization tension.** Standardizing house standards into public ones risks ossifying what currently works. Mitigation: release as a specification with worked examples and explicit "open questions" sections, not as a fixed standard.
- **Studio-culture dependence.** The Harness works partly because the UIUC studio around Daniel has co-developed habits of multi-modal critique. Transferring the technical system to a partner site without the cultural scaffolding may underperform. Mitigation: the studio-adoption guide treats the cultural scaffolding as a first-class deliverable, not an afterthought.
- **Sustainability beyond the grant.** What happens to the open-source release, the standards, and the partner-site pilots after Tier II funding ends? Mitigation: name a sustainability plan in the Work Plan — institutional commitment from UIUC's School of Architecture, GitHub-based community maintenance, optional Tier III follow-on.

## Open questions for the team

Numbered so we can address them before drafting prose.

1. **Project director.** Who is the PI of record on the proposal — John Clark, Hugh Swiatek, or a co-PI arrangement? UIUC's Office of Sponsored Programs may have an opinion.
2. **Partner institution(s).** Who are the partner architecture schools where we plan to add the additional BLV student users? Letters of commitment from each will be required. Do we have informal commitments yet, and from whom?
3. **Daniel Bein's role on the grant.** Co-PI? Compensated co-designer? Consultant? Research subject? The first three are the right framings; the fourth is wrong. The choice affects budget, letters, and the Staff section.
4. **Cycle target.** January 2027 or May 2027 deadline? Project start date constraints follow from this (DHAG specifies the start-date window for each cycle).
5. **Budget ceiling within Tier II.** Closer to $75K (lean) or $150K (full)? Drives every staffing decision.
6. **Indirect cost rate.** UIUC's federally negotiated indirect rate applies; what is the current rate, and how does it interact with the $150K Tier II ceiling? (The ceiling is total cost including indirect.)
7. **Existing IRB / accessibility-research approvals.** Studio observation and structured interviews with BLV students require human-subjects approval. Does the current ACADIA-paper work already have IRB coverage, and does that coverage extend to the proposed Tier II activities?
8. **Open-source license choice.** MIT, Apache 2.0, or GPL? The ACADIA paper commits to "open-source" without specifying. The choice matters for the Data Management Plan and the dissemination section.
9. **Tactile-standards co-development partners.** Are there accessibility-standards organizations (e.g., a tactile-graphics consortium, an architecture accessibility working group) we should propose to co-develop the formalized standards with? Naming a partner here strengthens the Significance section.
10. **Anthropic relationship in the NEH narrative.** The Anthropic pitch package is a parallel funding ask. How (if at all) do we mention Anthropic in the NEH narrative? Recommended: a brief mention as a technology provider used under standard commercial terms, with the methodology framed as substrate-agnostic.
