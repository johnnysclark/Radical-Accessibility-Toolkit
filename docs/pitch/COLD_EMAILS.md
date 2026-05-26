# Cold Email Templates

Three tailored versions for the three most likely first conversations. Each ≤200 words. Each leads with the user, not the tool. Each names exactly one ask, even when multiple are on the table.

Send from a `@illinois.edu` address. Attach `ONE_PAGER.md` (as PDF) and a link to the demo video. Do not attach the capability summary in the first email — offer it on reply.

---

## Template A — Societal impacts / beneficial deployments

**Subject:** A blind architecture student is designing buildings with Claude — and we'd like to talk

Hi [name],

I lead the Radical Accessibility Project at the UIUC School of Architecture. We co-design with Daniel Bein, a blind graduate student, an architectural design system built so that he — and people with motor impairments, cognitive fatigue, or deafblindness — can author buildings without a sighted intermediary at any step.

It runs on Claude. Two MCP servers (65 functions total) bridge Claude Code to the entire design pipeline; Skills package reusable capabilities; an accessible web client and lifecycle hooks make Claude Code itself usable with JAWS and NVDA. Daniel uses it daily — he types or speaks, hears confirmations, audits for ADA compliance, prints his floor plan on swell paper and reads it by touch, 3D-prints it to scale, and presents at studio reviews. No part of his workflow requires sight.

We have working software, a paper in flight (ACADIA: *The Full Stack of Inclusion*), and a research team running on goodwill. I'd value 20 minutes to show you what Daniel does in a normal afternoon and to ask whether Anthropic's beneficial-deployments work has a place for this.

One-pager attached. Demo video: [link].

Thanks for reading,
John Clark
[role] · UIUC School of Architecture
[contact]

---

## Template B — Claude Code product / DevRel

**Subject:** We shipped a Claude Code accessibility layer for screen readers — want to compare notes?

Hi [name],

The Ink TUI in Claude Code isn't usable with JAWS or NVDA. We hit that wall a year ago and ended up shipping our own accessible web client (`tools/webui/`) backed by an MCP channel server, plus a set of Claude Code lifecycle hooks that announce events through the JAWS TTS API via a WSL2-to-PowerShell bridge.

This is part of a larger project — the Radical Accessibility Project at UIUC — where a blind architecture grad student designs buildings via Claude Code, with two MCP servers (65 functions) and a Skills directory wiring it into a full tactile-output pipeline (PIAF swell paper, 3D models, ADA audits). One of the deepest production deployments of MCP + Skills + Claude Code we know of, and possibly the only one where the user can't see the screen at all.

We'd like to either upstream the accessibility work, partner on it, or just compare notes with whoever owns Claude Code accessibility internally. Happy to walk through it on a call — 30 minutes, screen-share-friendly. One-pager attached, demo at [link], repo at github.com/johnnysclark/Radical-Accessibility-Toolkit.

Thanks,
[name]
UIUC · Radical Accessibility Project

---

## Template C — Research credits / external research access

**Subject:** Research-credits request: accessibility-first architectural design on Claude (UIUC)

Hi [name],

I'm writing on behalf of the Radical Accessibility Project at the UIUC School of Architecture, a research initiative co-designed with a blind architecture graduate student. The project is built on Claude: two production MCP servers (65 functions across the design pipeline), Skills-packaged capabilities, and an accessible Claude Code client for screen-reader users.

We'd like to apply for Claude API and Claude Code credits to support student researcher usage over the next academic year. Specifically:

- Batch image-to-text description of architectural precedents (`tools/image-describer/`)
- Tactile-quality assessment of generated PIAF prints via Claude vision (`tools/tact/`)
- Day-to-day design conversation across three student researchers and the primary user

Current usage is rate-limited by personal Pro/Max subscriptions. A research-tier allotment would let us instrument the project properly and contribute findings back (we're submitting to ACADIA this cycle; happy to share drafts).

What's the right form or process? Happy to provide a budget, a usage estimate, and IRB / data-handling specifics on request.

One-pager attached. Repository: github.com/johnnysclark/Radical-Accessibility-Toolkit.

Best,
John Clark
UIUC School of Architecture
[contact]

---

## Follow-up at +7 days

Short. One paragraph. No new ask. Re-link the demo video.

> Hi [name] — circling back on the note below in case it landed during a busy week. Happy to make this as low-effort as a 15-minute call or as substantive as a full walkthrough; whichever fits. Demo here if it's useful: [link].

## Follow-up at +14 days

If still no reply: stop. Move to a different channel. A third email is noise.
