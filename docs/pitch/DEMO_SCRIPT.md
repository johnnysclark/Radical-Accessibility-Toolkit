# Demo Video — 90-Second Walkthrough

The highest-leverage artifact in the pitch packet. One short video that shows Daniel doing the loop. No narration over the top — let Daniel's screen reader and the actual command output be the soundtrack.

## Goal

Land three things in 90 seconds:

1. **A blind person is designing a building.** Not theoretically. Right now, in the video.
2. **It runs on Claude.** Visible MCP calls, Claude Code in the loop, screen-reader announcements of Claude's responses.
3. **It produces a real physical artifact.** The PIAF tactile print or 3D model in his hands at the end.

If a viewer ends with any one of those three impressions clear in their head, the demo did its job.

## Logistics

- **Length:** 90 seconds. Anything longer doesn't get watched.
- **Format:** Screen recording of the terminal + Claude Code, plus a single physical-world shot at the end of Daniel reading the tactile print. Captioned for sound-off viewing.
- **Captions:** Open captions burned in. Every command, every confirmation. Anthropic's accessibility-minded audience will notice if the demo about accessibility isn't itself captioned.
- **Audio:** Daniel's screen reader (NVDA or JAWS) at its actual speed. Do not slow it down or re-record in a "friendlier" voice. The point is the real interface.
- **No music.** Music covers what the screen reader is saying and undermines the point.
- **Daniel must approve the cut before release.** Non-negotiable.

## Storyboard

### Beat 1 (0:00–0:10) — Title card

Black screen, white text, screen reader reads it:

> "Daniel Bein is a blind architecture student at UIUC. This is how he designs buildings."

### Beat 2 (0:10–0:35) — Daniel speaks design intent to Claude Code

Screen: the accessible web client (`tools/webui/`) open. Daniel speaks:

> "Create a 6 by 3 bay grid for a school building, 24-foot spacing. Add a corridor on the x-axis. Add two accessible doors."

Claude Code panel shows the MCP calls happening in real time. Screen reader announces each confirmation:

> "OK. Bay A grid set to six by three. OK. Bay A corridor on. OK. Added door d1. OK. Added door d2."

### Beat 3 (0:35–0:55) — Audit + render

Daniel speaks:

> "Audit it for ADA, then render a tactile print."

Audit output reads aloud: doors meet minimum; corridor exceeds minimum. Then `render` completes; screen reader announces the PDF was saved.

### Beat 4 (0:55–1:20) — Physical world

Cut to Daniel at the laser printer, then at the PIAF heater, then at the desk. He runs his fingers over the raised lines of his floor plan. No commentary. Hold the shot.

Optional final touch: he picks up the printed 3D model from the previous workflow and holds it.

### Beat 5 (1:20–1:30) — Closing card

White text on black:

> "Radical Accessibility Project · UIUC School of Architecture"
> "Built on Claude, Claude Code, MCP, and Skills."
> "github.com/johnnysclark/Radical-Accessibility-Toolkit"

Screen reader reads it. Fade.

## Things to avoid

- Stock music, sweeping b-roll, drone shots, time-lapse. This is not a Kickstarter.
- "Inspirational" framing — "imagine if everyone could…" Do not. Show; don't sell.
- Hiding the screen reader. The screen reader *is* the interface.
- Sighted narrator voice-over. If anyone speaks, it's Daniel.
- Speeding up the screen reader for "watchability." The speed Daniel uses is the speed Daniel uses.

## Distribution

- Upload unlisted to YouTube + Vimeo (offer both; some Anthropic firewalls prefer one).
- Link from `ONE_PAGER.md` and every cold email.
- Do **not** post publicly until Daniel approves it for public release. The unlisted version is for outreach only at first.
