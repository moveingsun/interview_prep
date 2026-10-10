# 10 · ML & MLOps Fundamentals

[← Index](00-Index.md) · **Manager-round priority:** Medium · **Read time:** ~40 min

> **Why this matters for this role:** The JD lists "8+ years of hands-on ML" with TensorFlow, PyTorch, and scikit-learn, plus MLOps and production model monitoring. (One version of the posting says 3–5+ years, so the bar is probably flexible.) This is your biggest gap on paper. The manager will likely probe it once. Your goal is to answer **honestly and fluently**, then steer to where you're strong: production AI systems, data quality, evaluation, reliability, and cost.

## Primer: how to talk about this gap

**What the JD says vs. what you bring**

| JD asks for | What you actually have | Honest framing |
|---|---|---|
| Years of hands-on ML/DL with TF/PyTorch/sklearn | 8+ yrs engineering; MS in Information Systems with an ML concentration; ~1+ yr shipping LLM/agent systems in production | "Engineering-first AI engineer. My depth is in getting AI systems into production and keeping them correct." |
| Production AI models and agents | Load Deal AI, Data Intelligence, the Data Validation LLM judge, the current memory + RAG service ([S1](13-Behavioral-Story-Bank.md#s1), [S2](13-Behavioral-Story-Bank.md#s2), [S4](13-Behavioral-Story-Bank.md#s4), [S5](13-Behavioral-Story-Bank.md#s5)) | A direct match. Lead with this. |
| MLOps tooling, Docker/K8s, CI/CD | AKS, KEDA, Docker, Terraform, Buildkite CI/CD, Databricks, Airflow/Composer, Kronos (2M jobs/week for data scientists) ([S11](13-Behavioral-Story-Bank.md#s11), [S14](13-Behavioral-Story-Bank.md#s14)) | A strong match. MLOps is mostly platform and data engineering. |
| Model monitoring and observability | Datadog/PagerDuty, SLO tooling, per-turn cost tracking, data validation service ([S2](13-Behavioral-Story-Bank.md#s2), [S12](13-Behavioral-Story-Bank.md#s12)) | A strong match. Drift monitoring is data-quality monitoring with statistics. |
| Training deep nets from scratch | Limited `[fill in honestly: coursework / side projects]` | Say so. Explain how you'd work with data scientists and when a trained model beats an LLM. |

**Rules**
- **Don't** claim you've trained or tuned deep-learning models in production if you haven't. A good manager will find out in two follow-up questions.
- **Do** show you know the fundamentals cold (this page), know *when* classical ML beats an LLM (Q2), and can run the production lifecycle (Q13–Q16).
- **Do** have one recent hands-on data point. **Suggested 2-hour exercise this weekend:** train a scikit-learn logistic regression and a gradient-boosted model on a public imbalanced dataset, such as the Kaggle credit-card fraud set or a CMS public-use file. Compare PR-AUC, pick a threshold, and track the runs in MLflow (Databricks has it built in). Then you can truthfully say "I recently did X to refresh my hands-on skills." **Only say it if you do it.**

## Questions & answers

### Q1. The JD asks for years of hands-on machine-learning experience. Walk me through your ML background.  `[P0]`
**Say this first (~30 sec):** "My path into AI is from the engineering side. I spent eight years building data platforms and production backends, and for the last year-plus I've been shipping LLM and agent systems: a Cortex and LangGraph assistant with an eval set and cost tracking, an LLM-judge validation service, and now a memory plus RAG service on Azure Foundry. Classical model training is the lighter part of my background. I have the fundamentals from my master's and I know when a trained model beats an LLM. Where I'm strongest is the part where most AI projects actually fail: data quality, evaluation, reliability, security, and cost in production."

**If they dig deeper:**
- Give concrete production evidence: the 20-question eval set, citation checks, the per-turn cost log ([S1](13-Behavioral-Story-Bank.md#s1)); the LLM judge separating timing races from real defects ([S2](13-Behavioral-Story-Bank.md#s2)); the semantic-view agent at 85.6s → 8.8s ([S4](13-Behavioral-Story-Bank.md#s4)).
- At Wayfair you built and ran the orchestration platform data scientists used (2M jobs/week) and migrated 10+ data teams to Composer ([S10](13-Behavioral-Story-Bank.md#s10), [S11](13-Behavioral-Story-Bank.md#s11)). You understand ML workloads from the platform side.
- For a trained-model problem on this team, you'd pair with the data scientists on modeling and own the pipeline, evaluation harness, serving, and monitoring.
- `[fill in: MS coursework/projects, e.g., the models you built in the ML concentration at Northeastern]`

**Your angle:** Frame it as "engineering-first AI engineer". The JD itself stresses "hands-on builder", production systems, monitoring, and evaluation, which is your profile.

**Likely follow-ups:** "Have you used PyTorch or TensorFlow?" (Answer factually: `[fill in]`. If it was only coursework, say so and describe what you'd need to ramp up on.) · "How would you mentor someone on modeling if that's not your strength?" (Pair them with the right expert, focus your mentoring on evaluation and production rigor, and learn alongside them.)

---

### Q2. When would you use a classical ML model instead of an LLM, or vice versa?  `[P0]`
**Say this first (~30 sec):** "For a prediction on structured, tabular data, like a member risk score, a fraud flag on a claim, or readmission risk, a gradient-boosted model or logistic regression usually wins. It's cheaper, runs in milliseconds, gives calibrated probabilities, is explainable, and validates with well-understood methods. LLMs win on *unstructured* language: clinical notes, faxes, call transcripts, policy documents, generation, and flexible extraction when you have no labeled data. Often the best design is a hybrid: the LLM extracts structured fields from text, and a classical model or rules engine makes the scored decision."

**If they dig deeper:**
- **Cost and latency:** a GBM scores millions of claims for almost nothing. An LLM call per claim adds cost and seconds of latency.
- **Explainability and regulation:** coverage-related decisions must be explainable and auditable. Feature attributions (SHAP) on a tabular model are far easier to defend than a free-text rationale.
- **Labels:** no labels → LLM zero/few-shot. With labels → train. A common middle path is **distillation**: an LLM labels a few thousand examples, humans spot-check them, and you train a small classifier for high-volume serving.
- **Determinism:** classical models give the same output for the same input, which helps with audits and tests.

**Your angle:** Your Data Validation service is already a hybrid. Deterministic checks (row/aggregate parity, nulls, freshness, schema) do the heavy lifting, and the LLM judge only classifies the ambiguous cases ([S2](13-Behavioral-Story-Bank.md#s2)). Use it as the example: "use the LLM where judgment is needed, not everywhere."

**Likely follow-ups:** "Give an example at a health plan." (Prior-auth intake: an LLM extracts diagnosis and procedure codes and clinical facts from faxed records. Rules plus a trained model triage them. A nurse reviewer makes the decision.)

---

### Q3. Explain precision vs recall. For a model that flags potentially fraudulent claims, which matters more?  `[P1]`
**Say this first (~30 sec):** "Precision is: of everything we flagged, how much was really fraud. Recall is: of all the real fraud, how much we caught. It depends on what happens after the flag. If flags go to a human investigation team, false positives cost investigator time and provider friction, so we usually maximize recall subject to a precision floor set by investigator capacity, often measured as precision in the top-K queue. If a flag ever directly delayed or denied payment, false positives would harm members, so I'd require human review and push precision much higher."

**If they dig deeper:**
- Precision = TP / (TP + FP). Recall = TP / (TP + FN). F1 is their harmonic mean, useful as a single number when both matter equally, which is rarely true in business.
- **The threshold is a business decision.** Show stakeholders the precision-recall curve and the cost of each error type, then choose the threshold together.
- Contrast with **care-management outreach** (finding high-risk members): missing someone (FN) is costly and an extra outreach call (FP) is cheap, so favor recall.
- For **LLM systems** the same idea applies: retrieval recall@k (did we fetch the right chunk?) vs answer precision (are claims supported?).

**Likely follow-ups:** "How would you pick the threshold?" (Use expected cost per error type, capacity constraints, and a validation set. Then revisit after launch, because base rates drift.)

---

### Q4. ROC-AUC vs PR-AUC: when does each mislead you?  `[P1]`
**Say this first (~30 sec):** "ROC-AUC measures how well the model *ranks* positives above negatives across all thresholds. With heavy class imbalance, say 0.5% fraud, it can look great while the model still produces mostly false positives at any practical threshold. PR-AUC focuses on the positive class, so it's the more honest metric for rare events. In practice I report PR-AUC plus precision and recall at the operating threshold we'd actually use."

**If they dig deeper:** ROC uses the false-positive *rate*, which stays small when negatives are huge, hiding many absolute false positives. Also check **calibration**: does a 0.8 score mean 80%? That matters when scores feed downstream decisions or prioritization.

---

### Q5. Supervised vs unsupervised vs self-supervised learning: give a health-plan example of each.  `[P1]`
**Say this first (~30 sec):** "Supervised learning needs labeled outcomes, for example predicting whether a claim will be denied, or 30-day readmission, from historical labeled data. Unsupervised learning finds structure without labels: clustering members into segments, or anomaly detection on provider billing patterns. Self-supervised learning makes labels from the data itself. That's how LLMs and embedding models are pre-trained, by predicting the next or a masked token."

**If they dig deeper:** Mention semi-supervised and weak supervision, such as LLM-generated labels reviewed by humans. Also note that clustering output needs a human to interpret the segments before anyone acts on them.

---

### Q6. How do you split data, and what is data leakage? Give a healthcare example.  `[P1]`
**Say this first (~30 sec):** "Train to fit, validation to tune, test touched once at the end for an honest estimate. Leakage is when information the model wouldn't have at prediction time sneaks into training, so offline metrics look great and production disappoints. In claims data the classic leaks are a feature recorded *after* the outcome, like a denial reason code; the same member's claims appearing in both train and test; and random splits on data that's really time-ordered."

**If they dig deeper:**
- **Split by time** for anything predictive: train on past months, test on later ones.
- **Group by entity** (member, provider) so the model can't memorize individuals. Use `GroupKFold` in scikit-learn.
- **Fit preprocessing only on training data.** Scalers, encoders, and imputers fit on the full set leak test statistics. Use sklearn `Pipeline`s.
- **Point-in-time correctness:** features must reflect what was known *as of* the prediction timestamp. This is a core reason feature stores exist (Q16).

**Your angle:** Your timezone/DST fix for OSI PI data and the "loads-through cutoff rule" in the PnL reconciliation ([S8](13-Behavioral-Story-Bank.md#s8)) are the same discipline: *as-of* correctness in time-series data.

---

### Q7. Explain the bias-variance trade-off and how you'd fix overfitting.  `[P1]`
**Say this first (~30 sec):** "Bias is error from a model too simple to capture the pattern: it underfits, and both training and validation error are high. Variance is error from a model so flexible it memorizes noise: it overfits, with low training error but high validation error. To fix overfitting: more or better data, regularization, a simpler model, early stopping, or fewer features. To fix underfitting: add capacity or better features, or regularize less. Learning curves tell you which problem you have."

**If they dig deeper:**
- **Regularization:** L2 shrinks weights, L1 drives some to zero (feature selection). For neural nets: dropout, weight decay, data augmentation, early stopping.
- In tree ensembles: limit depth, require a minimum number of samples per leaf, lower the learning rate and add more trees, subsample.
- The **LLM analogy**: a prompt overfit to your 10 favorite examples, or a fine-tune that overfits a small dataset and loses general ability.

---

### Q8. How do you handle a heavily imbalanced dataset?  `[P1]`
**Say this first (~30 sec):** "First, use the right metric, PR-AUC or recall at a precision floor, never plain accuracy. A model that says 'never fraud' is 99.5% accurate. Then, in rough order: stratified splits; class weights in the loss; tuning the decision threshold; and resampling (undersampling the majority or SMOTE), applied only inside the training folds. If positives are extremely rare, frame it as anomaly detection. The best fix is often getting more positive labels."

**If they dig deeper:** Resampling distorts predicted probabilities, so **recalibrate** afterward if scores are used as probabilities. `imbalanced-learn` integrates with scikit-learn pipelines.

---

### Q9. What is cross-validation and when do you use it?  `[P2]`
**Say this first (~30 sec):** "Split the training data into k folds, train on k−1, validate on the remaining one, rotate, and average. That gives a more reliable estimate than one split, especially with limited data, and it's the standard way to tune hyperparameters. Choose the variant that matches the data: stratified for imbalance, grouped when you have repeat entities like members, and forward-chaining time-series splits for temporal data."

**If they dig deeper:** It's expensive for large deep models, which usually use a single holdout. Keep a final untouched test set either way.

---

### Q10. Explain gradient descent, backpropagation, and the learning rate in plain English.  `[P1]`
**Say this first (~30 sec):** "Training means minimizing a loss, a number that measures how wrong the model is. The gradient tells you which direction to nudge every weight to reduce the loss, and gradient descent takes small steps in that direction, repeatedly, on mini-batches of data. Backpropagation is the efficient bookkeeping, the chain rule applied backward through the layers, that computes the gradient for millions or billions of weights at once. The learning rate is the step size. Too big and training diverges, too small and it crawls or gets stuck."

**If they dig deeper:** Adam/AdamW are the default optimizers. Learning-rate warmup and decay schedules are standard for transformers. An **epoch** is one pass over the data. When loss goes to NaN or spikes, check the learning rate, data issues, and exploding gradients (use gradient clipping).

---

### Q11. scikit-learn vs PyTorch vs TensorFlow: when would you use each?  `[P1]`
**Say this first (~30 sec):** "scikit-learn for classical ML on tabular data: fast baselines, pipelines, and evaluation utilities, often alongside XGBoost or LightGBM, which usually beat deep nets on tabular data. PyTorch for deep learning and almost all modern LLM work, since the Hugging Face ecosystem, fine-tuning, and research are PyTorch-first. TensorFlow/Keras mainly where an organization already has TF models and serving in production. Keras 3 can also run on multiple backends. For new deep-learning work I'd default to PyTorch."

**If they dig deeper:** For a team, choose what matches existing models, skills, and the serving platform, and standardize so code review and mentoring are easier. ONNX can bridge frameworks for serving.

**Likely follow-ups:** "Which have you used?" (Answer factually: `[fill in]`.)

---

### Q12. When is fine-tuning an LLM worth it? What are SFT, LoRA/QLoRA, and DPO, and what data do you need?  `[P1]`
**Say this first (~30 sec):** "It's worth it when prompting plus RAG have plateaued on a narrow, high-volume task with a clear quality bar. Typical reasons: you need a consistent format or behavior, or you want a smaller, cheaper, faster model to do what a big model does. Don't fine-tune to add knowledge that changes, which is RAG's job. SFT trains on input-to-ideal-output examples. LoRA and QLoRA make that cheap by training small adapters. DPO tunes behavior from 'preferred vs rejected' response pairs. You usually need hundreds to a few thousand *high-quality* examples, plus a held-out eval set to prove it beat the prompt baseline."

**If they dig deeper:**
- **Process:** baseline the best prompt and RAG on the eval set → curate data (quality over quantity, cover edge cases) → train → compare on the *same* eval → check for regressions on general behavior → deploy behind a flag.
- **Hidden costs:** hosting cost for fine-tuned deployments, retraining when the base model is retired, and data curation effort, which is usually the largest.
- **Healthcare risk:** models can memorize training data. De-identify PHI, govern the dataset, and document it (model card).
- Some platforms, including Azure in Foundry, also offer **reinforcement fine-tuning with graders** for reasoning tasks. Mention it as a newer option, not your default.

**Your angle:** You'd treat this as an eval-gated decision. The habit comes from Load Deal AI ([S1](13-Behavioral-Story-Bank.md#s1)): no change ships without beating the eval set.

**Likely follow-ups:** "Where would the training data come from?" (Reviewed production transcripts, human-corrected outputs, thumbs-up/down pairs for DPO, all de-identified and with access approved.)

---

### Q13. Walk me through taking a model from a notebook to production. What does good MLOps look like?  `[P0]`
**Say this first (~30 sec):** "Treat the model like any other production service, plus data. Version the code, data, and model together. Track every experiment so results are reproducible. Register the approved model with its lineage and evaluation. Deploy through CI/CD with automated gates: tests, data validation, and 'beats the current model on the eval set'. Roll out with shadow or canary. Then monitor inputs, outputs, latency, cost, and, once labels arrive, actual performance, with retraining triggers. For LLM apps it's the same loop, with prompts and retrieval config as the versioned artifacts."

**If they dig deeper:**
- **Lifecycle:** frame the problem and metric → data pipelines with quality checks → experiment tracking (MLflow: params, metrics, artifacts) → **model registry** (versions, aliases like `champion`/`challenger`, approvals) → CI/CD with eval gates → serving (batch or online endpoint) → monitoring and alerting → retraining → governance (model card, audit trail).
- Google's **MLOps maturity levels**: 0 = manual notebooks, 1 = automated training pipeline, 2 = automated CI/CD of the pipelines themselves.
- *Hidden Technical Debt in ML Systems* (Sculley et al.): the model is a small box. Most of the work and risk is in data dependencies, glue code, and configuration.

**Your angle:** This is your home turf. You built a distributed job-execution service with dependency DAGs and stuck-run recovery ([S14](13-Behavioral-Story-Bank.md#s14)), ran Kronos at 2M jobs/week ([S11](13-Behavioral-Story-Bank.md#s11)), cut CI/CD deploy time by 50% at Wayfair, and use Databricks, which has managed MLflow built in `[fill in: whether you've used MLflow there]`.

**Likely follow-ups:** "How do you test an ML pipeline?" (Unit tests on transforms, data contracts and validation on inputs, a model-quality gate against a baseline, and smoke tests on the deployed endpoint.)

---

### Q14. Batch vs real-time serving: how do you decide?  `[P1]`
**Say this first (~30 sec):** "If predictions can be computed ahead of time and slightly stale is fine, such as nightly risk scores for all members, batch is cheaper, simpler, and easier to monitor. If the prediction depends on information that only exists at request time, like a claim being submitted or a chat turn, you need real-time serving with latency SLOs, fresh features, and autoscaling. A hybrid is common: precompute the heavy parts in batch and compute the request-specific part online."

**If they dig deeper:** Watch for **training-serving skew**, where online features are computed differently than in training. Streaming (Kafka/Event Hubs) sits between the two for near-real-time needs.

**Your angle:** The AMP landing page went 20s → 5s by having Databricks jobs precompute results into Redis ([S14](13-Behavioral-Story-Bank.md#s14)). That's the batch-precompute serving pattern exactly.

---

### Q15. What's the difference between data drift and concept drift, and how do you monitor them?  `[P1]`
**Say this first (~30 sec):** "Data drift means the inputs change. New procedure codes, a new plan product, a shift in member demographics. Concept drift means the relationship between inputs and outcome changes, for example fraudsters adapting or a policy change altering what gets approved. In healthcare, labels often arrive weeks later after adjudication, so I monitor input and prediction distributions as early warnings, using PSI or KS tests per feature. Then I measure true performance when labels land, with alerts and retraining triggers on both."

**If they dig deeper:**
- Monitor **data quality** too: nulls, schema changes, freshness. Most "drift" incidents are really broken upstream pipelines.
- **For LLM apps:** query-mix drift (new topics), retrieval-quality drift (new docs not indexed), and model-version changes. Track eval scores on sampled production traffic.

**Your angle:** Your Data Validation Service already checks parity, nulls, freshness, and schema between ADF outputs and sources ([S2](13-Behavioral-Story-Bank.md#s2)). Say: "Drift monitoring is that same discipline with statistical tests added."

---

### Q16. What is a feature store and when do you actually need one?  `[P2]`
**Say this first (~30 sec):** "A feature store is a central, versioned catalog of features that serves the *same* feature values offline for training, with point-in-time correctness, and online for low-latency serving. It's worth it when several models share features, when you serve in real time and must avoid training-serving skew, or when leakage has bitten you. For a single batch model it's overkill. A well-modeled warehouse table does the job."

**If they dig deeper:** Examples are Databricks Feature Engineering in Unity Catalog, Feast (open source), SageMaker Feature Store, and Vertex AI Feature Store.

---

### Q17. Azure ML vs SageMaker vs Vertex AI: what's the difference, and which would you pick?  `[P2]`
**Say this first (~30 sec):** "They cover the same lifecycle: managed notebooks, training compute, pipelines, experiment tracking, a model registry, batch and online endpoints, and monitoring. The right choice is mostly the company's existing cloud, identity, networking, and data gravity, not the feature list. On Azure, Azure ML handles classical and custom models, and Microsoft Foundry handles the GenAI side: model catalog, agents, and evaluation."

**If they dig deeper:**
- **Azure ML:** workspaces, compute clusters, pipelines, MLflow-native tracking, registries, managed online/batch endpoints, Responsible AI dashboard.
- **SageMaker:** training jobs, Studio, Pipelines, Model Registry, endpoints, Model Monitor. Bedrock is AWS's GenAI equivalent.
- **Vertex AI:** Workbench, Pipelines (Kubeflow-based), Model Registry, endpoints, Model Monitoring, Model Garden/Gemini.
- You've used Azure (AKS, Foundry) and GCP (Composer, BigQuery) in production, plus Databricks.

**Likely follow-ups:** "What does BCBSMA use?" Turn it around and ask them ([14](14-Questions-to-Ask.md)).

---

### Q18. How do you make sure a model is fair and explainable in a healthcare setting?  `[P1]`
**Say this first (~30 sec):** "Measure performance by subgroup, not just overall: age, sex, geography, line of business, and race/ethnicity where the data is available and its use is approved. Watch for proxy variables. The well-known Obermeyer study found a widely used care-management algorithm under-served Black patients because it predicted *cost* as a proxy for *need*. Use explainability like SHAP for tabular models, document everything in a model card, and keep a human in the loop for any adverse decision affecting a member."

**If they dig deeper:** Fairness metrics can conflict, so the choice between, for example, equal opportunity and demographic parity is a governance decision, not a purely technical one. See [08](08-Security-Responsible-AI-and-HIPAA.md) for NIST AI RMF and regulatory context.

**Your angle:** Your fail-closed entitlements work ([S9](13-Behavioral-Story-Bank.md#s9)) and the "never writes without confirmation" judge ([S2](13-Behavioral-Story-Bank.md#s2)) show the same instinct: safe defaults when the system could harm someone.

## Key terms

| Term | One-liner |
|---|---|
| Precision / Recall | Of flagged, % correct / of actual positives, % caught |
| PR-AUC vs ROC-AUC | Positive-class focused (honest for rare events) / ranking across thresholds (optimistic under imbalance) |
| Leakage | Info unavailable at prediction time sneaking into training |
| Bias / Variance | Underfitting / overfitting error |
| Regularization | Penalizing complexity (L1, L2, dropout, early stopping) |
| Calibration | Whether predicted probabilities match observed frequencies |
| Data drift / Concept drift | Input distribution shift / input→outcome relationship shift |
| PSI | Population Stability Index, a common drift statistic |
| Model registry | Versioned store of approved models with lineage and stage/alias |
| Feature store | Consistent offline/online features with point-in-time correctness |
| SFT / LoRA / DPO | Supervised fine-tune / low-rank adapters / preference-pair tuning |

## References
- [Machine Learning Crash Course (Google)](https://developers.google.com/machine-learning/crash-course): the fastest structured refresher on fundamentals; do the classification and imbalanced-data modules.
- [Rules of Machine Learning (Martin Zinkevich, Google)](https://developers.google.com/machine-learning/guides/rules-of-ml): practical engineering wisdom for production ML.
- [scikit-learn: Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html): precision/recall, PR-AUC, and threshold tuning with code.
- [scikit-learn: Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html): stratified, grouped, and time-series splitters.
- [scikit-learn: Common pitfalls (data leakage)](https://scikit-learn.org/stable/common_pitfalls.html): the leakage examples to quote.
- [imbalanced-learn](https://imbalanced-learn.org/stable/): resampling techniques that plug into sklearn pipelines.
- [3Blue1Brown: Neural networks series](https://www.3blue1brown.com/topics/neural-networks): the best visual explanation of gradient descent and backprop.
- [A Recipe for Training Neural Networks (Karpathy)](https://karpathy.github.io/2019/04/25/recipe/): how practitioners actually debug training.
- [PyTorch: Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html): a one-evening hands-on tour if you want PyTorch talking points.
- [Hugging Face TRL (SFT, DPO trainers)](https://huggingface.co/docs/trl/index) · [Hugging Face PEFT (LoRA)](https://huggingface.co/docs/peft/index): the standard fine-tuning libraries.
- [Fine-tuning in Azure OpenAI (Foundry)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/fine-tuning): managed SFT/DPO/RFT on your stack, including hosting considerations.
- [MLflow documentation](https://mlflow.org/docs/latest/): experiment tracking, model registry, and GenAI tracing/evaluation.
- [MLflow on Databricks](https://docs.databricks.com/aws/en/mlflow/): managed MLflow in a tool you already use.
- [MLOps: Continuous delivery and automation pipelines in ML (Google Cloud)](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning): the MLOps maturity levels 0/1/2.
- [Hidden Technical Debt in Machine Learning Systems (Sculley et al., NeurIPS 2015)](https://papers.nips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html): why the model is the smallest part of the system.
- [Chip Huyen's books (*Designing ML Systems*, *AI Engineering*)](https://huyenchip.com/books/): the best end-to-end production-ML reading.
- [Azure Machine Learning overview](https://learn.microsoft.com/en-us/azure/machine-learning/overview-what-is-azure-machine-learning) · [Azure ML MLOps: model management & deployment](https://learn.microsoft.com/en-us/azure/machine-learning/concept-model-management-and-deployment): the Azure ML platform pages.
- [Amazon SageMaker overview](https://docs.aws.amazon.com/sagemaker/latest/dg/whatis.html) · [Vertex AI overview](https://cloud.google.com/vertex-ai/docs/start/introduction-unified-platform): the equivalents on AWS and GCP.
- [Data drift explained (Evidently AI)](https://www.evidentlyai.com/ml-in-production/data-drift): drift types and statistical tests in plain English.
- [Feast feature store docs](https://docs.feast.dev/): an open-source feature store, useful for the concept.
- [SHAP documentation](https://shap.readthedocs.io/): feature attributions for explainability.
- [Dissecting racial bias in an algorithm used to manage the health of populations (Obermeyer et al., *Science* 2019)](https://doi.org/10.1126/science.aax2342): the canonical health-plan fairness case.
