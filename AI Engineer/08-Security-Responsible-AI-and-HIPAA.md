# 08 · Security, Responsible AI & HIPAA

[← Index](00-Index.md) · **Manager-round priority:** High · **Read time:** ~30 min

> **Why this matters for this role:** BCBSMA is a health plan, a HIPAA *covered entity* holding PHI for ~3M members. The JD calls out "healthcare and compliance requirements" and lists HIPAA/regulated-industry experience as preferred. The manager wants to know you won't be the person who puts PHI in a log file or lets an agent take an unapproved action. Your security instincts in [S9](13-Behavioral-Story-Bank.md#s9) (fail-closed entitlements) and [S2](13-Behavioral-Story-Bank.md#s2) (never writes without confirmation) are the bridge. Your healthcare exposure is [S13](13-Behavioral-Story-Bank.md#s13) (Cerner).

## Primer

**HIPAA in four sentences.**
1. **PHI** is individually identifiable health information (diagnoses, claims, member ID + name, dates of service, etc.) held by a *covered entity* (health plans, most providers, clearinghouses) or its *business associates*.
2. The **Privacy Rule** limits use and disclosure. Its **minimum necessary** standard says use only the PHI needed for the purpose.
3. The **Security Rule** requires administrative, physical, and technical safeguards for electronic PHI: access control, audit controls, integrity, transmission security.
4. Any vendor that touches PHI on your behalf (e.g., Microsoft for Azure OpenAI) must sign a **Business Associate Agreement (BAA)**.

**De-identification** (then it's no longer PHI):
- **Safe Harbor**: remove the 18 listed identifiers (names, geographic units smaller than a state, all date elements except year, phone, email, SSN, member/account numbers, etc.) and have no actual knowledge that the remainder identifies someone.
- **Expert Determination**: a qualified statistician certifies that the re-identification risk is very small. This is more flexible, and is used when you need to keep things like dates.

**Defense-in-depth picture for an LLM app:**

```
 user ─► [authN/authZ] ─► [input guard: Prompt Shields, PII detect] ─► orchestrator (LangGraph)
                                                                   │
              ┌────────────────────────────────────────────────────┤
              ▼                                                    ▼
   retrieval with security trimming                 tools: least privilege, allow-list,
   (filter by user's groups/plan)                   human approval for writes/actions
              │                                                    │
              └──────────────► LLM (Azure, under BAA) ◄────────────┘
                                   │
                    [output guard: groundedness, PII/PHI leak check, content filter]
                                   │
                         response + citations ─► user
   everywhere: redacted logs/traces · audit log (who saw what) · rate limits · encryption · private endpoints
```

## Questions & answers

### Q1. You're building an LLM app that touches member data. What are the HIPAA considerations?  `[P0]`
**Say this first (~30 sec):** "First, make sure every service that sees PHI is covered by a BAA and runs inside our compliance boundary. For us that's Azure OpenAI/Foundry and Azure AI Search in our tenant with private networking. Second, minimum necessary: the model only gets the PHI the task needs, and retrieval enforces the user's access rights. Third, PHI must not leak into places nobody's governing: logs, traces, eval datasets, long-term memory, caches. Fourth, audit: we can show who accessed what and why. I'd involve privacy and security early, not at launch."
**If they dig deeper:**
- **Data flow diagram first.** List every place PHI lands: prompts, vector index, chat history, memory store, traces, eval sets, analytics.
- **Retention:** set retention for chat history and memory, and support deletion requests.
- **Encryption** in transit and at rest (customer-managed keys if policy requires it). **Managed identity**, no keys in code. **Private endpoints**.
- **Dev/test:** use de-identified or synthetic data. Never copy production PHI to a laptop or a non-BAA SaaS tool.
- **Third-party tools** (LangSmith, other SaaS evals): check BAA and hosting before sending any traces.

**Your angle:** "At Cerner I worked on a healthcare revenue-cycle application ([S13](13-Behavioral-Story-Bank.md#s13)), so I've worked inside healthcare data rules. And in my current role I own the shared entitlements service ([S9](13-Behavioral-Story-Bank.md#s9)), where access checks fail closed. That's the mindset I'd bring: default deny, least privilege." Be honest: you haven't been the HIPAA owner. Say you'd partner with the privacy office.
**Likely follow-ups:** Can we send PHI to Azure OpenAI? What about to a model from the Foundry catalog that isn't sold by Microsoft? (See Q2.)

### Q2. Is it OK to send PHI to Azure OpenAI? What does Microsoft do with our prompts?  `[P0]`
**Say this first:** "With the right setup, yes. That's a common reason healthcare companies standardize on Azure. Microsoft offers a BAA covering in-scope Azure services, including Azure OpenAI. Prompts and completions aren't used to train models and aren't shared with OpenAI. The nuance is abuse monitoring: by default some content can be retained for a limited period (documented as up to 30 days) for abuse review, and approved customers can apply for modified abuse monitoring. I'd confirm our tenant's status and the exact in-scope services with security and legal, not assume."
**If they dig deeper:**
- **Not every model in the Foundry catalog has the same terms.** Models sold directly by Azure differ from marketplace or partner models. Check each one.
- Stateful features (agent threads, stored completions, file uploads) persist data in *our* resource. That's covered, but it now needs retention and access policy.
- Deploy in a US region / data zone if residency matters. Use private endpoints and disable public network access.

**Likely follow-ups:** What about using Claude/OpenAI directly? (Only with a BAA and an approved zero-retention configuration. Security and legal decide, not engineering.)

### Q3. How do you keep PHI out of logs, traces, and eval datasets?  `[P0]`
**Say this first:** "Redact by default at the edges. Logging and tracing go through one wrapper that masks known identifiers (member ID, name, DOB, SSN patterns) using a PII detector like Presidio or Azure AI Language PII/PHI detection. Full prompt and response capture is off by default, and where we need it for debugging it goes to a restricted, short-retention store with audited access. Eval sets are built from de-identified or synthetic data."
**If they dig deeper:**
- Use pseudonymous IDs (a hashed member ID) to correlate traces without exposing identity.
- PII detectors aren't perfect. Combine them with structural controls: don't put PHI in the prompt in the first place if an ID lookup will do.
- Make it a **code review checklist item**: "Does this log line or span attribute contain member data?"

**Your angle:** A concrete standard you'd set for the team (ties to [12](12-Team-Leadership-and-Delivery.md)).

### Q4. What is prompt injection, and how do you defend against it?  `[P0]`
**Say this first:** "Prompt injection is when text the model reads overrides your instructions. **Direct**: the user types 'ignore previous instructions.' **Indirect**: the malicious instruction is hidden in a retrieved document, email, or web page, which is the scarier one for RAG and agents. There's no complete fix at the model level, so I design so that a successful injection can't do much damage. Least-privilege tools, human approval for consequential actions, security trimming on data, and input/output filters like Azure Prompt Shields."
**If they dig deeper:**
- **Limit blast radius:** the agent runs with the *user's* permissions, not a super-user service account. Read-only by default. Write actions need confirmation.
- **Separate trusted from untrusted content:** delimit retrieved text, and tell the model it's data, not instructions. This helps but doesn't guarantee anything.
- **Prompt Shields** detects both user prompt attacks and document attacks (indirect injection).
- **Output handling:** never execute model output directly (SQL, code, URLs). Validate it, parameterize it, and allow-list it.
- **Exfiltration paths:** block rendering arbitrary external images/links in the chat UI (a classic data-leak trick).
- **Red-team it:** add injection cases to the eval set.

**Your angle:** [S2](13-Behavioral-Story-Bank.md#s2): "My data-validation agent never writes without confirmation. Even if it were tricked, a human approves every change." [S3](13-Behavioral-Story-Bank.md#s3): signed short-lived links and per-element permissions in Watt are the same principle.
**Likely follow-ups:** How would you test it? (An adversarial eval set: injection strings inside documents and tool outputs.)

### Q5. Walk me through the OWASP Top 10 for LLM applications.  `[P1]`
**Say this first:** "The 2025 list is: prompt injection, sensitive information disclosure, supply chain, data and model poisoning, improper output handling, excessive agency, system prompt leakage, vector and embedding weaknesses, misinformation, and unbounded consumption. For an agentic RAG app at a health plan, the ones I'd prioritize are injection, sensitive info disclosure, excessive agency, vector/embedding weaknesses (mostly access control on the index), and unbounded consumption."
**If they dig deeper (one-line mitigations):**

| # | Risk | Mitigation in our stack |
|---|---|---|
| LLM01 | Prompt injection | Prompt Shields, least-privilege tools, HITL for actions |
| LLM02 | Sensitive info disclosure | Security trimming, output PHI filter, minimum necessary |
| LLM03 | Supply chain | Pin models and packages, vetted model catalog, SBOM |
| LLM04 | Data/model poisoning | Control who can write to the KB, review document ingestion |
| LLM05 | Improper output handling | Validate/escape output, never `eval` SQL/code blindly |
| LLM06 | Excessive agency | Narrow tool scopes, approval gates, step limits |
| LLM07 | System prompt leakage | No secrets or authorization logic in prompts |
| LLM08 | Vector/embedding weaknesses | Per-document ACLs in the index, tenant isolation |
| LLM09 | Misinformation | Grounding + citations + "I don't know" + groundedness checks |
| LLM10 | Unbounded consumption | Rate limits/quotas (APIM), token caps, max agent steps |

**Likely follow-ups:** Which one worries you most for agents? (Excessive agency combined with indirect injection.)

### Q6. How do you make sure a user only sees documents they're allowed to see in RAG?  `[P0]`
**Say this first:** "Security trimming at retrieval time, never trusting the LLM to hide things. Each chunk in the index carries ACL metadata (groups, plan, line of business, or member ID). Every query adds a filter built from the authenticated user's claims. The model never sees content the user couldn't open themselves. Azure AI Search supports this with security filters, and newer versions can sync document-level permissions for some sources."
**If they dig deeper:** Test it with negative tests ("user A asks about user B's claim"). Keep the filter logic in one shared library, not re-implemented per app. For member-facing apps, scope every tool call to the authenticated member ID on the server side, never from the model's arguments.
**Your angle:** This is exactly your entitlements work ([S9](13-Behavioral-Story-Bank.md#s9), [S3](13-Behavioral-Story-Bank.md#s3)): a central entitlements service, fail-closed, and fast enough (~10ms) to check on every request. Strong answer for this manager.

### Q7. Should AI make coverage or prior-authorization decisions?  `[P0]`
**Say this first:** "My view: AI assists, licensed clinicians decide, especially on anything adverse like a denial. The AI can summarize the clinical record against the medical policy, highlight missing information, and draft the rationale with citations, so the nurse reviewer is faster and more consistent. But the determination stays with a human and is based on that individual member's records, not on a population-level prediction. That's also where regulation is heading."
**If they dig deeper:**
- **CMS (Feb 2024 FAQ on the MA final rule CMS-4201-F):** Medicare Advantage plans *may* use algorithms and AI to assist, but medical-necessity decisions must be based on the individual's circumstances (medical history, physician recommendations, clinical notes), not solely on an algorithm. Denials must follow publicly available coverage criteria.
- **Section 1557 (ACA nondiscrimination) rule:** covered entities must make reasonable efforts to identify and mitigate discrimination risk from patient-care decision-support tools.
- Several states have passed laws requiring physician review of AI-assisted denials (e.g., California SB 1120, 2024).
- Design implications: show the evidence and the policy citation, log what the AI suggested vs what the human decided, monitor approval/denial rates by demographic segment, and make it easy for the reviewer to disagree.

**Likely follow-ups:** How would you measure whether the assistant is biasing reviewers? (Track the override rate, compare outcomes before and after by segment, audit samples.)

### Q8. What does "responsible AI" mean to you in practice, not just as a slogan?  `[P0]`
**Say this first:** "Concretely, it's five things I'd build into the team's process. Know the **risk tier** of each use case, because an internal doc search isn't a denial letter. **Evaluate** quality and fairness before launch and keep monitoring after. Keep **humans in the loop** where the stakes are high. Be **transparent**: users know it's AI, and answers cite sources. And keep an **audit trail and an owner** for every model in production. NIST's AI Risk Management Framework (Govern, Map, Measure, Manage) is a good structure for it."
**If they dig deeper:** A lightweight intake form per use case (purpose, data, users, risk tier, human oversight, eval plan) reviewed with compliance. Model/system cards documenting intended use, limits, and eval results.
**Likely follow-ups:** How do you balance this with speed? (Tier it. Low-risk internal tools move fast with standard guardrails. High-risk ones get the full review. A one-size process kills velocity.)

### Q9. How would you check an AI system for bias or fairness?  `[P1]`
**Say this first:** "Define which groups and which harms matter for the use case, then measure. Slice eval results and production outcomes by segment (age band, language, line of business, region, and protected classes where available and legally appropriate). Look for differences in error rate, refusal rate, or recommendation outcomes. For generative assistants, also test language and reading-level differences: does it serve Spanish-speaking members as well?"
**If they dig deeper:** Watch for proxy variables (ZIP code). Keep humans reviewing outliers. Document known limitations.
**Likely follow-ups:** What if the data to slice by isn't available? (Use proxies carefully, run synthetic counterfactual tests by swapping names/attributes in the prompt, and escalate the gap to governance.)

### Q10. How do you explain an LLM's answer to a business user or auditor?  `[P1]`
**Say this first:** "LLMs aren't interpretable the way a linear model is, so I make the *system* explainable. Every answer cites the source passages it used. We log the retrieved context, prompt version, model version, and tool calls for each turn, so we can reconstruct exactly why it said what it said. For decision-support, the output is structured (criterion → evidence → met/not met) rather than one free-text verdict."
**Your angle:** Citation checks in [S1](13-Behavioral-Story-Bank.md#s1). The turn log in [S4](13-Behavioral-Story-Bank.md#s4) gives you the audit trail.

### Q11. How do you secure an agent's tools?  `[P0]`
**Say this first:** "Treat every tool like a public API that a not-fully-trusted caller can hit. Narrow, purpose-built tools instead of 'run any SQL.' The agent's identity is the user's delegated identity with least privilege. Arguments are validated against a schema and authorized on the server side. Read and write are separated, and writes need explicit human confirmation. Every call is audit-logged. And step limits and timeouts stop runaway loops."
**If they dig deeper:** For MCP servers, the same rules apply, plus vetting third-party servers and pinning versions. Watch for "confused deputy" problems, where the tool runs with more rights than the user who asked.
**Your angle:** [S2](13-Behavioral-Story-Bank.md#s2) (confirmation before writes), [S9](13-Behavioral-Story-Bank.md#s9) (fail-closed).

### Q12. What guardrails would you put on a member-facing chatbot?  `[P1]`
**Say this first:** "Input side: authentication, Prompt Shields, topic scoping (benefits/claims only, no medical advice), rate limits. Output side: content-safety filters, a groundedness check against retrieved plan documents, a PHI-leak check, and required citations. Behaviour: a clear 'I'm an AI assistant' disclosure, a safe fallback ('I'm not sure — here's how to reach Member Services'), and a fast handoff to a human for anything about denials, appeals, or urgent clinical concerns."
**Likely follow-ups:** What if someone describes a medical emergency or self-harm? (Hard-coded escalation path with crisis resources, tested in evals. It never depends on the model "deciding" to do it.)

### Q13. What should be in an audit log for an AI system?  `[P1]`
**Say this first:** "Who (user/service identity), when, what they asked, what data was accessed (doc IDs, member IDs touched), what tools were called with which arguments, which model and prompt version answered, what was returned, and any human approval or override. It's stored immutably with restricted access and a retention period that matches policy. That's what lets us answer an auditor, or a member complaint, months later."

### Q14. What's model governance, and how much process would you put around it?  `[P2]`
**Say this first:** "An inventory of every model/agent in production with an owner, intended use, risk tier, data used, eval results, and review date. In other words, model/system cards plus a change process. Higher-risk systems get periodic re-validation and sign-off. I'd keep it lightweight and automated where possible: the eval report from CI *is* the evidence."

### Q15. What's CMS-0057-F and why might it matter to an AI team at a health plan?  `[P2]`
**Say this first:** "It's the CMS Interoperability and Prior Authorization final rule from January 2024. For impacted payers, which include Medicare Advantage plans, Medicaid/CHIP, and ACA exchange plans, it requires faster prior-auth decisions (72 hours expedited, 7 calendar days standard for most of those programs), specific denial reasons, public reporting of prior-auth metrics, and FHIR-based APIs, including a Prior Authorization API, with most API requirements due starting January 2027. That means there's pressure to make prior-auth review faster and more consistent, which is a natural place for AI-assisted summarization. It also means more structured, FHIR-shaped data becomes available."
**If they dig deeper:** FHIR is the HL7 standard for exchanging healthcare data as REST resources (Patient, Claim, Coverage, Condition…). Da Vinci implementation guides cover payer use cases like prior auth.
**Note:** Phrase it as "my understanding". You don't need to be a regulatory expert, just show domain awareness.

## Key terms

| Term | One-liner |
|---|---|
| PHI | Individually identifiable health info held by a covered entity or business associate |
| Covered entity / BA | Health plan, provider, or clearinghouse / a vendor handling PHI for them |
| BAA | Contract making a vendor responsible for safeguarding PHI |
| Minimum necessary | Use or disclose only the PHI needed for the purpose |
| Safe Harbor / Expert Determination | The two HIPAA de-identification methods |
| Security trimming | Filtering retrieval results by the user's permissions |
| Excessive agency | An agent with more tools or permissions than its task needs |
| Prompt Shields | Azure AI Content Safety's direct and indirect injection detector |
| NIST AI RMF | Govern · Map · Measure · Manage risk-management framework |

## References
- [HHS: Summary of the HIPAA Privacy Rule](https://www.hhs.gov/hipaa/for-professionals/privacy/laws-regulations/index.html): official plain-language overview.
- [HHS: Minimum Necessary Requirement](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html): the core principle behind "only send what the task needs."
- [HHS: De-identification guidance (Safe Harbor & Expert Determination)](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html): the 18 identifiers and both methods.
- [HHS: Business Associate contracts](https://www.hhs.gov/hipaa/for-professionals/covered-entities/sample-business-associate-agreement-provisions/index.html): what a BAA is.
- [Microsoft: HIPAA/HITECH offering](https://learn.microsoft.com/en-us/compliance/regulatory/offering-hipaa-hitech): how Microsoft's BAA covers Azure services.
- [Azure OpenAI data, privacy, and security](https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-ai/openai/data-privacy): no training on your data, abuse monitoring, retention. Confirm current wording.
- [OWASP Top 10 for LLM Applications (2025)](https://genai.owasp.org/llm-top-10/): the standard risk list.
- [Prompt Shields (Azure AI Content Safety)](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/jailbreak-detection): direct and indirect injection detection.
- [Microsoft Presidio](https://microsoft.github.io/presidio/): open-source PII detection and anonymization for logs and prompts.
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) and its [Generative AI Profile (NIST AI 600-1)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf): governance vocabulary.
- [Reed Smith: CMS confirms MA organizations may use AI in coverage decisions (Feb 2024 FAQ)](https://www.reedsmith.com/en/perspectives/2024/02/cms-confirms-medicare-advantage-organizations-may-use-ai-in-making-coverage): a readable summary of the CMS position.
- [CMS Interoperability & Prior Authorization Final Rule (CMS-0057-F) fact sheet](https://www.cms.gov/newsroom/fact-sheets/cms-interoperability-and-prior-authorization-final-rule-cms-0057-f): prior-auth timelines and FHIR APIs.
- [HL7 FHIR overview](https://hl7.org/fhir/overview.html): what FHIR resources are, at a glance.
- [Anthropic: Mitigating prompt injection / jailbreak guidance](https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks): a practical vendor-side view of layered defenses.
