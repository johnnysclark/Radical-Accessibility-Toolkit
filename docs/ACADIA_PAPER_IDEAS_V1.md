# ACADIA 2026 Paper Ideas V1

**Project:** Radical Accessibility Project (UIUC School of Architecture)
**Authors:** John Clark + [collaborator]
**Started:** 2026-03-05
**Status:** Active brainstorm

---

## The Core Positioning Problem

ACADIA 2026 will be flooded with AI papers. Every other submission will demonstrate an LLM generating geometry, a diffusion model producing floor plans, or a chatbot driving Grasshopper. The novelty of "we used AI to make architecture" has evaporated. The question is no longer *can* AI assist design — it can — but *who does AI-assisted design include, and what does it make possible that was previously impossible?*

Our paper must not be another AI paper. It must be a pedagogy paper that happens to use AI. The distinction matters: AI papers describe what a system can do; pedagogy papers describe what a student can learn, and how the tools reshape the learning itself.

## What We Are Actually Arguing

**Radical Accessible Pedagogy** — the idea that designing architectural education tools for blindness first produces a pedagogy that is not merely inclusive but genuinely different and, in specific measurable ways, better.

This is not "we made Rhino accessible." This is: we built a complete CLI-driven design pipeline — controller, JSON state file, Rhino watcher, tactile output, AI description — where a blind graduate student authors parametric floor plans in studio. And the tool ecosystem we built to make that possible turns out to embody pedagogical principles the field has been arguing for but never operationalized:

- **Semantic over geometric.** The student works with named bays, corridors, and spatial relationships before coordinates. This is how spatial cognition develops (Piaget & Inhelder 1956, Millar 1994) and how blind spatial reasoning works (Loomis et al. 2001, Giudice 2018) — but it is also better pedagogy for everyone. Sighted students in visual CAD skip semantic understanding and go straight to pushing geometry around. The CLI forces the semantic step.

- **Explicit reflective conversation.** Every command gets a verbal response. The design dialogue is auditable, diffable, and repeatable. Schon's "reflective practitioner" made operational through a screen-reader-native protocol. Visual CAD's feedback is silent and ambient — you have to look to see what changed. The CLI tells you.

- **Crash-proof, version-controlled design process.** The student's work lives in a JSON file, not in Rhino's memory. Every state is recoverable. Every change is tracked. This was built because a blind user cannot visually confirm crash recovery — but it is the design process infrastructure every studio should have.

- **Physical-digital round-trip as default.** Tactile output (PIAF swell paper, 3D prints) and tactile input (pegboard) are not accommodations bolted on — they are integral to the workflow. The blind student authors through CLI, evaluates through touch, feeds back through CLI. This is the embodied design loop that fabrication-centered pedagogy (Sass, ACADIA 2024 Teaching Award) calls for, made concrete.

## How Claude Code Fits

This is where we distinguish ourselves from the AI-paper crowd. We are not using Claude to generate architecture. We are using Claude Code — specifically, as an AI-assisted development environment — to build the accessibility infrastructure itself.

Claude Code is the development tool that makes the Radical Accessibility pipeline possible at the speed a single faculty member and a graduate student need. It writes the CLI handlers, constructs the MCP server, generates the IronPython watcher scripts, builds the tactile rendering pipeline, and maintains the whole system while respecting the project's hard constraints: Python stdlib only, IronPython 2.7 compatibility for Rhino, screen-reader-friendly output, atomic file writes, zero external dependencies.

The argument is not "AI generates design." The argument is: **AI-assisted development tools (Claude Code) enable a lone researcher to build the accessible design infrastructure that the field has called for but no one has had the resources to construct.** The pipeline that lets Daniel design in studio exists because Claude Code collapses the development effort from a multi-year funded research lab project to something one person can build and maintain iteratively, in real time, responding to Daniel's needs week by week.

This is a different kind of AI contribution:
- Most AI papers: "AI generates geometry for designers"
- Our paper: "AI-assisted development enables a researcher to build tools that make design accessible to people the field has excluded"

The AI is not in the design loop. The AI is in the tool-building loop. That distinction is the paper's contribution to the AI discourse.

## How We Stand Out

The ACADIA 2026 submission pool will contain:

1. **LLM-to-geometry papers** (Raven, Ant, Text2CAD descendants). Our paper is not this. We are not generating geometry with LLMs. We are building accessibility infrastructure with AI-assisted development.

2. **AI-for-sustainability papers.** Different topic entirely.

3. **Diffusion/image-generation papers.** We have no images. We have a CLI.

4. **AI agent papers** (ConvoAI, CADialogue descendants). Closer to us, but their agents assist sighted designers. Our pipeline serves a blind designer, and the agent (Claude Code) built the pipeline, not the architecture.

5. **Equity/inclusion papers** (Noel, Cupkova lineage). We share their concerns but deliver a working system, not a call to action.

Our paper occupies a unique position: **a pedagogy paper about a blind student in a graduate architecture studio, where the accessible tools were built using AI-assisted development (Claude Code), and the resulting tool architecture embodies pedagogical principles that benefit all students.** No other submission will combine disability, pedagogy, tool-building, and AI in this configuration.

## What "Radical Accessible Pedagogy" Means — Working Definition

A pedagogical approach in which:

1. **The primary design case is non-visual.** Tools are designed for a blind user first. Sighted use is a secondary projection of a system that works without vision.

2. **The student is a co-designer of the tools, not a consumer.** Daniel's feedback reshapes the CLI weekly. The tools evolve from his experience, not from assumptions about his experience.

3. **The medium of design is text, not image.** Commands, state files, and verbal feedback constitute the design conversation. This is not a limitation — it is a pedagogical commitment to semantic explicitness.

4. **Physical artifacts are integral, not supplementary.** Tactile output and tactile input are part of the core workflow, not accommodations. Every student — blind or sighted — benefits from the physical-digital round-trip.

5. **The tool ecosystem is open, auditable, and recoverable.** JSON state files, atomic writes, version control, zero dependencies. The infrastructure of the learning environment is as considered as the curriculum.

6. **AI assists the toolmaker, not the designer.** Claude Code builds and maintains the pipeline. The student designs through the pipeline. The AI never makes a design decision on Daniel's behalf.

---

## Open Questions for Collaborator Discussion

- **Paper format:** Full paper (4,000–6,000 words) or short paper / demo / poster? The demo format lets us show the system in action, which is compelling. The full paper lets us make the theoretical argument. Can we do both — a full paper with a video supplement?

- **Framing emphasis:** Do we lead with pedagogy ("here is a new model for inclusive architectural education") or with the tool architecture ("here is what happens when you design CAD for blindness first, and by the way it is better pedagogy")? The brainstorm rearrangement document argues for leading with the field's current moment (text-to-geometry, AI) and revealing the pedagogy. But a pedagogy-first framing might hit differently.

- **Daniel's voice:** How much of the paper should be in Daniel's words? A co-authored paper where Daniel describes his experience is more powerful than a third-person case study. What is his comfort level?

- **Claude Code disclosure:** How explicitly do we describe the role of Claude Code in building the tools? Full transparency is consistent with the project's values. But we need to frame it carefully: "AI built the tools that make accessible design possible" is very different from "AI does the design." The risk is reviewers conflating the two.

- **Evaluation:** What evidence do we present? Options:
  - Daniel's studio work products (plans authored through CLI)
  - Before/after comparison (what Daniel could do before the tools vs. after)
  - Comparative task analysis (same design task in Grasshopper vs. CLI)
  - Qualitative interview with Daniel about the experience
  - Description of specific design sessions with command logs

- **Scope:** Do we cover the full pipeline (CLI + watcher + tactile + AI description + MCP) or focus on one slice? The full pipeline is more impressive but harder to describe in 6,000 words. A focused paper on the CLI + CMA + watcher triangle with the pedagogy argument might be tighter.

- **Title candidates:**
  - "Radical Accessible Pedagogy: What a Blind Architecture Student Reveals About Computational Design Education"
  - "The Model Is Not the Viewport: Born-Accessible Architectural Computing and the Text-to-Geometry Blind Spot"
  - "Not Another AI Paper: How AI-Assisted Development Enables Accessible Architectural Pedagogy"
  - "Blindness as Method: Constraint-Driven Innovation in Computational Design Pedagogy"
  - [your ideas here]

---

## Next Steps

- [ ] Collaborator reads brainstorm rearrangement doc and this document
- [ ] Align on framing emphasis (pedagogy-first vs. tool-first)
- [ ] Decide on Daniel's role in authorship and voice
- [ ] Decide on paper format (full / short / demo)
- [ ] Identify 3–5 key citations that anchor the argument
- [ ] Write a 300-word abstract as a forcing function
- [ ] Check ACADIA 2026 submission deadline and format requirements
