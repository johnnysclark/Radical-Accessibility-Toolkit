# Cold Email Templates

Three templates, one per ask category — money, credits, expertise. Each ≤200 words. Each leads with the user, not the tool. Each names exactly one ask, even when the other two are also on the table.

Send from a `@illinois.edu` address. Attach `ONE_PAGER.md` (as PDF) and a link to the demo video. Do not attach the capability summary in the first email — offer it on reply.

---

## Template A — Money ask (societal impacts / beneficial deployments)

**Subject:** A blind architecture student is designing buildings with Claude — we're looking for stipend support

Hi [name],

I lead the Radical Accessibility Project at the UIUC School of Architecture. We co-design with Daniel Bein, a blind graduate student, an architectural design system built so he — and people with motor impairments, cognitive fatigue, or deafblindness — can author buildings without a sighted intermediary at any step.

It runs on Claude. Two MCP servers (65 functions total) bridge Claude Code to the entire design pipeline; Skills package reusable capabilities; an accessible web client and lifecycle hooks make Claude Code itself usable with JAWS and NVDA. Daniel uses it daily — he types or speaks, hears confirmations, audits for ADA compliance, prints his floor plan on swell paper and reads it by touch, 3D-prints it to scale, and presents at studio reviews.

UIUC covers our equipment and lab costs. What we don't have is a stipend structure for the three student researchers (Ethan Anderson, Isaac Tu, Laura Heuser) and the co-designer (Daniel) doing the work. $60K–$80K/year would keep all four of them on the project through next academic year.

20 minutes to show you a working session, if you can spare it.

One-pager attached. Demo: [link].

Thanks for reading,
John Clark
[role] · UIUC School of Architecture
[contact]

---

## Template B — Expertise ask (Claude Code product / DevRel)

**Subject:** We shipped a Claude Code accessibility layer for screen readers — want to compare notes?

Hi [name],

The Ink TUI in Claude Code isn't usable with JAWS or NVDA. We hit that wall a year ago and ended up shipping our own accessible web client (`tools/webui/`) backed by an MCP channel server, plus a set of Claude Code lifecycle hooks that announce events through the JAWS TTS API via a WSL2-to-PowerShell bridge.

This is part of a larger project — the Radical Accessibility Project at UIUC — where a blind architecture grad student designs buildings via Claude Code, with two MCP servers (65 functions) and a Skills directory wiring it into a full tactile-output pipeline (PIAF swell paper, 3D models, ADA audits). As far as we can tell, the deepest production deployment of MCP + Skills + Claude Code anywhere, and possibly the only one where the user can't see the screen at all.

What we'd value, more than money: code review and a design partner from whoever owns Claude Code accessibility internally. We want to know whether what we built should be upstreamed, mirrored, or scrapped. 30 minutes, screen-share-friendly.

One-pager attached. Demo at [link]. Repo: github.com/johnnysclark/Radical-Accessibility-Toolkit.

Thanks,
[name]
UIUC · Radical Accessibility Project

---

## Template C — Credits ask (research / API access programs)

**Subject:** Research-credits request: accessibility-first architectural design on Claude (UIUC)

Hi [name],

I'm writing on behalf of the Radical Accessibility Project at the UIUC School of Architecture — a research initiative co-designed with a blind architecture graduate student. The project is built on Claude: two production MCP servers (65 functions across the design pipeline), Skills-packaged capabilities, and an accessible Claude Code client for screen-reader users.

We'd like to apply for Claude API and Claude Code credits to support student researcher and primary-user usage over the next academic year. Specifically:

- Batch image-to-text description of architectural precedents (`tools/image-describer/`)
- Tactile-quality assessment of generated PIAF prints via Claude vision (`tools/tact/`)
- Day-to-day design conversation across three student researchers and the primary user

Current usage is rate-limited by personal Pro/Max subscriptions. A research-tier allotment would let us instrument the project properly and contribute findings back (ACADIA paper this cycle; happy to share drafts).

What's the right form or process? Happy to provide a usage estimate and IRB / data-handling specifics on request.

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
