# 01 · Role, Company & Your Pitch

[← Index](00-Index.md) · **Manager-round priority:** High · **Read time:** ~15 min

> **Why this matters for this role:** The hiring manager decides two things in round 1: *Can this person lead my AI engineers?* and *Is the technical story real?* This page sets up both. Rehearse the pitch out loud until it takes ~90 seconds.

## Primer: what the job really is

The posting title is **Sr. AI Engineer**, but the body describes a **Lead AI Engineer**, a hands-on technical lead. It's not a people manager, and it's not a pure IC role.

| JD theme | What they literally ask for | Your evidence | Gap → honest framing |
|---|---|---|---|
| **Hands-on (40–50% coding)** | "You don't sit in meetings all day" | You ship end to end every week: AMP's 5 services + UI, Load Deal, Data Validation built solo ([S14](13-Behavioral-Story-Bank.md#s14), [S2](13-Behavioral-Story-Bank.md#s2)) | None. This is a strength. |
| **Agentic AI / GenAI / RAG design** | RAG, function calling, multi-step reasoning, tool use; LangChain/LangGraph | LangGraph pipelines agent with citation checks ([S1](13-Behavioral-Story-Bank.md#s1)), Cortex agents ([S4](13-Behavioral-Story-Bank.md#s4)), current memory + RAG + Azure AI Search service ([S5](13-Behavioral-Story-Bank.md#s5)) | About 1.5 years of applied GenAI, not 2+ years of agents. Frame it as depth and production rigor over tenure. |
| **Production: monitoring, eval, observability** | "Run AI models and agents in production" | 20-question eval set, per-turn cost tracking, LLM judge, turn logs ([S1](13-Behavioral-Story-Bank.md#s1), [S2](13-Behavioral-Story-Bank.md#s2), [S4](13-Behavioral-Story-Bank.md#s4)); Datadog/PagerDuty/SLO background at Wayfair | Strong. Lead with this. |
| **Mentor engineers, set standards, run code reviews and knowledge sharing** | "Coach engineers and create growth paths" | Specs the FE engineers implemented ([S3](13-Behavioral-Story-Bank.md#s3)); onboarded 10+ teams to Composer ([S10](13-Behavioral-Story-Bank.md#s10)); AI-dev enablement 36% → 80% ([S6](13-Behavioral-Story-Bank.md#s6)) | No formal lead title. Say: "I've led through ownership, specs, and enablement. Here's my concrete approach." See [11](11-Mentoring-and-Coaching.md) and [12](12-Team-Leadership-and-Delivery.md). |
| **Partner with Product Owners on estimates and delivery** | Requirements, estimates, quality vs speed | PnL reconciliation with the PM, 60+ discrepancies resolved ([S8](13-Behavioral-Story-Bank.md#s8)); Load Deal released Aug 2026 | Good. |
| **Technical escalation point** | ML pipelines, agents, cloud infra | 10× Snowflake cost spike ([S7](13-Behavioral-Story-Bank.md#s7)); entitlements 3–6s → 10ms ([S9](13-Behavioral-Story-Bank.md#s9)); OOM fix; Kronos on-call ([S11](13-Behavioral-Story-Bank.md#s11)) | Strong. |
| **Cloud + MLOps** | 2 of AWS/GCP/Azure; Docker, K8s, CI/CD | Azure (AKS, APIM, Service Bus, Key Vault, Foundry) **and** GCP (Composer, BigQuery); KEDA, Terraform, Buildkite | Meets "2 clouds". No AWS; say so plainly. |
| **"8+ yrs hands-on ML" (TensorFlow, PyTorch, sklearn)** | Classical ML/DL | MS coursework in ML; production LLM systems | **The biggest gap.** See [10 · ML & MLOps](10-ML-and-MLOps-Fundamentals.md) for honest framing. |
| **Healthcare / HIPAA (preferred)** | Regulated industry | Cerner revenue-cycle app ([S13](13-Behavioral-Story-Bank.md#s13)); energy trading is also regulated; fail-closed entitlements | Some exposure. Read [08](08-Security-Responsible-AI-and-HIPAA.md). |
| **Evaluate new LLMs and frameworks** | Track and recommend | Cortex vs LangGraph vs Foundry experience; Claude Code adoption | Good. Have a "bake-off on our own eval set" answer. |

**Logistics you should know (from public postings):** listed range is **$151.2K–$184.8K + variable pay**. The posting says in-office in Boston (Hingham is also listed) and mentions a "Flex" persona for local candidates. Ask about this; don't assume. The official careers page now shows the role as closed to new applicants, which is normal once a pipeline is full.

**Company snapshot:** Blue Cross Blue Shield of Massachusetts is a **not-for-profit** health plan headquartered in Boston with roughly **3 million members** (2026 press release). Related postings (Sr. AI Product Owner, GenAI Solution Architect, Associate Director GenAI) mention building an **"agentic AI framework"**, so expect questions about building reusable agent infrastructure for several teams. See [09 · System Design, scenario (d)](09-AI-System-Design-Scenarios.md).

**Typical health-plan AI use cases** (industry-wide; not confirmed as BCBSMA's roadmap, so ask about them):
member/benefits Q&A, call-center agent assist, prior-authorization support for clinical reviewers, claims and document intelligence, fraud/waste/abuse detection, care-management outreach, provider-data quality, and internal developer productivity.

## Questions & answers

### Q1. "Walk me through your background." / "Tell me about yourself."  `[P0]`
**Say this first (~90 sec), then stop:**
> "I'm a software engineer with about eight years in backend, data, and cloud. For the last year and a half I've focused on applied AI in production. I started at Cerner on a healthcare revenue-cycle application, then spent five years on Wayfair's data platform. There I led the move of our job-orchestration platform, which runs about 2 million jobs a week, onto Kubernetes, and onboarded more than ten data-engineering teams onto GCP Composer.
>
> At Boston Energy Trading I own the Asset Management Platform end to end. More recently I've been building our AI products. I built a domain assistant for load-deal questions in three weeks: a Snowflake Cortex agent plus a LangGraph agent with citation checks, an eval set, and per-turn cost tracking. I built a data-validation service where an LLM judge triages mismatches but never writes anything without human confirmation. Right now I'm building a service with short- and long-term memory and RAG on LangGraph and Azure AI Search in Foundry.
>
> What I'm looking for is to do that kind of production AI work and also grow a team that does it well. This role is literally that, and in healthcare, where I started."

**If they dig deeper:** pick whichever thread they react to: production rigor ([S1](13-Behavioral-Story-Bank.md#s1)), memory/RAG ([S5](13-Behavioral-Story-Bank.md#s5)), or enablement ([S6](13-Behavioral-Story-Bank.md#s6)).
**Your angle:** Keep it chronological but brief. Spend 70% of the time on the last 18 months.
**Likely follow-ups:** "Tell me more about the LangGraph agent." "What does the memory service do?" "Why leave after ~15 months?"

### Q2. "Why this role? Why Blue Cross?"  `[P0]`
**Say this first (~30 sec):** "Three reasons. First, the role: hands-on *and* leading, which is exactly the step I want. I don't want to stop coding, but I want to multiply my impact through a team. Second, the problem space. Healthcare AI has real stakes: grounding, privacy, and human-in-the-loop aren't nice-to-haves, and that's the kind of engineering I care about. Third, the mission. I started my career at Cerner in healthcare, and a not-for-profit plan serving about 3 million members in my own city is meaningful to me."
**If they dig deeper:** Mention the agentic AI framework: "Building shared agent infrastructure that several teams use is a platform problem, and platform work is what I did for five years at Wayfair."
**Your angle:** [S10](13-Behavioral-Story-Bank.md#s10), [S13](13-Behavioral-Story-Bank.md#s13).
**Likely follow-ups:** "What do you know about our AI work?" Be honest: "From the postings, an agentic framework, RAG, and evaluation focus. I'd love to hear where it stands."

### Q3. "Why are you leaving after about 15 months?"  `[P0]`
**Say this first:** "I've had great scope, but I'm effectively the only full-time engineer on my platform. I've proven I can own systems end to end. What I can't do there is build and grow a team around AI, and that's the next thing I want to get good at." Stay positive. Never criticize the current employer.
**Likely follow-ups:** "What would make you stay?" Answer: "a team to lead and a bigger AI mandate", which is consistent with your story.

### Q4. "You haven't had a lead title. Why should we trust you to lead engineers?"  `[P0]`
**Say this first (~30 sec):** "Fair question. I haven't had the title, but I've done the work that a lead does. When my manager resigned, I led three contract engineers on three projects for about two months while still writing the backend myself. On Watt I wrote the specs that our frontend engineers built from. At Wayfair I onboarded more than ten data-engineering teams onto a new platform, which meant teaching, docs, and office hours. At my current job I set up AI-assisted development for our codebase and moved AI-assisted commits from 36% to 80%. That's changing how people work, not just my own code. I have a concrete approach to mentoring and standards, and I'm happy to walk through it."
**If they dig deeper:** go to [11 · Mentoring](11-Mentoring-and-Coaching.md) Q1 and [12 · Team leadership](12-Team-Leadership-and-Delivery.md) on standards and first 90 days.
**Your angle:** [S3](13-Behavioral-Story-Bank.md#s3), [S6](13-Behavioral-Story-Bank.md#s6), [S10](13-Behavioral-Story-Bank.md#s10), plus [M1](13-Behavioral-Story-Bank.md#m1), leading three contractors for ~2 months.
**Likely follow-ups:** "Tell me about a time you mentored someone." "How do you handle someone who disagrees with you?"

### Q5. "The JD asks for 8+ years of hands-on ML with TensorFlow/PyTorch. How do you see your fit?"  `[P0]`
**Say this first:** "I'll be direct. My depth is in production AI systems: LLM applications, agents, RAG, evaluation, and the data and cloud infrastructure under them. It isn't in training deep-learning models from scratch. I know the fundamentals (metrics, overfitting, leakage, fine-tuning trade-offs), and I can work with data scientists on those models. But most of what this role describes, like agentic systems, RAG, monitoring, evaluation, and production reliability, is where I'm strongest. If there's a model-training need, I'd pair with a data scientist and ramp up quickly."
**Your angle:** Don't apologize, and don't overclaim. Then pivot to a concrete eval/production story ([S1](13-Behavioral-Story-Bank.md#s1), [S2](13-Behavioral-Story-Bank.md#s2)).
**Likely follow-ups:** "Have you fine-tuned a model?" If you haven't, say so, then show you know *when* fine-tuning is worth it ([02](02-LLM-Fundamentals.md), [10](10-ML-and-MLOps-Fundamentals.md)).

### Q6. "What's the AI project you're proudest of? Walk me through it."  `[P0]`
**Say this first:** Use [S1 Load Deal AI](13-Behavioral-Story-Bank.md#s1) (complete, fast, measured) or [S5 the current memory/RAG service](13-Behavioral-Story-Bank.md#s5) (closest to their stack). Structure: problem → users → architecture in one breath → how you knew it worked (eval) → what you'd do differently.
**If they dig deeper:** Be ready to whiteboard the architecture verbally: data sources → retrieval or semantic layer → agent graph → guardrails/citation check → UI → eval and cost logging.
**Likely follow-ups:** "How did you evaluate it?" ([07](07-Evaluation-and-Observability.md)). "Why LangGraph?" ([05](05-Agents-and-LangGraph.md)). "How do you handle hallucinations?" ([02](02-LLM-Fundamentals.md), [03](03-RAG.md)).

### Q7. "What does 40–50% hands-on mean to you? How would you split your week?"  `[P0]`
**Say this first:** "I'd protect blocks of focused time for the work that's highest leverage for me to code myself: the risky core pieces, like the agent orchestration or eval harness, plus prototypes for new patterns. Feature work that's a good growth opportunity goes to engineers, with me reviewing. The other half is design reviews, code reviews, 1:1s, unblocking, and working with the Product Owner. I'd also keep myself off the critical path for delivery so the team isn't blocked on me."
**Your angle:** See [12 · Team leadership](12-Team-Leadership-and-Delivery.md) on balancing coding and leading.

### Q8. "Where do you see AI going in health insurance over the next few years?"  `[P1]`
**Say this first:** "Near term, the value is in *assistive* AI that keeps humans accountable: summarizing clinical documents for reviewers, agent-assist for service reps, and document intelligence on claims and correspondence. The hard parts aren't the models. They're grounding, privacy, evaluation, and integration with systems of record. Regulators are also making clear that a human has to own coverage decisions. Agentic systems will grow, but mostly as well-bounded workflows with approvals, not fully autonomous agents."
**If they dig deeper:** mention interoperability (FHIR APIs, CMS prior-authorization rules) at a high level; see [08](08-Security-Responsible-AI-and-HIPAA.md).

### Q9. "How do you keep up with AI? What have you learned recently?"  `[P1]`
**Say this first:** Name 2–3 concrete things you actually follow and one you *changed your mind about*. Example: "I read primary sources: Anthropic's and LangChain's engineering posts, Microsoft Learn release notes for Foundry and AI Search, and practitioners like Hamel Husain on evals. Recently, context engineering changed how I build: I treat what goes into the context window as the main design surface, which is why our memory service summarizes and selects rather than appending everything."
**Your angle:** Be specific to your current project ([06](06-Memory-and-Context-Engineering.md)).

### Q10. "What are your salary expectations?"  `[P1]`
**Say this first:** "I've seen the posted range of roughly $151K to $185K plus variable pay. Based on my experience and the lead scope, I'd expect to be in the upper part of that range, but I'm flexible on the full package." `[fill in: your real number and walk-away point before Friday]`

### Q11. "Do you have experience with AWS / SageMaker / Vertex?"  `[P2]`
**Say this first:** "My production cloud experience is Azure today and GCP at Wayfair, with Composer, BigQuery, and Kubernetes. I haven't run production workloads on AWS. The concepts map closely (managed model endpoints, vector search, IAM, private networking), so I'd be productive quickly, but I won't claim depth I don't have."

### Q12. "What questions do you have for me?"  `[P0]`
See [14 · Questions to Ask](14-Questions-to-Ask.md). Always ask at least 3.

## References
- [Sr. AI Engineer posting (Built In Boston mirror)](https://www.builtinboston.com/job/sr-ai-engineer/8969316) — full job description. Re-read the night before.
- [Official BCBSMA careers listing](https://careers.bluecrossma.org/us/en/job/R08441/Sr-AI-Engineer) — official page (now shows the role as closed).
- [BCBSMA Newsroom](https://newsroom.bluecrossma.com/) — skim recent press releases for anything on AI, digital, or member experience.
- [BCBSMA Q1 2026 financial results](https://newsroom.bluecrossma.com/2025-05-15-Blue-Cross-Blue-Shield-of-Massachusetts-Announces-First-Quarter-2026-Financial-Results) — scale (≈3M members), not-for-profit context.
- [Sr. AI Product Owner posting (mentions the agentic AI framework)](https://www.builtinboston.com/job/sr-ai-product-owner/8039616) — hints at the team's direction.
