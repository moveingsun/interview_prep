# BCBSMA Sr. AI Engineer: Interview Prep Index

**Target:** Hiring-manager round, tentatively **Friday, Oct 16, 2026** · **Role:** [Sr. AI Engineer (Lead AI Engineer), Blue Cross Blue Shield of Massachusetts](https://www.builtinboston.com/job/sr-ai-engineer/8969316) · **Format:** no coding, but tech depth plus leadership and mentoring

> "八股文" in English: the closest terms are **"standard interview questions"**, **"interview fundamentals"**, or **"conceptual / theory questions"**. People also say **"canned answers"**, but that's slightly negative. This guide is your 八股文 set, tuned to this specific JD and your resume.

## How to use this guide
- Every page follows the same pattern: **Say this first** (a ~30-second spoken answer) → **If they dig deeper** → **Your angle** (your real experience) → **Likely follow-ups** → **References**.
- Question tags: `[P0]` likely in **this** manager round · `[P1]` likely in later technical rounds · `[P2]` depth / bonus.
- `[fill in: …]` marks details only you know. **The fill-ins are the most valuable prep you can do.** Answers built on your real details beat any template.
- Practice **out loud**. Reading is not rehearsing. Record yourself on the P0 questions at least once.

## What the manager round will likely look like (~45–60 min)
1. **Your pitch and background** (5–10 min) → [01](01-Role-Company-and-Your-Pitch.md)
2. **Deep dive on one AI project** (10–15 min): architecture, why those choices, how you know it works → [13 · S1/S5](13-Behavioral-Story-Bank.md), [05](05-Agents-and-LangGraph.md), [06](06-Memory-and-Context-Engineering.md), [07](07-Evaluation-and-Observability.md)
3. **Tech breadth checks** (10 min): RAG, agents, eval, safety, at the "explain the trade-off" level → [03](03-RAG.md), [08](08-Security-Responsible-AI-and-HIPAA.md), [09](09-AI-System-Design-Scenarios.md)
4. **Leadership and mentoring** (10–15 min): coaching juniors, code review, standards, working with Product Owners → [11](11-Mentoring-and-Coaching.md), [12](12-Team-Leadership-and-Delivery.md)
5. **Your questions** (5–10 min) → [14](14-Questions-to-Ask.md)

## Pages

| # | Page | What's inside | Mgr-round priority |
|---|---|---|---|
| 01 | [Role, Company & Your Pitch](01-Role-Company-and-Your-Pitch.md) | JD decoded vs your resume, gaps and honest framing, 90-sec pitch, why BCBSMA | **High** |
| 02 | [LLM Fundamentals](02-LLM-Fundamentals.md) | How LLMs work, tokens/context, hallucination, embeddings, tool calling, prompt vs RAG vs fine-tune | Medium |
| 03 | [RAG](03-RAG.md) | Chunking, hybrid search, reranking, security trimming, RAG eval, debugging bad answers, when not to use RAG | **High** |
| 04 | [Azure AI Search & Microsoft Foundry](04-Azure-AI-Search-and-Foundry.md) | Your current stack: indexes, vectors, hybrid + semantic ranker, agentic retrieval, Foundry agents, content safety | Medium-High |
| 05 | [Agents & LangGraph](05-Agents-and-LangGraph.md) | Workflow vs agent, LangGraph mental model, HITL, multi-agent patterns, MCP, framework choice | **High** |
| 06 | [Memory & Context Engineering](06-Memory-and-Context-Engineering.md) | Short- vs long-term memory, checkpointer vs store, PHI in memory, context engineering | **High** |
| 07 | [Evaluation & Observability](07-Evaluation-and-Observability.md) | Golden sets, LLM-as-judge, RAG/agent metrics, tracing, dashboards, safe model upgrades | **High** |
| 08 | [Security, Responsible AI & HIPAA](08-Security-Responsible-AI-and-HIPAA.md) | PHI/BAA, OWASP LLM Top 10, prompt injection, human-in-the-loop for coverage decisions | **High** |
| 09 | [AI System Design Scenarios](09-AI-System-Design-Scenarios.md) | Answer framework plus health-plan scenarios: benefits Q&A, prior-auth assist, agent-assist, agent platform | **High** |
| 10 | [ML & MLOps Fundamentals](10-ML-and-MLOps-Fundamentals.md) | Your biggest gap vs the JD: honest framing, core ML concepts, metrics, fine-tuning, MLOps | Medium |
| 11 | [Mentoring & Coaching](11-Mentoring-and-Coaching.md) | How you grow juniors: 1:1s, feedback, code review as teaching, AI-tool habits, underperformance | **High** |
| 12 | [Team Leadership & Delivery](12-Team-Leadership-and-Delivery.md) | Standards for AI code, estimating with POs, tech decisions, escalation, first 90 days | **High** |
| 13 | [Behavioral Story Bank](13-Behavioral-Story-Bank.md) | STAR stories S1–S14 from your resume, question→story map, stories you still need | **High** |
| 14 | [Questions to Ask](14-Questions-to-Ask.md) | Smart questions for the hiring manager, and a closing line | **High** |
| 15 | [Final-Day Cheat Sheet](15-Final-Day-Cheat-Sheet.md) | One page to read Friday morning | **High** |

## 7-day plan (Sat Oct 10 → Fri Oct 16)

| Day | Focus | Output (what "done" means) |
|---|---|---|
| **Sat 10/10** | [01](01-Role-Company-and-Your-Pitch.md) + [13](13-Behavioral-Story-Bank.md) + [05](05-Agents-and-LangGraph.md) | Pitch recorded once. All story `[fill in]`s done, including M1, C1, and F1. Can explain LangGraph state/nodes/edges/checkpointer out loud. |
| **Sun 10/11** | [06](06-Memory-and-Context-Engineering.md) + [03](03-RAG.md) + [04](04-Azure-AI-Search-and-Foundry.md) | Your 60-second "current architecture" description (S5) written and spoken. |
| **Mon 10/12** | [11](11-Mentoring-and-Coaching.md) + [12](12-Team-Leadership-and-Delivery.md) | One real mentoring story and your "first 90 days" answer said out loud. |
| **Tue 10/13** | [07](07-Evaluation-and-Observability.md) + [08](08-Security-Responsible-AI-and-HIPAA.md) | Can explain how you'd evaluate and monitor a healthcare assistant end to end. |
| **Wed 10/14** | [09](09-AI-System-Design-Scenarios.md) | Talk through 2 scenarios out loud in 10 min each (benefits Q&A + prior-auth assist). |
| **Thu 10/15** | [02](02-LLM-Fundamentals.md) + [10](10-ML-and-MLOps-Fundamentals.md) (skim) + **mock run** | Run all `[P0]` questions out loud (ideally with a friend), note weak spots, re-read those answers. |
| **Fri 10/16** | [15](15-Final-Day-Cheat-Sheet.md) + [14](14-Questions-to-Ask.md) + JD | Calm review only. No new material. |

If the interview moves earlier, do this minimum set: **01 → 13 → 11 → 05/06 → 14 → 15**.

## Top questions to expect in the manager round
*"01 Q4" means page 01, question 4. Open the page and jump to that heading.*

**About you**
1. Walk me through your background. → [01 Q1](01-Role-Company-and-Your-Pitch.md)
2. Why this role, and why Blue Cross? Why leave after about 15 months? → [01 Q2–Q3](01-Role-Company-and-Your-Pitch.md)
3. The JD asks for 8+ years of ML. How do you see your fit? → [01 Q5](01-Role-Company-and-Your-Pitch.md), [10 Q1](10-ML-and-MLOps-Fundamentals.md)
4. Walk me through an AI system you built: architecture, and how you knew it worked. → [01 Q6](01-Role-Company-and-Your-Pitch.md), [13 S1](13-Behavioral-Story-Bank.md#s1) / [S5](13-Behavioral-Story-Bank.md#s5), [04 Q1](04-Azure-AI-Search-and-Foundry.md), [06 Q1](06-Memory-and-Context-Engineering.md)

**Leading and mentoring**
5. You haven't had a lead title. Why should we trust you to lead? → [01 Q4](01-Role-Company-and-Your-Pitch.md), [11 "Read this first"](11-Mentoring-and-Coaching.md)
6. How do you mentor juniors? Tell me about a time you did. → [11 Q1, Q13](11-Mentoring-and-Coaching.md), [13 M1](13-Behavioral-Story-Bank.md#m1)
7. A junior's PR is weak, or full of AI-generated code they can't explain. → [11 Q5–Q6](11-Mentoring-and-Coaching.md)
8. How do you give hard feedback or handle underperformance? → [11 Q4, Q8](11-Mentoring-and-Coaching.md)
9. What standards would you set for an AI team? → [12 Q1](12-Team-Leadership-and-Delivery.md), [11 Q7](11-Mentoring-and-Coaching.md)
10. How do you estimate uncertain AI work with a Product Owner, and say no? → [12 Q2–Q3](12-Team-Leadership-and-Delivery.md)
11. How do you balance 40–50% coding with leading? → [12 Q11](12-Team-Leadership-and-Delivery.md), [11 Q10](11-Mentoring-and-Coaching.md), [01 Q7](01-Role-Company-and-Your-Pitch.md)
12. A senior engineer disagrees with your design. → [11 Q14](11-Mentoring-and-Coaching.md), [12 Q4](12-Team-Leadership-and-Delivery.md)
13. What would your first 90 days look like? → [12 Q13](12-Team-Leadership-and-Delivery.md)
14. Tell me about a conflict, a failure, or a time you pushed back. → [13 C1](13-Behavioral-Story-Bank.md#c1) / [F1](13-Behavioral-Story-Bank.md#f1) / [P1](13-Behavioral-Story-Bank.md#p1)

**Tech, at manager depth**
15. Explain LangGraph, and why you chose it. Workflow vs agent? → [05 Q1–Q2](05-Agents-and-LangGraph.md)
16. Short- vs long-term memory; checkpointer vs store. → [06 Q2–Q3](06-Memory-and-Context-Engineering.md)
17. How does RAG work, and how do you debug a wrong answer? → [03 Q3, Q9](03-RAG.md)
18. How do you know it's good enough to ship, and how do you monitor it? → [07 Q1, Q9](07-Evaluation-and-Observability.md)
19. Hallucinations, PHI, prompt injection, and should AI make coverage decisions? → [02 Q2](02-LLM-Fundamentals.md), [08 Q1, Q4, Q7](08-Security-Responsible-AI-and-HIPAA.md)
20. Design a benefits assistant or a shared agentic AI framework. → [09 Q1, Q4](09-AI-System-Design-Scenarios.md), [05 Q6](05-Agents-and-LangGraph.md)
21. How do you evaluate a new model or framework without chasing hype? → [12 Q5](12-Team-Leadership-and-Delivery.md)
22. What questions do you have for me? → [14](14-Questions-to-Ask.md)

## Your fill-in checklist (do these first; only you can)
- [ ] **S5**: your current memory + RAG + LangGraph + Azure AI Search service: purpose, graph, memory design, retrieval design, status, one hard problem
- [ ] **S1**: eval pass rate, cost per turn, users and adoption for Load Deal AI
- [ ] **S2**: coverage and impact numbers for the Data Validation Service
- [ ] **M1**: a real mentoring story · **C1**: a conflict · **F1**: a failure · **P1**: a pushback
- [ ] Salary number and walk-away point ([01 Q10](01-Role-Company-and-Your-Pitch.md))
- [ ] Confirm interview date, time, format, and interviewer name with the recruiter; look the interviewer up on LinkedIn

## Most useful external reading (if you only read five)
1. [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — the clearest mental model for workflows vs agents.
2. [LangGraph overview (LangChain docs)](https://docs.langchain.com/oss/python/langgraph/overview) — the official concepts.
3. [LangGraph persistence: checkpointers and stores](https://docs.langchain.com/oss/python/langgraph/persistence) — short- vs long-term memory, the way LangGraph defines them.
4. [Azure AI Search: hybrid search overview](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview) — your retrieval stack.
5. [Hamel Husain: Your AI product needs evals](https://hamel.dev/blog/posts/evals/) — the practitioner view of evaluation that managers love to hear.
