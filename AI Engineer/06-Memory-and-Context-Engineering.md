# 06 · Memory & Context Engineering

[← Index](00-Index.md) · **Manager-round priority:** High (it's your current project) · **Read time:** ~35 min

> **Why this matters for this role:** "Tell me about what you're building right now" is close to guaranteed. Memory is where an AI engineer's judgment shows: what to remember, where it lives, how it goes stale, and, in healthcare especially, **what you must not remember**. Your answers here are your most credible signal of hands-on agent work.

---

## Primer

### 1. The one-sentence mental model

**The model is stateless. "Memory" means what *you* choose to put back into the context window on the next call.** That makes memory a data-engineering and retrieval problem, not magic.

```
┌─────────────────────── Context window (what the model sees on THIS call) ───────────────────────┐
│ system prompt + rules │ long-term memories (selected) │ running summary │ recent msgs │ tool results │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
          ▲ select / compress                 ▲ select                          ▲ fetch live
 SHORT-TERM (thread-scoped)         LONG-TERM (cross-thread)          SOURCE-OF-TRUTH SYSTEMS
 LangGraph checkpointer             LangGraph Store / memory DB       eligibility, claims, benefits,
 key: thread_id                     key: namespace + key              EHR, policies (via tools / RAG)
 messages, scratchpad, summary      semantic / episodic / procedural  → never "remembered", always fetched
```

### 2. Short-term memory (thread-scoped)

- It lives in **graph state** (usually `messages`) and is persisted by the **checkpointer** after every step, keyed by `thread_id`.
- **The problem:** it grows without limit. Long histories cost money, add latency, and *degrade quality* (see context rot below).
- Techniques:
  - **Trim:** keep the last N tokens (`trim_messages`). Start on a human message and never split a tool-call/tool-result pair.
  - **Summarize:** keep a **running summary** plus the last *k* turns verbatim (`SummarizationMiddleware` in `create_agent`, or a summary node).
  - **Delete:** return `RemoveMessage(id=…)` to drop specific messages, such as bulky tool outputs.
  - **Offload:** store a large tool output in a separate state field or a file, and keep only a short reference in the messages.
- **Token budget example:** a 128k window doesn't mean "use 128k". Budget it, say ~2k for system and rules, ~1k for the memory profile, ~4k for retrieved docs, ~2k for the summary, ~6k for recent turns, and the rest as headroom.

### 3. Long-term memory (cross-thread)

- It lives in a **Store**. Items are JSON documents under a **namespace** (a tuple, like a folder, e.g. `("member", member_id, "preferences")`) and a **key**. Semantic search over items is optional (`index={"embed": …, "dims": …}`).
- The three memory types come from the CoALA paper, a cognitive-science framing:

| Type | What it stores | Health-plan example | Typical implementation |
|---|---|---|---|
| **Semantic** | Facts and preferences | "Prefers Spanish; prefers text over phone; caregiver for a parent" | Profile doc or a collection of facts |
| **Episodic** | Past experiences and interactions | "Last month we helped find an in-network PT; resolved" · few-shot examples of good resolutions | Episode summaries; example store |
| **Procedural** | How to behave (rules, instructions) | "For prior-auth questions, check plan type before answering" | Prompt or instructions updated via reflection, **human-reviewed** |

- **Profile vs collection:** a **profile** is one small JSON doc that's always injected and easy to read, but updates get error-prone as it grows. A **collection** is many small memory items with high recall that you search, but updating, de-duplicating, and deleting are harder.

### 4. Writing memories: hot path vs background

| | **Hot path** (during the turn) | **Background** (after or between turns) |
|---|---|---|
| How | The agent calls a `save_memory` tool | A separate job extracts memories from the transcript |
| Pros | Immediate and transparent ("I'll remember that") | No added latency; memory logic is separate from app logic; can batch and consolidate |
| Cons | Adds latency; splits the agent's attention; noisy writes | Memory isn't available until the job runs; you have to choose the trigger (end of session, debounce, cron) |

The **extraction and consolidation** step reads the transcript *plus existing memories* and decides whether to **add, update, or delete**. That's what stops duplicates and contradictions. LangChain's **LangMem** SDK (`create_memory_manager`, plus memory tools) and Foundry Agent Service's **Memory (preview)** both automate this.

### 5. Reading memories

Always inject the small **profile**. **Semantic-search** the collection using the current message (top-k, filtered by namespace), weighted for recency. Render memories **with provenance and dates** ("[2026-08-14, member said] prefers text"), so the model and the auditors can judge freshness.

### 6. Context engineering: the bigger frame

*"The delicate art and science of filling the context window with just the right information for the next step."* (Karpathy). LangChain groups the strategies into four:

| Strategy | Meaning | Examples |
|---|---|---|
| **Write** | Save context *outside* the window | Scratchpads, todo lists, long-term memories, files |
| **Select** | Pull in only what's relevant | Memory search, RAG, tool selection / loading tools dynamically |
| **Compress** | Keep the tokens, lose the bulk | Summarization, trimming, compaction of tool results |
| **Isolate** | Split context across boundaries | Sub-agents with their own windows, separate state fields, sandboxes |

**Context rot:** model accuracy drops as input grows, *even well inside the context window* (Chroma's 2025 study). It's related to "**lost in the middle**": information in the middle of a long context is used less reliably than information at the start or end. **Anthropic's guidance:** find "the smallest set of high-signal tokens" that maximises the chance of the right outcome.

### 7. Healthcare guardrails for memory (say these unprompted; they differentiate you)

- **Memory stores and checkpoints are PHI stores.** They need encryption at rest, private endpoints, RBAC, audit logs, and to sit under the BAA scope, the same as any clinical database.
- **Minimum necessary:** remember only what improves service. Prefer preferences over clinical facts, and classify memory fields.
- **Isolation:** derive the namespace from the **authenticated identity**, never from model output, and enforce it in the store layer so a prompt can't ask for another member's memories.
- **Source of truth wins:** *never* answer eligibility, claims, or benefits from memory. Fetch them live. Memory can hold "member asked about MRI coverage", never "MRI is covered".
- **Retention and deletion:** use TTLs aligned to the records-retention policy. HIPAA gives members rights of **access and amendment**. Deletion obligations come from org policy and state privacy law, so agree the rules with the privacy office and **design for deletion from day one** (per-member namespace, `delete_thread`, purge jobs).
- **Transparency:** members and agents should be able to see and correct "what the assistant remembers".
- **Memory poisoning:** injected text can get saved as a "memory" and replayed later. Don't store instructions as memories, validate what gets extracted, and keep provenance.

---

## Questions & answers

### Q1. "Tell me about the memory design of what you're building now, in 60 seconds." `[P0]`

*Fill in this template ([S5](13-Behavioral-Story-Bank.md#s5)) and rehearse it out loud until it fits in 60–75 seconds.*

> "We're building **[service]** for **[users]** so they can **[job to be done]**.
> **Short-term memory** is LangGraph's checkpointer on **[Postgres / Cosmos / Redis]**, keyed by a thread ID of **[e.g., user:session]**. We keep the last **[N]** turns verbatim and roll older turns into a running summary once we pass **[X]** tokens.
> **Long-term memory** lives in **[store]**, namespaced by **[user / tenant]**, and stores **[preferences / facts / episode summaries]**. We write it **[in the background after each session / through a tool]** and read it **[profile always + top-k semantic search]**.
> **Knowledge** is separate: RAG over an **Azure AI Search** index of **[docs]**, using hybrid search plus the semantic ranker, with **[security filters]**.
> The hardest problem so far was **[stale memories / latency / summaries losing detail]**, and we handled it by **[…]**. Next up is **[memory evals / retention policy / …]**."

**Tips:** draw the three-box diagram from the primer while you talk, know one or two real numbers (tokens per turn, p95 latency, number of memories per user), and say **why** you made each choice, not just what you chose.

**Likely follow-ups:** Why that store? What happens when memory contradicts a source system? How do you test it? What would you change?

---

### Q2. "What's the difference between short-term and long-term memory in an agent?" `[P0]`

**Say this first:** "Short-term memory is the **current conversation**: the messages and working state of one thread, saved by a checkpointer so the agent can continue, resume after a failure, or pause for a human. Long-term memory spans **threads**: facts, preferences, and past episodes about a user or the domain, kept in a separate store and *retrieved* into context when relevant. Short-term is like RAM for a session. Long-term is a personal database the agent queries."

**If they dig deeper:** different lifetimes (session vs months), different access patterns (load everything vs search and select), different governance (long-term needs consent, retention, and correction).

---

### Q3. "Checkpointer vs Store: when do you use which?" `[P0]`

**Say this first:** "The **checkpointer** saves the *whole graph state* after every step for one `thread_id`. Use it for conversation continuity, human-in-the-loop, crash recovery, and time travel. The **Store** is an application-defined key–value store, with optional semantic search, that's **shared across threads**. Use it for anything that should outlive a conversation, like preferences or learned facts. Most production apps use both, compiled into the same graph."

**If they dig deeper:**
- Checkpoint data is high-volume and short-lived, so it needs TTL and pruning. Store data is curated and long-lived, so it needs consolidation and correction.
- `InMemorySaver` / `InMemoryStore` are for tests only. Production options include `PostgresSaver` / `PostgresStore` and Redis or Mongo variants (Cosmos via partner/community packages).
- Nodes access the store through `runtime.store` (or an injected `store`). You `put` and `search` by namespace.

---

### Q4. "Design memory for a member-service assistant at a health plan." `[P0]`

**Say this first:** "I'd split it three ways. **Live data**, like eligibility, claims, and benefits, is never remembered; it's always fetched through tools with the member's entitlements. **Short-term**: the conversation state in a checkpointer, with a running summary so long chats stay cheap and accurate. **Long-term**: a *small*, consented, per-member profile of preferences and open issues, written in the background after the session and shown to the member and to the call-centre rep. All of it is treated as PHI."

**If they dig deeper:**
- **Namespace:** `("member", <id from auth token>)`. A separate `("org", "faq_episodes")` namespace holds de-identified good resolutions as few-shot examples.
- **What to remember:** language and channel preferences, accessibility needs, an open case or ticket ID, the last topic. **Not** diagnoses or claim details; those are re-fetched live.
- **Writes:** background extraction at session end, with add/update/delete consolidation against the existing profile and provenance plus a timestamp on each item.
- **Reads:** inject the profile (under ~500 tokens) and search episodes only when relevant.
- **Handoff:** when the member escalates to a human, give the rep the summary and the profile, so the member doesn't have to repeat themselves.
- **Governance:** retention TTL, a correction UI, audit logs, private networking, encryption, and evals for leakage across members.
- **Metrics:** repeat-contact rate, average handle time on handoffs, CSAT, and memory precision (sampled human review).

**Your angle:** apply your [S9](13-Behavioral-Story-Bank.md#s9) entitlement thinking: memory reads are authorization decisions, and they **fail closed**.

---

### Q5. "How do you stop memory from going stale or wrong?" `[P0]`

**Say this first:** "Four layers. **Store less**: only stable preferences, never things the source system owns. **Consolidate on write**: extraction compares against existing memories and updates or deletes rather than appending duplicates. **Age it**: timestamps, TTLs, and recency weighting at retrieval. **Let the truth win**: memories are rendered with their dates as hints, the prompt says live tool data overrides memory, and members or reps can correct them."

**If they dig deeper:** run periodic re-validation jobs; on contradiction, the new value wins and the old one is kept in an audit trail; set a confidence threshold for writes; never store model *inferences* as facts (only what the user explicitly said); and test memory with regression evals (see Q9).

---

### Q6. "What's the difference between memory and RAG?" `[P0]`

**Say this first:** "Both retrieve things into context, but they're different data. **RAG** is *shared, curated knowledge*, like policies, plan documents, and clinical criteria. Authors write it, it's versioned, and it's the same for everyone with access. **Memory** is *personal, system-written state* that comes from interactions. It's per user, mutable, and needs consent and correction. I keep them in separate stores with separate governance, even if both happen to use vector search."

**Your angle:** your current design has both. Azure AI Search for knowledge plus the memory store; see [03](03-RAG.md) and [04](04-Azure-AI-Search-and-Foundry.md).

---

### Q7. "How do you handle a 200-turn conversation?" `[P1]`

**Say this first:** "I don't send 200 turns. I keep the system prompt and the profile fixed, a **running summary** of older turns, the **last k turns verbatim**, and only the tool results that are still relevant. I trigger summarization on a token threshold, and I keep key facts, like the case ID and decisions made, in **structured state fields** instead of hoping the summary preserves them."

**If they dig deeper:**
- Summaries lose detail, so preserve entities, numbers, and commitments explicitly in state. Never split tool-call/result pairs when trimming.
- Offload big tool outputs.
- Keep the stable prefix stable so **prompt caching** works.
- The full transcript stays in the checkpointer or audit log for compliance; the *context* is what gets compressed.
- Very long tasks: use sub-agents with their own windows that return condensed results (the *isolate* strategy).

---

### Q8. "Hot-path vs background memory writes: which do you prefer?" `[P1]`

**Say this first:** "Background by default, because it adds no user-facing latency, the agent stays focused on the task, and I can consolidate properly. I use the hot path only when the user *explicitly* asks ('remember that I prefer text') and expects it to take effect immediately. Even then, the tool writes to a validated, scoped namespace."

---

### Q9. "How do you evaluate memory?" `[P1]`

**Say this first:** "I test it as its own component. **Extraction**: given a transcript, did it store the right facts and nothing it shouldn't (precision and recall against labelled transcripts)? **Retrieval**: given a new question, did the relevant memories come back? **End to end**: multi-turn and multi-session scenarios where turn 30 depends on something said in session 1. **Safety**: no cross-member leakage, no PHI beyond the policy, and injected instructions don't get saved."

**If they dig deeper:**
- Scripted multi-session test cases ("session 1: prefers Spanish → session 2: answer should be in Spanish").
- Contradiction cases ("moved from MA to NH" → old fact updated).
- Benchmarks like **LoCoMo** and **LongMemEval** exist, but domain scenarios matter more.
- Measure memory **token cost** and **latency** too.

**Your angle:** extend the eval discipline from [S1](13-Behavioral-Story-Bank.md#s1) (20-question set) to memory scenarios. See [07](07-Evaluation-and-Observability.md).

---

### Q10. "What is context engineering, and why do people say it's replacing prompt engineering?" `[P1]`

**Say this first:** "Prompt engineering is wording one instruction well. Context engineering is designing *everything* the model sees at each step: instructions, tools, retrieved knowledge, memories, history, and tool results, all within a token budget. In agents that's what decides quality, because most failures I see are context failures, like the wrong document, a stale memory, or too much noise, rather than bad wording. The four moves are write, select, compress, and isolate."

---

### Q11. "What are 'context rot' and 'lost in the middle', and how do they change your design?" `[P1]`

**Say this first:** "Accuracy drops as context grows, even far below the window limit, and models use information in the middle of a long context less reliably than information at the edges. So I treat the window as a scarce budget rather than a bucket. I retrieve fewer, better chunks, rerank, put critical instructions and evidence at the start or end, summarize history, and isolate sub-tasks in sub-agents. I verify with evals rather than assuming that a bigger window means better answers."

---

### Q12. "Where would you store agent memory on Azure, and why?" `[P1]`

| Option | Good for | Trade-offs |
|---|---|---|
| **Azure Database for PostgreSQL** (+ pgvector) | Checkpointer *and* Store in one transactional DB (`PostgresSaver` / `PostgresStore`); familiar ops | You manage scaling, vacuum, and pruning; vector search is fine at moderate scale |
| **Azure Cosmos DB** (NoSQL + vector search) | Partition per member (natural isolation), built-in TTL, global scale | RU cost modelling; LangGraph checkpointer support via partner/community packages |
| **Azure Managed Redis** | Hot, low-latency short-term state; TTL | Durability settings; memory cost; not a system of record |
| **Azure AI Search** | Rich hybrid search over large *knowledge* collections; security filters | Not transactional, has indexing lag; better for shared knowledge than per-user mutable memory |
| **Foundry Agent Service Memory (preview)** | Managed extraction and consolidation, item CRUD, TTL | Preview status; less control; confirm compliance scope before using with PHI |

**Say this first:** "For most teams I'd start with Postgres, because one transactional store covers both checkpoints and long-term memory, with pgvector for search. I'd move hot session state to Redis or memory to Cosmos only when scale or latency forces it. Azure AI Search stays for shared knowledge, not per-user memory."

`[fill in: what you chose in S5 and why]`

---

### Q13. "What are the privacy and HIPAA risks of agent memory, and how do you mitigate them?" `[P1]`

**Say this first:** "Memory turns a stateless model into a **PHI data store**, so it inherits every obligation of one. The risks are cross-member leakage, over-collection, stale or incorrect data being acted on, retention beyond policy, and poisoning through injected content. The mitigations are namespace isolation enforced from the auth token, minimum-necessary schemas, encryption and private networking under the BAA, TTLs and deletion paths, audit logs, member-visible and correctable memory, and evals specifically for leakage."

**If they dig deeper:** HIPAA gives rights of access and amendment, so a member's request to see or correct what the assistant remembers is a real requirement. Keep memories out of application logs. Keep de-identified episodic examples separate from identifiable profiles. See [08](08-Security-Responsible-AI-and-HIPAA.md).

---

### Q14. "Give examples of semantic, episodic, and procedural memory." `[P2]`

**Say this first:** "**Semantic** is facts: 'the member prefers Spanish'. **Episodic** is experiences: 'last time, this kind of billing question was resolved by checking the coordination-of-benefits record', often used as few-shot examples. **Procedural** is how to act: the agent's own instructions, for example a learned rule to check plan type before answering prior-auth questions. I update procedural memory only through human-reviewed prompt changes, never automatically, in a regulated setting."

---

### Q15. "Profile vs collection for long-term memory?" `[P2]`

**Say this first:** "A profile is one small JSON document per user that's always in context. It's easy to read and reason about, but it's error-prone to update as it grows. A collection is many small items you search. It has better recall and is easy to append to, but it's harder to de-duplicate, update, and present as a whole. I usually combine them: a tight profile for the stable preferences, plus a searchable collection of episodes."

---

### Q16. "Could the agent learn and improve its own instructions? How would you do it safely?" `[P2]`

**Say this first:** "Yes, through reflection, where an LLM reviews traces and feedback and proposes prompt changes. In healthcare I'd make that **offline and gated**: proposals become PRs, they run against the eval suite, a human approves them, and they ship like code. The agent never rewrites its own production instructions on the fly."

---

### Q17. "How do memory and multi-agent systems interact?" `[P2]`

**Say this first:** "Isolation is the point. Sub-agents get their own context windows, so the supervisor only sees condensed results. Shared memory is explicit: shared state keys or store namespaces, with clear ownership of which agent can write what. Otherwise agents overwrite each other's facts or leak context that one of them shouldn't see."

---

### Q18. "A junior wants to 'just put the whole history in the context, the window is huge.' How do you coach them?" `[P1]`

*This tests technical judgment and mentoring together.*

**Say this first:** "I wouldn't just say no. I'd have them **run the experiment**. We'd take a few long real conversations, compare full history against summary plus recent turns on our eval set, and look at accuracy, latency, and cost per turn. Context rot usually shows up in the numbers, and they learn the habit I actually care about: making design decisions with evals instead of intuition. Then we pair on implementing the summarization node."

**Your angle:** this is your coaching style in a nutshell. See [11](11-Mentoring-and-Coaching.md).

---

## Key terms

| Term | Meaning |
|---|---|
| Thread / `thread_id` | One conversation's checkpoint history |
| Namespace | Folder-like tuple that scopes long-term memories (e.g., per member) |
| Consolidation | Merging new memories with existing ones (add / update / delete) |
| Compaction | Summarizing or condensing context when it gets too long |
| Context rot | Quality degrading as the context gets longer |
| Provenance | Where and when a memory came from |

## References

- [LangChain: Memory concepts](https://docs.langchain.com/oss/python/concepts/memory). Short- vs long-term; semantic, episodic, procedural; hot path vs background; profile vs collection.
- [LangGraph: Add and manage memory](https://docs.langchain.com/oss/python/langgraph/add-memory). Trimming, `RemoveMessage`, summarization, Store usage, production backends.
- [LangGraph: Persistence](https://docs.langchain.com/oss/python/langgraph/persistence). How checkpointers and stores work.
- [LangMem SDK docs](https://langchain-ai.github.io/langmem/) and [launch post](https://blog.langchain.com/langmem-sdk-launch/). Memory extraction and consolidation tooling.
- [Microsoft Foundry: Memory in Foundry Agent Service (blog)](https://devblogs.microsoft.com/foundry/introducing-memory-in-foundry-agent-service/). Azure's managed memory (preview).
- [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents). Compaction, note-taking, sub-agents; "smallest set of high-signal tokens".
- [LangChain blog: Context engineering for agents](https://blog.langchain.com/context-engineering-for-agents/). The write / select / compress / isolate framework.
- [Chroma Research: Context Rot](https://research.trychroma.com/context-rot). Evidence that longer inputs degrade accuracy.
- [Lost in the Middle (Liu et al., 2023)](https://arxiv.org/abs/2307.03172). Position effects in long contexts.
- [CoALA: Cognitive Architectures for Language Agents](https://arxiv.org/abs/2309.02427). Origin of the semantic, episodic, procedural framing.
- [MemGPT (Packer et al., 2023)](https://arxiv.org/abs/2310.08560). OS-style memory paging for LLMs.
- [Azure Cosmos DB for AI agents](https://learn.microsoft.com/en-us/azure/cosmos-db/ai-agents). Azure's take on agent memory stores.
- [pgvector on Azure Database for PostgreSQL](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/how-to-use-pgvector). Vector search in Postgres.
- [HHS: HIPAA minimum necessary requirement](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html). Why you remember less.
- [HHS: Individuals' right of access under HIPAA](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/access/index.html). Members' rights over their data.
