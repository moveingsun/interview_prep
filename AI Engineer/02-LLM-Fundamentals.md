# 02 · LLM Fundamentals

[← Index](00-Index.md) · **Manager-round priority:** Medium · **Read time:** ~35 min

> **Why this matters for this role:** The JD asks you to "track new LLMs… and recommend adoption", own GenAI integrations, and weigh cost and complexity trade-offs. A hiring manager will check that you can explain the basics simply, which shows you can teach them to juniors, and that your model and cost choices rest on a clear mental model.

## Primer

```
TRAINING (done by the model vendor)                         INFERENCE (what you pay for per call)
───────────────────────────────────                         ─────────────────────────────────────
1. Pre-training                                              prompt text
   next-token prediction on trillions of tokens                  │  tokenizer
   → "base model": knows language + facts, not helpful           ▼
2. Instruction tuning (SFT)                                  [tokens] ──► transformer layers (attention + MLP)
   curated prompt → ideal response pairs                         │
   → follows instructions                                        ▼
3. Preference tuning (RLHF / DPO) + RL on verifiable tasks   probability distribution over next token
   → helpful, safe, good at reasoning                            │  sampling (temperature / top-p)
                                                                 ▼
                                                             one token → append → repeat until stop
```

Remember three things:

1. An LLM is a **next-token predictor**. Everything else is built on top of that: chat, tools, reasoning, and agents.
2. The model only "knows" two things: **what is in its weights**, which is frozen at the training cutoff, and **what is in the context window right now**. RAG, memory, and tools exist to put the right things into the context.
3. You pay for, and wait on, **tokens**: input tokens plus output tokens. Output tokens are slower and usually cost more.

## Questions & answers

### Q1. Explain how a large language model works to a non-technical stakeholder.  `[P0]`
**Say this first (~30 sec):** "It's an autocomplete trained on a huge share of the internet and books. Given some text, it predicts the most likely next word, adds it, and repeats. Training on that much text teaches it grammar, facts, and patterns of reasoning. A second phase teaches it to follow instructions and be helpful. It has no database of facts and doesn't look anything up unless we give it a tool. So if we need it to answer from *our* benefits documents, we have to hand it those documents at question time. That's what RAG does."

**If they dig deeper:**
- Text is split into **tokens**: word pieces, about 3/4 of an English word each. The model maps each token to a vector, and stacked **transformer** layers let every token "pay attention" to the others to build up meaning in context.
- The output at each step is a **probability distribution** over the vocabulary. Sampling settings such as temperature decide how adventurous the choice is.
- The weights are frozen at a **training cutoff**. The model doesn't learn from your conversation unless you build memory around it.

**Your angle:** You explain this to business users regularly: traders using Load Deal AI ([S1](13-Behavioral-Story-Bank.md#s1)) and cost analysts using Data Intelligence ([S4](13-Behavioral-Story-Bank.md#s4)). Close with the business consequence: "That's why we ground it in our data and measure it with an eval set."

**Likely follow-ups:** "So why does it make things up?" (Q2) · "Does it learn from what our members type?" (No, not by default. With Azure OpenAI in Foundry, prompts and completions are not used to train the models. Long-term memory is something *we* build; see [06](06-Memory-and-Context-Engineering.md).)

---

### Q2. Why do LLMs hallucinate, and how do you reduce it in production?  `[P0]`
**Say this first (~30 sec):** "The model is trained to produce *plausible* text, not *true* text. Training and benchmarks have historically rewarded guessing over saying 'I don't know', so when it lacks the facts it fills the gap fluently. You can't eliminate that, but you can engineer around it. Ground answers in retrieved sources and require citations. Verify those citations. Let the model abstain. Push calculations to tools instead of letting it do math. Measure hallucination rate with an eval set. In healthcare, anything high-stakes goes through a human."

**If they dig deeper:**
- **Causes:** gaps in parametric knowledge, a stale training cutoff, ambiguous prompts, retrieved context that is wrong or irrelevant, long noisy contexts, and pressure to always answer. The OpenAI paper *Why Language Models Hallucinate* (2025) argues that eval incentives reward confident guessing.
- **Mitigations, layered:**
  1. **Grounding:** RAG with good retrieval. Bad retrieval leads to confident wrong answers ([03](03-RAG.md)).
  2. **Instructions:** "Answer only from the provided sources. If the answer isn't there, say so."
  3. **Citations plus verification:** check that every cited passage exists and actually supports the claim, either programmatically or with an LLM judge.
  4. **Tools for facts and numbers:** text-to-SQL or an API call instead of the model recalling numbers.
  5. **Structured output:** constrain the answer to fields and enums where possible.
  6. **Lower temperature** for factual tasks.
  7. **Groundedness detection:** Azure AI Content Safety has a groundedness check.
  8. **Human-in-the-loop** for consequential actions such as coverage, clinical, or payment decisions.
  9. **Evals:** track a faithfulness/groundedness metric over time ([07](07-Evaluation-and-Observability.md)).

**Your angle:** Load Deal AI's LangGraph agent had **citation checks**, and numeric answers came from a Cortex semantic view, not model memory ([S1](13-Behavioral-Story-Bank.md#s1), [S4](13-Behavioral-Story-Bank.md#s4)). The Data Validation LLM judge **never writes without confirmation** ([S2](13-Behavioral-Story-Bank.md#s2)). That's the "human-in-the-loop for consequential actions" principle in practice.

**Likely follow-ups:** "How do you *measure* hallucination?" (A golden set plus a faithfulness metric: claims supported by context ÷ total claims, scored by an LLM judge calibrated against human labels.) · "What if retrieval returns a document that contradicts the question's intent?"

---

### Q3. When would you use prompting vs RAG vs fine-tuning?  `[P0]`
**Say this first (~30 sec):** "I go in that order. Prompting first, because it's cheapest and fastest to iterate. RAG when the model needs knowledge it doesn't have, especially knowledge that changes or must be cited or permission-controlled, like plan documents and policies. Fine-tuning is for *behavior*, not knowledge: a consistent format or style, a narrow high-volume task where I want a smaller, cheaper model, or when prompting has plateaued on my eval set. They combine. A fine-tuned model can still use RAG."

| Need | Prompting | RAG | Fine-tuning |
|---|---|---|---|
| Knowledge that changes (benefits, policies, formularies) | ✗ only what fits in the prompt | **✓ best**: update the index, not the model | ✗ goes stale, expensive to refresh |
| Citations / auditability | ✗ | **✓** | ✗ knowledge is baked in, can't cite |
| Per-user access control (member A must not see member B) | n/a | **✓** security trimming at retrieval | ✗ can't permission what's in weights |
| Consistent output format, tone, jargon | ✓ often enough | – | **✓** when prompting isn't reliable |
| Narrow high-volume task on a cheaper/faster model | – | – | **✓** (distill to a small model) |
| Time to first version | hours | days–weeks | weeks, plus labeled data |
| Data needed | a few examples | the documents | hundreds–thousands of high-quality examples |
| PHI risk | low (transient) | controlled (index ACLs) | **higher**: training data can be memorized |

**If they dig deeper:**
- People often fine-tune to "teach the model our docs". That's usually a mistake: it hallucinates a blend of the docs and can't cite them.
- Fine-tuning costs don't stop at training. On Azure there is hosting cost for the fine-tuned deployment, plus retraining when the base model is retired.
- Long context (stuffing everything into the prompt) is a fourth option. It's fine for small, stable corpora, but cost, latency, and context rot (Q5) make RAG better at scale.

**Your angle:** Your current Foundry service uses RAG on Azure AI Search plus memory, not fine-tuning ([S5](13-Behavioral-Story-Bank.md#s5)). Explain why: `[fill in: content changes often / need citations / access control]`. Load Deal AI used a *curated knowledge base* and a semantic view instead of training anything ([S1](13-Behavioral-Story-Bank.md#s1)).

**Likely follow-ups:** "Have you fine-tuned a model?" Be honest. If not: "Not in production. I've evaluated it as an option, and here's when I'd reach for it…" (see [10](10-ML-and-MLOps-Fundamentals.md) Q12).

---

### Q4. How do you choose which model to use for a use case?  `[P0]`
**Say this first (~30 sec):** "I start from an eval set, not a leaderboard. First I prove the task is solvable with the strongest model available. Then I step down to cheaper, faster models until quality drops below the bar. Besides quality I weigh latency, cost *per completed task*, context length, tool-calling and structured-output reliability, and for us compliance: is it covered by our BAA, and in which region does the data stay? Then I keep it swappable behind an interface so a model change is a config change plus an eval run."

**If they dig deeper:**
- **Frontier vs small:** Frontier models handle reasoning, ambiguous instructions, and multi-step tool use. Small models (mini/nano tier, Phi, small open-weight models) handle classification, extraction, routing, and summarization at a fraction of the cost and latency.
- **Reasoning models:** see Q15.
- **Open-weight vs hosted API:** Open-weight models (Llama, Mistral, Qwen, gpt-oss, and others) give you control, on-prem or VNet deployment, fine-tuning freedom, and possibly lower cost at very high volume. In exchange you own GPU serving, scaling, patching, and safety layers. Hosted APIs (Azure OpenAI in Foundry and other catalog models) are faster to production and come with enterprise compliance.
- **Data residency and compliance:** PHI must go only to services covered by a **BAA**. Prefer regional over global deployments if data-residency policy requires it. Check content-logging and abuse-monitoring settings.
- **Operational factors:** quotas and rate limits, provisioned vs pay-as-you-go throughput, and the model **retirement schedule**, since Azure retires model versions on a published timeline.
- **Routing:** often the answer is "several models". A cheap model classifies intent and only hard cases go to the expensive model.

**Your angle:** You tracked **per-turn cost** in Load Deal AI ([S1](13-Behavioral-Story-Bank.md#s1)). Say what you'd change knowing those numbers. In Foundry today: `[fill in: which models you deployed and why]`.

**Likely follow-ups:** "A new model came out yesterday. Do we switch?" (Q17) · "How do you avoid vendor lock-in?" (Use an abstraction layer such as LangChain chat models, the Foundry model catalog, or your own interface, keep prompts in version control, and keep the eval harness model-agnostic.)

---

### Q5. What are tokens and context windows, and why doesn't a 1M-token context window make RAG obsolete?  `[P1]`
**Say this first (~30 sec):** "A token is a chunk of text, roughly 3/4 of a word. The context window is how many tokens the model can see at once: instructions, history, retrieved documents, and its own output. Big windows help, but filling them is expensive and slow. Models also use long contexts unevenly. They're best at the start and end and weaker in the middle, and quality degrades as input grows, which is called 'context rot'. So I still retrieve a small set of the *most relevant* chunks. Less, better context usually beats more context."

**If they dig deeper:**
- **Lost in the Middle** (Liu et al., 2023): accuracy is highest when the relevant fact sits at the beginning or end of the context and drops in the middle.
- **Context rot** (Chroma research, 2025): performance degrades with input length even on simple tasks, and distractors make it worse.
- Attention cost grows with sequence length, which affects latency, and you pay for every input token on every call.
- Practical rules: put stable instructions first (this also helps prompt caching), put the question near the end, rerank to put the best chunks where the model reads them, and summarize or trim conversation history ([06](06-Memory-and-Context-Engineering.md)).

**Your angle:** Your memory service has to *decide* what goes into context: recent turns, summarized older turns, and retrieved long-term facts. That is context engineering in practice ([S5](13-Behavioral-Story-Bank.md#s5)).

**Likely follow-ups:** "How do you manage a long conversation?" (Use sliding window plus summarization, and move durable facts into long-term memory.)

---

### Q6. What's the difference between pre-training, instruction tuning, and RLHF/DPO?  `[P1]`
**Say this first (~30 sec):** "Pre-training is self-supervised next-token prediction on a massive corpus. That gives you a base model that knows language and facts but just continues text. Instruction tuning, or supervised fine-tuning, trains it on prompt-to-ideal-response pairs so it follows instructions. Preference tuning then aligns it with what humans prefer. RLHF does this by training a reward model on human rankings and optimizing against it with reinforcement learning. DPO skips the reward model and learns directly from 'chosen vs rejected' answer pairs."

**If they dig deeper:**
- RLHF (InstructGPT, 2022): collect human rankings → train a reward model → optimize the policy with PPO plus a penalty for drifting from the SFT model.
- DPO (2023): simpler and more stable. It is a classification-style loss on preference pairs, with no separate reward model or RL loop.
- Reasoning models add **reinforcement learning on verifiable rewards**: math answers that can be checked, code that passes tests. That teaches long chains of thought.
- Why it matters to you: as a consumer of hosted models you mostly *use* these stages. But SFT and DPO are also what you'd run yourself if you fine-tune ([10](10-ML-and-MLOps-Fundamentals.md) Q12).

**Likely follow-ups:** "Which would you use to fix the tone of our assistant?" (Prompt first. If that fails, SFT on good examples. DPO if you have pairs of good and bad responses, for example from user thumbs-up/down.)

---

### Q7. What does "attention" do in a transformer?  `[P1]`
**Say this first (~30 sec):** "Attention lets each token look at every other token in the context and decide how much each one matters to its meaning. In 'The claim was denied because *it* lacked a referral', attention helps 'it' connect to 'claim'. Many attention heads in many layers build up a rich, context-aware representation. That's what lets transformers handle long-range dependencies and train in parallel, unlike older recurrent networks."

**If they dig deeper:**
- Each token produces a **query**, a **key**, and a **value** vector. Attention weights = softmax(Q·Kᵀ / √d). The output is the weighted sum of values.
- **Multi-head:** several attention patterns run in parallel, for example syntax, coreference, and position.
- GPT-style models are **decoder-only** with *causal* masking: a token can only attend to earlier tokens.
- Cost scales roughly quadratically with sequence length. The **KV cache** stores past keys and values so generation doesn't recompute them, and prompt caching reuses that cache across requests (Q13).

**Likely follow-ups:** "Encoder vs decoder?" (Encoders like BERT see the whole input and suit embeddings and classification. Decoders generate text.)

---

### Q8. What do temperature and top-p do? Can you make an LLM deterministic?  `[P1]`
**Say this first (~30 sec):** "Both control how the next token is sampled. Temperature sharpens or flattens the probability distribution: low means focused and repeatable, high means more varied. Top-p restricts sampling to the smallest set of tokens covering p of the probability mass. For extraction, classification, and grounded Q&A I use low temperature. For brainstorming, higher. Temperature 0 is *not* a determinism guarantee, though. GPU batching and floating-point effects can still change outputs, so I design and evaluate for variance instead of assuming it away."

**If they dig deeper:**
- Usually tune temperature *or* top-p, not both.
- Sources of nondeterminism: batch-dependent kernels, floating-point non-associativity, mixture-of-experts routing, and silent model updates if you don't pin versions. See Thinking Machines' *Defeating Nondeterminism in LLM Inference* (2025).
- Many **reasoning models ignore or restrict** sampling parameters, so check the model docs.
- Testing implication: run evals several times or with a reasonable sample size, and assert on *properties* (schema-valid, contains citation, correct label), not exact strings.

**Likely follow-ups:** "How do you write tests for something nondeterministic?" (See [07](07-Evaluation-and-Observability.md).)

---

### Q9. What are embeddings and how are they used?  `[P1]`
**Say this first (~30 sec):** "An embedding is a vector, a list of numbers, that represents the *meaning* of a piece of text. Texts with similar meaning land close together, so 'Is physical therapy covered?' sits near a chunk about 'rehabilitative services benefits' even with no shared words. We compare them with cosine similarity. They power semantic search in RAG, plus clustering, deduplication, classification, and semantic caching."

**If they dig deeper:**
- **Cosine similarity** = the angle between vectors: dot product of normalized vectors, ranging from −1 to 1. Most embedding models return normalized vectors, so dot product equals cosine.
- **Choosing a model:** start from the MTEB leaderboard, then test on *your* queries and documents, since domain jargon such as CPT codes and plan names matters. Trade-offs are dimension size (storage, latency), max input tokens, multilingual support, and hosting and compliance.
- **Matryoshka-style models** (e.g., OpenAI `text-embedding-3-*`) let you truncate dimensions to save storage at a small quality cost.
- **Changing the embedding model means re-embedding everything.** Version your index.
- **Bi-encoder vs cross-encoder:** embeddings (bi-encoder) are fast for recall across millions of documents. A cross-encoder **reranker** reads the query and document together for precision on the top ~50 ([03](03-RAG.md)).
- Embeddings miss exact identifiers such as member IDs and codes, which is why **hybrid search** (keyword plus vector) usually wins.

**Your angle:** Azure AI Search vector and hybrid fields in your current project: `[fill in: embedding model + dimensions]` ([S5](13-Behavioral-Story-Bank.md#s5)).

**Likely follow-ups:** "How would you know your embedding model is the bottleneck?" (Measure retrieval recall@k on a labeled query set, and compare models and hybrid vs vector-only.)

---

### Q10. What prompt-engineering techniques do you actually rely on?  `[P1]`
**Say this first (~30 sec):** "Clarity beats tricks. A system prompt with the role, the task, the *why*, and the rules. Inputs clearly delimited, for example in XML tags. An explicit output format. Two or three diverse few-shot examples including an edge case. An explicit instruction for what to do when unsure. For complex tasks I break the work into a chain of smaller prompts rather than one mega-prompt. And I treat prompts as code: version-controlled, reviewed, and nobody changes one without running the eval set."

**If they dig deeper:**
- **Few-shot:** examples steer format strongly. Make them diverse, or the model copies their quirks.
- **Chain-of-thought:** asking the model to reason before answering helps multi-step problems. With reasoning models it's built in, so don't over-prescribe the steps.
- **Long documents:** put the docs first and the question last. Ask it to extract relevant quotes before answering.
- **Decomposition / prompt chaining:** each step is simpler, testable, and debuggable. These are the "workflows" in Anthropic's *Building Effective Agents*.
- **Negative instructions** ("don't do X") work worse than positive ones ("do Y").
- **Team practice:** keep a prompt template library and require eval evidence in code review for prompt changes. This teaches juniors that prompts are engineering artifacts ([11](11-Mentoring-and-Coaching.md)).

**Your angle:** Your CLAUDE.md and the domain knowledge base (10 docs, ~100 sections) are context engineering for a coding agent. You've seen first-hand how much good context changes output quality ([S6](13-Behavioral-Story-Bank.md#s6)).

**Likely follow-ups:** "How do you stop prompt changes from causing regressions?" (Run the eval set in CI. See [07](07-Evaluation-and-Observability.md).)

---

### Q11. How do you get reliable structured output (JSON) from an LLM?  `[P1]`
**Say this first (~30 sec):** "Use the provider's schema-constrained structured-output mode, which Azure OpenAI and most major APIs now support, rather than just asking for JSON. Define the schema with Pydantic so the same model validates the response. Keep schemas simple with enums for categorical fields. Then validate business rules after parsing. A valid schema doesn't mean correct values. On failure, retry once with the validation error, then fall back gracefully."

**If they dig deeper:**
- "JSON mode" only guarantees valid JSON. **Strict schema** mode guarantees it matches *your* schema through constrained decoding.
- Field order matters: put a short `reasoning` field *before* the `decision` field if you want the model to think first.
- Make "unknown" a valid enum value so the model isn't forced to guess. This is also a hallucination control.
- Schema-constrained output is also how tool-call arguments are generated (Q12).

**Your angle:** Load Deal AI rendered SQL, tables, and charts in the chat UI ([S1](13-Behavioral-Story-Bank.md#s1)). That needs a structured response contract between the agent and the frontend.

**Likely follow-ups:** "What if the schema is huge?" (Split into steps, or use several smaller calls.)

---

### Q12. How does function/tool calling actually work under the hood?  `[P1]`
**Say this first (~30 sec):** "The model never executes anything. You send it tool definitions: a name, a description, and a JSON schema for the parameters. When it decides a tool is needed, it returns a structured 'tool call' with arguments. *Your code* validates and executes it and sends the result back as a tool message. The model then continues or calls another tool, in a loop until it produces a final answer. That loop is the core of every agent, including LangGraph's ReAct pattern."

**If they dig deeper:**
- **Tool descriptions are prompts.** The model picks tools based on them, so write them for the model: when to use the tool, when *not* to, and examples of arguments.
- `tool_choice` can force a specific tool, require any tool, or forbid tools. **Parallel tool calls** let independent lookups run at once.
- **Security:** model-generated arguments are *untrusted input*. Validate them, and execute with the **end user's permissions**, not a superuser service account. Keep tools least-privilege and require confirmation for writes ([08](08-Security-Responsible-AI-and-HIPAA.md), OWASP "Excessive Agency").
- Keep the tool count manageable. Too many similar tools confuse the model, so group them or route first.
- **MCP** standardizes how tools are exposed to models across apps ([05](05-Agents-and-LangGraph.md)).

**Your angle:** Entitlements are your specialty: shared entitlements service, fail-closed checks ([S9](13-Behavioral-Story-Bank.md#s9)), and UI-element permissions in Watt ([S3](13-Behavioral-Story-Bank.md#s3)). "Tools run with the caller's entitlements, and fail closed" is a strong senior answer.

**Likely follow-ups:** "What happens when a tool fails or times out?" (Return a structured error to the model so it can retry or explain, cap retries and loop iterations, and make tools idempotent.)

---

### Q13. What levers do you have to reduce LLM cost and latency?  `[P0]`
**Say this first (~30 sec):** "First measure cost and latency *per completed task*, not per token. Then the main levers: (1) right-size the model, routing easy requests to a small model; (2) send less context, meaning fewer, better chunks and summarized history; (3) prompt caching, with the stable prefix first; (4) cap output tokens and ask for concise structured output; (5) batch API for anything that isn't interactive; (6) stream responses so perceived latency drops; (7) run independent calls in parallel; and (8) provisioned throughput when volume is steady and latency SLOs matter."

**If they dig deeper:**
- **Prompt caching:** providers reuse the computed prefix of repeated prompts. Azure OpenAI caches automatically for long-enough prompts (≥1,024 tokens) and discounts cached input tokens. Anthropic uses explicit cache breakpoints, and cache reads cost a fraction of normal input. Design for it with system prompt, tool definitions, and static docs first, and the variable user turn last.
- **Batch APIs** (Azure OpenAI Global Batch and others) offer roughly 50% lower price for async jobs with a 24-hour target turnaround. Good for nightly document processing and eval runs.
- **Semantic caching:** return a cached answer for near-duplicate questions. Be careful with personalized or PHI answers: cache key scoping and invalidation are where bugs hide.
- **Provisioned throughput (PTU)** vs pay-as-you-go: PTU gives predictable latency and reserved capacity at steady high volume. Pay-as-you-go suits spiky or early-stage workloads.
- **Latency anatomy:** time-to-first-token (driven by input size and the queue) plus output tokens ÷ tokens per second. Output length usually dominates, so make outputs shorter.
- Agents multiply cost: each loop iteration re-sends the growing context. Cap iterations and compress tool results.

**Your angle:** You have strong cost evidence. **Per-turn cost tracking** in Load Deal AI ([S1](13-Behavioral-Story-Bank.md#s1)), the **10× Snowflake cost spike** you diagnosed and fixed ([S7](13-Behavioral-Story-Bank.md#s7)), and query time 85.6s → 8.8s ([S4](13-Behavioral-Story-Bank.md#s4)). Say: "I treat token spend like warehouse spend. Instrument it per request, then attack the biggest line item."

**Likely follow-ups:** "Our GenAI bill doubled last month. Walk me through how you'd investigate." (Break it down by app, model, and feature; tokens in vs out; cache hit rate; agent loop counts; retries; then fix the top contributor. Same playbook as S7.)

---

### Q14. What is LoRA / parameter-efficient fine-tuning?  `[P2]`
**Say this first (~30 sec):** "Instead of updating all of a model's billions of weights, LoRA freezes them and trains small low-rank 'adapter' matrices added to some layers, often well under 1% of the parameters. That makes fine-tuning far cheaper in GPU memory and storage, and you can keep many small adapters for one base model. QLoRA does the same on a 4-bit quantized base model, so even large models can be tuned on a single GPU."

**If they dig deeper:** Rank `r` controls adapter capacity. At serving time adapters can be merged into the weights or hot-swapped per tenant or task. Hugging Face PEFT is the standard library. Managed fine-tuning in Azure or other platforms hides this behind an API.

**Likely follow-ups:** "When is fine-tuning worth it at all?" (See Q3 and [10](10-ML-and-MLOps-Fundamentals.md) Q12.)

---

### Q15. When would you use a reasoning model vs a standard model?  `[P1]`
**Say this first (~30 sec):** "Reasoning models spend extra 'thinking' tokens before answering, also called test-time compute. They're clearly better at multi-step problems: complex planning, tricky tool orchestration, math, code, reconciling conflicting sources. They cost more and are slower, and that's wasted on extraction, classification, or a straightforward grounded answer. I use them where my eval shows a real quality gain, often only as the planner or for the hard-case branch of a router, and I tune the reasoning-effort setting."

**If they dig deeper:** Many reasoning models expose an effort or thinking-budget parameter and restrict temperature. Hidden reasoning tokens are billed as output tokens. Prompting differs: give the goal and constraints, not step-by-step instructions.

**Your angle:** Reconciling the PnL against the traders' workbook ([S8](13-Behavioral-Story-Bank.md#s8)) is the kind of multi-source, rule-heavy reasoning where these models earn their cost.

**Likely follow-ups:** "How do you control the latency hit?" (Stream a status indicator, route only hard cases to the reasoning model, and cache plans.)

---

### Q16. What are quantization and distillation, and when do they matter?  `[P2]`
**Say this first (~30 sec):** "Quantization stores weights at lower precision, say 16-bit down to 8- or 4-bit. Memory and cost fall, speed rises, and quality drops a little. Distillation trains a small 'student' model to imitate a big 'teacher' on your task, so you get most of the quality at a fraction of the cost. Both matter most when you self-host open-weight models. With hosted APIs you get the benefit by picking the smaller SKU, which is often distilled already."

**If they dig deeper:** Distillation is a practical enterprise pattern. Use the frontier model to label data, then train a small classifier or fine-tune a small LLM for a high-volume narrow task such as routing or intent classification.

**Likely follow-ups:** "Would you self-host for PHI reasons?" (Usually not needed. HIPAA-eligible hosted services under a BAA, with private networking, satisfy most requirements. Self-host only for specific control or cost needs at scale.)

---

### Q17. A new model version comes out. How do you decide whether to upgrade, and how do you roll it out?  `[P1]`
**Say this first (~30 sec):** "Pin model versions in production so nothing changes under us. When a new model appears, or the current one approaches retirement, run our eval set against it and compare quality, cost per task, and latency. If it wins, roll it out like any risky change: behind a flag, shadow or canary on a slice of traffic, watch the dashboards, then promote. Prompts sometimes need retuning, so that's part of the evaluation, not a surprise afterward."

**If they dig deeper:**
- Azure publishes **model deprecation and retirement dates**, so put them on the team calendar and avoid forced emergency migrations.
- Keep an internal "model scorecard" per use case: quality, cost, latency, safety findings.
- This is part of the JD's "evaluate new LLMs and recommend adoption", so make it a lightweight, repeatable process rather than a vibe check.

**Your angle:** The 20-question eval set from Load Deal AI ([S1](13-Behavioral-Story-Bank.md#s1)) is exactly the asset that makes upgrades safe. Mention you'd grow it from real user traffic.

**Likely follow-ups:** "Who decides, you or product?" (Engineering brings the data. Product owns the trade-off if quality and cost conflict. See [12](12-Team-Leadership-and-Delivery.md).)

## Key terms

| Term | One-liner |
|---|---|
| Token | Unit of text the model reads/writes (~3/4 of an English word) |
| Context window | Max tokens (input + output) the model can attend to in one call |
| Temperature / top-p | Sampling controls: randomness / probability-mass cutoff |
| Embedding | Vector capturing meaning; compared with cosine similarity |
| SFT | Supervised fine-tuning on prompt → ideal response pairs |
| RLHF / DPO | Preference tuning with a reward model + RL / directly from preference pairs |
| LoRA / QLoRA | Parameter-efficient fine-tuning via small adapters / on a 4-bit base |
| KV cache / prompt caching | Reuse computed attention states within / across requests |
| Reasoning model | Spends hidden "thinking" tokens before answering |
| PTU | Provisioned throughput units: reserved model capacity on Azure |
| BAA | Business Associate Agreement: required before sending PHI to a vendor |

## References
- [Attention Is All You Need (Vaswani et al., 2017)](https://arxiv.org/abs/1706.03762): the original transformer paper; skim the figures.
- [The Illustrated Transformer (Jay Alammar)](https://jalammar.github.io/illustrated-transformer/): the best visual explanation of attention.
- [Intro to Large Language Models (Andrej Karpathy, 1-hr talk)](https://www.youtube.com/watch?v=zjkBMFhNj_g): gives you the plain-English vocabulary for Q1.
- [Training language models to follow instructions with human feedback (InstructGPT)](https://arxiv.org/abs/2203.02155): RLHF, the source.
- [Direct Preference Optimization (Rafailov et al., 2023)](https://arxiv.org/abs/2305.18290): DPO, the source.
- [Why Language Models Hallucinate (Kalai et al., 2025)](https://arxiv.org/abs/2509.04664): why models guess instead of abstaining.
- [Lost in the Middle (Liu et al., 2023)](https://arxiv.org/abs/2307.03172): position effects in long contexts.
- [Context Rot (Chroma Research)](https://research.trychroma.com/context-rot): quality degrades with input length.
- [Defeating Nondeterminism in LLM Inference (Thinking Machines)](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/): why temperature 0 isn't deterministic.
- [Chain-of-Thought Prompting (Wei et al., 2022)](https://arxiv.org/abs/2201.11903): the CoT paper.
- [Prompt engineering overview (Anthropic docs)](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview): practical, vendor-neutral-ish techniques.
- [Prompt engineering techniques (Azure OpenAI in Foundry)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/prompt-engineering): Microsoft's version; matches your stack.
- [Structured outputs (Azure OpenAI)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/structured-outputs): schema-constrained JSON on your platform.
- [Function calling (Azure OpenAI)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/function-calling): the tool-call loop.
- [Prompt caching (Azure OpenAI)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/prompt-caching): requirements and how discounts apply.
- [Prompt caching (Anthropic docs)](https://platform.claude.com/docs/en/build-with-claude/prompt-caching): explicit cache breakpoints; good for explaining the concept.
- [Global Batch (Azure OpenAI)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/batch): async jobs at lower cost.
- [Provisioned throughput (Azure OpenAI)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/provisioned-throughput): PTU vs pay-as-you-go.
- [Reasoning models (Azure OpenAI)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/reasoning): reasoning effort and parameter differences.
- [Model deprecations and retirements (Azure OpenAI)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/model-retirements): the upgrade calendar for Q17.
- [Groundedness detection (Azure AI Content Safety)](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/groundedness): a managed hallucination check.
- [Embeddings (Google ML Crash Course)](https://developers.google.com/machine-learning/crash-course/embeddings): a clear embeddings primer.
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard): where to start when picking an embedding model.
- [LoRA (Hu et al., 2021)](https://arxiv.org/abs/2106.09685) · [QLoRA (Dettmers et al., 2023)](https://arxiv.org/abs/2305.14314): the PEFT sources.
- [Hugging Face PEFT docs](https://huggingface.co/docs/peft/index): the practical LoRA library.
- [Quantization overview (Hugging Face Transformers)](https://huggingface.co/docs/transformers/main/en/quantization/overview): the quantization options in one page.
- [Distilling the Knowledge in a Neural Network (Hinton et al., 2015)](https://arxiv.org/abs/1503.02531): the distillation source.
- [Patterns for Building LLM-based Systems & Products (Eugene Yan)](https://eugeneyan.com/writing/llm-patterns/): the practitioner's map of evals, RAG, caching, guardrails.
- [Building Effective Agents (Anthropic)](https://www.anthropic.com/engineering/building-effective-agents): prompt chaining and routing workflows (Q10, Q13).
