# SOURCES — Where to pull from when drafting

Index of source material we can mine when drafting the NEH narrative and supporting documents. Organized by intended use rather than by file location.

## Tier 1: Canonical source

### ACADIA 2026 paper

- **Path:** `docs/grants/neh-dhag/source-material/ACADIA_2026_paper.md`
- **Authoritative as of:** 2026-05-27 (user-uploaded docx).
- **Use for:** abstract claims, the "two gaps" environmental scan, the five constitutive properties, the four candidate implications for studio practice, the figure inventory, the references list.
- **Carries over verbatim or near-verbatim:**
  - Section 1 Introduction (paragraphs 1–3) — direct material for the NEH **Overview** and **Significance** sections.
  - Section 3 *Two Gaps in the Literature* — directly becomes the NEH **Environmental Scan** with light reframing.
  - Section 4.5 *The Five Constitutive Properties* — anchors the **Work Plan**'s "what we are refining" articulation.
  - Section 5 *Implications for Adaptive Studio Practice* — feeds the **Significance and Impact** and **Final Products and Dissemination** sections.
- **Needs reframing for NEH:**
  - The "this research is a work in progress" framing is appropriate for ACADIA but should be sharpened in NEH voice to "DHAG Tier II will move this from a single-case prototype to an evaluated and disseminated pattern."
  - Single-case humility language stays — NEH reviewers value methodological honesty — but pair it with a concrete Tier II work plan that addresses the gap.

## Tier 2: Project documentation already on `master`

### `README.md` (repo root)
- Use for: project overview boilerplate, tool inventory, current capability claims.

### `docs/MANUAL.md`
- Use for: technical specifics in the **Work Plan** — what the controller, watcher, and channels actually are; how the tactile pipeline runs end-to-end.

### `docs/MCP_GUIDE.md`
- Use for: AI integration architecture in the **Work Plan** — the MCP function inventory, the channel-server design, how Claude Code is wrapped.

### `docs/ACADIA_PAPER_EXAMPLE_V1.md` … `V6.md` and `docs/ACADIA_PAPER_OUTLINES.md`
- Use for: alternate framings of the same arguments. Prior drafts sometimes contain a sentence that lands better than the published version. Mine selectively; the canonical text is `source-material/ACADIA_2026_paper.md`.

### `docs/ACADIA_BRAINSTORM_REARRANGED.md` and `docs/ACADIA_PAPER_IDEAS_V1.md`
- Use for: unfiltered claim inventory. When a section needs an angle the current paper underplays, check here first.

### `docs/references/ArchAltText.md`, `docs/references/ArchitecturalContext.md`
- Use for: Macro/Meso/Micro alt-text methodology — the linguistic-renderer story in the **Work Plan** and as a **dissemination** product.

### `docs/WORKING_DOCUMENT_Summer2025.md`
- Use for: historical timeline / prior work in the **History and Duration** section.

## Tier 3: Anthropic pitch package (raw-read only, do not import)

The Anthropic pitch lives on branch `claude/charming-dijkstra-80gsc`. We are not merging from it; we read individual files via raw GitHub URLs.

Base URL: `https://raw.githubusercontent.com/johnnysclark/Radical-Accessibility-Toolkit/d75eabf9ec8f3ea31fbe388b1236abfcba7b5d04/docs/pitch/`

### `BUDGET.md`
- **Use for:** budget *structure* — stipend categories, UIUC-cost-share assumptions (equipment, fabrication, lab covered by UIUC and excluded from the ask), travel categories.
- **Reframe:** drop the "API credits" line entirely (NEH does not fund commercial software subscriptions in this form). Translate stipend categories into NEH-allowable cost categories (salaries/wages, fringe, travel, materials and supplies, publication costs, indirect costs).

### `CAPABILITY_SUMMARY.md`
- **Use for:** quick capability inventory — bulleted list of what the system can do, useful for the NEH **Overview** section.
- **Reframe:** rewrite "deepest accessibility deployment of Claude's product stack" framing as substrate-agnostic methodology language.

### `STRATEGY.md`, `ONE_PAGER.md`, `COLD_EMAILS.md`, `DEMO_SCRIPT.md`, `TESTIMONIAL_DRAFT.md`, `FAQ.md`
- **Use sparingly.** These are Anthropic-audience-specific. Phrases that land for an Anthropic reader (competitive differentiation, vendor partnership, credits ask) actively misfire for NEH reviewers. Skim for any non-pitch sentence — e.g., a clean description of Daniel Bein's daily workflow — and discard the rest.

## Tier 4: External references (cite directly in proposal)

- DHAG NOFO + landing page (see `PROGRAM_NOTES.md`).
- The ACADIA paper's full reference list (in `source-material/ACADIA_2026_paper.md` — Hamraie 2017, Boys 2014, DisOrdinary Architecture, Schön 1987, Way & Barner 1997, Kennedy 1993, Celani et al. 2013, Watanabe et al. 2014, Kłopotowska & Magdziak 2021, Zhang et al. 2025 A11yShape, Khan et al. 2024 Text2CAD, Li et al. 2025 CAD-Llama, Wang et al. 2025 CAD2Program, Ghosh & Coppola 2024, Wainwright 2019, Gipe-Lazarou 2025, Anthropic 2024 MCP, Anthropic 2026 Claude Code, Chen 2025 rhino-mcp).
- DHAG-funded precedent projects (to identify during drafting): scan NEH's funded-projects database for prior accessibility-focused DHAG awards and cite at least one as field context in the Environmental Scan.

## Pull patterns

When drafting a section, the typical pull order is:

1. Open `OUTLINE.md` and find the section's source-paragraph pointers.
2. Open `source-material/ACADIA_2026_paper.md` and read those paragraphs.
3. Decide which sentences carry over verbatim, which need reframing into NEH voice, which need expansion with material not in the paper.
4. Check Tier 2 docs for any expansion material before writing new prose.
5. Only consult Tier 3 (Anthropic pitch) for budget or capability-list structure, never for narrative voice.
