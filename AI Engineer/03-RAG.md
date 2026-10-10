# 03 · Retrieval-Augmented Generation (RAG)

[← Index](00-Index.md) · **Manager-round priority:** High · **Read time:** ~35 min

> **Why this matters for this role:** The JD names "RAG architectures" as something you'll *own the design of*. A health plan's knowledge (benefit documents, medical policies, prior-auth lists, provider manuals, call-center scripts) is a textbook RAG corpus. Your current project ([S5](13-Behavioral-Story-Bank.md#s5)) and Load Deal AI ([S1](13-Behavioral-Story-Bank.md#s1)) are both RAG systems, so expect "walk me through how you built it" follow-ups.

---

## Primer

**Mental model:** RAG = *a search engine + an LLM that writes the answer from what the search engine found.* Most bad RAG answers are **search failures**, not model failures.

```
INGESTION  (offline / incremental, runs on a schedule or on change events)
┌──────────┐   ┌───────────────┐   ┌────────────────────┐   ┌──────────────┐   ┌─────────┐   ┌────────────────────────────┐
│ Sources  │──►│ Parse / OCR   │──►│ Clean + enrich     │──►│ Chunk        │──►│ Embed   │──►│ Index                      │
│ PDFs,    │   │ layout-aware, │   │ dedupe, metadata:  │   │ structure-   │   │ (embed- │   │ vector + keyword (BM25)    │
│ SharePt, │   │ tables → md   │   │ plan_id, effective │   │ aware, with  │   │ ding    │   │ + filterable metadata/ACLs │
│ policies │   │               │   │ date, ACL groups   │   │ overlap      │   │ model)  │   │ (e.g., Azure AI Search)    │
└──────────┘   └───────────────┘   └────────────────────┘   └──────────────┘   └─────────┘   └────────────────────────────┘

QUERY  (online, every user turn)
 User question
   │
   ▼
 Rewrite / route ──► Hybrid retrieve (BM25 + vector) ──► Fuse (RRF) ──► Rerank ──► Pack context ──► LLM answers ──► Groundedness / ──► Answer
 (standalone query,   with security + metadata                         (cross-     (top 5–10,      with citations   safety checks      + citations
  intent, sub-qs)     filters applied IN the search                     encoder)    token budget)
   ▲                                                                                                                       │
   └────────────────────────────── traces, eval metrics, user feedback ◄───────────────────────────────────────────────────┘
```

**Running healthcare example used below:** a member (or a call-center rep) asks *"Is an MRI of my knee covered under my plan, and do I need prior authorization?"* The corpus is plan benefit documents (Evidence of Coverage, Summary of Benefits), medical policies, and the prior-auth code list. The right answer depends on **which plan** the member has and **which policy version** is in effect.

---

## Questions & answers

### Q1. What is RAG, and why use it instead of fine-tuning or just a bigger context window?  `[P0]`
**Say this first (~30 sec):** RAG retrieves relevant passages from our own data at question time and gives them to the LLM as context, so the model answers from *our* sources instead of its training memory. I reach for it when the knowledge is proprietary, changes often, or needs citations and access control. Fine-tuning teaches *behavior and format*, not fresh facts. A huge context window works for a few documents, but it's expensive per call and has no per-user permissions.

**If they dig deeper:**
- **RAG vs fine-tuning:** RAG is for *knowledge* (updatable by re-indexing, citable, permission-aware). Fine-tuning is for *skills/style* (output format, domain tone, classification) and is a poor way to add facts: it's hard to update, can't cite, and can still hallucinate.
- **They combine:** fine-tune (or prompt) for format and refusal behavior, and use RAG for facts.
- **Why RAG is the default in regulated industries:** auditability (each answer traces to a source document and version), freshness (a policy changes, you re-index that night), and security (filter documents by the user's entitlements before the model ever sees them).
- Original paper: Lewis et al., 2020 (Facebook AI). The industry pattern has moved far beyond it (hybrid search, reranking, agentic retrieval).

**Your angle:** In Load Deal AI ([S1](13-Behavioral-Story-Bank.md#s1)) you combined a curated knowledge base for definitions/business rules with a semantic layer for numbers. That's a "RAG plus the right tool for structured data" design, which is exactly the senior answer.
**Likely follow-ups:** "When would you fine-tune?" (see [02 · LLM Fundamentals](02-LLM-Fundamentals.md)) · "Isn't long context making RAG obsolete?" (Q15)

---

### Q2. Explain RAG to a non-technical business stakeholder.  `[P0]`
**Say this first (~30 sec):** "It's an open-book exam. Instead of asking the AI to remember everything, we let it look up the answer in *our* approved documents first, then write a reply and show which pages it used. If the answer isn't in the book, it should say so rather than guess."

**If they dig deeper:**
- What the stakeholder actually cares about: **accuracy** (we measure it against a test set before launch), **trust** (every answer has a source link), **control** (we decide which documents are in the "book" and who can open which pages), and **freshness** (update the document, the answer updates).
- The limit to set expectations on: it's only as good as the documents. If two policies contradict each other, the bot will surface that conflict, not resolve it.

**Your angle:** This shows the communication skill the JD asks for ("technical and non-technical audiences"). Mention that you worked directly with a PM and traders on Load Deal ([S8](13-Behavioral-Story-Bank.md#s8)).
**Likely follow-ups:** "How would you report quality to leadership?" (see [07 · Evaluation](07-Evaluation-and-Observability.md))

---

### Q3. Walk me through how you'd design a RAG system end to end, e.g., a benefits Q&A assistant.  `[P0]`
**Say this first (~30 sec):** I start with requirements, not tools: who the users are (members vs. call-center reps), what accuracy and latency bar we need, which sources are authoritative, and what permissions apply. Then I design two pipelines. **Ingestion:** layout-aware parsing, structure-aware chunking with metadata like plan ID and effective date, embeddings, and a hybrid index. **Query:** rewrite the question, run hybrid retrieval filtered by the user's plan and permissions, rerank, and generate an answer with citations, plus a groundedness check. Evaluation and tracing are designed in from day one, not bolted on.

**If they dig deeper:**
1. **Clarify:** Users? Channels? Is it advisory or decision-making? (Coverage *determinations* must stay with humans.) Languages? Volume and peaks (open enrollment)?
2. **Sources and ownership:** Who owns each document set? How often does it change? Which version wins on conflict?
3. **Ingestion:** Document Intelligence / layout model → Markdown with headings and tables; chunk by section; attach metadata (`plan_id`, `product`, `effective_from/to`, `doc_type`, `acl_groups`, `source_url`, `version`).
4. **Retrieval:** hybrid (BM25 + vector) → RRF → semantic/cross-encoder rerank → top 5–10 chunks; filter on `plan_id`, `effective_date`, and ACLs **inside** the query.
5. **Generation:** system prompt that says "answer only from sources, cite chunk IDs, say you don't know otherwise"; structured output `{answer, citations[], confidence}`; low temperature.
6. **Guardrails:** prompt-injection shields, PII/PHI handling, groundedness detection, and an "escalate to a human" path.
7. **Evaluation:** a golden set built with SMEs, retrieval and generation metrics, run in CI on every prompt/model/index change.
8. **Ops:** tracing per turn (query → retrieved IDs → prompt → answer), cost per turn, latency p50/p95, feedback capture, and index-freshness monitoring.
9. **Rollout:** internal agent-assist for call-center reps first (a human in the loop), then member-facing once metrics hold.

**Your angle:** Map it to your current build ([S5](13-Behavioral-Story-Bank.md#s5)): "In my current project I'm using Azure AI Search for hybrid retrieval inside a LangGraph flow…" `[fill in: your index design, metadata, and how memory feeds the query]`.
**Likely follow-ups:** "What would you build first in week 1?" · "What's the biggest risk?" (stale or contradictory documents, and permission leaks)

---

### Q4. How do you chunk documents? How do you pick chunk size and overlap?  `[P0]`
**Say this first (~30 sec):** I chunk by **document structure** (sections, headings, table boundaries) rather than a fixed character count, then cap size. A common starting point is roughly 300–800 tokens with 10–25% overlap, but I treat size as a hyperparameter I tune against a retrieval eval set, not a guess. Small chunks are precise but lose context; big chunks keep context but dilute the embedding and waste prompt tokens.

**If they dig deeper:**
- **Strategies, from simple to better:** fixed-size with overlap → recursive/sentence-aware → **structure-aware** (Markdown headers, HTML sections, page layout) → semantic chunking (split where embedding similarity drops).
- **Tables:** never split a table mid-row. Keep it as one chunk (as Markdown) and repeat the header row and caption if you must split it. Benefit grids (copays, deductibles) are the classic failure point.
- **Add context to each chunk:** prefix the document title and section path ("EOC 2026 › Outpatient Imaging › MRI"). **Contextual retrieval** (Anthropic) goes further: an LLM writes a 50–100-token blurb situating each chunk before embedding and BM25 indexing. Anthropic reported 49% fewer failed retrievals, and 67% fewer when combined with reranking.
- **Small-to-big / parent-child:** embed small chunks for precise matching, but return the parent section to the LLM for context. Azure AI Search supports this through index projections (one source document → many chunk documents with a parent key).
- **Microsoft's published experiments** found ~512-token chunks with 25% overlap a strong default for hybrid + semantic ranking. That's a good anchor, but validate on your own data.

**Your angle:** In Load Deal AI ([S1](13-Behavioral-Story-Bank.md#s1)) you *curated* the knowledge base (10 docs, ~100 sections, [S6](13-Behavioral-Story-Bank.md#s6)). Hand-curated, well-sectioned content is the cheapest chunking win there is.
**Likely follow-ups:** "How would you know your chunking is wrong?" (recall@k drops; answers cite half a table; questions that span sections fail)

---

### Q5. What is hybrid search, and why does it usually beat pure vector search? What is RRF?  `[P0]`
**Say this first (~30 sec):** Hybrid search runs a keyword (BM25) query and a vector query in parallel and merges the results. Vectors catch *meaning* ("knee scan" ≈ "MRI of lower extremity"); keywords catch *exact tokens* that embeddings blur, like CPT/HCPCS codes, drug names, plan IDs, and acronyms. In healthcare that exact-match half matters a lot. The results are merged with Reciprocal Rank Fusion, which combines by *rank* rather than raw score, so you don't have to normalize BM25 and cosine scores onto one scale.

**If they dig deeper:**
- **RRF formula:** `score(d) = Σ 1 / (k + rank_i(d))`, summed over each result list, with `k ≈ 60`. Documents ranked well in *both* lists rise to the top.
- In Azure AI Search, a hybrid query automatically uses RRF. You can weight vector queries, and semantic ranking then reranks the fused top 50.
- Microsoft's benchmark: hybrid + semantic reranking beat pure vector and pure keyword across their test sets.
- **When pure vector is fine:** short, conversational content with no codes or identifiers. Still, hybrid is rarely worse, so it's my default.

**Your angle:** Name what your current index uses ([S5](13-Behavioral-Story-Bank.md#s5)): `[fill in: hybrid? semantic ranker? which fields are searchable vs vectorized?]`.
**Likely follow-ups:** "How do you weight keyword vs vector?" (tune on the eval set; vector weights in the query) · "What comes after fusion?" (Q13, reranking)

---

### Q6. How do you enforce access control in RAG? Why is it critical in healthcare?  `[P0]`
**Say this first (~30 sec):** Permissions must be enforced **in the retrieval query, before anything reaches the LLM**. I store ACL metadata (allowed groups/users, sensitivity label, plan or line of business) on every chunk and apply it as a filter using the caller's real identity. Never "retrieve everything and ask the model not to mention it," because once text is in the prompt you've already disclosed it. In healthcare, a leak means PHI exposure under HIPAA, so the system has to **fail closed**: if we can't resolve the user's entitlements, return nothing.

**If they dig deeper:**
- **Patterns:** (1) security-filter string fields with the user's group IDs passed as a filter (works anywhere, generally available in Azure AI Search); (2) native identity-aware trimming, where the search service checks the user's Entra token against synced ACLs (Azure AI Search supports this in preview for ADLS Gen2, SharePoint, and Purview labels).
- **Propagate identity end to end:** UI → API → agent → search uses the *user's* identity (on-behalf-of), not one god-mode service account.
- **Pre-filter vs post-filter:** pre-filtering inside the search guarantees you still get *k* results; post-filtering in app code can leave you with zero and tempts people to widen the search.
- **ACL sync lag:** permissions change at the source, and the index only knows after the next sync. Measure that lag and keep it inside what the security team accepts.
- **Defense in depth:** separate indexes per sensitivity tier (no PHI in a general-knowledge index), minimize PHI at ingestion, and audit-log *which chunks were retrieved for whom*.
- **Multi-tenant:** for employer groups/plans, filter by `plan_id`, which is both a correctness *and* a privacy control.

**Your angle:** This is your strongest bridge. You owned the shared entitlements service ([S9](13-Behavioral-Story-Bank.md#s9)), made AMP access checks fail closed, and built Watt's entitlements-driven registry ([S3](13-Behavioral-Story-Bank.md#s3)). Say: "Authorization is the part of RAG I have the most production scar tissue on."
**Likely follow-ups:** "How do you test it?" (eval cases with users who *shouldn't* see a doc; assert zero hits) · see [08 · Security & HIPAA](08-Security-Responsible-AI-and-HIPAA.md)

---

### Q7. How do you reduce hallucinations and make answers grounded and citable?  `[P0]`
**Say this first (~30 sec):** First, fix retrieval, because most "hallucinations" in RAG come from the model not getting the right passage. Then constrain generation: answer only from the provided sources, cite chunk IDs, and abstain when the sources don't cover the question. Finally, *verify*: check each citation actually supports the claim, run a groundedness check, and route low-confidence or high-stakes answers to a human.

**If they dig deeper:**
- **Prompt and format:** structured output (`answer`, `citations[]`, `answer_found: bool`); low temperature; instructions that say "if not in sources, say 'I couldn't find this in your plan documents.'"
- **Abstain thresholds:** if the top reranker score is below a threshold (e.g., Azure semantic ranker < ~2 on its 0–4 scale), don't answer and offer escalation.
- **Post-hoc verification:** a citation checker (does chunk X contain support for sentence Y?), Azure AI Content Safety groundedness detection, or an LLM judge on a sample.
- **UX:** show sources inline and make the "talk to a person" path easy.
- **Domain rule:** the assistant *explains* coverage. It does not *decide* coverage or medical necessity, and that line is a design requirement.

**Your angle:** You built **citation checks** into the LangGraph pipelines agent ([S1](13-Behavioral-Story-Bank.md#s1)), and your Data Validation LLM judge "never writes without confirmation" ([S2](13-Behavioral-Story-Bank.md#s2)). Both are concrete examples of verify-then-act.
**Likely follow-ups:** "What if the source documents conflict?" (surface both with dates; prefer the latest effective version; flag the conflict to content owners)

---

### Q8. How do you evaluate a RAG system?  `[P0]`
**Say this first (~30 sec):** I evaluate **retrieval and generation separately**, because they fail differently. For retrieval: given a question, did the right chunk show up in the top *k* (recall@k, MRR)? For generation: is the answer faithful to the retrieved context, relevant to the question, and correct against a reference? Everything runs on a golden dataset built with subject-matter experts and grows from real production failures. It runs in CI on every prompt, model, or index change, so we catch regressions before users do.

**If they dig deeper:**
- **Retrieval metrics:**
  - *recall@k*: fraction of questions whose relevant chunk appears in the top *k*. This is the most important one, because the LLM can ignore extra noise but can't use what isn't there.
  - *precision@k*: fraction of the top *k* that's relevant (matters for token cost and distraction).
  - *MRR*: mean of 1/rank of the first relevant hit (is the best chunk near the top?).
  - *nDCG@k*: graded relevance with a position discount (when some chunks are "more relevant" than others).
- **Generation metrics (RAGAS-style):** *faithfulness/groundedness* (are claims supported by the context?), *answer/response relevance*, *context precision* and *context recall*, and *answer correctness* vs. a reference.
- **LLM-as-judge:** scalable, but calibrate it against human labels on a sample (aim for high agreement) and watch for biases (verbosity, position, self-preference).
- **Golden set:** start with 50–100 realistic questions with expected source docs and answers; include *negative* cases (out-of-scope, should-abstain, should-not-see-due-to-permissions).
- **Online:** thumbs up/down, escalation-to-human rate, abstain rate, citation click-through, and repeat-question rate.

**Your angle:** You shipped a **20-question eval set** and **per-turn cost tracking** for Load Deal AI ([S1](13-Behavioral-Story-Bank.md#s1)). Say how you'd scale that pattern to a team: eval sets as code, owned per feature, gating merges. See [07 · Evaluation](07-Evaluation-and-Observability.md).
**Likely follow-ups:** "How big should the eval set be?" · "Who labels it?" (SMEs and reps; budget for it explicitly)

---

### Q9. A user says the bot gave a wrong answer. How do you debug it?  `[P0]`
**Say this first (~30 sec):** I pull the trace for that turn and walk the pipeline backwards to find *which stage* failed, so I fix the right layer. Was the right document even in the index? Was it retrieved in the top *k*? Did it survive reranking and the context-packing cut? Did the model use it correctly? Then I add the case to the eval set so it can't regress.

**If they dig deeper:** a decision tree:
1. **Ingestion:** Is the source doc indexed, and is it the current version? Did parsing mangle it (scanned PDF, table split)? Is the metadata right (wrong `plan_id` or effective date)?
2. **Access:** Did a permission filter correctly or *incorrectly* exclude it?
3. **Query understanding:** Was a follow-up ("what about for my daughter?") rewritten into a standalone query? Wrong intent route?
4. **Retrieval:** Is the right chunk in the top 50? If not, it's a recall problem: try hybrid weights, synonyms (CPT code ↔ name), chunking, or embeddings.
5. **Ranking/packing:** Retrieved but cut by the reranker or token budget? That's precision/ordering.
6. **Generation:** Right chunk in the prompt but a wrong answer? The model ignored or misread it ("lost in the middle"), the prompt is ambiguous, or sources conflict. Fix the prompt or ordering, or use a stronger model.
7. **Data truth:** Sometimes the document itself is wrong or outdated, so route it to the content owner.

**Your angle:** This is the same discipline as your PnL reconciliation ([S8](13-Behavioral-Story-Bank.md#s8)): 60+ discrepancies triaged by root cause, ending with all 32 deals matching. It's also your Snowflake cost-spike hunt ([S7](13-Behavioral-Story-Bank.md#s7)): measure, isolate, then fix.
**Likely follow-ups:** "What tooling do you need for this?" (end-to-end tracing with retrieved chunk IDs and scores; see [07](07-Evaluation-and-Observability.md))

---

### Q10. When is RAG the wrong tool?  `[P0]`
**Say this first (~30 sec):** RAG is great for "what does the document say?" It's bad at questions that need **computation over structured data**: counts, sums, trends, top-N. Retrieving 10 chunks can't answer "how many prior-auth requests for MRIs were denied last quarter?" For that I use text-to-SQL over a **governed semantic layer**, or call an API for live transactional data like claim status. Many real assistants are routers: RAG for policy text, SQL for metrics, APIs for member-specific records.

**If they dig deeper:**
- **Aggregations and analytics** → text-to-SQL against a semantic model (defined metrics, joins, and synonyms) so the LLM doesn't invent joins.
- **Exact lookups / live data** (claim status, eligibility, accumulators) → a tool/API call with the member's identity, not an index snapshot.
- **Small, static corpus** → just put it in the prompt with prompt caching.
- **Behavior/format problems** → prompting or fine-tuning, not retrieval.
- **Deterministic rules** (e.g., "is this CPT code on the prior-auth list?") → a lookup table or rules engine; the LLM only explains the result.

**Your angle:** This is *exactly* your Load Deal AI design ([S1](13-Behavioral-Story-Bank.md#s1)): a Snowflake Cortex agent over a **semantic view** for numbers plus a curated KB for meaning, and your Data Intelligence layer ([S4](13-Behavioral-Story-Bank.md#s4)), where semantic views cut cost-query time from 85.6s to 8.8s. Lead with this; it's a differentiator.
**Likely follow-ups:** "How do you make text-to-SQL safe?" (read-only role, row-level security, allow-listed views, query cost limits, show the SQL)

---

### Q11. How do you choose an embedding model?  `[P1]`
**Say this first (~30 sec):** Benchmarks like MTEB are a shortlist, not the answer. I evaluate two or three candidates on *our* retrieval eval set and weigh quality against dimensions/storage, cost, latency, max input length, language coverage, and whether the model is available inside our compliance boundary. PHI can't go to an endpoint without a BAA.

**If they dig deeper:**
- **Dimensions:** more dims means more memory. Models trained with Matryoshka (MRL), like OpenAI `text-embedding-3-*`, can be truncated (e.g., 3072 → 1024) with small quality loss.
- **Domain:** general models handle most insurance text; clinical text with heavy terminology may benefit from a domain or fine-tuned embedder, but prove it with the eval first.
- **Multilingual:** a Massachusetts member base needs Spanish, Portuguese, Chinese, Haitian Creole, and more, so test cross-lingual retrieval.
- **Versioning:** changing embedding models means **re-embedding everything**. Store the model name/version with the index and do a blue/green index swap.
- Query and document must use the *same* model (or a model explicitly trained as a query/doc pair).

**Your angle:** `[fill in: which embedding model you use in S5 and why]`.
**Likely follow-ups:** "Would you fine-tune an embedding model?" (only with labeled query–passage pairs and a measured recall gap)

---

### Q12. Vector indexes: what's ANN, and what are the trade-offs of HNSW vs exhaustive kNN?  `[P1]`
**Say this first (~30 sec):** Exhaustive kNN compares the query to every vector, so it's exact but scales linearly. Approximate nearest neighbor (ANN) algorithms like HNSW build a layered proximity graph and navigate it greedily, giving sub-linear search with slightly imperfect recall. HNSW is the usual default; you tune recall vs. latency vs. memory. Exhaustive kNN is for small corpora, heavily filtered queries, or building ground truth to measure ANN recall.

**If they dig deeper:**
- **HNSW knobs:** `m` (links per node: more means better recall and more memory), `efConstruction` (build-time candidate list: better graph, slower indexing), `efSearch` (query-time candidate list: better recall, slower queries).
- HNSW lives **in memory**, so vector index size drives cost. **Quantization** (scalar int8, binary) cuts memory several-fold, and oversampling plus rescoring with full-precision vectors recovers most of the quality.
- **Filters + ANN:** pre-filtering keeps result counts right but can slow the graph walk on very selective filters. Some engines switch to exhaustive search when the filter is tiny.
- **Similarity metric:** cosine for most text embeddings (dot product equals cosine on normalized vectors).

**Your angle:** Relate it to your performance work ([S14](13-Behavioral-Story-Bank.md#s14), [S9](13-Behavioral-Story-Bank.md#s9)): "same trade-off thinking as caching and indexing in AMP: measure p95, then tune."
**Likely follow-ups:** "How would you measure ANN recall?" (compare against exhaustive-kNN results on a sample)

---

### Q13. What does a reranker do, and when is it worth the latency?  `[P1]`
**Say this first (~30 sec):** First-stage retrieval uses bi-encoders: query and documents are embedded *separately*, which is fast but coarse. A reranker is usually a **cross-encoder** that reads the query and each candidate *together* and scores relevance much more accurately, but it's too slow to run on the whole corpus. So: retrieve ~50 cheaply, rerank, and keep the top 5–10. It's almost always worth it for RAG, because better top-5 precision means fewer tokens and fewer wrong answers.

**If they dig deeper:**
- **Options:** Azure AI Search semantic ranker (reranks the top 50, score 0–4, also returns captions), Cohere Rerank, open-source `bge-reranker`, or an LLM as reranker (most accurate, most expensive).
- **Bonus:** reranker scores are better calibrated than raw similarity, which makes them useful for **abstain thresholds** (Q7).
- **Cost:** adds tens to a few hundred ms. Mitigate by reranking fewer candidates, or skipping it for high-confidence keyword hits.

**Your angle:** `[fill in: do you use the semantic ranker in S5? what top-k?]`
**Likely follow-ups:** "Bi-encoder vs cross-encoder in one sentence?" (separate embeddings vs joint attention over the pair)

---

### Q14. Query transformation: rewriting, multi-query, HyDE, decomposition. When would you use each?  `[P1]`
**Say this first (~30 sec):** User questions are often bad search queries, so I transform them before retrieving. The highest-value one is **conversational rewrite**: turning "what about for my daughter?" into a standalone query using chat history. Beyond that: multi-query for recall, decomposition for multi-part questions, and HyDE when questions and documents are written very differently. Each adds an LLM call, so I route: simple questions skip it.

**If they dig deeper:**
- **Rewrite / condense:** required for multi-turn chat; a small, fast model is fine.
- **Multi-query:** generate 3–5 paraphrases, retrieve for each, and fuse with RRF; improves recall on vague questions.
- **Decomposition:** "Compare MRI coverage between my HMO and PPO options" → two sub-queries → combine. This is the core of agentic retrieval (Q16).
- **HyDE:** have the LLM write a *hypothetical answer*, embed that, and search with it. It helps when queries are short and docs are formal, but a confidently wrong hypothetical can steer retrieval off course.
- **Step-back:** ask a more general question first ("what are the imaging coverage rules?") to retrieve background.
- **Domain synonym expansion:** CPT code ↔ procedure name, brand ↔ generic drug names (synonym maps in Azure AI Search).

**Your angle:** Your short-term memory work ([S5](13-Behavioral-Story-Bank.md#s5)) is directly relevant, because conversation history is what makes rewrite possible. See [06 · Memory](06-Memory-and-Context-Engineering.md).
**Likely follow-ups:** "How do you know a transformation helps?" (A/B it on the retrieval eval: recall@k with vs. without)

---

### Q15. With million-token context windows, is RAG dead? Long context vs RAG?  `[P1]`
**Say this first (~30 sec):** No, they're complementary. Long context is great when the relevant material is a few large documents for one session, like summarizing a member's 200-page appeal file. But stuffing everything into every call costs more and adds latency per request, and quality degrades as context grows ("lost in the middle," context rot). It also can't enforce per-user permissions or give precise citations. In practice I use retrieval to select and long context to give the model more of what's relevant.

**If they dig deeper:**
- **Cost math:** tokens per call × calls per day. Retrieving 4k tokens vs. sending 400k is roughly a 100× difference, before latency.
- **Prompt caching** changes the math for a *static* shared prefix (e.g., one policy manual used by everyone): it gets cheaper on repeat, but still has no ACLs.
- **Research:** Liu et al., "Lost in the Middle" (2023): models use information at the start and end of the context better than the middle.
- **Design rule:** put the most relevant chunks first or last, and keep packed context tight.

**Your angle:** Tie to the cost discipline in your per-turn cost tracking ([S1](13-Behavioral-Story-Bank.md#s1)) and the Snowflake spike ([S7](13-Behavioral-Story-Bank.md#s7)): "I always ask what this costs per turn at production volume."
**Likely follow-ups:** "When would you choose long context?" (single-document deep analysis, low volume, no fine-grained ACL needs)

---

### Q16. What is agentic RAG? When is it worth it?  `[P1]`
**Say this first (~30 sec):** In classic RAG, retrieval happens once, always. In agentic RAG, the LLM *decides* whether to retrieve, which source or tool to use, and whether the results are good enough, and loops (retrieve → grade → rewrite → retrieve again) until it can answer. It handles multi-hop and multi-source questions much better, but costs more calls, more latency, and is harder to evaluate. So I route: simple questions take the single-shot path, and only complex ones go to the agent loop, with a hard cap on iterations.

**If they dig deeper:**
- **Known patterns:** *Corrective RAG (CRAG)*, which grades retrieved docs and falls back to another source or a rewrite if they're poor; *Self-RAG*, where the model reflects on whether retrieval is needed and whether its output is supported; and *Adaptive RAG*, which routes by query complexity.
- **LangGraph fit:** nodes for `route → retrieve → grade_documents → (rewrite ↺ | generate) → check_grounding`, with conditional edges and a `recursion_limit` or max-loop counter in state.
- **Managed option:** Azure AI Search *agentic retrieval* / Foundry IQ knowledge bases do LLM query planning into parallel subqueries for you (see [04](04-Azure-AI-Search-and-Foundry.md)).
- **Eval:** add trajectory metrics (tool choice correctness, number of loops) on top of answer metrics.

**Your angle:** Your LangGraph pipelines agent with citation checks ([S1](13-Behavioral-Story-Bank.md#s1)) is a small agentic RAG. Describe its graph. See [05 · Agents & LangGraph](05-Agents-and-LangGraph.md).
**Likely follow-ups:** "How do you stop it from looping forever?" (max iterations, budget in state, fallback answer)

---

### Q17. How do you keep the index fresh, and handle document versions?  `[P1]`
**Say this first (~30 sec):** Incremental indexing driven by change detection: only new or modified documents get re-parsed and re-embedded, and deletions are propagated via soft-delete flags. In healthcare, versioning matters as much as freshness. A medical policy has effective dates, and the *old* version still governs a claim with an earlier service date, so I index versions with `effective_from/to` metadata and filter by date instead of overwriting.

**If they dig deeper:**
- **Idempotent upserts** keyed by `doc_id + chunk_no + version`; delete orphaned chunks when a document shrinks.
- **Change detection:** high-water mark (last-modified timestamp) or change feed; indexers in Azure AI Search support this natively for Blob and SQL sources.
- **Full re-index** (new chunking or embedding model) → build a new index, run the eval, swap an **index alias** (blue/green), and keep the old one for rollback.
- **Monitor:** index lag (source updated → searchable), document counts per source, and failed-parse rate.

**Your angle:** Your Data Validation Service ([S2](13-Behavioral-Story-Bank.md#s2)) already checks pipeline outputs for freshness, nulls, and parity. Propose the same checks for the RAG ingestion pipeline. Your Databricks-precomputed Redis cache ([S14](13-Behavioral-Story-Bank.md#s14)) is also a freshness-vs-speed trade-off you've managed.
**Likely follow-ups:** "A policy changed yesterday; how fast is the bot correct?" (state your SLA and how you'd measure it)

---

### Q18. How do you reduce cost and latency of a RAG system?  `[P1]`
**Say this first (~30 sec):** Measure first: per-turn tokens, cost, and a latency breakdown by stage. Then the big levers: send fewer, better tokens (rerank and keep the top 5 instead of 20); use small models for routing and rewriting, and the big model only for the final answer; cache aggressively; parallelize retrieval; and stream the response so perceived latency drops.

**If they dig deeper:**
- **Model routing:** a small model for classify/rewrite/grade; a larger model for synthesis only when needed.
- **Caching:** embedding cache for repeated queries; **prompt caching** for the static system prompt and instructions; semantic answer cache for FAQ-style questions (be careful: never cache member-specific or PHI-bearing answers across users).
- **Retrieval:** quantized vectors, tuned `k`, a single hybrid call instead of several round trips.
- **Infra:** provisioned throughput (PTU) for steady high volume (predictable latency); batch APIs for offline jobs like re-summarizing documents.
- **Skip work:** don't retrieve for greetings or chit-chat (router); short-circuit deterministic lookups.

**Your angle:** Strong. You took the AMP landing page from 20s to 5s and outage management from 7s to 1s ([S14](13-Behavioral-Story-Bank.md#s14)), took Snowflake spend from ~100 to ~11 credits/day ([S7](13-Behavioral-Story-Bank.md#s7)), and built per-turn cost tracking ([S1](13-Behavioral-Story-Bank.md#s1)). Same playbook: profile, find the dominant cost, remove it.
**Likely follow-ups:** "What's your target latency?" (time-to-first-token < ~1–2s for chat; full answer a few seconds; agree on it with product)

---

### Q19. How do you handle tables, scanned PDFs, and images in source documents?  `[P2]`
**Say this first (~30 sec):** Parsing quality caps everything downstream, so I use a layout-aware parser (e.g., Azure Document Intelligence's layout model) that outputs Markdown with headings and real tables, and OCR for scans. Tables stay whole as their own chunks with header rows. For images and diagrams, I either generate text descriptions with a vision model at ingestion or use multimodal embeddings.

**If they dig deeper:**
- Validate parsing on a sample of real documents. Benefit summaries and fee schedules are table-heavy, and a broken table produces confidently wrong copays.
- Keep page numbers and section paths in metadata so citations can deep-link.
- Flag low-OCR-confidence pages for human review rather than silently indexing garbage.

**Your angle:** Your streaming XML parser fix (>1 GB → ~200 MB, [S14](13-Behavioral-Story-Bank.md#s14)) shows you take ingestion engineering seriously.
**Likely follow-ups:** "How would you test parsing quality?" (golden documents with known table values; assert extracted values)

---

### Q20. What is GraphRAG, and would you use it here?  `[P2]`
**Say this first (~30 sec):** GraphRAG (from Microsoft Research) uses an LLM at indexing time to extract entities and relationships into a knowledge graph, then builds summaries of communities of related entities. It shines on **global or multi-hop** questions like "what are the recurring themes across all appeals this year?", which chunk retrieval can't answer because no single chunk contains it. The cost is heavy, slow indexing. I'd only use it after showing plain hybrid RAG fails on an important class of questions.

**If they dig deeper:**
- **Local vs global search:** local answers entity-centric questions by walking the graph; global uses community summaries for corpus-wide sensemaking.
- **Healthcare fits:** relationships like provider ↔ network ↔ plan, or drug ↔ condition ↔ policy, where structured graph data may already exist (then use the graph directly, not LLM extraction).

**Your angle:** Show judgment: "I'd start with hybrid + rerank + a semantic layer, and add a graph only for proven multi-hop needs."
**Likely follow-ups:** "Graph DB vs LLM-extracted graph?" (if the relationships already exist in systems of record, use those; they're more accurate)

---

## Key terms

| Term | One-liner |
|---|---|
| Chunk | A retrievable unit of a document (section/paragraph), with metadata |
| Embedding | A vector representing meaning; similar texts → nearby vectors |
| BM25 | Classic keyword-relevance scoring (term frequency × rarity, length-normalized) |
| ANN / HNSW | Approximate nearest-neighbor search; HNSW = layered proximity graph |
| Hybrid search | Keyword + vector in parallel, fused (usually by RRF) |
| RRF | Reciprocal Rank Fusion: `Σ 1/(k + rank)`, k ≈ 60 |
| Bi-encoder vs cross-encoder | Separate embeddings (fast) vs joint query+doc scoring (accurate) |
| recall@k / MRR / nDCG | Found it in top k? / how high is the first hit? / graded, position-discounted relevance |
| Faithfulness / groundedness | Every claim in the answer is supported by the retrieved context |
| Security trimming | Filtering results by the caller's permissions inside the search query |
| Contextual retrieval | Prepending LLM-written context to each chunk before indexing |
| Agentic RAG | The LLM decides when/what to retrieve and iterates |

## References
- [Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (2020)](https://arxiv.org/abs/2005.11401): the original RAG paper; know the name, not the details.
- [Azure AI Search: RAG overview](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview): Microsoft's framing of classic vs agentic RAG on your stack.
- [Azure Architecture Center: RAG solution design and evaluation guide](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-solution-design-and-evaluation-guide): end-to-end phases (prep, chunking, enrichment, embedding, retrieval, eval); great to skim before a design question.
- [Azure AI Search: chunking large documents](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents): chunking strategies and sizing guidance.
- [Microsoft: Outperforming vector search with hybrid retrieval and reranking](https://techcommunity.microsoft.com/blog/azure-ai-services-blog/azure-ai-search-outperforming-vector-search-with-hybrid-retrieval-and-reranking/3929167): the benchmark behind "hybrid + semantic ranker" and the 512-token/25% overlap finding.
- [Azure AI Search: Hybrid search scoring (RRF)](https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking): RRF formula and how fusion works.
- [Anthropic: Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval): contextual embeddings + contextual BM25 + reranking; the 49%/67% numbers.
- [Azure Document Intelligence for RAG](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept/retrieval-augmented-generation): layout-aware parsing and semantic chunking of PDFs/tables.
- [Pinecone: Rerankers and two-stage retrieval](https://www.pinecone.io/learn/series/rag/rerankers/): clear bi-encoder vs cross-encoder explanation.
- [Gao et al., HyDE: "Precise Zero-Shot Dense Retrieval without Relevance Labels"](https://arxiv.org/abs/2212.10496): the hypothetical-document trick.
- [Liu et al., "Lost in the Middle" (2023)](https://arxiv.org/abs/2307.03172): why long context isn't free.
- [RAGAS: available metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/): faithfulness, context precision/recall, response relevancy definitions.
- [Jason Liu: Systematically improving your RAG](https://jxnl.co/writing/2024/05/22/systematically-improving-your-rag/): a practitioner's playbook (synthetic evals, segmenting failures); great for the debugging question.
- [Hamel Husain: Your AI product needs evals](https://hamel.dev/blog/posts/evals/): how good teams build eval loops.
- [LangGraph: Agentic RAG tutorial](https://docs.langchain.com/oss/python/langgraph/agentic-rag): retrieve → grade → rewrite → generate as a graph; maps to your stack.
- [Corrective RAG (CRAG) paper](https://arxiv.org/abs/2401.15884) and [Self-RAG paper](https://arxiv.org/abs/2310.11511): named agentic-RAG patterns.
- [Microsoft GraphRAG](https://microsoft.github.io/graphrag/) and [paper: "From Local to Global"](https://arxiv.org/abs/2404.16130): when graph-based retrieval helps.
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard): embedding model shortlist (then eval on your own data).
- [Malkov & Yashunin, HNSW paper](https://arxiv.org/abs/1603.09320): the ANN algorithm behind most vector DBs.
- [Eugene Yan: Patterns for building LLM-based systems](https://eugeneyan.com/writing/llm-patterns/): evals, RAG, guardrails, caching in one classic post.
- [Chip Huyen: Building a generative AI platform](https://huyenchip.com/2024/07/25/genai-platform.html): where RAG sits in a full platform (routing, caching, guardrails, observability).
