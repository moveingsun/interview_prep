# 13 · Behavioral Story Bank (STAR)

[← Index](00-Index.md) · **Manager-round priority:** High · **Read time:** ~20 min, then rehearse out loud

> **Why this matters for this role:** Managers judge leadership through stories, not opinions. Every "how would you…" answer is twice as convincing with "…and here's when I did it." These stories come from your resume. **Fill every `[fill in]` before Friday.** Specific names, numbers, and what *you* said are what make a story believable.

## How to tell a story (2 minutes max)

- **S**ituation (15 sec): context and stakes, in one or two sentences.
- **T**ask (10 sec): what *you* owned.
- **A**ction (60 sec): what *you* did, using "I" not "we", including one decision and its trade-off.
- **R**esult (20 sec): a number, plus who benefited.
- **L**esson (15 sec): what you'd do differently. Seniors always have one.

Tip: open with a one-line headline ("This is about a 10× cost spike I tracked down in a day…") so the listener knows where it's going.

## Question → story map

| If they ask about… | Primary | Backup |
|---|---|---|
| An AI system you built end to end | [S1](#s1) | [S5](#s5), [S2](#s2) |
| How you evaluate or monitor AI quality | [S1](#s1) | [S2](#s2), [S4](#s4) |
| Human-in-the-loop / safety / responsible AI | [S2](#s2) | [S9](#s9) |
| Leading without authority / influencing | [S6](#s6) | [S10](#s10), [S3](#s3) |
| Mentoring / teaching | [M1](#m1) | [S10](#s10), [S6](#s6) |
| Working with product / stakeholders | [S8](#s8) | [S3](#s3) |
| Ambiguity / unclear requirements | [S8](#s8) | [S1](#s1) |
| Debugging under pressure / escalation | [S7](#s7) | [S9](#s9), [S11](#s11) |
| Performance / scale | [S9](#s9) | [S14](#s14), [S11](#s11) |
| Large migration / change management | [S11](#s11) | [S10](#s10) |
| Prioritization when overloaded | [S14](#s14) | [S1](#s1) |
| Incidents / operational culture | [S12](#s12) | [S11](#s11) |
| Security / access control mindset | [S9](#s9) | [S3](#s3) |
| A failure or mistake | [F1](#f1) *(fill in)* | the "Lesson" part of [S7](#s7) or [S8](#s8) |
| Conflict / disagreement | [C1](#c1) *(fill in)* | [S8](#s8) |
| Healthcare experience | [S13](#s13) | [S2](#s2) |

---

<a id="s1"></a>
## S1 · Load Deal AI: a domain assistant in 3 weeks
- **Situation:** Load-deal questions (pricing, volumes, PnL) required someone who knew both the data model and the business rules. `[fill in: who asked them, e.g., traders/analysts, and how they got answers before]`
- **Task:** Build a domain assistant fast, and make it trustworthy, not just impressive in a demo.
- **Action:** Used a **Snowflake Cortex agent** over a **semantic view** for numeric questions, so the model writes SQL against governed definitions instead of guessing, plus a **curated knowledge base** for business rules. Added a **LangGraph pipelines agent** with **citation checks**: answers must point to their sources. Built a **20-question eval set** with expected answers, logged **per-turn cost**, and shipped a chat UI that renders the SQL, tables, and charts so users can verify results.
- **Result:** Delivered in **3 weeks**. `[fill in: eval pass rate, avg cost/turn, adoption/users, feedback]`
- **Lesson:** "Eval first. The 20 questions were what let me change prompts and models without fear. I'd also bring a business user in earlier to write those questions." `[adjust to your real lesson]`
- **Use for:** proudest project, eval, RAG vs SQL, speed of delivery.

<a id="s2"></a>
## S2 · Data Validation Service with an LLM judge (built solo)
- **Situation:** ADF pipelines load data into Snowflake and SQL Server. Mismatches between outputs and sources were found late and triaged manually. Many were *timing races* (data arriving mid-check) rather than real defects.
- **Task:** Automate validation end to end and cut the noise.
- **Action:** Built checks for row and aggregate parity, nulls, freshness, and schema. Added an **LLM judge** that classifies each mismatch as a timing race or a real defect. Made a key design decision: **the system never writes or fixes anything without human confirmation.** The AI triages; a person decides.
- **Result:** `[fill in: # pipelines covered, false-alarm reduction, time saved, a real defect it caught]`
- **Lesson:** "LLM judges need calibration. I compared its labels with my own on `[fill in: N]` cases before trusting it."
- **Use for:** human-in-the-loop, responsible AI, LLM-as-judge, working solo end to end.

<a id="s3"></a>
## S3 · Watt (AI Shell): specs other engineers built from
- **Situation:** The company needed one sign-in front door for multiple AI apps (Doc Intelligence, Data Intelligence, Data Validation) with consistent permissions.
- **Task:** Own the backend and define the contract the frontend team would build against.
- **Action:** Designed an **entitlements-driven app registry**, **signed short-lived bundle links**, **UI-element-level permissions**, and API-gateway routing. **Wrote the specs the frontend engineers implemented.** `[fill in: how you reviewed their work / answered questions / handled a spec change]`
- **Result:** `[fill in: number of apps onboarded, time to add a new app]`
- **Lesson:** "A clear written spec is the cheapest form of leadership. It let people move without waiting on me."
- **Use for:** leading through design, cross-team work, security.

<a id="s4"></a>
## S4 · Data Intelligence: plain-language questions over cost data
- **Situation:** Cost and market-data questions needed analysts and were slow.
- **Action:** Built the Snowflake Cortex layer: a cost schema, **semantic views**, an agent, and a **turn log** for every interaction (for observability and eval mining).
- **Result:** Cost-query time **85.6s → 8.8s**. `[fill in: what drove the speedup — semantic view vs raw tables, pre-aggregation, etc.]`
- **Use for:** "when RAG is the wrong tool" (structured data → semantic layer / text-to-SQL), observability.

<a id="s5"></a>
## S5 · Current project: memory + RAG on LangGraph and Azure AI Search (Foundry)
- **Situation:** `[fill in: what the service is for and who uses it]`
- **Task:** `[fill in: your ownership]`
- **Action:** `[fill in: graph shape (nodes), short-term memory (checkpointer type, trimming/summarization), long-term memory (store, namespaces, what is remembered and when it's written), retrieval (index design, hybrid + semantic ranker, chunking), guardrails, eval]`
- **Result / status:** `[fill in: what's live, early metrics, what you're solving next]`
- **Lesson / open question:** `[fill in: one honest hard problem, e.g., stale memories, retrieval misses, latency]`
- **Use for:** "what are you working on now", memory, RAG, Azure. Templates are in [04](04-Azure-AI-Search-and-Foundry.md) and [06](06-Memory-and-Context-Engineering.md).

<a id="s6"></a>
## S6 · Driving AI-assisted development across a codebase
- **Situation:** The Load Deal domain is complex, and AI coding tools kept losing context between sessions.
- **Action:** Set up Claude Code for the repo (CLAUDE.md, code graph, docs). Built a **domain knowledge base** (10 docs, ~100 sections) that carries load-deal context across sessions. `[fill in: did you share it with others, demo it, write guidelines?]`
- **Result:** AI-assisted commits **36% → 80%** (Jun → Aug 2026). `[fill in: quality guardrails — e.g., review rules, tests required]`
- **Lesson:** "AI tools amplify whatever context and standards you give them. The investment is in docs and review discipline, not the tool."
- **Use for:** influencing how people work, team productivity, juniors and AI tools, evaluating new tools.

<a id="s7"></a>
## S7 · The 10× Snowflake cost spike
- **Situation:** Warehouse spend jumped to about **100 credits/day**, roughly 10× normal.
- **Action:** Profiled query history and found a **query loop consuming 98% of execution time**. `[fill in: how you found it — query_history, warehouse metering, tagging]` Removed the loop. `[fill in: and added a guard/alert so it couldn't recur?]`
- **Result:** Back to about **11 credits/day**.
- **Lesson:** "Cost is a production metric. Now I put cost tracking in from day one, which is why S1 has per-turn cost."
- **Use for:** escalation point, debugging, cost awareness in AI (token cost is the same story).

<a id="s8"></a>
## S8 · Reconciling the PnL engine with the traders' workbook
- **Situation:** Before release, the new PnL engine had to match the traders' trusted Excel workbook, and it didn't.
- **Action:** Worked with the PM to raise and resolve **60+ discrepancies**, documented across 7 Confluence pages (for example, a missing forward curve and the loads-through cutoff rule). Proposed moving to a **whole-month basis**.
- **Result:** **All 32 deals matched**. Released Aug 2026, saving **3 hours/day** of manual work.
- **Lesson:** "Ambiguity was in the business rules, not the code. Writing each rule down and getting sign-off was what unblocked us."
- **Use for:** stakeholder partnership, ambiguity, quality, and why AI evals need SMEs.

<a id="s9"></a>
## S9 · Shared entitlements service: 3–6s → ~10ms, fail-closed
- **Action:** Eliminated **N+1 permission lookups**, added Redis-first entitlements and indexes, and made access checks **fail closed** (on an error, deny).
- **Result:** Entitlement checks **3–6s → ~10ms**, across AMP, Load Deal, Mobile, and Watt.
- **Use for:** security mindset (directly relevant to RAG security trimming and PHI access), performance.

<a id="s10"></a>
## S10 · Wayfair: onboarding 10+ teams to GCP Composer + Dataform
- **Situation:** Enterprise tech transformation; the on-prem data processing tool was being retired.
- **Action:** Led the migration and **onboarded 10+ data-engineering teams**. `[fill in: docs, office hours, migration guides, how you handled a resistant team]`
- **Result:** `[fill in: timeline met? # pipelines migrated?]`
- **Lesson:** "Adoption is a people problem. Templates and office hours beat mandates."
- **Use for:** influence without authority, teaching at scale, change management, platform thinking for an "agentic AI framework".

<a id="s11"></a>
## S11 · Wayfair: Kronos to Kubernetes
- **Action:** Migrated Kronos (≈2M jobs/week) from on-prem Windows VMs to Kubernetes. Redesigned the GitHub integration.
- **Result:** Supported **200% throughput** at holiday peak. Commit-tracking failures **−85%**; availability **99.5% → 99.9%**.
- **Use for:** large migration, reliability, scaling.

<a id="s12"></a>
## S12 · Wayfair: incident culture and tooling
- **Action:** Improved the **Post-mortem Wizard** (25% more complete incident docs). Built a Slack app for SLO-violation and job alerts (**3,000+ users, 100+ channels**).
- **Use for:** blameless postmortems, operational excellence, being the escalation point.

<a id="s13"></a>
## S13 · Cerner: healthcare revenue-cycle management
- **Action:** Built UI components for an enterprise healthcare revenue-cycle app (patient arrival tracking, appointment inquiry migration while maintaining data integrity).
- **Use for:** "Why healthcare?", familiarity with healthcare workflows and data sensitivity.

<a id="s14"></a>
## S14 · AMP: sole engineer across five services
- **Situation:** Sole full-time engineer for over a year on AMP's services (analytics, metadata, models, outage, market data) and React UI.
- **Action:** Prioritized by user pain and risk. Landing page **20s → 5s** (Redis precompute, parallelism, entitlement fixes; Snowflake reads 13 → 3). Outage management **7s → 1s**. Built a **KEDA job-execution service** from scratch (leader election, DAGs, cascade-cancel, stuck-run recovery). Fixed revenue bugs overstating values up to **12×**.
- **Use for:** prioritization, ownership, "you'll be the escalation point". Also a hook for why you want a team: "I've maxed out what one person can do."

---

## Stories you still need (prepare before Friday)

<a id="m1"></a>
### M1 · Leading three contractors after my manager resigned (~2 months)
- **Situation:** When my manager resigned `[fill in: month, 2026]`, I became the day-to-day lead for three contract engineers on three projects for about two months `[fill in: until a new manager started / what ended it]`:
  - **AI project** `[fill in: which one, e.g., Load Deal AI or Watt]`: an offshore backend contractor and a frontend engineer.
  - **PnL engine:** I built the backend, and the same frontend engineer built the UI.
  - **AMP:** a second frontend engineer. I assigned and reviewed the UI work.
- **Task:** Keep all three projects moving without a manager, while still writing much of the backend code myself.
- **Action:** I set up a daily loop.
  - **End of day:** I wrote a Confluence page or a long message for each person: what to build next, why, and what "done" looks like. For the offshore contractor this meant a full day of progress while I was offline.
  - **Morning, on my way in:** a short chat with each of them on progress and blockers.
  - **In the office:** I reviewed their pull requests, then spent several hours working through problems together.
  - **The rest of the day:** my own backend work.
  - `[fill in: how you set priorities across the three projects, and who you aligned with (PM, skip-level manager)]`
- **Result:** `[fill in: what shipped in those two months (did the PnL release in Aug 2026 fall in this window?), and one contractor who became more independent. What could they do at the end that they couldn't at the start?]`
- **Lesson:** `[adjust to your real lesson]` "Clear written instructions were what made it work across time zones. If the goal and the reason were written down, they could make good decisions without waiting for me."
- **How to say it honestly:** "I led their work day to day." Don't say "I was their manager" unless you also handled hiring, performance, or contracts.
- **Use for:** mentoring, the "no lead title" question, mentoring while coding 40–50% of the time, delegation, working with offshore teams.

<a id="c1"></a>
### C1 · A disagreement or conflict  `[fill in]`
Good shapes: you disagreed with a PM or engineer on a design or scope; you used data or a prototype to resolve it; you "disagreed and committed" when overruled. Avoid stories where the other person is the villain.

<a id="f1"></a>
### F1 · A failure or mistake  `[fill in]`
Pick a real mistake with real impact, then what you changed afterward (a process, a test, or an alert). Candidates: a bug that reached production, an estimate that slipped, or a design you had to redo. Own it in the first sentence.

<a id="p1"></a>
### P1 · Pushing back on a stakeholder or saying no  `[fill in]`
For example, declining a feature or a deadline with a trade-off offer ("we can do X by Friday or X+Y by the 20th").

## References
- [The STAR method explained (MIT CAPD)](https://capd.mit.edu/resources/the-star-method-for-behavioral-interviews/) — the format and examples.
- [Amazon Leadership Principles](https://www.amazon.jobs/content/en/our-workplace/leadership-principles) — not this company, but a widely used checklist of the traits behavioral questions probe (ownership, dive deep, earn trust, hire and develop).
