# 15 · Final-Day Cheat Sheet (read Friday morning)

[← Index](00-Index.md) · **Read time:** ~10 min · No new material today. Just warm up.

## The 3 things you want the manager to remember
1. **"He ships production AI, end to end, with evals and cost tracking"**: Load Deal AI in 3 weeks ([S1](13-Behavioral-Story-Bank.md#s1)) and the current memory + RAG service ([S5](13-Behavioral-Story-Bank.md#s5)).
2. **"He builds the guardrails healthcare needs"**: human-in-the-loop by design ([S2](13-Behavioral-Story-Bank.md#s2)), fail-closed access ([S9](13-Behavioral-Story-Bank.md#s9)), citation checks ([S1](13-Behavioral-Story-Bank.md#s1)).
3. **"He makes other engineers better"**: specs others built from ([S3](13-Behavioral-Story-Bank.md#s3)), 10+ teams onboarded ([S10](13-Behavioral-Story-Bank.md#s10)), AI-assisted commits 36% → 80% ([S6](13-Behavioral-Story-Bank.md#s6)).

## Pitch skeleton (90 sec)
Cerner (healthcare) → Wayfair data platform (Kronos to K8s, 2M jobs/week, onboarded 10+ teams) → BETM: own AMP end to end → applied AI: Load Deal AI (Cortex + LangGraph, evals, cost) · Data Validation (LLM judge, human confirms) · now memory + RAG on LangGraph + Azure AI Search → **"I want to keep building and grow a team that builds this well, in healthcare."**

## Tech one-liners

| Topic | One-liner you can say |
|---|---|
| **RAG** | "Ingest → chunk by structure → embed → index. At query time: rewrite → **hybrid** (BM25 + vector, fused with **RRF**) → **rerank** → **security-trim** → generate with **citations** → check groundedness." |
| **Bad RAG answer** | "First, was the right chunk *retrieved*? If not, it's a retrieval problem (chunking, query, filters, hybrid). If it was retrieved but the answer is wrong, it's a generation problem (prompt, context order, model). I check with traces and the eval set." |
| **When not RAG** | "Aggregations and numbers go to SQL over a governed semantic layer, not vector search. That's why Load Deal AI used a Cortex semantic view." |
| **Azure AI Search** | "Index with vector + text fields; integrated vectorization for chunking and embedding; hybrid query + semantic ranker (L2 rerank); filters for security trimming; agentic retrieval / Foundry IQ knowledge bases for multi-query planning. I check GA vs preview before depending on it." |
| **LangGraph** | "A graph over shared **state**: **nodes** are functions, **edges** decide what runs next (conditional edges for routing), **reducers** merge updates. Compile with a **checkpointer** and a `thread_id` and you get persistence, **interrupts** for human approval, and durable resume." |
| **Workflow vs agent** | "Start with the simplest workflow: chaining, routing, or parallelization. Use an autonomous agent only when the path truly can't be predicted. Multi-agent only when context or permissions need isolating." |
| **Memory** | "Short-term = thread state in the **checkpointer**, kept in budget by trimming or summarizing. Long-term = **store** with namespaces per user, holding facts and preferences (semantic), past episodes (episodic), and learned instructions (procedural). Written in the background, retrieved selectively. Memory never overrides systems of record." |
| **Context engineering** | "Write, select, compress, isolate. The context window is the product, and more context isn't better (context rot)." |
| **Evals** | "Golden set from SMEs and real logs → code checks first → **LLM judge calibrated against human labels**, binary pass/fail → run in CI on every prompt or model change → online monitoring + feedback → mine failures back into the set." |
| **Observability** | "Trace every turn (prompt, retrieved docs, tool calls, tokens, latency, cost). Dashboards: p95 latency, TTFT, cost/turn, error and 429 rate, groundedness, thumbs-down, escalation rate." |
| **Hallucination** | "Ground with retrieval, require citations, verify claims against sources, let the model say 'I don't know', constrain output with schemas, and keep humans in the loop for high-stakes decisions." |
| **Security** | "OWASP LLM Top 10. Prompt injection, especially *indirect* via documents, is #1. Defense in depth: Prompt Shields / input filtering, least-privilege tools, human approval for writes, output validation, security trimming, no secrets in prompts." |
| **HIPAA** | "PHI only under a BAA, minimum necessary, encryption, access control and audit logs, no PHI in logs or traces unless controlled, de-identify where possible (Safe Harbor / Expert Determination). AI assists; **a human owns coverage decisions.**" |
| **Prompt vs RAG vs fine-tune** | "Prompt first. RAG when the model lacks *knowledge*. Fine-tune when it lacks *behavior or format* at scale. Each step only when the eval set shows the previous one is insufficient." |
| **Cost/latency** | "Route easy requests to small models, use prompt caching, stream, batch offline work, cap tokens and agent steps, track cost per turn from day one." |
| **System design order** | "Users & success metric → data & constraints (PHI) → architecture → model → **eval plan** → guardrails → observability & cost → rollout (shadow → pilot with HITL → scale) → team plan." |

## Leadership one-liners

| Topic | One-liner |
|---|---|
| **Mentoring approach** | "Match support to the person and the task: direct for new skills, coach as they grow, delegate when ready. Weekly 1:1s, a written growth plan, and real ownership of something that matters." |
| **Feedback** | "Situation → Behavior → Impact, then ask for their view. Promptly and privately. Praise specifically and in public." |
| **Code review** | "Reviews teach. Explain *why*, separate must-fix from nit, review the design early so the PR isn't the first time I see it, and for AI code also check prompts, evals, PHI in logs, and tool permissions." |
| **Juniors + AI tools** | "Use them, but you own every line. Explain it in review, write tests, and know when not to trust it. I model that myself." |
| **Standards** | "Prompts versioned as code; evals gate prompt and model changes; no PHI in logs; least-privilege tools; cost budget per feature; ADRs for big decisions." |
| **Estimating AI work** | "Timebox a spike, agree on an eval-based 'good enough' bar with the PO up front, then estimate the build. Report progress as eval scores, not just tickets." |
| **New tech** | "Bake-off on *our* eval set, measuring quality, latency, cost, security, and team fit, then a short ADR. Not hype." |
| **Disagreement** | "Make the decision criteria explicit, prototype or measure if cheap, decide, document, and disagree-and-commit." |
| **First 90 days** | "30: listen, learn the systems and people, ship something small. 60: own a meaningful piece, propose the 2–3 highest-value standards (evals, review checklist). 90: those standards are running, and each engineer has a growth plan." |
| **No lead title** | "I've led through ownership, specs, and enablement, and for two months after my manager resigned I led three contractors day to day." Then tell [M1](13-Behavioral-Story-Bank.md#m1). |
| **ML gap** | "My depth is production AI systems, not training deep-learning models from scratch. Here's what I know and how I'd partner and ramp." |

## Top 4 questions to ask ([14](14-Questions-to-Ask.md))
1. What does the team need most from this role right now?
2. Where is the agentic AI framework today?
3. How do you evaluate GenAI systems before and after release, and how does compliance review work?
4. What would make you say in six months that this hire was a great decision?

## Logistics checklist
- [ ] Interviewer name and LinkedIn checked · [ ] Video link tested, camera at eye level, quiet room
- [ ] Resume, JD, and this page open in a second window · [ ] Water · [ ] Pen and paper for their answers
- [ ] Start with energy: smile, a short "thanks for making the time", then the pitch
- [ ] If you don't know something: "I haven't done X directly. Here's how I'd approach it…", then reason out loud.
