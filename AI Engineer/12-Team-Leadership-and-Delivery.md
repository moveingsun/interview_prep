# 12 · Team Leadership and Delivery

[← Index](00-Index.md) · **Manager-round priority:** High · **Read time:** ~35 min

> **Why this matters for this role:** The JD asks you to "establish code review, testing, documentation, and knowledge-sharing standards," "work with Product Owners on requirements and estimates," act as "the main technical escalation point," "evaluate new LLMs, agent frameworks, and MLOps tools," and partner with Data Engineering, Platform, Product, Operations, and compliance, all while coding 40–50% of the time. This page covers *how you run the work*. [11 · Mentoring](11-Mentoring-and-Coaching.md) covers *how you grow the people*.

---

## Primer: a tech lead's operating system (use as a mental map)

```
   PEOPLE         grow them  ───────────────► 11-Mentoring-and-Coaching.md
     │
   STANDARDS      short list, enforced by tooling (PR template, CI eval gate, linters)
     │
   DECISIONS      proportional to reversibility → design doc / ADR for the expensive ones
     │
   DELIVERY       predictable parts estimated; quality parts time-boxed + eval-gated
     │
   PRODUCTION     tracing, evals on live traffic, cost alarms, kill switches, blameless postmortems
     │
   STAKEHOLDERS   PO, Data Eng, Platform, Compliance/Privacy, Ops SMEs: involve early, write it down
```

**Testing pyramid for LLM applications:** know this picture well, it answers several questions.
```
                 ┌──────────────────────────────┐
                 │  Human review / UAT          │ few & expensive: SMEs (e.g., nurse reviewers,
                 │                              │ member-service leads) grade sampled outputs
                 ├──────────────────────────────┤
                 │  LLM-as-judge evals          │ faithfulness/groundedness, relevance, tone;
                 │                              │ judge calibrated against human labels
                 ├──────────────────────────────┤
                 │  Deterministic evals         │ golden set: right doc retrieved (recall@k),
                 │  (golden dataset)            │ citation present & valid, schema valid,
                 │                              │ correct tool chosen, SQL parses / executes
                 ├──────────────────────────────┤
                 │  Unit + integration tests    │ tools, parsers, chunkers, auth/entitlement checks,
                 │  (no LLM or a fake LLM)      │ graph routing with a stub model; fast, every commit
                 └──────────────────────────────┘
   + Online: tracing on every call, user feedback, sampled production evals, drift and cost alerts
```

---

## Questions & answers

### Q1. What engineering standards would you set for an AI engineering team?  `[P0]`
**Say this first (~30 sec):** "A short list, enforced by tooling rather than willpower, in three groups. First, normal good engineering: small PRs, tests, CI, docs. Second, AI-specific rules: prompts and model configs versioned as code, every prompt or model change runs the eval suite, tools get least-privilege permissions, and every LLM call is traced with its cost. Third, healthcare rules: no PHI in logs or in prompts sent to services that aren't covered, and retrieval always enforces the user's access rights."

**If they dig deeper: the AI code-review checklist I'd put in the PR template**
- [ ] **Prompt, model, or retrieval config changed?** Eval run attached with before/after scores, and no regression past the agreed threshold.
- [ ] **Prompts live in the repo**, templated and versioned. No live edits in a portal.
- [ ] **Model pinned** to a specific deployment or version, with a fallback defined.
- [ ] **Structured outputs validated** (Pydantic or JSON schema), with parse failures handled.
- [ ] **Tools:** inputs validated, least privilege, idempotent where possible. Destructive or member-impacting actions require human approval.
- [ ] **Retrieval enforces the user's entitlements** (security trimming), and failures *fail closed*.
- [ ] **No PHI/PII** in logs, traces, error messages, or test fixtures. Use de-identified data only.
- [ ] **Secrets** in Key Vault or managed identity. No keys in code.
- [ ] **Agent loops** have timeouts, retries with backoff, and a max-iterations cap.
- [ ] **Cost:** token budget per request, and cost logged per turn.
- [ ] **Prompt injection:** untrusted text (retrieved docs, user input, tool output) can never trigger privileged tools on its own.
- [ ] **Docs:** ADR updated if the design changed, plus a runbook entry for new failure modes.

**How to get buy-in:** write the standards *with* the team, start with about five rules, automate them (PR template, CI eval gate, linters, secret scanning), and revisit quarterly.

**Your angle:** [S1](13-Behavioral-Story-Bank.md#s1) (eval set, citation checks, per-turn cost tracking) · [S9](13-Behavioral-Story-Bank.md#s9) (fail-closed access checks) · [S6](13-Behavioral-Story-Bank.md#s6) (CLAUDE.md is your standards written down where both humans and AI tools read them).

**Likely follow-ups:** "How do you test something non-deterministic?" Answer: use the pyramid above, set temperature low where possible, assert on properties rather than exact strings, and use thresholds over a dataset rather than single cases. See [07 · Evaluation](07-Evaluation-and-Observability.md).

---

### Q2. How do you estimate AI work with a Product Owner when outcomes are uncertain?  `[P0]`
**Say this first:** "I split it into the predictable parts and the part that isn't. Plumbing, UI, auth, and integration I estimate normally. The quality part, 'will the model answer correctly 90% of the time,' I don't pretend to estimate. I time-box it. We agree up front on 'good enough' as eval targets, run a one- or two-week spike to get a baseline, and then plan a series of eval-gated milestones. The PO gets real numbers to plan with, plus a decision point if quality plateaus."

**If they dig deeper:**
1. **Define success with the PO before building.** For example: ≥ 90% correct on a 150-question golden set, zero PHI leaks, p95 latency < 5s, < $0.05 per conversation. Also define what failure looks like, such as "a wrong answer is worse than 'I don't know, here's who to call.'"
2. **Run a 1–2 week spike** to get a baseline on the eval set. That tells you how far you are from the target, which is the real uncertainty.
3. **Eval-gated milestones:** internal alpha (eval ≥ X) → pilot with N real users (eval ≥ Y plus feedback) → GA.
4. **Appetite, not estimate** (Shape Up): "How much is this worth to us? Six weeks?" Fixed time, variable scope.
5. **Give ranges with confidence levels,** not single dates, and update weekly with an eval-trend chart.
6. **Agree on the fallback ahead of time:** narrower scope, human-in-the-loop, or stop.

**Your angle:** [S1](13-Behavioral-Story-Bank.md#s1): you delivered Load Deal AI in 3 weeks. `[fill in: how you scoped it, what you cut, and how you knew it was good enough]` · [S8](13-Behavioral-Story-Bank.md#s8): close PM collaboration around a release.

**Likely follow-ups:** "The PO needs a date now." Answer: give a firm date for the spike result and a range for the rest. · "What if you miss the eval target?" Answer: that's the pre-agreed fallback conversation, backed by data.

---

### Q3. How do you say no, or negotiate scope?  `[P0]`
**Say this first:** "I rarely say a flat no. I say 'yes, and here's what it costs,' and I offer options: if we add this, here's what slips, or here's a narrower version we can ship safely by the date. There is one category where I hold the line: anything that risks PHI exposure, or an AI making a coverage-affecting decision without human review. There I explain the risk in business terms and bring in compliance."

**If they dig deeper:** the options menu is smaller scope, a later date, more people, or (only for non-critical features) a lower quality bar. Show the eval data, write the decision down, and if needed, escalate *together* with the PO and a one-page trade-off.

**Your angle:** [S14](13-Behavioral-Story-Bank.md#s14): as the sole engineer on AMP, you constantly triaged competing asks. `[fill in: a request you reshaped instead of refusing]`

---

### Q4. How do you make and record technical decisions?  `[P0]`
**Say this first:** "In proportion to how reversible the decision is. If it's easy to reverse, the owner decides quickly. Expensive decisions, like framework choice, vector store, or data model, get a short design doc or RFC, a review with the people affected, and an ADR recording the context, options, decision, and consequences. The ADR matters most six months later, when someone asks why we chose LangGraph."

**If they dig deeper: ADR template** (Michael Nygard's format plus two fields)
```markdown
# ADR-012: Use LangGraph for multi-step agent orchestration
Status: Accepted (2026-10-20)
Context: what forces are at play (requirements, constraints, team skills)
Options considered: A / B / C with pros & cons
Decision: what we chose
Consequences: what gets easier, what gets harder, new risks
Revisit when: e.g., "Foundry Agent Service supports X" or "p95 > 8s"
```

**Framework or vendor selection rubric (weighted, then prototype the top two):**

| Criterion | Questions to ask |
|---|---|
| Fit | Does it handle our control flow, state, and human-in-the-loop needs? |
| Production features | Persistence/checkpointing, streaming, retries, tracing, evaluation hooks |
| Platform fit | Runs in our Azure tenant, works with Foundry, AI Search, managed identity, private networking |
| Compliance | Covered under our BAA? Data residency, audit logging |
| Team | Can the team learn it? Can we hire for it? |
| Maturity | Release cadence, breaking changes, license, community |
| Lock-in / exit cost | How hard is it to leave? |
| Cost | Licensing, hosting, ops burden |

**Build vs. buy:** buy or use managed services for undifferentiated work (vector search → Azure AI Search, model hosting → Foundry). Build what *is* the differentiation or what compliance requires: domain tools, eval sets, workflow orchestration, guardrails. Check total cost of ownership and whether the team can operate it.

**Your angle:** In [S1](13-Behavioral-Story-Bank.md#s1) you used *both* a Snowflake Cortex agent (structured data via a semantic view) and a LangGraph agent (pipelines), which is a strong "right tool for the job" example. `[fill in: why that split]`

---

### Q5. How do you evaluate a new LLM or agent framework without chasing hype?  `[P0]`
**Say this first:** "Benchmarks and launch posts tell me what's worth testing, not what to adopt. I run a bake-off on *our* eval set with the same prompts and retrieval, comparing quality, latency, cost per task, and failure modes. For frameworks, I build the same thin slice in each and check the production features: persistence, human-in-the-loop, tracing, and how it fails. Then it goes through an ADR and a staged rollout behind a flag."

**If they dig deeper:**
- **Model-swap process:** offline eval → shadow traffic → canary percentage → full rollout. Keep the previous deployment as a fallback, pin versions, and track the provider's model retirement dates.
- **What usually breaks on a model swap:** prompts tuned to the old model, output-format drift, different refusal rates, and tokenizer or price changes that move cost per task.
- **Keep a lightweight internal tech radar** (adopt / trial / assess / hold) so the team isn't re-debating the same tools.

**Your angle:** In [S1](13-Behavioral-Story-Bank.md#s1), per-turn cost tracking means you can compare models on cost per task, not just price per token.

---

### Q6. You're the technical escalation point. Walk me through handling a production incident in an AI system.  `[P0]`
**Say this first:** "Same incident discipline as any system: mitigate first, diagnose second, learn third, plus a few AI-specific moves. To mitigate, roll back the prompt or model version, switch to a fallback, or turn the feature off with a flag. To diagnose, use traces: is it retrieval, the model, a tool, or the data? Then run a blameless postmortem, and add the failing cases to the eval set so they can't regress silently."

**If they dig deeper: AI incident types and the first move for each**

| Incident type | Example | First move |
|---|---|---|
| Quality regression | Model version auto-updated, index rebuilt, source data changed | Roll back the config or index. Compare eval scores before and after. |
| Safety / privacy | PHI in a response or log, prompt injection triggers a tool | Kill switch. **Notify privacy/compliance immediately** (breach process). |
| Cost spike | Agent loop, context blow-up | Max-iteration cap, cost alarm, throttle |
| Latency / availability | Provider 429 throttling, quota exhaustion | Fallback deployment or region, backoff, queue |
| Tool failure | Downstream API changed | Circuit breaker, graceful "I can't do that right now" |

- **Prepare before it happens:** feature flags, routing config for models, per-request token caps, cost and quality alerts, and a runbook.
- **Communication:** stakeholder updates on a fixed cadence, even when the update is "no new info."
- **Postmortem:** timeline, contributing factors, and action items with owners. I have a junior co-write it with me, because it's a great way to learn the system.

**Your angle:** [S12](13-Behavioral-Story-Bank.md#s12): you built tooling for incident postmortems at Wayfair. [S7](13-Behavioral-Story-Bank.md#s7): you found a 10× cost spike caused by a loop using 98% of execution time, which is directly analogous to an agent stuck in a loop. [S11](13-Behavioral-Story-Bank.md#s11): availability 99.5% → 99.9%.

**Likely follow-ups:** "How do you catch quality regressions when nothing throws an error?" Answer: run evals on sampled production traffic, track groundedness and citation-validity dashboards, collect user thumbs up/down, and alert on drift.

---

### Q7. How do you balance tech debt against new features?  `[P1]`
**Say this first:** "I tie debt to things the PO cares about, like speed, reliability, and cost, and I pay it down continuously rather than through heroic rewrites. A standing slice of each sprint, roughly 15–20%, goes to debt and platform work, and the team prioritizes by pain: what slows us down most or wakes us up at night."

**If they dig deeper:** keep a debt register and quantify items: credits per day ([S7](13-Behavioral-Story-Bank.md#s7)), page latency 20s → 5s ([S14](13-Behavioral-Story-Bank.md#s14)). The highest-priority AI debt is anything that makes *every future change risky*: unversioned prompts, no eval set, hard-coded model names, no tracing.

**Your angle:** [S14](13-Behavioral-Story-Bank.md#s14): you rebuilt the metric calculation into one maintainable pipeline.

---

### Q8. How do you work across teams: Data Engineering, Platform, Product, Compliance?  `[P0]`
**Say this first:** "Involve them early, make their lives easier, and write things down. For AI work, the data team owns the sources we retrieve from, the platform team owns the runtime and networking, and compliance and privacy effectively have a veto. So I bring them a design doc *before* we build, not a finished feature to approve. And I try to give back: shared tooling, clear interfaces, and good docs."

**If they dig deeper:**
- **Data Engineering:** data contracts and freshness SLAs for indexed sources, and lineage, so we know which documents feed which index.
- **Platform:** AKS, private endpoints, managed identity, and ideally a shared LLM gateway (for example, APIM in front of model deployments) for quotas, logging, and cost chargeback.
- **Compliance / Privacy / Security:** data classification, BAA coverage, a threat model that includes prompt injection, audit logging, and model risk review, all at *design* time.
- **Product and Operations:** success metrics, plus operational SMEs (member services, clinical reviewers) to label eval data and define what "correct" means.

**Your angle:** [S3](13-Behavioral-Story-Bank.md#s3): Watt was platform-style work, with APIM routing, entitlements across apps, and specs handed to the frontend team. [S9](13-Behavioral-Story-Bank.md#s9): a shared service used by four apps. [S10](13-Behavioral-Story-Bank.md#s10): onboarding 10+ teams through influence rather than authority.

---

### Q9. How do you explain AI limitations to non-technical stakeholders?  `[P0]`
**Say this first:** "With concrete examples and numbers, not jargon. I show the eval results, like '92 of 100 test questions right, and here are the 8 it got wrong and why,' and I frame the design around the failures: what happens when it's wrong, who catches it, and how we'd know. That makes 'it's probabilistic' tangible, and it lets *them* make an informed risk decision."

**If they dig deeper:**
- **Analogy that lands:** "It's like a very fast new hire who has read every document but sometimes misremembers. So we make it cite its sources, and a person checks the high-stakes answers."
- **Demos include failure cases.** Don't oversell.
- **Separate *assistive* from *automated*:** in health insurance, clinical and coverage decisions keep a human accountable.
- **Translate cost and latency into business units:** dollars per conversation, seconds per answer.

**Your angle:** [S8](13-Behavioral-Story-Bank.md#s8): you explained discrepancies to the PM and traders in their terms. [S1](13-Behavioral-Story-Bank.md#s1): citations shown in the UI as a trust mechanism. [S2](13-Behavioral-Story-Bank.md#s2): the LLM judge "never writes without confirmation."

---

### Q10. Two engineers on your team are in conflict. What do you do?  `[P1]`
**Say this first:** "First I talk to each of them privately to understand what's really going on. Usually it's a disagreement about the work that turned personal, or unclear ownership. If it's about the work, I bring them together and turn it into a decision with criteria, data, and an owner. If it's ownership, I clarify roles. If it's about behavior, it's a feedback conversation, and if it continues I bring in their manager."

**If they dig deeper:** act early so it doesn't fester, don't take sides publicly, anchor on the shared goal, and follow up a week later.

---

### Q11. How do you balance 40–50% coding with leading? What do you code, and what do you delegate?  `[P0]`
**Say this first:** "I code the things that unblock or de-risk the team, and I delegate the things that grow the team. So I take spikes, shared foundations like the eval harness or tracing, tricky integrations, and production fires. I stay *off* the critical path of features, because when I get pulled into an escalation or a meeting, the team shouldn't stall waiting for me."

**If they dig deeper:**
- **Example week:** about 45% coding (spikes, foundations, fixes), 20% reviews and pairing, 15% design and decisions, 10% 1:1s and mentoring, 10% stakeholders.
- **Code review is my highest-leverage "coding" time.**
- **AI-assisted development** lets me get more done in each focused coding block ([S6](13-Behavioral-Story-Bank.md#s6)).

**Your angle:** [S14](13-Behavioral-Story-Bank.md#s14): you've been a high-throughput individual contributor. Show you know the shift: "my output now is the team's output."

---

### Q12. How would you drive adoption of AI-assisted development across the team?  `[P0]`  *(your differentiator)*
**Say this first:** "I've done this on my current team, so I'd follow the same playbook. Start with context: a CLAUDE.md or equivalent with our conventions, architecture, and commands, plus a domain knowledge base, so the tools write code that fits our system. Then show rather than mandate, by pairing with people on real tickets. Set guardrails: you own every line, tests and evals still gate merges, and no PHI or secrets go into tools that aren't approved. And measure it. On my team, AI-assisted commits went from 36% to 80% in about two months, and I'd watch cycle time and change-fail rate to make sure quality held."

**If they dig deeper:**
- **Rollout:** champions pair with others → a shared library of prompts and workflows → team retros on what works and what doesn't.
- **Measures:** adoption rate, PR cycle time, review rounds, change-fail rate, escaped defects, and a short developer survey. DORA 2025: AI *amplifies* existing strengths and weaknesses, so fix the basics too.
- **Security:** approved enterprise tools only, no PHI in prompts, secret scanning in CI.
- **For juniors:** see [11 · Mentoring Q6](11-Mentoring-and-Coaching.md).

**Your angle:** [S6](13-Behavioral-Story-Bank.md#s6). Be ready with specifics: `[fill in: what's in your CLAUDE.md; what the "code graph" is; how you measured AI-assisted commits (for example, Co-Authored-By trailers); what quality signal you watched; one honest downside you hit]`.

**Likely follow-ups:** "Any downsides?" Have a real one ready. Common ones: larger PRs, reviewers skimming, and code that's subtly non-idiomatic for the codebase until the context docs improve.

---

### Q13. What would your first 90 days look like?  `[P0]`
**Say this first:** "Listen and learn, deliver something small, then improve how the team works. In the first month I'd meet everyone, read the code and ADRs, understand the agentic framework and where it hurts, and ship a few small PRs to learn the deploy path. In the second month I'd own a meaningful piece, ideally one that improves quality or reliability, like the eval or tracing setup, and start regular 1:1s and code-review norms. In the third month I'd propose, with the team, a short list of standards and a roadmap for the gaps we found."

| Phase | Focus | Concrete outputs |
|---|---|---|
| **Days 1–30: Learn** | People, system, domain | 1:1 with each engineer, the PO, data and platform leads, and the compliance contact. A system map. Read past incidents. Learn the domain (members, providers, claims, prior authorization). Ship 2–3 small PRs. |
| **Days 31–60: Contribute** | Own something real | Ship a quality or reliability improvement. Start the weekly trace review. Baseline the metrics: eval scores, latency, cost, DORA. |
| **Days 61–90: Improve** | Standards and roadmap | Co-written standards (Q1), a gap roadmap for evals, observability, and security, and growth plans with each junior. |

**Don't:** rewrite things in month one, or import your old company's practices before understanding why things are the way they are.

**Your angle:** [S10](13-Behavioral-Story-Bank.md#s10) (you onboarded 10+ teams by understanding their needs first) · [S6](13-Behavioral-Story-Bank.md#s6).

---

### Q14. How do you measure your team's success?  `[P0]`
**Say this first:** "Three lenses: outcomes, delivery, and team health. Outcomes are the business and product metrics; for an AI feature that means task success, eval scores, adoption, and cost per task. Delivery is DORA-style: lead time, deploy frequency, change-fail rate, and recovery time. Team health is whether people are growing and want to stay. I'm wary of vanity metrics like lines of code or story points."

| Lens | Metrics | Example |
|---|---|---|
| **Outcomes (AI-specific)** | Eval pass rate trend, groundedness/faithfulness, % answers with valid citations, human-override or escalation rate, containment/deflection (member service), user satisfaction | "Faithfulness 0.86 → 0.93 over the quarter" |
| **Efficiency** | p95 latency, $ per conversation or task, token usage | "$0.04 per conversation at p95 3.2s" |
| **Delivery (DORA)** | Change lead time, deployment frequency, failed-deployment recovery time, change fail rate, deployment rework rate | "Prompt changes go to prod same day, behind the eval gate" |
| **Team health** | Growth-plan progress, 1:1 signals, a light pulse survey (SPACE dimensions), retention | "Every junior owns a component by Q2" |

**Your angle:** [S1](13-Behavioral-Story-Bank.md#s1) (per-turn cost tracking) · [S12](13-Behavioral-Story-Bank.md#s12) (MTTR focus at Wayfair).

---

### Q15. What's your definition of done for an AI feature?  `[P1]`
**Say this first:** "It's merged, it's measured, and it's operable. That means code reviewed and tested, the eval set updated with the feature's cases and passing thresholds, tracing and dashboards in place, a cost estimate, the PHI and threat-model checklist done, a flag and rollback path, a runbook, and the PO has accepted it against the success criteria we agreed on up front."

---

### Q16. A stakeholder wants to launch before quality is there. What do you do?  `[P1]`
**Say this first:** "I make the gap visible with data and offer a safe way to launch something. For example: 'We're at 82% against a 90% target, and here are the failure types.' Then: launch to internal users first, keep a human in the loop, or narrow the scope to the question types where we're above the bar. Ideally the launch gates were agreed before we started, so this becomes a check against the plan instead of an argument. If they still want to go, I write down the risk and escalate together. In healthcare I won't compromise on anything touching PHI or member-impacting decisions."

---

## Key terms

| Term | One-line meaning |
|---|---|
| ADR | Architecture Decision Record: a short doc capturing context, decision, and consequences |
| RFC / design doc | Proposal circulated for feedback *before* building |
| Eval gate | CI step that blocks a merge if eval scores regress past a threshold |
| Shadow / canary | Run the new model on copied traffic without serving it (shadow), or serve it to a small percentage (canary) |
| DORA metrics | Change lead time, deployment frequency, failed-deployment recovery time, change fail rate, deployment rework rate |
| SPACE | Satisfaction, Performance, Activity, Communication, Efficiency: a multi-dimensional developer-productivity framework |
| Appetite | Shape Up: a fixed time budget for a problem, with scope flexing to fit |
| Security trimming | Filtering retrieved documents to what the requesting user is allowed to see |

---

## References
- [Google Engineering Practices: Code review](https://google.github.io/eng-practices/review/): basis for your team's review norms.
- [Google: Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html): why small PRs; useful when coaching.
- [ADR GitHub organization](https://adr.github.io/): ADR formats and tools.
- [Michael Nygard: Documenting architecture decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions): the original ADR post.
- [Joel Parker Henderson: ADR templates](https://github.com/joelparkerhenderson/architecture-decision-record): copy-paste templates and examples.
- [DORA: Software delivery performance metrics](https://dora.dev/guides/dora-metrics-four-keys/): the current five delivery metrics.
- [DORA: State of AI-assisted Software Development 2025](https://dora.dev/research/2025/dora-report/): AI as an amplifier; relevant to your AI-adoption story.
- [The SPACE of Developer Productivity (ACM Queue)](https://queue.acm.org/detail.cfm?id=3454124): a team-health and productivity framework beyond output counts.
- [Shape Up: Set boundaries (appetite)](https://basecamp.com/shapeup/1.2-chapter-03): fixed time, variable scope for uncertain work.
- [Google SRE Book: Postmortem culture](https://sre.google/sre-book/postmortem-culture/): blameless postmortems.
- [Martin Fowler: The practical test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html): the classic pyramid your LLM version extends.
- [Hamel Husain: Your AI product needs evals](https://hamel.dev/blog/posts/evals/): eval-driven development and error analysis.
- [Eugene Yan: Patterns for building LLM-based systems & products](https://eugeneyan.com/writing/llm-patterns/): evals, guardrails, caching, feedback; good vocabulary for standards.
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents): "start simple"; useful when justifying framework choices.
- [Claude Code: Best practices](https://www.anthropic.com/engineering/claude-code-best-practices): CLAUDE.md and agentic coding workflows behind your S6 story.
- [Will Larson: Writing engineering strategy](https://lethain.com/eng-strategies/): how to turn many decisions into a coherent strategy.
- [Will Larson: Your first 90 days as CTO or VP Engineering](https://lethain.com/first-ninety-days-cto-vpe/): written for executives, but the learn → contribute → improve shape fits a lead.
- [Lara Hogan: Questions for our first 1:1](https://larahogan.me/blog/first-one-on-one-questions/): for your first-30-days 1:1s.
- [ThoughtWorks Technology Radar](https://www.thoughtworks.com/radar): the adopt/trial/assess/hold model for an internal radar.
- [METR: Early-2025 AI and experienced developer productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/): evidence for measuring AI-tool impact rather than assuming it.
