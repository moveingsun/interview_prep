# 05 · Agents & LangGraph

[← Index](00-Index.md) · **Manager-round priority:** High · **Read time:** ~40 min

> **Why this matters for this role:** The core of the JD is to "design and oversee complex AI agent components", and BCBSMA is building an **agentic AI framework**. LangGraph is listed in the preferred qualifications, and it's what you use today. Expect four kinds of question: explain it, when would you *not* use it, how do you make it reliable, and how would you teach it to a junior.

---

## Primer

### 1. Workflow vs agent (the distinction that matters most)

Anthropic's framing in *Building effective agents*:

- **Workflow:** LLMs and tools follow **predefined code paths**. *You* decide the steps.
- **Agent:** the LLM **decides its own steps** and tool calls, in a loop, until the task is done.

The rule of thumb is to start with the simplest thing that works (one LLM call plus retrieval), then a workflow, and use an agent only when you can't predict the steps in advance. More autonomy means more cost, more latency, and errors that compound.

| Pattern | What it is | Health-plan example |
|---|---|---|
| **Prompt chaining** | Step A → gate/check → step B | Extract fields from a prior-auth request → validate → draft a summary |
| **Routing** | Classify, then send to a specialised handler | Member question → benefits / claims / pharmacy / human |
| **Parallelization** | *Sectioning* (split the work) or *voting* (run the same task N times) | Run 3 guardrail checks in parallel; vote on "is this a denial letter?" |
| **Orchestrator–workers** | An LLM splits the task into subtasks at runtime, workers execute, results are combined | Answer a policy question that spans several medical-policy documents |
| **Evaluator–optimizer** | One LLM generates, another critiques, loop | Draft a member letter → reviewer checks reading level and compliance → revise |
| **Autonomous agent** | An LLM with tools, in a loop, using feedback from the environment | Investigate a claim discrepancy across several systems |

### 2. The agent loop (ReAct / tool calling)

```
 user msg ─► LLM ──tool_calls?──yes──► your code runs tools ─► append ToolMessage(s) ─┐
              ▲                                                                       │
              └───────────────────────────────────────────────────────────────────────┘
                     └──no──► final answer
```

The model **never runs a tool itself**. It emits a structured message ("call `lookup_benefits` with `{service: "MRI"}`"), your code validates and executes it, appends the result, and calls the model again. Agent reliability comes down to controlling this loop: which tools are available, which arguments are allowed, how many iterations run, and what happens on an error.

### 3. LangGraph mental model: "a state machine where some steps are LLM calls"

1. **State.** A typed object (`TypedDict` or Pydantic) that every node reads and partially updates. Each key can have a **reducer** that says how updates merge. The default overwrites. `add_messages` appends, merges by message ID, and supports `RemoveMessage`. `operator.add` concatenates lists.
2. **Nodes.** Plain Python functions of the form `state → partial update`. A node can be an LLM call, a tool run, retrieval, validation, or anything else.
3. **Edges.** These decide what runs next. A normal edge always goes A→B. A **conditional edge** is a function that reads state and returns the next node's name. `START` and `END` mark the entry and exit.

You then `compile()` the graph, optionally with a **checkpointer** (short-term memory) and a **store** (long-term memory), and run it with `invoke` or `stream`, passing a `thread_id`.

**Execution model:** the graph runs in **super-steps**, in the Pregel / bulk-synchronous style. All nodes scheduled for a step run in parallel. Their updates are merged through the reducers, a checkpoint is saved, and the next step starts. This is why reducers matter: if two parallel nodes write the same key, you need a merge rule.

```python
# Illustrative sketch: the ReAct loop drawn as a graph
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver   # tests only; PostgresSaver etc. in prod

class State(TypedDict):
    messages: Annotated[list, add_messages]   # reducer: append, don't overwrite
    member_id: str

tools = [lookup_benefits, search_policy_docs]
llm = model.bind_tools(tools)

def call_model(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

def route(state: State):
    return "tools" if state["messages"][-1].tool_calls else END

g = StateGraph(State)
g.add_node("agent", call_model)
g.add_node("tools", ToolNode(tools))
g.add_edge(START, "agent")
g.add_conditional_edges("agent", route, ["tools", END])
g.add_edge("tools", "agent")
graph = g.compile(checkpointer=InMemorySaver())

cfg = {"configurable": {"thread_id": "member-123:session-9"}, "recursion_limit": 15}
graph.invoke({"messages": [("user", "Is an MRI covered?")], "member_id": "123"}, cfg)
```

In LangChain 1.0 the same thing is one call: `create_agent(model, tools, ...)`. You drop down to raw LangGraph when you need custom control flow, such as deterministic validation nodes, routing, approvals, or fan-out.

### 4. Features you should be able to name and explain

| Concept | One-liner | Why you care |
|---|---|---|
| **Checkpointer + `thread_id`** | Saves a snapshot of state after every super-step, keyed by thread | Conversation memory, resume after a crash, human-in-the-loop, time travel |
| **Store** | Cross-thread JSON key–value store with namespaces and optional semantic search | Long-term memory (see [06](06-Memory-and-Context-Engineering.md)) |
| **`interrupt()` / `Command(resume=…)`** | Pause inside a node, return a payload to the caller, resume later with human input | Approval before writes; clarification questions |
| **`Command(goto=…, update=…)`** | A node returns both a state update *and* the next destination | Agent handoffs and dynamic routing without a separate edge function |
| **`Send(node, payload)`** | Fan out N copies of a node with different inputs | Map-reduce, e.g. summarise 20 documents in parallel and then combine |
| **Subgraphs** | A compiled graph used as a node in another graph | Team ownership; a reusable "retrieval subgraph" shared across agents |
| **`recursion_limit`** | Maximum super-steps per run (raises `GraphRecursionError`) | Guard against runaway loops |
| **Stream modes** | `values`, `updates`, `messages` (tokens), `custom`, `checkpoints`, `tasks`, `debug` | Token streaming to the UI, progress events ("searching policy docs…") |
| **Durable execution** | Resume from the last checkpoint after a failure; `durability` setting controls when checkpoints are written | Long-running workflows. Side effects must be idempotent or wrapped in `@task` |
| **Time travel** | Replay or fork from any earlier checkpoint (`get_state_history`) | Debugging and "what if" analysis |

> ⚠️ **Interrupt gotcha:** on resume, the node **re-runs from the top**, so code before `interrupt()` runs twice. Put side effects *after* the interrupt (or in a separate node) or make them idempotent. Don't wrap `interrupt()` in a bare `try/except`, because the pause works by raising an exception.

### 5. Where LangGraph sits in 2026

- **LangGraph 1.0** went GA in **October 2025** with no breaking changes. Durable execution, streaming, and human-in-the-loop are first-class features.
- **LangChain 1.0 `create_agent`** (`from langchain.agents import create_agent`) is the high-level agent, and it **runs on LangGraph**. You customise it with **middleware**, for example `SummarizationMiddleware`, `HumanInTheLoopMiddleware`, `PIIMiddleware`, `ToolRetryMiddleware`, `ModelRetryMiddleware`, model fallback, and call limits. Hooks such as `before_model`, `after_model`, `wrap_model_call`, and `wrap_tool_call` run around each model or tool call. It is the recommended successor to `langgraph.prebuilt.create_react_agent`.
- **Deep Agents** (`deepagents`) is LangChain's harness for long-running agents, with planning, sub-agents, a virtual filesystem, and context management.
- **Microsoft side:** **Microsoft Agent Framework** succeeds Semantic Kernel and AutoGen and reached 1.0 GA in April 2026. **Foundry Agent Service** is the managed runtime; *hosted agents* went GA in July 2026 and can run code from other frameworks. Foundry IQ knowledge bases can be exposed over **MCP**, so a LangGraph agent can use them as well.

---

## Questions & answers

### Q1. "Explain LangGraph to me as if I were a manager. Why did you choose it?" `[P0]`

**Say this first (~30 sec):** "LangGraph lets me lay out an AI workflow as a graph of steps. Some steps are LLM calls and some are plain code, and they all share one state object. Unlike a black-box agent, I decide where the model gets to make choices, where code enforces the rules, and where a human has to approve. Every step is also checkpointed, so conversations have memory, a failed run can resume, and I can pause for an approval. In a regulated setting I want deterministic guardrails around a non-deterministic model, and that's why I chose it."

**If they dig deeper:**
- State + nodes + edges + reducers. The checkpointer gives short-term memory and the store gives long-term memory.
- Compared with a plain loop, I don't rebuild persistence, streaming, retries, or human-in-the-loop myself.
- Compared with a fully managed agent service, I keep explicit control flow and I can test each node with a hand-built state dict.

**Your angle:** In [S1](13-Behavioral-Story-Bank.md#s1), the LangGraph pipelines agent had a **citation-check step**, a deterministic node that runs after generation. That's exactly the "code enforces the rules" point. Your current project is [S5](13-Behavioral-Story-Bank.md#s5). `[fill in: one sentence on why your team picked LangGraph]`

**Likely follow-ups:** When would you *not* use it? How is it different from LangChain? How do you deploy it?

---

### Q2. "Workflow vs agent: when do you give the LLM autonomy?" `[P0]`

**Say this first:** "Workflows are my default. I give autonomy only when the path really can't be predicted and the value justifies the extra cost and risk. In healthcare, anything that changes data or affects a member decision stays on a deterministic path with a human approval."

**If they dig deeper:**
- I decide on four things: how predictable the steps are, how costly an error is, the latency budget, and whether I can evaluate it.
- I think of an **autonomy dial**: single call → chain → router → agent with read-only tools → agent with write tools behind approval.
- Errors compound. If each step is 95% reliable, ten chained steps are about 60% reliable (0.95¹⁰ ≈ 0.6).
- Constrained autonomy is often the best of both. An example is text-to-SQL over a **semantic view** instead of raw tables.

**Your angle:** In [S2](13-Behavioral-Story-Bank.md#s2), the LLM judge *classifies* defects but **never writes without confirmation**. In [S1](13-Behavioral-Story-Bank.md#s1) and [S4](13-Behavioral-Story-Bank.md#s4), the Cortex agent is constrained by a semantic view.

**Likely follow-ups:** Give an example where you started with an agent and moved back to a workflow, or the reverse.

---

### Q3. "Walk me through how tool calling actually works." `[P0]`

**Say this first:** "The model gets each tool's name, description, and JSON schema. When it needs a tool, it returns a structured tool call with a name and arguments instead of text. My code validates the arguments, runs the tool **with the user's permissions**, and sends the result back as a tool message, and then the model continues. The model never touches the system directly, so authorization, validation, and logging live in my code, not in the prompt."

**If they dig deeper:**
- Models can request **parallel tool calls**. `tool_choice` can force a tool, and structured output is essentially a forced tool call.
- I return tool *errors* to the model as messages so it can self-correct, but for safety errors I abort.
- Tool descriptions are prompt engineering. Once there are a couple of dozen tools, selection quality drops, so I route or load tools dynamically.
- I cap the size of tool results, because large payloads blow up the context and the cost.

**Likely follow-ups:** How does the model "know" which tool to use? What if it hallucinates an argument?

---

### Q4. "How would you make an agent reliable enough for production?" `[P0]`

**Say this first:** "I treat it like a distributed system with one non-deterministic component. I **bound** it with step limits, timeouts, and token budgets. I **validate** everything that crosses a boundary: structured outputs against schemas, tool arguments, and things like citations. I make **failure explicit** with retries, fallback models, and a graceful 'I can't answer that, here's a human' path. Then I **measure** it with evals and tracing so I know when it regresses."

**If they dig deeper** (checklist):
- `recursion_limit` or model-call limits, a per-run token and dollar budget, and a wall-clock timeout.
- Pydantic-validated structured output, retried once or twice on a validation failure, then a safe failure.
- **Idempotency keys** on write tools, and side effects placed after interrupts.
- Model fallback (primary → secondary deployment or region), 429/backoff handling, and a circuit breaker.
- **Deterministic post-checks:** citations must exist in the retrieved documents, numbers must match the source, and PHI filters run on output.
- A **durable checkpointer** (Postgres, Redis, or Cosmos) so a pod restart doesn't lose a conversation.
- Tracing on every node and tool call, recording tokens and latency, with alerts on loop rate, fallback rate, and escalation rate.
- An **eval gate in CI** for any prompt, model, or tool change.

**Your angle:** In [S1](13-Behavioral-Story-Bank.md#s1) you had citation checks, an eval set, and per-turn cost tracking. In [S9](13-Behavioral-Story-Bank.md#s9), access checks fail closed. In [S14](13-Behavioral-Story-Bank.md#s14), the KEDA job service has stuck-run recovery and cascade-cancel, which shows the same distributed-systems instincts.

**Likely follow-ups:** What's the most common production failure you've seen in an LLM app? How do you alert on quality rather than just uptime?

---

### Q5. "Multi-agent: when does it make sense, and when is it a mistake?" `[P0]`

**Say this first:** "Multi-agent helps when one agent has too many tools or too much context to choose well, when subtasks really can run in parallel, or when different teams own different capabilities. It's a mistake when it just copies the org chart. Every extra agent adds model calls, latency, cost, and new failure modes, such as context getting lost at handoffs. My default is a single agent with well-designed tools, and I split only when evals show that tool selection or context is the bottleneck."

**If they dig deeper** (pattern menu):

| Pattern | How it works | Good for | Cost |
|---|---|---|---|
| **Supervisor / subagents-as-tools** | A main agent calls specialist agents as tools | Parallel research; centralised control | Extra hop through the supervisor |
| **Handoffs (swarm)** | The active agent transfers control with a tool call that updates state (`Command(goto=…)`) | Conversational specialists (benefits → pharmacy) | Sequential |
| **Router** | Classify once, dispatch to specialist(s), synthesise | Cheap, predictable, parallelisable | Stateless, so one routing call per request |
| **Hierarchical** | Supervisors of supervisors | Very large tool or domain surface | Complexity |
| **Custom workflow** | A LangGraph graph mixing deterministic steps and agent steps | Most enterprise cases | You design it |

- Anthropic reported that its multi-agent research system used about **15× the tokens of a chat**, which was worth it for hard, parallel research and wasteful elsewhere. Cognition's *Don't build multi-agents* post argues that failures to share context are the main risk.

**Your angle:** In [S1](13-Behavioral-Story-Bank.md#s1) you had **two specialised agents**: a Cortex agent for SQL over a semantic view and a LangGraph pipelines agent. That's domain routing. `[fill in: how requests were routed between them]`

**Likely follow-ups:** How do agents share state? How do you debug a multi-agent failure?

---

### Q6. "How would you design a reusable agentic AI framework that multiple teams build on?" `[P0]`

*BCBSMA is building one, so this is very likely to come up in some form.*

**Say this first:** "The platform should own what every team either gets wrong or must not get wrong: identity and authorization, model access, guardrails, PHI handling, tracing, evaluation, and deployment. Teams own their prompts, tools, and graphs. It should be a **paved road, not a cage**: a template repo, a library of approved tools and retrieval components, and a standard eval and release process."

**If they dig deeper** (layers):
1. **Runtime:** LangGraph (or Agent Framework) templates, with a durable checkpointer and store as managed services and a standard state-schema convention.
2. **Model gateway:** APIM / AI gateway in front of the Foundry deployments, handling auth, per-team quotas, token metering, fallback, content safety, and logging.
3. **Tool registry:** tools as **MCP servers** or registered functions, each with a schema, an owner, scopes, a PHI classification, and rate limits. Read and write tools are separated, and write tools carry an approval policy.
4. **Knowledge:** a shared retrieval service on Azure AI Search / Foundry IQ with security trimming and per-domain indexes.
5. **Guardrails as default middleware:** input/output filters, prompt-injection shields, PII redaction, and citation checks.
6. **Observability & eval:** OpenTelemetry tracing, cost per team, agent, and turn, an eval harness with golden sets, a CI gate, and online feedback.
7. **Governance:** an agent registry, risk tiering (human review required by tier), audit logs, and model and agent cards.
8. **Developer experience:** cookiecutter templates, local dev, docs, example agents, and office hours.
- **Success metrics:** time to first agent in production, number of teams onboarded, percentage of agents on the paved road, and incident rate.

**Your angle:** [S3](13-Behavioral-Story-Bank.md#s3) **Watt AI Shell** *is* a platform front door: an entitlements-driven app registry, APIM routing, and specs you wrote for other engineers. [S10](13-Behavioral-Story-Bank.md#s10), where you onboarded 10+ teams to Composer, is your adoption playbook. [S6](13-Behavioral-Story-Bank.md#s6) is developer enablement.

**Likely follow-ups:** How do you stop teams bypassing it? (Make the paved road the easiest path and enforce guardrails at the gateway.) Build or buy?

---

### Q7. "How would you explain LangGraph to a junior engineer in two minutes?" `[P0]`

*This tests your mentoring as much as your knowledge.*

**Say this first (the script):** "Think of it as a flowchart that actually runs. The boxes are Python functions, the arrows decide what runs next, and there's one shared notebook, the *state*, that every box can read and write. Some boxes call an LLM. An arrow can be conditional: 'if the model asked for a tool, go to the tools box; otherwise finish.' Each time a box finishes, LangGraph saves a snapshot of the notebook, and that gives us conversation memory, crash recovery, and the ability to pause for a human. Your job is to keep each box small and testable, put the rules in code instead of in prompts, and let the LLM decide only where it has to."

**Then how you'd teach it:**
- **Pair-build** a three-node graph together, then render it with `graph.get_graph().draw_mermaid()`.
- Walk through a real **trace** in LangSmith or Foundry tracing, so they see what the model saw at each step.
- Progression: deterministic nodes → add one tool → add a conditional edge → add a checkpointer → add an interrupt.
- Review their PRs by reading the traces, not just the diff.

**Your angle:** In [S6](13-Behavioral-Story-Bank.md#s6) you built a domain knowledge base and CLAUDE.md so that context carries across sessions. That's the same instinct as writing docs juniors can learn from. See [11](11-Mentoring-and-Coaching.md).

---

### Q8. "LangGraph vs a plain loop vs `create_agent` vs Microsoft Agent Framework / Foundry Agent Service vs OpenAI Agents SDK / CrewAI: how do you choose?" `[P1]`

**Say this first:** "I score them on how much control flow I need, persistence and human-in-the-loop needs, team skills, hosting and governance constraints, lock-in, and maturity. They're also not mutually exclusive: a LangGraph agent can call Foundry models, use Azure AI Search, and run as a Foundry hosted agent."

| Option | Best when | Watch out for |
|---|---|---|
| Plain loop over the model SDK | One tool, a prototype | You'll end up rebuilding persistence, retries, and streaming |
| LangChain `create_agent` + middleware | A standard tool-calling agent that needs guardrail hooks quickly | Unusual flows (you can drop down to LangGraph) |
| **LangGraph** | Custom control flow, human-in-the-loop, durable long-running work, mixed deterministic and agentic steps | Learning curve; you own hosting unless you use LangSmith Deployment or Foundry hosted agents |
| Microsoft Agent Framework | Azure/.NET-heavy shops; graph workflows plus agents; native Foundry integration | Younger ecosystem |
| Foundry Agent Service | Managed hosting, built-in tools (AI Search, code interpreter), Entra identity, enterprise governance | Less control over flow; platform coupling |
| OpenAI Agents SDK | Lightweight handoffs and guardrails | Centred on OpenAI |
| CrewAI | Quick role-based "crew" prototypes | Coarser control |

**Your angle:** You run LangGraph on Foundry today. `[fill in: what drove that choice: control, team familiarity, portability?]`

---

### Q9. "How do you design good tools for an agent?" `[P1]`

**Say this first:** "A tool is an API whose caller is non-deterministic. A few well-named, purpose-built tools with tight schemas beat a thin wrapper around every endpoint. Read tools are safe to retry. Write tools must be idempotent and least-privilege, and they usually sit behind a human confirmation."

**If they dig deeper:**
- Names and descriptions *are* prompts: say when to use the tool and when not to.
- **Consolidate:** one `get_member_benefit_summary(member_id, service)` rather than five raw endpoints.
- Constrain arguments with enums, `Literal`, or Pydantic, and **validate on the server side as well**.
- Return concise, high-signal results (truncation, pagination, IDs for follow-up calls) and error messages the model can act on.
- Run tools **on behalf of the end user's identity**, not as an all-powerful service account, and enforce entitlements inside the tool.
- **PHI:** return only the minimum necessary fields.
- Use idempotency keys and a dry-run mode, require confirmation via `interrupt`, and log every call.

**Your angle:** [S2](13-Behavioral-Story-Bank.md#s2) never writes without confirmation. [S9](13-Behavioral-Story-Bank.md#s9) has entitlements and fails closed. [S3](13-Behavioral-Story-Bank.md#s3) has UI-element permissions.

---

### Q10. "What are MCP and A2A, in plain English?" `[P1]`

**Say this first:** "**MCP**, the Model Context Protocol, is a standard plug for connecting AI apps to tools and data. You write a tool server once and any MCP client can use it, whether that's Claude, Copilot, LangChain, or Foundry agents. Think USB-C for tools. **A2A**, Agent-to-Agent, is a standard for agents talking to *other agents* across systems and vendors: they discover each other's capabilities through an 'agent card', send tasks, and get results back. In short, MCP is agent ↔ tools and A2A is agent ↔ agent."

**If they dig deeper:**
- **MCP primitives:** tools, resources, and prompts. Transports are stdio for local and streamable HTTP for remote, with OAuth-based auth.
- **Risks:** tool poisoning (malicious tool descriptions), over-broad permissions, and untrusted servers. Mitigate with an allowlist of servers, a gateway, and per-tool scopes.
- Both are now under the Linux Foundation: MCP through the Agentic AI Foundation, and A2A as a project originally from Google.
- **Why it matters for a framework:** a tool registry built as MCP servers can be reused across teams *and* across frameworks. Foundry IQ knowledge bases are already exposed over MCP.

---

### Q11. "How do you test and evaluate an agent?" `[P1]`

**Say this first:** "At three levels. Unit tests cover deterministic nodes and tools. Component evals cover each LLM step: router accuracy, retrieval recall, extraction accuracy. End-to-end evals on a golden set check the final answer *and* the **trajectory**: did it call the right tools, in a sensible order, with the right arguments, in a reasonable number of steps? They run in CI on every prompt or model change, and I keep sampling production traces back into the dataset."

**If they dig deeper:**
- **Trajectory match modes:** strict, unordered, subset, or superset, or an LLM-as-judge on the trajectory.
- **Metrics:** task success, tool-call accuracy, steps per task, cost per task, p95 latency, escalation rate.
- **Multi-turn:** simulated users. **Safety:** a red-team set for prompt injection and PHI leakage.
- Because LangGraph state is explicit, you can test any node by passing it a hand-built state dict.
- Calibrate LLM judges against human labels before you trust them.

**Your angle:** [S1](13-Behavioral-Story-Bank.md#s1) had a 20-question eval set plus citation checks, and [S2](13-Behavioral-Story-Bank.md#s2) used an LLM judge. More in [07](07-Evaluation-and-Observability.md).

---

### Q12. "Agents are slow and expensive. How do you manage cost and latency?" `[P1]`

**Say this first:** "Use fewer and cheaper calls. Don't use an agent where a workflow will do, route easy requests to smaller models, run independent steps in parallel, cache, and stream so the user sees progress. And I measure **cost per turn**, so it's a number rather than a feeling."

**If they dig deeper:**
- **Model tiering:** a small model for routing and classification, a large one only for hard reasoning.
- **Prompt caching:** put the stable prefix (system prompt and tool definitions) first.
- Trim context, cap tool-result size, use parallel tool calls and `Send` fan-out, and add a semantic cache for FAQ-type questions.
- Use `messages` streaming for tokens and `custom` streaming for progress events.
- **Azure:** provisioned throughput (PTU) for steady load and pay-as-you-go for spiky load; batch APIs for offline jobs.

**Your angle:** [S1](13-Behavioral-Story-Bank.md#s1) tracked per-turn cost. [S4](13-Behavioral-Story-Bank.md#s4) cut query time from 85.6s to 8.8s. [S14](13-Behavioral-Story-Bank.md#s14) and [S7](13-Behavioral-Story-Bank.md#s7) show the same performance and cost mindset applied to LLMs.

---

### Q13. "What is a checkpointer, and why does it matter in production?" `[P1]`

**Say this first:** "It saves a snapshot of the graph state after every step, keyed by `thread_id`. That gives you conversation continuity, resume-after-crash, human-in-the-loop pauses that can last hours or days, and time-travel debugging. In production you use a durable backend such as Postgres, Redis, or Cosmos. `InMemorySaver` is only for tests."

**If they dig deeper:**
- Storage grows quickly because there's a checkpoint per step, so you need TTL or pruning.
- **Checkpoints contain PHI**, so they need encryption, retention rules, and access control.
- Design the thread ID deliberately (e.g. `tenant:user:session`). Handle "double-texting", where two requests hit the same thread at once.
- The checkpointer is separate from the long-term store; see [06](06-Memory-and-Context-Engineering.md).

---

### Q14. "How does human-in-the-loop work in LangGraph?" `[P1]`

**Say this first:** "Inside a node I call `interrupt(payload)`, for example 'approve sending this letter?'. The graph pauses, checkpoints, and returns that payload to the caller. Later, possibly hours later, I resume on the same `thread_id` with `Command(resume=decision)`. `interrupt` returns the decision and the node carries on. With `create_agent`, `HumanInTheLoopMiddleware` does this per tool, with approve, edit, or reject."

**If they dig deeper:**
- It requires a checkpointer. The node re-runs from the top on resume, so side effects go after the interrupt. Never wrap `interrupt()` in `try/except`.
- **Patterns:** approve or reject a tool call, edit its arguments, review the output, or ask for clarification.

**Your angle:** In [S2](13-Behavioral-Story-Bank.md#s2), the validation service never writes without confirmation.

---

### Q15. "What are reducers, and why do they matter?" `[P2]`

**Say this first:** "A reducer is the rule for merging a node's update into a state key. The default overwrites. `add_messages` appends, de-duplicates by ID, and supports `RemoveMessage`. You can also write custom ones. They matter for parallel branches: if two nodes update the same key in one super-step without a reducer, LangGraph raises an `InvalidUpdateError`."

---

### Q16. "Explain `Send` and `Command`." `[P2]`

**Say this first:** "`Send` is dynamic fan-out: from a conditional edge you return `[Send('summarize', {'doc': d}) for d in docs]`, N parallel copies run, and a reducer collects their results. That's map-reduce. `Command` lets a node return a state update *and* a `goto` together, which is how agent handoffs work. `Command(resume=…)` is also how you resume after an interrupt."

---

### Q17. "An agent keeps calling the same tool in a loop. What do you do?" `[P2]`

**Say this first:** "I **prevent** it with `recursion_limit` or model-call limits. I **detect** it with a counter in state, such as the same tool with the same arguments N times. I **recover** by forcing a final answer or escalating to a human. Then I find the root cause in the traces. It's usually an ambiguous tool description or an unhelpful error message that the model keeps retrying against."

---

### Q18. "How do you version and deploy agents safely?" `[P2]`

**Say this first:** "Prompts, tool schemas, graph code, and the model deployment version are versioned *together*, as one release. Every change goes through an eval gate, then a canary or shadow rollout behind a feature flag, with one-click rollback. I pin model versions and re-run evals before any model upgrade. When the state schema changes, I make the change additive so existing checkpoints still load."

---

## Key terms

| Term | Meaning |
|---|---|
| ReAct | Reason + Act: the model alternates reasoning with tool calls and observations |
| Super-step | One parallel tick of graph execution, followed by a checkpoint |
| Thread | One conversation or run history, identified by `thread_id` |
| Trajectory | The sequence of steps and tool calls an agent took |
| HITL | Human-in-the-loop |
| MCP / A2A | Agent↔tool protocol / agent↔agent protocol |

## References

- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents). The workflow-vs-agent patterns; read this first.
- [Anthropic: Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents). Tool design principles.
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system). When multi-agent pays off, plus the token-cost data.
- [Cognition: Don't build multi-agents](https://cognition.ai/blog/dont-build-multi-agents). The counter-argument (context sharing).
- [LangGraph overview (docs)](https://docs.langchain.com/oss/python/langgraph/overview). Official entry point.
- [LangGraph Graph API: state, nodes, edges, reducers, Send, Command](https://docs.langchain.com/oss/python/langgraph/graph-api). Core concepts in depth.
- [LangGraph: Workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents). The Anthropic patterns implemented in LangGraph.
- [LangGraph persistence (checkpointers & stores)](https://docs.langchain.com/oss/python/langgraph/persistence). Threads, checkpoints, time travel.
- [LangGraph interrupts (human-in-the-loop)](https://docs.langchain.com/oss/python/langgraph/interrupts). Pause/resume semantics and gotchas.
- [LangGraph streaming](https://docs.langchain.com/oss/python/langgraph/streaming). The stream modes.
- [LangChain agents (`create_agent`)](https://docs.langchain.com/oss/python/langchain/agents) and [middleware](https://docs.langchain.com/oss/python/langchain/middleware). The high-level agent on top of LangGraph.
- [LangChain multi-agent patterns](https://docs.langchain.com/oss/python/langchain/multi-agent). Subagents, handoffs, router, skills, and when not to go multi-agent.
- [LangChain Academy: Intro to LangGraph (free course)](https://academy.langchain.com/courses/intro-to-langgraph). Best hands-on way past "shallow".
- [Microsoft Agent Framework overview](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview). Microsoft's successor to Semantic Kernel and AutoGen.
- [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview). Managed agent runtime on Azure.
- [Model Context Protocol](https://modelcontextprotocol.io/). MCP spec and concepts.
- [A2A protocol](https://a2a-protocol.org/). Agent-to-agent spec.
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/). For comparison (handoffs, guardrails).
- [agentevals (trajectory evaluators)](https://github.com/langchain-ai/agentevals). Open-source trajectory evaluation.
- [ReAct paper (Yao et al., 2022)](https://arxiv.org/abs/2210.03629). The original reason+act loop.
