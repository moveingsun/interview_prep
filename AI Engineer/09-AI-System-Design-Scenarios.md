# 09 · AI System Design Scenarios

[← Index](00-Index.md) · **Manager-round priority:** High · **Read time:** ~40 min (practice out loud)

> **Why this matters for this role:** The JD has you owning "solution design for agentic AI systems, GenAI integrations, RAG architectures, and infrastructure," and being the technical escalation point. A hiring manager won't ask you to code. They'll say *"How would you build X for our members?"* and listen for structure, trade-offs, safety, and how you'd get a team to deliver it. Practice each scenario as a 5–8 minute talk track.

## Primer: a reusable answer framework

Say the steps out loud. Interviewers reward visible structure.

```
1. Clarify      → who are the users, what's the job-to-be-done, what does success look like (metric)?
2. Data & risk  → sources, freshness, PHI?, who may see what, risk tier (info vs decision support vs action)
3. Architecture → ingestion → retrieval/tools → orchestration (LangGraph) → model(s) → UI/API
4. Model choice → quality vs latency vs cost; start with a strong model, optimize later
5. Eval plan    → golden set, metrics, release thresholds (see 07)
6. Guardrails   → security trimming, injection defense, HITL for decisions/actions (see 08)
7. Ops          → tracing, dashboards, cost per turn, alerts, fallbacks
8. Rollout      → shadow → pilot with friendly users → staged GA; feedback loop
9. Team plan    → milestones, who owns what, what I'd build myself vs delegate
```

Rule of thumb: **spend the first 1–2 minutes clarifying**, and **always end with how you'd measure success and roll out safely**. If time is short, name the step you're skipping.

**Default reference architecture** (reuse it across scenarios):

```
            ┌──────────────── Ingestion (batch / event) ─────────────────┐
 SharePoint │ crack docs → chunk → enrich metadata (plan, year, ACL) →   │
 PDFs, KB   │ embed → Azure AI Search index (vector + keyword fields)    │
            └────────────────────────────────────────────────────────────┘
 client ─► APIM (auth, quotas, token metering) ─► API (FastAPI on AKS / Container Apps)
                                                     │
                                         LangGraph orchestrator
                          ┌─────────────┬────────────┼──────────────┬─────────────┐
                          ▼             ▼            ▼              ▼             ▼
                    input guards   retrieve (hybrid  tools (claims  LLM (Foundry   output guards
                    (Prompt        + semantic rank,  API, benefits  deployment,    (groundedness,
                    Shields)       security filter)  API; scoped)   pinned ver.)   PHI check)
                                                     │
                     checkpointer (short-term memory) · store (long-term memory)
                     traces → App Insights / LangSmith · eval pipeline in CI
```

## Questions & answers

### Q1. Design an assistant that answers members' questions about their benefits and coverage.  `[P0]`
**Clarify (say these out loud):** Member-facing (web/app) or internal for call-center reps? (Internal first is lower risk. Recommend it as phase 1.) Which plans and products? General plan documents or *this member's* specifics (deductible met, claims status)? Languages? Success metric: containment rate, CSAT, call deflection, accuracy on a golden set.

**Talk track (~30 sec version):** "Phase 1 is RAG over plan documents (Evidence of Coverage, Summary of Benefits, policies), grounded with citations. Phase 2 adds member-specific tools: accumulators and claims status through existing APIs, scoped to the authenticated member on the server side. LangGraph routes between 'general benefits question' (RAG), 'my account' (tool calls), and 'needs a human' (handoff). Anything about denials, appeals, or clinical advice goes to a human."

```
member ─► auth ─► router ─┬─► RAG over plan docs (filter: member's plan_id + plan_year) ─┐
                          ├─► tools: get_accumulators(member_id from token), claim_status ─┼─► answer + citations
                          └─► handoff to Member Services (appeals, clinical, low confidence)┘
```

**Key design points:**
- **Metadata filters are critical:** plan ID, plan year, effective date, line of business. The #1 error source is answering from the *wrong plan's* document.
- **Hybrid search + semantic ranker.** Benefits text is full of exact terms (CPT codes, "out-of-pocket maximum") where keyword matching helps.
- **Grounding:** answer only from retrieved context, cite the section, and say "I don't know" with a handoff when retrieval confidence is low.
- **Numbers come from systems of record** (tools), never generated from documents. "Your deductible remaining is $X" must come from the accumulator API.

**Trade-offs:** Member-facing means a higher bar (accessibility, multilingual, legal review of disclaimers) than an internal rep assistant. Starting internal gets real data and SME feedback with a human filter in front.
**Failure modes:** wrong plan year; outdated documents; the model "computing" cost shares; overconfident answers on edge cases (out-of-network, prior auth required).
**Metrics:** accuracy and groundedness on a golden set per category; containment; escalation rate; thumbs-down rate; p95 latency; cost per conversation.
**Your angle:** [S1](13-Behavioral-Story-Bank.md#s1) is the same pattern: a domain assistant combining a semantic layer for numbers with a curated KB for explanations, plus citation checks. "I learned that numeric questions should hit a governed data layer, not RAG."

### Q2. Design a prior-authorization assistant for nurse reviewers.  `[P0]`
**Clarify:** Which services and policies (start with one high-volume category)? What do the inputs look like (faxed PDFs, clinical notes, structured FHIR data)? What's the reviewer's workflow today? Success: review time per case, consistency, turnaround SLA compliance (see CMS-0057-F in [08](08-Security-Responsible-AI-and-HIPAA.md)), override rate.

**Talk track:** "The AI never decides. It prepares the case. It extracts relevant clinical facts from the submitted documents, maps them against each criterion in the applicable medical policy, and shows met / not met / missing information, with a citation to the page in the record and the policy clause. The nurse sees that side by side, edits, and makes the call. We log what the AI suggested vs what the reviewer decided."

```
PA request + docs ─► doc intelligence (OCR, layout) ─► chunk + PHI-scoped store (per case)
                                                         │
 medical policy KB (versioned) ─► retrieve criteria ─► LangGraph: for each criterion:
                                                         find evidence → assess → cite
                                                         │
                         structured summary {criterion, evidence, page, status, confidence}
                                                         │
                        reviewer UI ─► human decision ─► audit log (AI suggestion vs decision)
```

**Key design points:**
- **Structured output** per criterion (JSON schema), not free text. It's easier to review, evaluate, and audit.
- **Per-case isolation:** a case's documents are only retrievable within that case. No cross-member leakage.
- **Policy versioning:** use the policy version effective on the date of service.
- **Missing-info detection** is often the biggest win: request missing records early instead of pending.

**Trade-offs:** More automation (auto-approve clear approvals) vs the regulatory and reputational risk. If ever considered, auto-*approve* only, never auto-deny, and only with governance sign-off.
**Failure modes:** OCR errors on faxes; evidence found but misread (negation: "no history of…"); automation bias (reviewers rubber-stamping). Watch the override rate. If it's near zero, that's suspicious.
**Metrics:** criterion-level precision/recall against nurse labels; time per review; override rate; turnaround SLA; fairness slices.
**Your angle:** [S2](13-Behavioral-Story-Bank.md#s2): the LLM proposes, the human confirms, and nothing is written without approval. Same philosophy.

### Q3. Design a call-center agent-assist with short-term and long-term memory.  `[P0]`
**Clarify:** Real-time during the call (needs speech-to-text and low latency) or after-call (summaries)? What does "remember" mean: this call's context, or the member's history across calls? Success: average handle time (AHT), first-call resolution, after-call work time.

**Talk track:** "Short-term memory is the live conversation state, kept in a LangGraph checkpointer per call/thread, with summarization when the transcript gets long. Long-term memory is durable facts about the member across calls ('prefers Spanish', 'open appeal on claim X', 'called twice about the same bill'), kept in a store namespaced by member ID, with strict retention and access. Most 'memory' here should come from systems of record. CRM and claims are the truth. AI memory is for summaries and preferences, not a shadow database of PHI."

```
call audio ─► speech-to-text (streaming) ─► LangGraph (thread_id = call_id)
                                              ├─ short-term: checkpointer (messages, running summary)
                                              ├─ long-term: store[("member", member_id)] → prior-call summaries, prefs
                                              ├─ RAG: policies / scripts / KB
                                              └─ tools: CRM, claims, eligibility (read-only)
                                              ▼
                       rep sidebar: suggested answers + next best action + live summary
 after call ─► summarize → rep edits/approves → write to CRM + long-term store (background job)
```

**Key design points:**
- **Write memory in the background, after the rep approves the summary.** That's better quality and gives a human check on what's persisted.
- **Memory hygiene:** TTL/retention, a way to delete, no raw PHI beyond what's needed, and a provenance tag on each memory item (source, date).
- **Latency:** suggestions need to land within ~1–2s, so use a smaller/faster model for live suggestions and a bigger one for the after-call summary.

**Trade-offs:** Rich long-term memory personalizes and saves time, but it's PHI, can go stale, and can be wrong. Prefer re-deriving from systems of record over remembering.
**Metrics:** AHT, after-call work time, suggestion acceptance rate, summary edit distance (how much reps change it), rep CSAT.
**Your angle:** Your current project ([S5](13-Behavioral-Story-Bank.md#s5)) uses short- and long-term memory with LangGraph. Explain how *you* split thread state vs the store, and what you decided not to remember. `[fill in]` See [06](06-Memory-and-Context-Engineering.md).

### Q4. We're building a shared "agentic AI framework" that many teams will build agents on. How would you design it?  `[P0]`
**Clarify:** Who are the consumers (data scientists, app teams, low-code users)? How many agents and teams? What has to be standardized vs left flexible? Success: time-to-first-agent for a new team, number of agents in production, incidents, cost visibility.

**Talk track:** "I'd build a 'paved road', not a monolith. Standardize the cross-cutting concerns every agent needs: identity and entitlements, model access through a gateway, a tool/connector registry, memory and persistence, guardrails, tracing, evals, and deployment. Leave the agent logic itself to the teams, using LangGraph as the default orchestration. The best platform is one where the secure, observable way is also the easiest way."

```
 team agents (LangGraph graphs, templates)  ── built on ──►  Platform SDK + templates
 ┌───────────────────────────────────────────────────────────────────────────────┐
 │ Model gateway (APIM): auth, quotas per team, token metering, fallback, router  │
 │ Tool registry / MCP servers: vetted connectors (claims, eligibility, docs),    │
 │   each with scopes + owner                                                    │
 │ Knowledge: shared Azure AI Search indexes / knowledge bases with ACLs          │
 │ Memory: managed checkpointer (Postgres) + long-term store with retention       │
 │ Guardrails: Prompt Shields, PHI filters, HITL interrupt pattern                │
 │ Observability: OTel tracing → App Insights; cost dashboards per team/agent     │
 │ Evals: dataset + CI template; release gates                                    │
 │ Governance: agent registry (owner, risk tier, data, eval results)              │
 └───────────────────────────────────────────────────────────────────────────────┘
```

**Key design points:**
- **Start from 2–3 real use cases** and extract the platform from them. Don't build the platform in a vacuum.
- **Golden path template:** `cookiecutter`-style repo with graph skeleton, eval suite, tracing, and CI already wired. A new agent in a day, not a month.
- **Tool registry with ownership:** each tool has an owner team, scopes, and an SLA. Prefer MCP for interoperability.
- **Multi-tenancy:** per-team quotas and cost attribution, so one team's runaway agent doesn't starve others (429s).
- **Versioning and deprecation** policies for the SDK and models.

**Trade-offs:** Too opinionated and teams bypass you. Too loose and you get 20 inconsistent, ungoverned agents. Make the guardrail layer mandatory and the orchestration flexible. Build vs buy: Foundry Agent Service (managed hosting, built-in tools) vs self-hosted LangGraph (control, portability). Many orgs use both. Pick per workload.
**Your angle:** Strong fit. [S3](13-Behavioral-Story-Bank.md#s3): you built Watt, the *front door* for multiple AI apps (registry, entitlements, signed links, gateway routing). [S10](13-Behavioral-Story-Bank.md#s10): you onboarded 10+ teams onto Composer, so you know adoption is a product problem. [S6](13-Behavioral-Story-Bank.md#s6): you set team-wide AI tooling standards. [S12](13-Behavioral-Story-Bank.md#s12): you built an internal developer platform (Backstage) at Wayfair.

### Q5. Design a pipeline to extract data from claims documents / correspondence.  `[P1]`
**Clarify:** Document types (claim forms, EOBs, appeal letters, ID cards, medical records)? Volume and latency (batch overnight vs near real-time)? Accuracy needs per field? What happens downstream with the data?

**Talk track:** "It's a classic document-intelligence pipeline: classify, extract, validate, route. I'd use a layout/OCR service (Azure AI Document Intelligence has prebuilt models, including US health insurance cards) for structure, then an LLM with a strict JSON schema for the fields the prebuilt models don't cover. Every field gets validated with business rules, and low-confidence documents go to a human review queue. Human corrections feed back into the eval set."

```
 intake (blob/event) ─► classify doc type ─► OCR/layout ─► field extraction (prebuilt model │ LLM + JSON schema)
        ─► validate (rules: member exists, dates valid, totals add up, code formats)
        ─► confidence ≥ threshold? ── yes ─► write to system of record (idempotent)
                                   └─ no ──► human review queue ─► corrections → eval set
```

**Key design points:** It's batch, so use **batch APIs** (cheaper) and queue-based autoscaling. Writes must be **idempotent** (dedupe on doc hash). **Field-level confidence** and validation rules catch most LLM errors cheaply.
**Metrics:** field-level precision/recall, straight-through-processing rate, human review rate, cost per document, throughput.
**Your angle:** This is your data-engineering home turf. [S2](13-Behavioral-Story-Bank.md#s2) is validation and parity checks with an LLM judge. [S14](13-Behavioral-Story-Bank.md#s14): your KEDA job-execution service is exactly the queue-driven autoscaling backbone. Also the streaming XML OOM fix (>1GB → ~200MB) from your resume.

### Q6. How do you choose which model to use?  `[P0]`
**Say this first:** "I start with the most capable model that meets compliance, to prove the task is solvable and set a quality ceiling on the eval set. Then I optimize down. Can a smaller, cheaper, faster model hit the bar for this step? Often the router or classifier step can use a small model while the final answer uses a big one. The decision is driven by the eval results plus latency and cost budgets, not by benchmarks or hype."
**If they dig deeper:** Check context window, tool-calling and structured-output reliability, regional availability and data residency, rate limits/quota, version lifecycle (retirement dates), and cost per 1K tokens at expected volume.

### Q7. How would you reduce the cost and latency of an LLM application?  `[P0]`
**Say this first:** "Measure first, per step, then pull the biggest levers. Shrink the context, because tokens drive both cost and latency. Route easy requests to smaller models. Cache stable prompt prefixes. Stream the response so perceived latency drops. Cap agent steps. For batch workloads, use batch APIs. And pick the right deployment type: pay-as-you-go for spiky traffic, provisioned throughput for steady, latency-sensitive load."
**If they dig deeper (the levers):**

| Lever | Effect | Watch out for |
|---|---|---|
| Context trimming (fewer/better chunks, summarize history) | ↓ cost, ↓ latency, often ↑ quality | Dropping the one chunk that mattered. Validate with evals |
| Model routing / cascade (small model first, escalate if low confidence) | ↓ cost 50–80% on easy traffic | Router errors. Eval the router itself |
| Prompt caching (stable system prompt + tools first, variable parts last) | ↓ input cost and latency on repeated prefixes | Only works if the prefix is byte-identical; order matters |
| Semantic caching (reuse answers to similar questions) | Big savings on FAQ-like traffic | **Risky with personalized or PHI answers**. Cache only generic, non-member-specific answers, and scope by plan/version |
| Streaming | ↓ perceived latency (TTFT) | Output guards must handle partial text |
| Parallel tool calls / parallel retrieval | ↓ wall-clock | Rate limits |
| Batch API (async, discounted) | ↓ cost for offline jobs | Hours of turnaround |
| Max steps / token budgets per request | Caps runaway agents | Must fail gracefully |
| PTU (provisioned throughput) vs pay-as-you-go | PTU: predictable latency, reserved capacity; PAYG: elastic, pay per token | PTU is wasted if utilization is low. Spill over to PAYG for bursts |

**Your angle:** Your whole resume is performance and cost work: [S7](13-Behavioral-Story-Bank.md#s7) (10× cost spike), [S4](13-Behavioral-Story-Bank.md#s4) (85.6s → 8.8s), [S14](13-Behavioral-Story-Bank.md#s14) (20s → 5s with caching and precomputation), [S1](13-Behavioral-Story-Bank.md#s1) (per-turn cost tracking). "I approach LLM cost the same way I approached Snowflake cost: instrument, find the hot spot, fix the loop."

### Q8. The assistant is giving confident but wrong answers in production. What do you do?  `[P0]`
**Say this first:** "Contain, diagnose, fix, prevent. **Contain:** if it's high-risk (coverage, money), narrow the scope or route those intents to a human right away. That's a config flag, not a redeploy. **Diagnose:** pull the traces for the reported cases and classify them. Was the right source not retrieved, retrieved but ignored, was the source itself wrong or stale, or is the model reasoning badly? **Fix** the dominant cause. **Prevent:** add the cases to the eval set, add a groundedness or citation check that blocks unsupported answers, and set up an alert on that metric."
**If they dig deeper:**
- Retrieval fixes: metadata filters (plan year), chunking, hybrid search, reranking.
- Generation fixes: "answer only from context, otherwise say you don't know", required citations, and a groundedness check before showing the answer.
- Calibration: show confidence or "verify with…" language for edge categories. Make "I don't know" an acceptable, tested behavior.
- Communicate: tell stakeholders what happened, the blast radius, and the fix. Treat it like an incident with a blameless postmortem.

**Your angle:** [S12](13-Behavioral-Story-Bank.md#s12) Post-mortem Wizard: you built incident-postmortem tooling, so lean on that culture. [S8](13-Behavioral-Story-Bank.md#s8): root-cause classification with the PM.

### Q9. When would you NOT use an LLM or an agent?  `[P0]`
**Say this first:** "When a deterministic solution works: rules, SQL, a lookup, or a classic ML model. These are cheaper, faster, testable, and auditable. In healthcare especially, anything that's a calculation (cost share, eligibility) should come from systems of record. I also avoid agents when a fixed workflow will do. A predictable chain of steps beats an autonomous loop for most enterprise tasks. I add autonomy only where the path genuinely can't be known in advance."
**Your angle:** In [S1](13-Behavioral-Story-Bank.md#s1)/[S4](13-Behavioral-Story-Bank.md#s4), numeric questions go to a governed semantic layer (Cortex semantic views), not free-form LLM reasoning. The LLM picks the query, the warehouse computes the number.

### Q10. How do you handle rate limits (429s) and provider outages?  `[P1]`
**Say this first:** "At the gateway: APIM in front of model deployments with token-based quotas per consumer, load balancing across multiple deployments or regions, and circuit breakers. In the app: retries with exponential backoff and jitter for 429/5xx, timeouts on every call, and a graceful fallback (a smaller model, a cached generic answer, or 'we're having trouble, here's how to reach us'). Steady high-volume workloads go on provisioned throughput."
**If they dig deeper:** Separate quotas for interactive vs batch traffic so a batch job can't starve the chat users. LangGraph checkpoints let a long workflow resume after a failure instead of restarting.
**Your angle:** Your APIM and workload-identity work, and the KEDA autoscaling service ([S14](13-Behavioral-Story-Bank.md#s14)).

### Q11. How would you roll out a new AI feature safely?  `[P0]`
**Say this first:** "In stages, with gates. Offline evals pass the agreed threshold. **Shadow mode**: runs on real traffic, logged but not shown, and we compare. **Pilot** with a small group of friendly internal users and SMEs who give feedback. **Staged rollout** behind a feature flag (5% → 25% → 100%) with dashboards and a kill switch. For high-risk outputs, the human-in-the-loop stays permanently, not just during the pilot."
**Your angle:** [S8](13-Behavioral-Story-Bank.md#s8): for the PnL release you reconciled against the traders' workbook *before* trusting the system. That's parallel-run validation, the same idea as shadow mode.

### Q12. How would you break a design like this into work for a team of 3–4 engineers?  `[P0]`
**Say this first:** "Thin end-to-end slice first. In the first two weeks, one narrow use case goes all the way from ingestion to UI with tracing and a 20-case eval set, even if every piece is basic. Then parallelize along clean seams: one engineer owns ingestion and the index, one owns the orchestration graph and tools, one owns evals and observability, and I take the riskiest piece myself plus reviews. Juniors get well-scoped pieces with a clear definition of done (for example, adding eval cases and a new tool behind an existing interface) and pair with me on the first one."
**If they dig deeper:** Write a short design doc / ADR for the big decisions (framework, index schema, memory design) so the team aligns before building. Demo every week to the PO.
**Your angle:** [S3](13-Behavioral-Story-Bank.md#s3): you wrote the specs the frontend engineers implemented. [S1](13-Behavioral-Story-Bank.md#s1): you shipped a working assistant in 3 weeks. See [12](12-Team-Leadership-and-Delivery.md) for estimation and delivery.

## References
- [Building effective agents (Anthropic)](https://www.anthropic.com/engineering/building-effective-agents): workflows vs agents. "Start simple" is the best argument for Q9.
- [Building A Generative AI Platform (Chip Huyen)](https://huyenchip.com/2024/07/25/genai-platform.html): layer-by-layer platform design (gateway, guardrails, caching, routing). Maps to Q4.
- [Patterns for Building LLM-based Systems & Products (Eugene Yan)](https://eugeneyan.com/writing/llm-patterns/): evals, RAG, guardrails, caching, and feedback patterns.
- [Azure OpenAI deployment types](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/deployment-types): standard / global / data zone / provisioned / batch.
- [Provisioned throughput (PTU) concepts](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/provisioned-throughput): when reserved capacity pays off.
- [Azure OpenAI prompt caching](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/prompt-caching): how prefix caching works and how to structure prompts for it.
- [Model router in Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/model-router): managed routing between models by prompt complexity.
- [AI gateway capabilities in Azure API Management](https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities): token limits, semantic caching, load balancing, token metrics.
- [Azure AI Document Intelligence overview](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview): OCR, layout, prebuilt models (incl. health insurance card).
- [CMS-0057-F fact sheet](https://www.cms.gov/newsroom/fact-sheets/cms-interoperability-and-prior-authorization-final-rule-cms-0057-f): why prior-auth speed matters (Q2).
- [AI Engineer interview questions: RAG, agents, evals, production (PracHub)](https://prachub.com/resources/ai-engineer-interview-questions-2026-rag-agents-evals-and-production-systems): candidate-reported design prompts (incl. an insurance-claims agent) to practice with.
