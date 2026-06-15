# Anthropic Pitch — Strategy

Internal team doc. Not for external distribution.

## The pitch

The Radical Accessibility Project at UIUC is a working architectural design system built around a blind primary user, Daniel Bein. Every part of it runs on Claude: two MCP servers (65 functions across the design pipeline), Skills-packaged capabilities, an accessible Claude Code client we built because the Ink TUI isn't screen-reader compatible, and lifecycle hooks that announce events through the JAWS TTS API. Daniel uses it daily — he types or speaks design commands, hears confirmations through NVDA, audits for ADA compliance, prints his floor plan on swell paper, reads it with his fingers, 3D-prints it to scale, and presents at studio review. No sighted intermediary at any step.

It is, as far as we can tell, the deepest accessibility deployment of Claude's product stack anywhere. We did not set out to make it that — we set out to make Daniel an architect. The integration is real and the work is in flight: an ACADIA paper this cycle, working software at github.com/johnnysclark/Radical-Accessibility-Toolkit, three student researchers (Ethan Anderson, Isaac Tu, Laura Heuser) shipping code, two faculty leads (John Clark, Hugh Swiatek).

Equipment, fabrication, and lab costs are covered through UIUC. What's not covered is what we want from Anthropic.

## The asks

Direct. Three options. Any combination.

### 1. Money

Stipends for the people doing the work. Ethan, Isaac, Laura, and a co-designer stipend for Daniel. Roughly $60K–$80K/year covers the four of them plus modest travel for paper presentation. This is the difference between students who graduate carrying institutional memory out the door and students who can keep working.

### 2. Credits

Claude API + Claude Code credits to uncap student and primary-user usage. Current usage hits personal-subscription rate limits during batch image description, OCR runs, and day-to-day design-conversation work. A research-tier allotment removes the ceiling.

### 3. Expertise

Time from the people at Anthropic who own Claude Code accessibility, MCP, and the Skills format. Code review on our webui + screen-reader hooks. A design partner who can tell us whether what we built should be upstreamed, mirrored, or scrapped. Possibly the most valuable of the three asks; the cheapest for Anthropic to provide.

Any one of the three meaningfully changes the next year. All three change what's possible.

## Why Anthropic specifically

The project is Claude-native. MCP is the only protocol designed for the kind of semantic, auditable, multi-tool integration accessibility requires. Claude Code is the only agentic interface a screen-reader user can reasonably extend. Skills give us a clean unit of capability alongside our existing macros. Switching providers would require rebuilding the integration substrate, and we don't want to.

The case for Anthropic is not "give us money because we're a good cause." It's: here is a working production deployment of your full product stack in a domain your competitors cannot credibly claim. Funding it — with money, credits, or expertise — gives Anthropic a use case its beneficial-AI framing can actually point at, in a discipline (architecture) that has been visibly hostile to non-visual practitioners for a hundred years.

## Channels (run in parallel — none is reliable cold)

| Channel | Best-fit ask | Notes |
|---|---|---|
| Anthropic societal impacts / beneficial deployments | money, credits | Mission alignment is strongest here |
| Claude Code product / DevRel | expertise | Engage via anthropics/claude-code GitHub Issues + Discussions; this is where the people we want already are |
| External researcher / API access programs | credits | Apply through anthropic.com forms; fast turnaround |
| Warm intros (LinkedIn) | any | UIUC alumni at Anthropic; Anthropic staff posting about MCP, Claude Code, accessibility |

Tailor per channel (see `COLD_EMAILS.md`). Do not send identical email to multiple addresses.

## Internal coalition (UIUC, in parallel)

External outreach lands better when UIUC is already behind the project. Build the internal coalition in parallel with — not after — the external pitch. Units worth a single targeted conversation:

- **DRES (Disability Resources & Educational Services)** — Daniel's primary access partner; campus office whose endorsement carries weight with any disability-focused funder.
- **CITL (Center for Innovation in Teaching & Learning)** — funds and amplifies teaching-innovation work; aligns with RAP Studio.
- **Beckman Institute** — interdisciplinary research center; possible home for the multimodal-interaction subproject.
- **Siebel Center for Design** — design-research center; aligns with RAP Desk.
- **NCSA / Illinois Computes** — research-computing capacity; possible compute/storage support and a credible co-applicant on NSF CISE proposals.
- **School of Architecture leadership + FAA Dean's office** — administrative support, course buyouts, hiring authority.
- **Sponsored Research Office** — required path for any federal application; engage early to avoid late-stage F&A surprises.
- **CS / Information Sciences faculty** — potential co-PIs for NSF HCC and cross-departmental work.
- **Provost's office digital accessibility initiatives** — campus-level accessibility owns relationships with JAWS/NVDA/AT vendors RAP also depends on.

The internal pitch is shorter than the external one. UIUC can become the national testbed for accessible AI design education by turning a high-need accommodation problem into reusable research infrastructure. Lead with that.

## Gating checks before any outreach

1. John, Hugh, and Daniel sign off on all artifacts. Daniel approves his testimonial verbatim and approves any use of his name or image.
2. Read every artifact through NVDA. If our pitch about accessibility isn't accessible, we lose the room before entering it.
3. Pre-test the cold email on two friendly non-Anthropic contacts for tone.
