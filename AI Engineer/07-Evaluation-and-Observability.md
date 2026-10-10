# 07 · Evaluation & Observability (LLMOps)

[← Index](00-Index.md) · **Manager-round priority:** High · **Read time:** ~30 min

> **Why this matters for this role:** The JD says you will "establish monitoring, evaluation, and observability" for production agents. A lead who can explain *how we know it works* (and how we'd notice when it stops working) is exactly what the manager is hiring. [S1](13-Behavioral-Story-Bank.md#s1) (20-question eval set, citation checks, per-turn cost) and [S2](13-Behavioral-Story-Bank.md#s2) (LLM judge) are your best evidence. Lead with them.

## Primer

**Mental model: evals are the unit tests and observability is the production monitoring.** You need both, plus a loop that feeds production failures back into the test set.

```
            ┌──────────── offline (before release) ────────────┐
 golden set ─► run app ─► scorers (code checks │ LLM judge │ human) ─► report ─► CI gate
     ▲                                                                       │
     │                                                                       ▼
     │        ┌──────────── online (in production) ──────────────┐       release
     └─────── │ traces ─► dashboards/alerts ─► sampled LLM-judge │ ◄─────────┘
  new failure │ user feedback (👍/👎, escalations) ─► error analysis │
  cases       └──────────────────────────────────────────────────┘
```

Three kinds of scorer, cheapest first:
1. **Code-based checks**: deterministic. Valid JSON or schema, the SQL runs, the citation IDs exist in the retrieved set, no PHI patterns in the output, latency is under budget.
2. **LLM-as-judge**: for fuzzy qualities like faithfulness, relevance, tone, and policy compliance. Keep it binary and narrow, and calibrate it against human labels.
3. **Human review**: SMEs label a sample. This is the ground truth that you calibrate everything else against.

## Questions & answers

### Q1. How do you evaluate an LLM application? How do you know it's "good enough" to ship?  `[P0]`
**Say this first (~30 sec):** "I treat it like test-driven development. Before tuning anything, I build a golden set of real questions with expected answers or acceptance criteria, agreed with the business SME. Every change runs against it, with deterministic checks first, then an LLM judge for fuzzy criteria, then human spot checks. 'Good enough' is a threshold we agree on up front, for example 90% correct with zero unsupported claims on the critical categories. Then we keep measuring in production, because offline evals never cover everything."
**If they dig deeper:**
- Define success with the business owner first: what a wrong answer costs, and which question categories are high-risk (anything about coverage or money).
- Score per category, not just overall. 92% overall can hide 60% on the one category that matters.
- Track quality, latency, and cost together. A change that gains 2 points of quality but doubles cost is a product decision, not an engineering one.
- Release gates: offline pass, then shadow/pilot with a small user group, then a staged rollout with online monitoring.

**Your angle:** [S1](13-Behavioral-Story-Bank.md#s1): you built a 20-question eval set *and* per-turn cost tracking, and added citation checks to the LangGraph agent. Say what the threshold was and what failed first. `[fill in: pass rate before/after, what kind of questions failed]`
**Likely follow-ups:** Where did the 20 questions come from? Is 20 enough? Who labels the answers? How do you stop the eval set from going stale?

### Q2. How do you build a golden dataset? How big should it be?  `[P0]`
**Say this first:** "I mix three sources. Real questions from SMEs and the people who'll use it. Production logs once we have them, especially failures and thumbs-down. And synthetic variations to cover edge cases. I start small: 20–50 high-quality examples are enough to iterate on day one. I grow it to a few hundred as we see real traffic, and I version it like code."
**If they dig deeper:**
- **Coverage over volume:** stratify by intent and category, difficulty, and risk. Include "should refuse" or "out of scope" cases, multi-turn cases, and adversarial ones (prompt injection).
- **Labels:** for RAG, store the question, the reference answer *or* rubric, and the expected source docs. The expected sources let you score retrieval separately from generation.
- **Synthetic data:** generate it from your documents with an LLM, but have humans review a sample. Synthetic sets skew easy and "too clean."
- **Versioning:** keep the dataset in git or in a LangSmith/Foundry dataset with a version tag, and record which dataset version each eval run used. Never silently edit an example.
- **Avoid leakage:** don't tune prompts on your holdout slice.

**Your angle:** In [S1](13-Behavioral-Story-Bank.md#s1) you started at 20 questions, which is the right instinct. Be ready to say how you'd scale it: "Next I'd mine the turn log for failed or thumbs-down turns and have the PM label them."
**Likely follow-ups:** How do you get SMEs' time? (Small batches, a simple labeling UI, and showing them that it reduces their review burden.)

### Q3. Offline vs online evaluation: what's the difference and why do you need both?  `[P0]`
**Say this first:** "Offline evals run on a fixed dataset before release. They're repeatable and catch regressions. Online evals run on live traffic: sampled LLM-judge scoring, user feedback, business metrics like containment or escalation. Offline tells you whether you made it worse. Online tells you whether it works on the questions people actually ask, which are always different from what we imagined."
**If they dig deeper:** Online signals arrive late and are noisy (most users don't click thumbs), so you combine implicit signals (rephrasing, abandonment, handoff to a human) with explicit ones. Production failures get triaged and added to the offline set, and that closes the loop.
**Likely follow-ups:** How do you sample production traffic for review without exposing PHI to too many people? (Role-restricted review queue, de-identified views, audit trail. See [08](08-Security-Responsible-AI-and-HIPAA.md).)

### Q4. When do you use an LLM-as-judge, and what are its pitfalls?  `[P0]`
**Say this first:** "I use an LLM judge for qualities that code can't check, like whether the answer is supported by the retrieved context or whether it addressed the question. But I treat the judge as a model that also needs evaluating. I validate it against human labels before trusting it, and I keep the judgment narrow and binary: pass/fail on one criterion, with a written rationale."
**If they dig deeper (known biases):**
- **Position bias:** in pairwise comparisons it prefers the first (or second) answer. Fix: swap the order and run both.
- **Verbosity bias:** longer answers score higher. Fix: put "length is not quality" in the rubric and judge specific criteria.
- **Self-preference:** a model favors its own outputs. Fix: use a different model family as the judge when you can.
- **Scale drift:** 1–10 scores are inconsistent between runs and between judges. Binary pass/fail per criterion is more reliable and easier to act on.
- **Calibrate:** have SMEs label ~100 cases, then measure the judge's agreement with them (precision/recall on "fail"). Re-check when you change the judge prompt or model.
- Ask for **reasoning before the verdict**, include few-shot examples of pass and fail, and give the judge the same context the app had.

**Your angle:** [S2](13-Behavioral-Story-Bank.md#s2): your Data Validation judge decides one narrow question ("timing race vs. real defect") and **never writes without confirmation**. That's a well-scoped judge with a human-in-the-loop on actions. `[fill in: how you checked the judge was right, e.g., compared against your own labels on N cases]`
**Likely follow-ups:** How do you know the judge is right? What's the cost of judging every production turn? (Sample it, e.g., 5–10%, plus 100% of flagged turns.)

### Q5. What metrics do you use for a RAG system?  `[P0]`
**Say this first:** "I split it into retrieval and generation, because they fail differently. For retrieval: did we fetch the right chunks? I measure recall@k, hit rate, and MRR against labeled source docs. For generation: is the answer faithful to the retrieved context, is it relevant to the question, and are the citations correct? If the answer is wrong but retrieval was right, I fix the prompt or the model. If retrieval was wrong, no prompt will save it."
**If they dig deeper:**

| Stage | Metric | What it tells you |
|---|---|---|
| Retrieval | Recall@k / hit rate | Was the needed chunk in the top-k at all? |
| Retrieval | MRR / nDCG | Was it ranked near the top? |
| Retrieval | Context precision | How much of the context was noise? |
| Generation | Faithfulness / groundedness | Is every claim supported by the context? (hallucination check) |
| Generation | Answer relevance / correctness | Did it answer *this* question, and correctly versus the reference? |
| Generation | Citation accuracy | Do cited sources actually contain the claim? |
| System | Refusal correctness | Says "I don't know" when context is missing? |

Tools: RAGAS, LangSmith evaluators, the Foundry built-in evaluators (groundedness, relevance, retrieval), Azure AI Content Safety groundedness detection.
**Your angle:** The citation checks in [S1](13-Behavioral-Story-Bank.md#s1) are a code-based faithfulness gate. For your Azure AI Search work ([S5](13-Behavioral-Story-Bank.md#s5)), mention measuring recall@k when you compared hybrid search against vector-only search, or semantic ranker on versus off. `[fill in if you did]`
**Likely follow-ups:** How do you get labeled source docs cheaply? (Have SMEs mark "which doc answers this", or generate questions *from* chunks so the source is known.)

### Q6. How do you evaluate an agent (multi-step, tool-using), not just a single LLM call?  `[P0]`
**Say this first:** "At three levels. **Final outcome**: did it complete the task correctly? **Trajectory**: did it call the right tools with the right arguments, in a sensible order, without loops? **Single step**: for the important nodes, such as the router or a SQL generator, I unit-test that node in isolation. Outcome is what the user cares about. Trajectory and step evals tell me *where* it broke."
**If they dig deeper:**
- **Tool-call accuracy:** correct tool selected, arguments that pass schema validation, no unnecessary calls.
- **Efficiency:** number of steps and tokens per task. Agents that loop are expensive and slow.
- **Safety:** never called a write or action tool without approval, and stayed within its permitted tools.
- **Non-determinism:** run each case several times (e.g., 3–5) and report the pass rate, not a single pass/fail.
- In LangGraph, each node is a function, so you can test nodes directly with fixture state. LangSmith can score whole trajectories.

**Your angle:** In [S1](13-Behavioral-Story-Bank.md#s1) the LangGraph "pipelines agent" has distinct nodes (route, retrieve, answer, citation check), and each one can be evaluated separately. Say that's how you'd structure a team's eval suite.
**Likely follow-ups:** How do you make agent evals deterministic enough for CI? (Pin the model version, temperature 0 where possible, mock external tools, use pass-rate thresholds.)

### Q7. How do you stop a prompt or model change from silently breaking things? (CI for LLM apps)  `[P0]`
**Say this first:** "Prompts, model versions, and retrieval configs are code. They live in git, get reviewed in a PR, and every PR that touches them triggers the eval suite. The PR shows a diff report: pass rate per category, versus main, plus cost and latency. If a critical category drops below the threshold, the merge is blocked. That's the standard I'd set for the team."
**If they dig deeper:**
- **Fast tier** on every PR (~50 cases, cheap judge). **Full tier** nightly or before release.
- Store results so you can see trends over time and compare runs.
- Make the bar explicit in the team's definition of done: "a prompt change without an eval run is not reviewable."
- Watch out for flakiness: use thresholds with tolerance, and re-run borderline failures.

**Your angle:** This is the leadership version of [S6](13-Behavioral-Story-Bank.md#s6). You've already set up team-level AI tooling standards (CLAUDE.md, docs). Eval gates are the same kind of guardrail, applied to the product.
**Likely follow-ups:** Who owns the eval suite? (The team does. Every feature PR adds eval cases, the same way it adds tests.)

### Q8. Azure retires the model version you're on and you have to upgrade. How do you do it safely?  `[P0]`
**Say this first:** "I treat it like a dependency upgrade with a regression suite. Run the full eval set on the new version side by side. Compare quality per category, plus latency, cost, and refusal rate. Look at the diffs by hand, because new models change tone and format. Then roll out gradually behind a config flag, watch the online metrics, and keep the old deployment available for fast rollback until the retirement date."
**If they dig deeper:**
- Pin explicit model versions in deployments. Don't let auto-upgrade change behavior under you.
- Re-tune prompts if needed. Prompts are often over-fit to one model.
- Check structured-output and tool-calling compatibility, token limits, and pricing differences.
- Track retirement dates and plan upgrades quarterly, not in a last-minute scramble.

**Likely follow-ups:** What if the new model is better on average but worse on one critical category? (Keep the old one for that route, or fix it with prompts and examples before switching. Don't ship a regression in a high-risk category.)

### Q9. What do you put on the production dashboard for an AI service?  `[P0]`
**Say this first:** "Four groups. **Reliability**: error rate, 429 throttling, timeouts, p50/p95 latency, and time-to-first-token for streaming. **Cost**: tokens in and out and dollars per turn, per user, and per feature. **Quality**: groundedness or judge pass rate on a sample, refusal rate, citation-failure rate, thumbs-down rate. **Business**: containment or deflection (resolved without a human), escalation rate, task completion. Each has an owner and an alert threshold."
**If they dig deeper:**
- **TTFT** matters more than total latency for chat UX. Streaming hides total latency.
- Break down cost by **node or step** in agents. Usually one step (a big-context call, or a retry loop) is the culprit.
- Alert on **rate of change**, e.g., a sudden jump in tokens per turn usually means a retrieval bug or an agent loop.
- Segment by user group and channel, because aggregate numbers hide problems.

**Your angle:** Per-turn cost tracking in [S1](13-Behavioral-Story-Bank.md#s1) and the turn log in [S4](13-Behavioral-Story-Bank.md#s4). Also your ops background: Datadog and PagerDuty, the SLO Slack app used by 3,000+ people ([S12](13-Behavioral-Story-Bank.md#s12)). "I've run SLO-driven alerting before; LLM services need the same discipline plus quality and cost signals."
**Likely follow-ups:** What SLOs would you set? (e.g., p95 under 8s end-to-end for a RAG answer, availability of 99.9%, cost per conversation under $X. Agree them with the PO.)

### Q10. How do you trace a LangGraph / agent application in production?  `[P1]`
**Say this first:** "With distributed tracing. Each request is one trace, and each node, LLM call, retrieval, and tool call is a span. Each span records inputs and outputs, tokens, latency, and model version. In LangGraph you get that from LangSmith almost for free. In Azure, Foundry tracing is built on OpenTelemetry and sends to Application Insights. I prefer OpenTelemetry with the GenAI semantic conventions so we're not locked into one vendor, and so it joins up with our existing APM."
**If they dig deeper:**
- Propagate a **conversation/thread ID** and **user ID (pseudonymous)** on every span, so you can replay a whole conversation.
- **PHI in traces** is the big risk. Redact or hash at the SDK layer, limit who can read traces, and set retention. Prompt/response content capture should be a deliberate decision, not a default. See [08](08-Security-Responsible-AI-and-HIPAA.md).
- Link traces to feedback: a thumbs-down should jump straight to its trace.

**Likely follow-ups:** LangSmith vs Foundry tracing? (LangSmith is LangGraph-native and has excellent eval and dataset tooling, but it's a SaaS, so check the BAA and hosting options. Foundry/App Insights stays inside the Azure tenant and compliance boundary. For a healthcare company, data residency often decides it.)

### Q11. How do you collect and use user feedback?  `[P1]`
**Say this first:** "Explicit feedback: thumbs up or down with an optional reason. Implicit feedback: rephrasing, copying the answer, abandoning, escalating to a human. I don't just count it. Someone does a weekly error analysis: read 30–50 bad interactions, label *why* they failed (retrieval miss, wrong doc version, bad reasoning, out of scope), and fix the biggest bucket first. Failures become new eval cases."
**If they dig deeper:** Error analysis beats dashboards for finding *what to fix*. It's also a great mentoring exercise for juniors, because it builds intuition fast.
**Likely follow-ups:** How would you prioritize? (By frequency × severity. A rare error about coverage can outrank common formatting issues.)

### Q12. How do you A/B test an LLM feature?  `[P1]`
**Say this first:** "Same as any product experiment, but with an online quality metric added. Randomize by user or conversation, not by request, so the experience stays consistent. Define the primary metric up front: resolution or containment, task completion, or thumbs-up rate. Add guardrail metrics: cost, latency, escalation, and judge-scored groundedness. Run until you have enough volume, then decide. For high-risk features I prefer a shadow mode first, where the new version runs and is logged but not shown."
**Likely follow-ups:** What if traffic is too low for statistical power? (Lean on offline evals plus SME pairwise preference reviews instead.)

### Q13. How do you manage and version prompts?  `[P1]`
**Say this first:** "Prompts are versioned in git next to the code that uses them, as templates with typed variables. Changes go through PR review with an eval diff attached. At runtime each trace logs the prompt version and model version, so any answer can be traced back to exactly what produced it. A prompt registry (LangSmith prompts, Foundry) is useful if non-engineers need to edit, but git stays the source of truth."
**Likely follow-ups:** Should product people edit prompts directly? (Yes, in a sandbox with evals. Promotion to production still goes through review.)

### Q14. What is "drift" for an LLM app, and how do you detect it?  `[P1]`
**Say this first:** "Three kinds. **Input drift**: users start asking new things, like a new plan year or new benefit. **Knowledge drift**: the source documents change and the index gets stale. **Model drift**: the provider changes or retires a model. I detect them by monitoring topic or intent distribution and the rate of 'I don't know' and low-retrieval-score answers, by watching index freshness (time since last successful indexer run), and by re-running the eval suite on a schedule even when nothing changed."
**If they dig deeper:** For health plans, the annual benefits cycle (Jan 1 plan changes, open enrollment) is a predictable drift event. Plan for re-indexing and re-evaluation ahead of it.
**Likely follow-ups:** How do you handle old and new plan-year documents at the same time? (Metadata filters by plan year and effective date, and the answer cites the effective date. See [03](03-RAG.md).)

### Q15. How do you track and control cost per conversation?  `[P1]`
**Say this first:** "Measure it first. Log tokens and computed dollars on every LLM span, then aggregate per turn, per conversation, per feature, and per tenant. Then optimize the biggest line items: trim context, cache stable prompt prefixes, route easy requests to a smaller model, and cap agent steps. Set a budget alert per feature so a loop or a bad deploy can't run up a surprise bill."
**Your angle:** [S1](13-Behavioral-Story-Bank.md#s1) per-turn cost tracking; [S7](13-Behavioral-Story-Bank.md#s7): you found a 10× Snowflake cost spike and fixed it back to ~11 credits/day. "Same instinct: measure, find the loop, fix it." More optimizations in [09](09-AI-System-Design-Scenarios.md).

### Q16. A stakeholder says "the bot is giving bad answers." What do you do first?  `[P0]`
**Say this first:** "Get specific examples and find their traces. Then classify the failure. Was the right document not retrieved? Retrieved but ignored? Was the document itself outdated? Was the question out of scope? Or is the model just wrong? Each has a different fix. I add those examples to the eval set so the fix is verified and can't regress, then I report back to the stakeholder with what we found and what changed."
**Your angle:** This is the same muscle as [S8](13-Behavioral-Story-Bank.md#s8): you worked through 60+ PnL discrepancies with the PM by classifying root causes (a missing forward curve, the cutoff rule) instead of patching symptoms one by one.

### Q17. What would you teach a junior engineer about evals in their first month?  `[P0]`
**Say this first:** "Three habits. One: never say 'it looks better', say 'it went from 78% to 86% on the eval set, and here are the three cases that still fail.' Two: read the data. Spend an hour reading real traces before changing a prompt. Three: every bug becomes a test case. I'd pair with them on one error-analysis session and have them own a slice of the eval set."
**Likely follow-ups:** See [11 · Mentoring & Coaching](11-Mentoring-and-Coaching.md).

## Key terms

| Term | One-liner |
|---|---|
| Golden set | Curated, versioned inputs with expected outputs or rubrics |
| LLM-as-judge | An LLM scores outputs against a rubric. Must be calibrated against humans |
| Faithfulness / groundedness | Every claim in the answer is supported by the provided context |
| Recall@k / MRR / nDCG | Retrieval quality: was the right doc found, and how high was it ranked |
| Trajectory eval | Scoring the sequence of an agent's steps and tool calls, not just the final answer |
| TTFT | Time to first token, the perceived latency for streaming UIs |
| Containment / deflection | Share of conversations resolved without a human handoff |
| OTel GenAI semconv | Standard OpenTelemetry attribute names for LLM spans (model, tokens, operation) |

## References
- [Your AI Product Needs Evals (Hamel Husain)](https://hamel.dev/blog/posts/evals/): the most practical guide to eval-driven development and error analysis.
- [Using LLM-as-a-Judge for Evaluation (Hamel Husain)](https://hamel.dev/blog/posts/llm-judge/): binary judgments, calibrating against domain experts.
- [Evaluating the Effectiveness of LLM-Evaluators (Eugene Yan)](https://eugeneyan.com/writing/llm-evaluators/): survey of judge reliability and biases.
- [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena (Zheng et al., 2023)](https://arxiv.org/abs/2306.05685): the original paper on position, verbosity, and self-enhancement bias.
- [Demystifying evals for AI agents (Anthropic)](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): agent evals, graders, and trajectory vs outcome.
- [RAGAS metrics](https://docs.ragas.io/en/stable/concepts/metrics/): definitions of faithfulness, context precision/recall, and more.
- [LangSmith evaluation concepts](https://docs.langchain.com/langsmith/evaluation-concepts): datasets, evaluators, offline vs online, for LangGraph apps.
- [Microsoft Foundry observability (evaluation, monitoring, tracing)](https://learn.microsoft.com/en-us/azure/foundry/concepts/observability): Azure-native evals and tracing to App Insights.
- [OpenTelemetry semantic conventions for GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/): standard span attributes for LLM and agent telemetry.
- [Groundedness detection (Azure AI Content Safety)](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/groundedness): a managed check for ungrounded claims.
- [Patterns for Building LLM-based Systems (Eugene Yan)](https://eugeneyan.com/writing/llm-patterns/): evals, guardrails, caching, and feedback patterns in one overview.
