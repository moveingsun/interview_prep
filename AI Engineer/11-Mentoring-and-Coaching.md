# 11 · Mentoring and Coaching

[← Index](00-Index.md) · **Manager-round priority:** High · **Read time:** ~35 min

> **Why this matters for this role:** The JD asks you to "mentor AI engineers," "coach engineers and create growth paths," "run knowledge-sharing sessions," and "lead through teaching and example," while still coding 40–50% of the time. The hiring manager wants to know whether you'll make the team better or just be a strong individual contributor.

---

## Read this first: how to frame your leadership experience honestly

You haven't held a people-manager title, and this role doesn't read like a people-manager role. It's a hands-on lead. You *have* done that job: for about two months after your manager resigned, you led three contractors day to day while still coding ([M1](13-Behavioral-Story-Bank.md#m1)). Don't apologize, and don't inflate it. Say what you have done, then show you have a deliberate approach.

**Framing line (memorize the shape, not the words):**
> "I haven't been a people manager, and from the description this is a hands-on lead role, which is the kind of leadership I've been doing. When my manager resigned, I led three contract engineers day to day for about two months while still writing the backend code. I own systems end to end, I write the specs other engineers build from, I onboarded more than ten data-engineering teams onto a new platform at Wayfair, and I set up the AI-assisted workflow my current team now uses for about 80% of its commits. For growing people, I have a specific approach, which I'll walk you through."

| What the role needs | Your evidence | Story |
|---|---|---|
| Set direction others execute | Wrote the Watt specs the frontend engineers implemented | [S3](13-Behavioral-Story-Bank.md#s3) |
| Teach at scale, drive adoption | Onboarded 10+ data-engineering teams to Composer and Dataform | [S10](13-Behavioral-Story-Bank.md#s10) |
| Raise the team's engineering practice | CLAUDE.md, code graph, domain knowledge base; AI-assisted commits 36% → 80% | [S6](13-Behavioral-Story-Bank.md#s6) |
| Push for quality with non-engineers | PnL reconciliation with the PM: 60+ discrepancies resolved, all 32 deals matched | [S8](13-Behavioral-Story-Bank.md#s8) |
| Learning culture after failure | Post-mortem Wizard: 25% more complete incident docs | [S12](13-Behavioral-Story-Bank.md#s12) |
| Lead engineers day to day while coding | Led 3 contractors on 3 projects for ~2 months after your manager resigned: end-of-day written handoffs, morning check-ins, PR reviews, pairing | [M1](13-Behavioral-Story-Bank.md#m1) |

**Avoid:** saying "I was their manager." Say "I led their work day to day," which is accurate. Also avoid saying "I mentored" without a specific example ready.

---

## Primer

### 1. Managing, mentoring, coaching, sponsoring: four different jobs

| Mode | What you do | What it sounds like | Example on an AI team |
|---|---|---|---|
| **Mentoring** | Share your experience and advice | "Here's how I'd approach it, and why." | Walk a junior through how you traced the 10× Snowflake cost spike to one query loop. |
| **Coaching** | Ask questions so *they* find the answer | "What have you tried? What would you check next?" | Junior says retrieval is bad. You ask: "How would you tell whether it's the chunking or the query?" |
| **Sponsoring** | Spend your credibility on their behalf | "Sam built this. They should present it to the PO." | Put a junior's name on the eval-harness demo to leadership. |
| **Managing** | Own performance, compensation, and hiring | Reviews, PIPs, promotions | Usually the manager's job. As tech lead you give input and evidence. |

A common shorthand: *a mentor talks **with** you, a coach talks **to** you, a sponsor talks **about** you.* Juniors need a lot of mentoring at first. Mid-level engineers need more coaching and sponsorship.

### 2. Situational Leadership (SLII): match your style to the person *and* the task

Blanchard's SLII model rates each person on each task by **competence** and **commitment**, then picks a style to match:

| Development level (per task) | Typical signs | Your style | What you actually do |
|---|---|---|---|
| **D1** Enthusiastic beginner: low competence, high commitment | New to RAG, excited | **S1 Directing** | Give a worked example, a checklist, and pair on the first one. |
| **D2** Disillusioned learner: some competence, low commitment | "Evals keep failing and I don't know why" | **S2 Coaching** | Still directive, plus lots of encouragement. Explain the why and ask questions. |
| **D3** Capable but cautious: high competence, variable commitment | Can do it but keeps checking with you | **S3 Supporting** | Stop giving answers. "What do you think? Go with it." |
| **D4** Self-reliant achiever | Owns it | **S4 Delegating** | Hand over the outcome, agree check-ins, stay out of the way. |

**The key insight to say in the interview:** development level is *per task, not per person*. A junior can be D4 on FastAPI endpoints and D1 on agent evaluation, so you delegate one and direct the other in the same week.

### 3. SBI(I): a feedback script that stays on facts

The Center for Creative Leadership's model, with the optional fourth step:

- **Situation:** when and where it happened.
- **Behavior:** what you observed, as an action and not a judgment.
- **Impact:** the effect on users, the team, or you.
- **Intent:** *ask* what they were going for, before you assume anything.

> "In Tuesday's release (**S**), the prompt change was merged without running the eval suite (**B**). Faithfulness dropped from 0.91 to 0.78 in staging, and the PO saw a wrong citation in the demo (**I**). Walk me through what happened. What were you aiming for? (**I**)"

Then agree on a next step together. For example: "Eval runs are now a CI gate. Can you add that check?"

### 4. GROW: a structure for coaching conversations

| Step | Purpose | Questions you ask |
|---|---|---|
| **G**oal | What do they want from this conversation or this quarter? | "What would a great outcome look like?" |
| **R**eality | Where are things now? | "What have you tried? What does the trace show? What's actually blocking you?" |
| **O**ptions | Generate choices *before* picking one | "What are three ways you could attack this? What would you do with no constraints?" |
| **W**ill / Way forward | Commit to a next step | "What will you do first, and by when? What do you need from me?" |

---

## Questions & answers

### Q1. How do you mentor junior engineers?  `[P0]`
**Say this first (~30 sec):** "I adapt to the person and the task, but the backbone stays the same: a clear growth goal, a weekly 1:1, work that stretches them one notch, and fast feedback through code review and pairing. Early on I'm directive, with pairing, worked examples, and checklists. As they show competence, I switch to asking questions and then to handing over whole problems. The goal is that within a few months they own a component end to end and can defend its trade-offs in a design review."

**If they dig deeper:**
- **Weekly 30-min 1:1 that belongs to them.** Their agenda comes first (template below), and I keep a shared running doc so nothing gets lost.
- **Stretch work sized one notch up:** add a tool to an existing agent → own a retrieval improvement measured on the eval set → own a new agent workflow.
- **Pairing 1–2× per week in month one, with the junior driving.** I narrate how I think: "I'm opening the trace first because…"
- **Code review is the main teaching channel.** I explain the why, label nits versus blocking issues, and link to docs (see Q5).
- **Make my own thinking visible.** I write design docs before code and have *them* review mine. Juniors learn a lot from critiquing a senior's doc.
- **Sponsor them.** They demo their work to the PO and stakeholders, not me.
- **How I know it's working:** better questions over time, fewer review rounds per PR, more blockers raised early, and eventually they can take an escalation alone.

**Your angle:** In [S6](13-Behavioral-Story-Bank.md#s6) you wrote a domain knowledge base (10 docs, ~100 sections) so context wasn't stuck in your head. The same instinct applies to people: write it down once and teach from it. [S10](13-Behavioral-Story-Bank.md#s10) is teaching at scale. Your one-on-one example is [M1](13-Behavioral-Story-Bank.md#m1): daily written instructions, morning check-ins, PR review, then pairing. `[fill in: one contractor from M1. What could they not do at the start that they could do at the end?]`

**Likely follow-ups:** "How much time per week does that take?" · "How do you know it's working?" · "Tell me about a mentee who struggled."

---

### Q2. Walk me through how you'd onboard a junior onto an AI/agent codebase.  `[P0]`
**Say this first:** "First real PR in week one, ownership of a small component by day 60, and a feature end to end with its eval by day 90. I front-load the context that's hard to pick up alone, like how the agent is wired, how we evaluate, and the PHI rules. Then the scope grows step by step."

**If they dig deeper: the 30/60/90 plan**

| When | Goal | Concrete activities |
|---|---|---|
| **Week 1** | Productive and safe | One-command local setup. Architecture walkthrough with me. Read the ADRs. Run the agent locally. **Read 10 real traces together** in LangSmith or Foundry tracing. PHI/HIPAA rules: what never goes in logs, prompts, or test fixtures. First PR: small, such as fixing a tool docstring or adding eval cases. |
| **Days 1–30** | Learn the inner loop: *change → run evals → read the diff → PR* | Turn 10–20 real (de-identified) failures into golden eval cases. Fix a bug found in traces. Pair twice a week. Learn the domain vocabulary: member, provider, claim, prior authorization, EOB. |
| **Days 31–60** | Own a component | For example, a new agent tool with input validation, unit tests, and eval cases. Or a chunking change measured by recall@k. Present it at the team knowledge-share. |
| **Days 61–90** | Own a feature | Write a 1–2 page design doc, get it reviewed, and ship behind a feature flag with a dashboard. Shadow the escalation or on-call rotation. |

**Artifacts I'd keep current:** a "How our agent works" doc, a domain glossary, an eval how-to, and a CLAUDE.md/AGENTS.md, so a junior's AI coding tools get the same context the junior does.

**Your angle:** [S1](13-Behavioral-Story-Bank.md#s1): you shipped an agent in 3 weeks, so you know which parts are hard to learn (semantic-view design, citation checks, building the eval set). [S6](13-Behavioral-Story-Bank.md#s6): you've already written the kind of context doc that cuts ramp-up time for people and AI tools alike.

**Likely follow-ups:** "What if they're behind at day 30?" · "How would you onboard someone strong in ML but new to production engineering, or the reverse?"

---

### Q3. How do you grow someone from junior to mid-level?  `[P0]`
**Say this first:** "The jump from junior to mid is mostly about scope and independence. It's going from 'implement this well-defined task' to 'here's a problem, figure out the approach and tell me the trade-offs.' So I deliberately widen what I hand them, I stop giving answers and start asking questions, and I make sure their growth is visible to whoever decides promotions."

**If they dig deeper:**
- **Name the gap concretely** against the company's career ladder (ask your manager for BCBSMA's). Pick 2–3 *behaviors*, not "be more senior." Example: "Independently designs a retrieval change, measures it, and presents trade-offs."
- **Write a growth plan together** (template below) and review it monthly.
- **Widen scope in steps:** task → feature → component ownership → cross-team problem.
- **Practice ambiguity:** give a vague problem, like "answers about out-of-network benefits are poor; find out why," and coach them through breaking it down using GROW.
- **Practice communication:** they write the design doc, present it in review, and send the update to the PO.
- **Keep evidence:** have them maintain a brag document (Julia Evans) so the promotion case writes itself. I sponsor by mentioning specific wins to their manager.

**Your angle:** Your own path at Wayfair went SE → SE II → SE III. `[fill in: what a lead or manager did that helped you level up]`. Then say: "what helped me most was X, so I do X for others." This is authentic and memorable.

**Likely follow-ups:** "Someone wants a promotion but isn't ready. What do you say?" Answer: honest gap, concrete evidence needed, a plan with a date. Don't overpromise.

---

### Q4. How do you give hard feedback?  `[P0]`
**Say this first:** "Early, privately, specific, and about behavior, not personality. I use situation, behavior, impact. Then I ask about their intent before I assume anything, and we agree on what happens next. I also give a lot of specific positive feedback the rest of the time, so the hard conversation isn't the only signal they ever get from me."

**If they dig deeper:**
- Use the SBI(I) script from the primer and say it out loud once.
- **Timing:** within a day or two, while it's fresh. Anything personal stays out of public channels and PR threads.
- **Care personally and challenge directly** (Radical Candor). The failure mode I watch for in myself is "ruinous empathy," meaning sitting on feedback to be nice.
- **Follow up:** check in the next week and *explicitly* acknowledge improvement.
- **If it repeats or is serious:** bring in their manager with documented, factual examples. That's fairer to them than letting it surface for the first time in a review.

**Your angle:** In [S8](13-Behavioral-Story-Bank.md#s8) you raised 60+ discrepancies with the PM and traders: written up, data-first, no blame. That's hard feedback sent upward and sideways. `[fill in: a time you gave or received difficult feedback and what changed]`

**Likely follow-ups:** "What if they get defensive?" Answer: pause, restate the impact, ask for their view, and focus on the next step. It's fine to continue the next day.

---

### Q5. A junior's PR is weak. How do you review it?  `[P0]`
**Say this first:** "I treat code review as my main teaching channel. First I check whether the approach is right. If it isn't, I'll get on a 15-minute call rather than leave 40 comments on code that should be structured differently. Then I separate blocking issues from nits, explain the why with a link, suggest rather than dictate, and call out what they did well."

**If they dig deeper:**
- **Google's standard:** approve once the change *improves overall code health*, even if it isn't perfect. Comments explain the reasoning. Label `Nit:`, `Optional:`, `FYI:`.
- **Review order:** design/approach → correctness and tests → AI and safety specifics (was the eval run? is the prompt versioned? tool permissions? PHI in logs?) → readability → nits.
- **Too big?** Ask them to split it, and teach small, focused changes.
- **Same mistake again?** Don't keep fixing it in comments. Pair once, then add it to the team checklist or a linter so the tooling catches it next time.
- **Turnaround within one business day.** Slow reviews kill a junior's momentum.
- **Sometimes let a non-critical, suboptimal choice through** and discuss it later. People learn more from owning a decision.

**Example comment (say it like this):**
> "**Blocking:** this retries the claims-lookup tool on *any* exception, including 4xx errors, so bad input will hammer the API. Suggest retrying only on timeouts and 5xx, with backoff. Happy to pair on it for 15 minutes. **Nice:** the Pydantic schema on the tool input is exactly right."

**Your angle:** In [S3](13-Behavioral-Story-Bank.md#s3) you wrote specs and then reviewed the frontend engineers' implementation against them. `[fill in: review norms you followed at Wayfair, such as PR templates or required reviewers]`

**Likely follow-ups:** "How do you review AI-generated PRs?" (see Q6) · "How do you keep reviews from becoming a bottleneck?"

---

### Q6. A junior over-relies on AI coding tools and ships code they don't understand. What do you do?  `[P0]`
**Say this first:** "I'm a big believer in AI-assisted development. On my current team I helped take us from 36% to 80% AI-assisted commits, so I'd never ban it. But the rule is that you own every line you submit, and if you can't explain it in review, it isn't ready. I coach that by asking them to walk me through the diff, and I set up guardrails that make good AI use the default."

**If they dig deeper:**
- **Norm:** the author is accountable. The PR description says how the change was verified, with tests and an eval run.
- **In review,** I ask "why this approach?" and "what happens if the tool returns nothing?" These aren't gotchas. They build the habit of reading AI output critically.
- **Teach a better workflow:** have the AI explain and plan before it writes code, work in small steps, write tests first, and read every diff. Using AI to *explain* unfamiliar code is a great learning accelerator.
- **Codebase context:** a CLAUDE.md/AGENTS.md with our conventions, so AI output fits our system instead of generic patterns.
- **Deliberate practice for juniors:** some work done hands-on, such as debugging a production trace or doing a design sketch, so the fundamentals still form.
- **Measure, don't assume.** METR's 2025 study found experienced open-source developers took about 19% *longer* with early-2025 AI tools, even though they believed they were faster. DORA's 2025 report calls AI an *amplifier* of a team's existing practices, good or bad.

**Your angle:** [S6](13-Behavioral-Story-Bank.md#s6) is exactly this story. `[fill in: what guardrails you set, how you measured "AI-assisted" (for example, Co-Authored-By trailers), and one problem you caught in review]`

**Likely follow-ups:** "How do you measure whether AI tools help?" Answer: cycle time, change-fail rate, review rounds, and escaped defects, never lines of code.

---

### Q7. How do you teach eval discipline and "prompts as code" to juniors?  `[P0]`
**Say this first:** "I make it part of the definition of done. Any change to a prompt, a model, a retrieval setting, or a tool runs against the eval set, and the PR shows before-and-after scores. Juniors learn it fastest by doing it. Their first tasks are adding eval cases from real failures and reading traces. Once they've watched a 'harmless' prompt tweak drop faithfulness, they never skip the evals again."

**If they dig deeper:**
- **Prompts live in the repo,** templated, versioned, and reviewed like code. No editing prompts live in a portal.
- **The eval set comes from real failures** (de-identified) and covers in-scope questions, out-of-scope questions that should be refused, adversarial and prompt-injection cases, and multi-turn memory cases.
- **Error-analysis habit (Hamel Husain):** read 20–50 traces, label the failure modes, count them, and fix the biggest bucket first.
- **Three kinds of checks:** deterministic (schema valid, citation present, SQL parses), LLM-as-judge (calibrated against human labels), and human review by SMEs for high-stakes cases.
- **CI gate:** evals run in the pipeline, and a regression past the threshold blocks the merge.
- **Ritual:** a weekly 30-minute **trace review** where the team reads failing traces together. It's the single best teaching session I know for AI engineering.

**Your angle:** [S1](13-Behavioral-Story-Bank.md#s1) had a 20-question eval set, citation checks, and per-turn cost tracking. [S2](13-Behavioral-Story-Bank.md#s2) had an LLM judge with a human-confirmation step. "I built these habits on my own projects. On a team I'd make them the default."

**Likely follow-ups:** "How big should the eval set be?" · "How do you keep it from going stale?" (Add every production failure, and review coverage monthly.) See also [07 · Evaluation](07-Evaluation-and-Observability.md).

---

### Q8. Someone on your team is underperforming. What do you do?  `[P0]`
**Say this first:** "First I figure out why, because the fix is different for each cause: unclear expectations, a skill gap, the wrong kind of work, or something going on outside work. I'd have a direct, private conversation with specific examples, write down clear expectations, give support and a short timeline, and check in weekly. If it doesn't improve, I partner with their manager. As tech lead I give honest input, but formal performance management is the manager's call."

**If they dig deeper:**
- **Diagnose in order:** expectations (did they know what good looks like?) → ability (skill gap: pairing, training) → motivation or fit → personal circumstances (be human, and point them to their manager or the EAP).
- **Check myself first:** did I set them up to fail with vague tickets, missing context, or oversized scope?
- **A concrete 30-day plan** with 2–3 measurable expectations. For example: PRs under ~400 lines, evals run on every prompt change, blockers raised within a day.
- **Document conversations factually.**
- **Don't route around them** by quietly taking their work. That hides the problem and stalls their growth.

**Your angle:** Be honest that you haven't run a formal PIP and that the tech lead partners with the manager on this. `[fill in: a time you helped a struggling teammate, or a team that struggled with the Composer migration (S10)]`

**Likely follow-ups:** "What if it's a senior engineer?" · "When would you escalate?" (When there's no change after the agreed timeline, or immediately for conduct or compliance issues.)

---

### Q9. How do you build psychological safety on a team?  `[P0]`
**Say this first:** "Mostly by modeling it. I admit my own mistakes out loud, in postmortems and in standup. I ask for critique of my own designs first. And I meet bad news with 'thanks for raising it' and curiosity, not blame. Google's research on team effectiveness found psychological safety mattered most of all, and on an AI team it matters even more, because you need people to flag weird model behavior early instead of hoping it goes away."

**If they dig deeper:**
- **Blameless postmortems** (Google SRE): focus on the system, not the person.
- **Design reviews:** ask quieter people first, and send a written pre-read so everyone can contribute, including people who think better in writing.
- **The lead says "I don't know, let's find out."**
- **Spikes are allowed to fail.** Exploration is judged by what we learned.
- **I take the heat** when the honest answer to a stakeholder is "this AI feature isn't ready."
- **Safety doesn't mean low standards.** High standards plus high safety is the learning zone.

**Your angle:** [S12](13-Behavioral-Story-Bank.md#s12): you improved the incident-postmortem tool, which shows you care about learning culture. [S8](13-Behavioral-Story-Bank.md#s8): data-first, no-blame discrepancy reviews.

**Likely follow-ups:** "How would you know your team lacks it?" Signs: silence in reviews, surprises found late, no questions in public channels, incidents found by users instead of engineers.

---

### Q10. How do you mentor when you're also coding 40–50% of the time?  `[P0]`
**Say this first:** "I build mentoring into the work instead of stacking it on top. Pairing and code review are already half the teaching, and design reviews are most of the rest. I protect two or three deep-work blocks a week for my own coding. And I choose coding work that doesn't block anyone, like prototypes, spikes, shared infrastructure, and hard fixes, rather than a critical-path feature a junior could grow on."

**If they dig deeper:**
- **Calendar shape:** deep work on, say, Mon/Wed/Thu mornings; 1:1s, reviews, and office hours in the afternoons.
- **Review SLA:** same or next day, done in batches.
- **Async first:** design docs, short recorded walkthroughs, and a Q&A channel. Answers I give twice become docs.
- **Scale myself:** CLAUDE.md, runbooks, and checklists cut down on repeated questions ([S6](13-Behavioral-Story-Bank.md#s6)).

**Your angle:** [M1](13-Behavioral-Story-Bank.md#m1) is this exact situation. For two months you coded all day, wrote each contractor's instructions at the end of the day, checked in on the way to work, and reviewed PRs and paired in the morning. [S14](13-Behavioral-Story-Bank.md#s14): as the sole engineer on five services plus a UI, you had to prioritize ruthlessly and document well.

**Likely follow-ups:** "What happens when you fall behind on your own work?" Answer: re-plan with the PO and drop my own scope before cutting 1:1s or reviews.

---

### Q11. How do you help engineers grow in a field that changes this fast?  `[P1]`
**Say this first:** "I teach durable fundamentals plus a method for evaluating new things, rather than chasing every release. Retrieval, evaluation, system design, and security don't change every month. For new models and frameworks, the team learns to run a bake-off on our own eval set instead of trusting benchmarks or social media."

**If they dig deeper:**
- **Protected learning time** each sprint, plus a rotating 15-minute "what's new and does it matter to us?" slot in the team meeting.
- **A monthly paper or blog club:** one person summarizes, and the team discusses whether it would help us.
- **Rotate spike ownership,** so juniors get to evaluate new tools using a template: problem, eval results, cost, risk, recommendation.
- **An internal tech radar** (adopt / trial / assess / hold), modeled on ThoughtWorks.
- **Certifications help** (such as Azure AI Engineer), but projects matter more.

**Your angle:** You moved from data platform work to applied AI in about a year by building things ([S1](13-Behavioral-Story-Bank.md#s1), [S2](13-Behavioral-Story-Bank.md#s2), [S4](13-Behavioral-Story-Bank.md#s4), [S5](13-Behavioral-Story-Bank.md#s5)). `[fill in: 3 sources you actually follow]`

---

### Q12. How do you run knowledge-sharing sessions?  `[P1]`
**Say this first:** "Short, regular, and tied to real work. My favorite formats are a weekly trace or incident review where we look at real failures together, demos where whoever built something presents it, and design reviews with written pre-reads. Everything gets written down so it outlives the meeting."

| Format | Cadence | Notes |
|---|---|---|
| Trace review | Weekly, 30 min | Pick 5 failing traces and label the failure modes. Fixes become eval cases. |
| Demo | Biweekly, 10–15 min each | The builder presents, not the lead. This doubles as sponsorship. |
| Design review | As needed | 1–2 page doc with a 48-hour pre-read. Decisions go into an ADR. |
| Lunch-and-learn | Monthly | Rotating presenter. Juniors present too. |
| Postmortem readout | After incidents | Blameless. Action items have owners. |

**Rules:** rotate presenters, record sessions, and turn at least one takeaway into a doc, checklist, or eval case each time.

**Your angle:** [S10](13-Behavioral-Story-Bank.md#s10) `[fill in: did you run office hours, workshops, or migration guides for the 10+ teams?]`. The in-app Knowledge Center on AMP ([S14](13-Behavioral-Story-Bank.md#s14)) and the domain KB ([S6](13-Behavioral-Story-Bank.md#s6)) are knowledge sharing built into the product and the codebase.

---

### Q13. Tell me about a time you mentored someone.  `[P0]`  *(scaffold to fill in)*
**Pick an example that has:** a real person, a specific starting gap, *your* concrete actions, a visible result, and something you learned.
**Use [M1](13-Behavioral-Story-Bank.md#m1):** leading three contractors for ~2 months after your manager resigned. To make it a *mentoring* story and not only a coordination story, focus on **one** of the three people and what changed for them. `[fill in: which contractor, their starting gap, and what they could do at the end]`

**STAR template:**
- **Situation:** "[Role] joined [team] from [background]. They were struggling with [specific gap]."
- **Task:** "I was their [onboarding buddy / tech lead on X]. The goal was for them to [own Y by Z]."
- **Action:** three specific things. For example: "I paired with them twice a week on…", "I changed my reviews to…", "I gave them ownership of…", "I had them present… to…"
- **Result:** "Afterward they [could do what]. [Metric or outcome.] Today they [where they are now]."
- **Learning:** "I learned to [ask before telling / size work smaller / give feedback sooner]."

**Avoid:** a story where you only answered questions, or one where you ended up doing the work for them.
**If you have no formal example,** use [S6](13-Behavioral-Story-Bank.md#s6) or [S10](13-Behavioral-Story-Bank.md#s10) as "mentoring at scale." But still prepare at least one one-on-one story, because the manager will likely ask for it.

---

### Q14. A senior engineer disagrees with your design. How do you handle it?  `[P0]`
**Say this first:** "I treat it as useful, because they've usually seen something I haven't. First I make sure I can state their position better than they can. Then we agree on the decision criteria, like latency, cost, risk, and team skills, *before* we argue options. If we're still split, we run a small spike or test both on the eval set and let the data decide. We record the decision and the dissent in an ADR. Once it's decided, we commit, and we revisit if the data changes."

**If they dig deeper:**
- **Two-way versus one-way doors:** move fast on reversible decisions and slow down on irreversible ones.
- **Time-box the debate.** Then disagree and commit.
- **If they were right, say so publicly.**
- **If it can't be resolved,** escalate *together* with a shared write-up, not separately.

**Your angle:** [S8](13-Behavioral-Story-Bank.md#s8): disagreements with the PM and traders were resolved with data (moving to a whole-month basis made all 32 deals match). `[fill in: a design disagreement you had, for example about the KEDA job service or the Kronos migration]`

---

### Q15. How do you delegate the interesting work instead of keeping it?  `[P0]`
**Say this first:** "I have to be deliberate, because the interesting work is exactly what grows people. My rule: if someone on the team can do it at 70–80% of my speed and would grow from it, it's theirs, and I support. I keep work that's urgent and only I can do, or a throwaway spike. And I delegate the whole problem, meaning the outcome and the why, not a task list."

**If they dig deeper:**
- **Delegate outcomes with context:** goal, constraints, definition of done, check-in points.
- **Match to development level:** in a new area, pair or direct first, then let go (SLII).
- **Don't redo their work.** Give feedback in review instead.
- **Make it visible:** they present it.

**Your angle:** Show self-awareness: "I've been the sole engineer on AMP for a year, so my natural risk is holding on too tight. My guard against that is X." Interviewers like this kind of honesty. [S3](13-Behavioral-Story-Bank.md#s3): you wrote the spec and let the frontend engineers own the implementation. In [M1](13-Behavioral-Story-Bank.md#m1) you handed the AMP UI work to a frontend engineer and kept the backend yourself.

---

### Q16. How would you describe your leadership style?  `[P0]`
**Say this first:** "Hands-on and teaching-focused. I lead by building alongside the team, setting clear standards, and explaining the reasons behind them. I adjust how directive I am per person and per task: very hands-on with someone new to an area, very hands-off with someone who owns it. And I care about making the team's work visible to the rest of the organization."

**Likely follow-ups:** "What would your teammates say is your weakness as a lead?" Have an honest one ready: `[fill in: for example, "I can over-own things after a year as a sole engineer; I now delegate deliberately by…"]`

---

### Q17. A junior is afraid to ask questions and stays stuck for days. What do you do?  `[P1]`
**Say this first:** "I make asking a team norm, not a personality test. We have a 'stuck rule': if you've been stuck for about an hour, post what you've tried in the team channel. I model it by asking questions publicly myself. And in 1:1s I ask *what* they're stuck on, not *whether* they're stuck."

**If they dig deeper:** praise good questions in public, pair them with a peer buddy as well as with me, and look at their PR timing to spot silent struggling early.

---

## Templates

### Weekly 1:1 agenda (30 min, their topics first)
```markdown
## 1:1 — <name> — <date>
**Their topics (first ~15 min):**
-
**Blockers / where I can help:**
-
**Feedback, both directions:**
- One thing going well (specific):
- One thing to adjust (SBI):
- "Anything I could do differently for you?"
**Growth (every 2–4 weeks):** progress on growth-plan focus area; next stretch opportunity
**Action items:** (owner · date)
```
**First 1:1 questions (from Lara Hogan):** How do you like to get feedback, in writing or in person, right away or later? What does a great week look like for you? What drains your energy? What are you hoping to grow in this year? How will I know if you're upset or frustrated?

### Growth plan (one page, reviewed monthly)
```markdown
# Growth plan — <name> — <quarter>
**Current → target:** e.g., Engineer I → Engineer II (per company ladder)
**Strengths to keep using:** ...

**Focus areas (max 3).** For each:
- Behavior we want to see: "Independently designs a retrieval change, measures it
  (recall@k + faithfulness), and presents the trade-offs."
- Opportunity: "Own chunking redesign for benefits PDFs (Nov)."
- Support from me: "Pair on eval harness week 1; review design doc."
- Evidence it's done: "Design doc approved; eval delta shown; demo to PO."

**Learning:** course / reading / shadowing
**Visibility:** where they'll present or write
**Check-ins:** monthly — <dates>
```

---

## Key terms

| Term | One-line meaning |
|---|---|
| SLII | Blanchard's Situational Leadership II: match directing, coaching, supporting, or delegating to a person's competence × commitment *on a task* |
| SBI / SBII | Situation, Behavior, Impact (+ Intent): CCL's feedback model |
| GROW | Goal, Reality, Options, Will: a structure for coaching conversations |
| Sponsorship | Using your influence to create visible opportunities for someone |
| Psychological safety | Shared belief that it's safe to take interpersonal risks on the team (top factor in Google's Project Aristotle) |
| Brag document | A running record of your accomplishments, kept for reviews and promotions |
| Blameless postmortem | Incident review that focuses on systems and contributing factors, not on blaming a person |

---

## References
- [Lara Hogan: Questions for our first 1:1](https://larahogan.me/blog/first-one-on-one-questions/): concrete first-1:1 questions; steal them.
- [Lara Hogan: What does sponsorship look like?](https://larahogan.me/blog/what-sponsorship-looks-like/): practical examples of sponsoring versus mentoring.
- [Lara Hogan: Resources](https://larahogan.me/resources/): feedback equation, 1:1 templates, manager tools.
- [Camille Fournier: *The Manager's Path* (O'Reilly)](https://www.oreilly.com/library/view/the-managers-path/9781491973882/): chapters on mentoring and tech lead are directly relevant.
- [StaffEng: Staff archetypes](https://staffeng.com/guides/staff-archetypes/): the "Tech Lead" archetype is basically this job.
- [StaffEng: Work on what matters](https://staffeng.com/guides/work-on-what-matters/): Will Larson on where senior engineers should spend their time.
- [CCL: Use Situation-Behavior-Impact (SBI) to understand intent](https://www.ccl.org/articles/leading-effectively-articles/closing-the-gap-between-intent-vs-impact-sbii/): the original SBI/SBII model.
- [GROW model (Wikipedia)](https://en.wikipedia.org/wiki/GROW_model): overview of the coaching framework.
- [Situational leadership theory (Wikipedia)](https://en.wikipedia.org/wiki/Situational_leadership_theory): Hersey–Blanchard and SLII development levels and styles.
- [Radical Candor: Our approach](https://www.radicalcandor.com/our-approach/): "care personally, challenge directly"; avoiding ruinous empathy.
- [Google Engineering Practices: Code review](https://google.github.io/eng-practices/review/): the standard most teams borrow.
- [Google: The standard of code review](https://google.github.io/eng-practices/review/reviewer/standard.html): "approve if it improves overall code health."
- [Google: How to write code review comments](https://google.github.io/eng-practices/review/reviewer/comments.html): explain why, label nits, be kind.
- [Google re:Work: Understand team effectiveness](https://rework.withgoogle.com/intl/en/guides/understand-team-effectiveness): Project Aristotle and psychological safety.
- [Google SRE Book: Postmortem culture](https://sre.google/sre-book/postmortem-culture/): how to run blameless postmortems.
- [Julia Evans: Get your work recognized: write a brag document](https://jvns.ca/blog/brag-documents/): give this to every junior.
- [Hamel Husain: Your AI product needs evals](https://hamel.dev/blog/posts/evals/): the error-analysis habit you teach juniors.
- [METR: Measuring the impact of early-2025 AI on experienced OSS developer productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/): why you measure AI-tool impact instead of assuming it.
- [DORA: State of AI-assisted Software Development 2025](https://dora.dev/research/2025/dora-report/): "AI is an amplifier" of existing team practices.
