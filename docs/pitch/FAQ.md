# FAQ — Objection Handling

Anticipated questions and what we say. Internal team doc; some answers also get folded into follow-up emails.

---

### Q: Why Anthropic and not OpenAI, Google, or a foundation?

Because the toolkit is already Claude-native and rebuilding it for another stack would be months of work for no user benefit. MCP is the only protocol designed for the kind of semantic, auditable, multi-tool integration accessibility requires. Claude Code is the only agentic interface a screen-reader user can reasonably extend. Skills give us a clean unit of capability alongside our existing macros. And on mission: accessibility is closer to Anthropic's beneficial-AI framing than to a generic productivity story.

We are not playing providers against each other. If Anthropic passes, the project continues — it just stays small.

---

### Q: Why now? What changes if you wait six months?

Three things degrade. First, the students (Ethan, Isaac, Laura) are running on goodwill; without stipends, they graduate and the institutional memory leaves with them. Second, the ACADIA paper goes out this cycle — the credibility window is open now. Third, the toolkit is at the right level of maturity to be a case study: production enough to be real, small enough to be legible. In six months it will either have grown into something Anthropic should have funded earlier or shrunk into something they missed entirely.

---

### Q: Isn't this just a research project? How does it become something Anthropic can point at as a product story?

It already is something to point at — Daniel uses it daily, it produces physical artifacts, the demo video shows the loop end to end. Funding makes it more polished and reproducible, not more real. A reference deployment doesn't require commercialization; it requires legibility. We have that.

---

### Q: How big is the addressable population, honestly?

Architecture students who are blind: small. Architects, designers, and built-environment professionals with vision impairments, motor impairments, cognitive fatigue, or deafblindness combined: meaningful. The general principle — that the same input/logic/output separation generalizes across disabilities — is documented in the README's Use Cases section and is the substantive claim of the ACADIA paper. The system is built for the hardest case; the easier cases come along free.

But the real Anthropic-side question isn't market size. It's: does this demonstrate Claude's product surfaces in a way that competitors cannot credibly claim? Yes. There is no equivalent OpenAI deployment. There is no equivalent Google deployment. There is no equivalent open-source deployment.

---

### Q: What happens if Claude Code or MCP changes in a way that breaks your integration?

It has happened, and we've handled it. The project tracks Claude Code's release cadence and updates accordingly — the most recent example is the webui channel-server work and hooks restructuring. Closer ties to Anthropic would let us anticipate breaking changes instead of reacting to them; that is, in fact, part of the case for partnership.

---

### Q: Why is the controller stdlib-only but the rest of the project takes pip dependencies?

Deliberate. The controller (`controller/`) must run anywhere Python 3 runs, with no installation step a screen-reader user has to debug. The tools (`tools/tact/`, `tools/tasc/`, etc.) and the MCP layer (`mcp/`) are allowed to have richer dependency graphs because they're installed once during `python setup.py` and then never touched. The constraint exists because accessibility intolerates installation pain.

---

### Q: What does Daniel get out of this?

Stipend (in the budget), co-authorship on outputs, agency over how his testimonial and image are used, and tools that get better instead of worse over time. Daniel is a co-designer, not a research subject. Every artifact about the project, including this FAQ, is reviewed by him before it leaves the team.

---

### Q: Is the project open source? What's the license?

Yes. MIT. Repository: github.com/johnnysclark/Radical-Accessibility-Toolkit. No closed-source carve-outs are planned. If a sponsored research arrangement requires a different licensing posture for some component, we'd need to talk about it specifically — but the baseline is and will remain MIT.

---

### Q: If we give you API credits, how do you measure whether it mattered?

Three numbers: students who shipped work that needed Claude, conference papers acknowledging Claude API support, and Daniel's report on whether his day-to-day usage was uncapped. We'll send a quarterly note with those.

---

### Q: If we say no, what happens?

Project continues on personal subscriptions and goodwill labor. Pace slows. Ethan graduates; Isaac and Laura cycle through; the institutional memory thins. The ACADIA paper still goes out. Daniel continues to use the toolkit. We try again next year with a different funder.

The pitch is not "fund this or it dies." The pitch is "fund this and it becomes something you'll want to point at."

---

### Q: What's the smallest first step that's worth our time?

A 20-minute call with someone who has scope to either approve a credits grant or refer us to someone who does. We bring the demo video. You bring whatever questions this FAQ didn't answer.
