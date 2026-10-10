# Handoff: BCBSMA Sr. AI Engineer interview prep

*Written Fri Oct 9, 2026 at the end of a local Claude Code session, so the work can continue in a Claude cloud session.*
*Read this whole file before doing anything. The study guide itself is in [`AI Engineer/`](AI%20Engineer/00-Index.md).*

## 1. Who and what

- **Candidate:** Kurt Wang, Boston. Software engineer with 8+ years in backend, data engineering, cloud, and (for about the last 1.5 years) applied AI. Native Chinese speaker; the interview is in English. Kurt asked for the AI "八股文", meaning **standard interview questions / fundamentals** with model answers.
- **Role applied for:** **Sr. AI Engineer, Blue Cross Blue Shield of Massachusetts** (req R08441).
  - The official posting now says it's no longer accepting applications. Full JD text is still on the [Built In Boston mirror](https://www.builtinboston.com/job/sr-ai-engineer/8969316).
  - The body really describes a **hands-on Lead AI Engineer**:
    - 40–50% coding.
    - Mentors AI engineers, coaches growth paths, sets code-review, testing, and docs standards, and runs knowledge-sharing sessions.
    - Owns agentic AI, GenAI, and RAG design, plus production monitoring, evaluation, and observability.
    - Technical escalation point.
    - Partners with Product Owners on estimates.
    - Evaluates new LLMs and frameworks.
    - Healthcare, HIPAA, and compliance context.
  - Required: 8+ years of ML (TensorFlow/PyTorch/sklearn), 2+ years of agentic AI, 2 of AWS/GCP/Azure. Preferred: LangChain/LangGraph, LLM evaluation frameworks, HIPAA.
  - Range $151.2K–$184.8K plus variable pay. In-office in Boston (Hingham also listed), "Flex persona" mentioned.
  - Related BCBSMA postings mention building an **"agentic AI framework"**.
- **Next interview:** **hiring-manager round, tentatively Fri Oct 16, 2026** (to be confirmed). No coding challenge. Expect tech depth at the "explain / design / trade-offs" level, **plus how he'd lead, mentor, and coach juniors**.
- **Kurt's current work:** building a service at his company with short- and long-term memory, RAG, LangGraph, and Azure AI Search inside Azure AI Foundry (now branded Microsoft Foundry). He describes his LangGraph knowledge as "shallow."

## 2. Resume summary (the PDFs are NOT in this repo)

- **Boston Energy Trading & Marketing, Software Engineer (Jul 2025–present)**
  - Sole full-time engineer on the Asset Management Platform (AMP): 5 services plus a React UI.
  - Load Deal service and PnL engine, released Aug 2026, saving 3 hours/day.
  - Shared entitlements service: 3–6s → ~10ms, fail-closed.
  - KEDA job-execution service built from scratch.
  - Snowflake cost spike: ~100 → ~11 credits/day.
  - Claude Code enablement: AI-assisted commits rose from 36% to 80%.
  - **Applied AI:**
    - Load Deal AI, built in 3 weeks: a Cortex agent plus semantic view, a LangGraph agent with citation checks, a 20-question eval set, and per-turn cost tracking.
    - Watt AI Shell: backend for the AI-app front door; he wrote the specs the frontend engineers implemented.
    - Data Intelligence: Cortex cost queries 85.6s → 8.8s.
    - Data Validation Service: an LLM judge triages mismatches and never writes without human confirmation.
- **Wayfair (2020–2025), SE → SE III, Data Platform**
  - Kronos (2M jobs/week) moved to Kubernetes, supporting 200% peak throughput.
  - Onboarded 10+ teams to GCP Composer and Dataform.
  - Post-mortem Wizard; Slack SLO app with 3,000+ users.
  - Backstage observability platform.
  - Wayfair Data Engineer co-op (2018).
- **Cerner (2018–2020):** healthcare revenue-cycle app (Java).
- **Education:** MS Information Systems, Northeastern; BS IoT Engineering, BUPT.
- **Gaps vs the JD, with the honest framing used in the guide:**
  - No formal lead title. He leads through ownership, specs, and enablement.
  - Limited deep-learning training experience. His depth is production AI systems.
  - No AWS. He has Azure plus GCP.
  - **Never coach exaggeration.**

## 3. What exists (all in `AI Engineer/`)

- **Index:** `00-Index.md`. It has a 7-day plan (Sat 10/10 → Fri 10/16), the ~22 most likely manager-round questions linked to their answers as page + Q#, a fill-in checklist, and the top 5 readings.

| # | Page | Qs |
|---|---|---|
| 01 | Role, Company & Your Pitch (JD vs resume table, 90-sec pitch, gap answers) | 12 |
| 02 | LLM Fundamentals | 17 |
| 03 | RAG | 20 |
| 04 | Azure AI Search & Microsoft Foundry | 19 |
| 05 | Agents & LangGraph (strongest primer, code sketch) | 18 |
| 06 | Memory & Context Engineering | 18 |
| 07 | Evaluation & Observability | 17 |
| 08 | Security, Responsible AI & HIPAA | 15 |
| 09 | AI System Design Scenarios (benefits Q&A, prior-auth assist, agent-assist, agent platform, claims extraction) | 12 |
| 10 | ML & MLOps Fundamentals (gap framing first) | 18 |
| 11 | Mentoring & Coaching (SLII, SBI, GROW, 1:1 and growth-plan templates) | 17 |
| 12 | Team Leadership & Delivery (AI code-review checklist, ADRs, estimation, first 90 days) | 16 |
| 13 | Behavioral Story Bank: stories S1–S14 from the resume, plus M1/C1/F1/P1 to fill in | — |
| 14 | Questions to Ask | — |
| 15 | Final-Day Cheat Sheet | — |

The page template and conventions are in [`CLAUDE.md`](CLAUDE.md).

## 4. Facts verified during the session (don't re-research unless stale)

- **Microsoft Foundry and its agents:**
  - Azure AI Foundry has been renamed **Microsoft Foundry**. Content filters are now called "Guardrails."
  - **Foundry Agent Service hosted agents went GA in July 2026** and support LangGraph via `langchain-azure-ai[hosting]`. Some add-ons, such as source-code deployment, are still in preview.
  - **Microsoft Agent Framework** (the successor to Semantic Kernel and AutoGen) reached 1.0 GA in April 2026. This comes from secondary sources.
- **Azure AI Search:**
  - **Agentic retrieval / Foundry IQ:** GA only in REST `2026-04-01` with minimal reasoning effort. LLM query planning and answer synthesis are preview (`2026-08-01-preview`).
  - Native ACL / Entra-based permission trimming is preview. Security filters are the GA option.
- **LangChain / LangGraph:** LangGraph 1.0 went GA in Oct 2025. LangChain 1.0 `create_agent` plus middleware runs on LangGraph and replaces `create_react_agent`. Docs live at docs.langchain.com.
- **Regulation:**
  - **California SB 1120 (2024)** requires a licensed clinician to make medical-necessity denials; AI may assist. Verified.
  - The CMS Feb 2024 Medicare Advantage AI FAQ is cited via a Reed Smith summary, not the primary CMS document.
- **BCBSMA:** not-for-profit, ~3M members (Q1 2026 results press release). No public 2026 AI announcement found.
- **Link check (Oct 9):**
  - All internal links resolve.
  - 191 of 199 external links return 200.
  - 8 links return 403 because the sites block bots, but the pages exist: hhs.gov ×5, oreilly.com, queue.acm.org, and a doi.org link.

## 5. Open items

**Only Kurt can fill these in.** They're the highest-value prep:
- [ ] **S5:** his current memory + RAG + LangGraph + Azure AI Search service. Templates: `04` Q1, `06` Q1, and `13` S5.
- [ ] **S1 / S2 numbers:** eval pass rate, cost per turn, users, and the Data Validation impact.
- [ ] **M1** (a real mentoring story), **C1** (conflict), **F1** (failure), **P1** (pushback) in `13`.
- [ ] Salary number and walk-away point (`01` Q10).
- [ ] Interviewer name, date, and format confirmed with the recruiter.

**Offered but not started (good next tasks for the cloud session):**
1. **Mock interview:** ask the `[P0]` questions one at a time, in manager style, with follow-ups. Score each answer on structure, specificity, use of a story, and length. Coach in short bullets, and have him retry.
2. **Help Kurt draft his fill-ins** by interviewing him, then write them into `13` and the templates.
3. Optionally, publish a phone-friendly web page version of the guide.

**Later rounds (not started):** a deeper technical round is likely, so expand the `[P1]` material and add system-design practice. Also a possible final round with senior leadership or stakeholders.

## 6. Logistics

- **Repo:** `github.com/moveingsun/interview_prep` (**private**), branch `main`. Kurt reads it on his phone in the GitHub app, so keep pages mobile-friendly: short paragraphs, no very wide tables or code lines.
- **Not in the repo** (they're only on Kurt's Mac): `Resume/` PDFs, `Blind 75/`, and `Question/`, which are LeetCode practice files.
- **Link checker:** `python3 tools/check_links.py . /tmp/urls.txt` checks internal links and anchors and writes the external URLs to a file. Curl those URLs to verify them; the curl command is in `CLAUDE.md`.
- **Local session:** Kurt's local Claude Code session on his Mac created everything up to this point. If he edits files in the GitHub app, pull before editing.
