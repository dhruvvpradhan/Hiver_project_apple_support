# Hiver SDE Intern Take-Home — AI Support Agent for AppleSupport

## 1. Overview

This project builds an AI customer-support agent for **AppleSupport** using the Customer Support on Twitter (TWCS) dataset.

The agent has three responsibilities:

1. Classify an incoming customer message into one of 13 support intents.
2. Retrieve historically similar AppleSupport conversations and use them as evidence for drafting a response.
3. Decide whether the message should be auto-handled or escalated to a human, with an explicit reason.

The design intentionally favors **simplicity, auditability, and measurable failure modes** over a complex generative architecture.

> **Core idea:** A support agent should not only produce a plausible answer. It should know when its evidence and confidence are insufficient to safely handle the customer.

---

# 2. Problem framing

For AppleSupport, I define a good support agent as one that:

* correctly identifies the customer's primary problem,
* uses historically relevant AppleSupport interactions as grounding,
* produces a relevant and actionable response,
* avoids confidently answering when the evidence is weak,
* escalates ambiguous or risky cases to a human.

I deliberately chose **not** to build:

* a fully autonomous production support system,
* a large fine-tuned language model,
* a long-term customer memory system,
* tool/API integrations with Apple,
* automated account or device actions.

The assignment is primarily about demonstrating that the system can make **defensible support decisions**, not about building a production-scale customer service platform.

---

# 3. Dataset and brand selection

The primary dataset is the **Customer Support on Twitter** dataset from ThoughtVector.

I selected **AppleSupport** because it contains a sufficiently large number of customer-support interactions and covers a diverse set of technical, account, device, connectivity, purchasing, and service-related problems.

The raw dataset contains roughly 3M tweets. For development and evaluation, I use a subsample focused on AppleSupport rather than attempting to process the entire dataset during every experiment.

This is consistent with the assignment's expectation that a subsample is acceptable.

---

# 4. Intent taxonomy

I defined 13 intents directly from recurring AppleSupport customer-support themes.

| Intent                         | Description                                                                       |
| ------------------------------ | --------------------------------------------------------------------------------- |
| `ios_update_problem`           | Problems specifically involving iOS/macOS/watchOS updates                         |
| `battery_problem`              | Battery drain, charging, power, or battery-health problems                        |
| `device_performance_crash`     | Device-wide freezing, crashing, restarting, hanging, or severe lag                |
| `app_problem`                  | A problem primarily affecting a specific application                              |
| `keyboard_input_problem`       | Keyboard, typing, autocorrect, or text-input issues                               |
| `connectivity_problem`         | Wi-Fi, Bluetooth, cellular, or network connectivity problems                      |
| `messaging_facetime_problem`   | iMessage, SMS/Messages, or FaceTime problems                                      |
| `apple_id_account_problem`     | Apple ID, password, authentication, verification, or account-access problems      |
| `hardware_device_problem`      | Physical device damage or hardware failure                                        |
| `apple_watch_problem`          | Apple Watch/watchOS-specific problems                                             |
| `icloud_media_storage_problem` | iCloud, Photos, iCloud Drive, syncing, or storage problems                        |
| `purchase_order_billing`       | Purchases, orders, refunds, billing, payment, discounts, gift cards, or trade-ins |
| `other_unknown`                | Insufficient context, unsupported topics, or genuinely uncategorizable messages   |

### Annotation principles

I use a single primary intent per example.

Important rules include:

* **Symptom first:** when a message contains both a suspected cause and a symptom, classify primarily by the customer-facing symptom.
* **Specific app wins:** if one named app is malfunctioning, prefer `app_problem` over generic device performance.
* **System-wide problems:** multiple apps or device-wide freezing/crashing maps to `device_performance_crash`.
* **Apple Watch wins:** Watch-specific issues are classified as `apple_watch_problem`.
* **Hardware means physical failure/damage:** a generic black screen or freeze is not automatically considered hardware failure.
* **Context matters:** short follow-up messages are classified using available conversation context; otherwise they go to `other_unknown`.

---

# 5. System architecture

```text
Customer message
       │
       ▼
Intent classifier
(TF-IDF + Logistic Regression)
       │
       ▼
Confidence / risk gate
       │
       ├──────────────► Escalate to human
       │
       ▼
Historical case retrieval
       │
       ▼
Relevant AppleSupport response
       │
       ▼
Grounded response draft
       │
       ▼
Auto-handle / Escalate
```

The current implementation uses classical ML and retrieval rather than a large generative model.

This makes the system relatively easy to inspect and reproduce, while also giving clear places where a future LLM could be introduced.

---

# 6. Intent classification

## Baseline 1 — Majority classifier

The trivial baseline always predicts the most common intent in the evaluation set.

Results:

* Accuracy: **21.5%**
* Macro-F1: **2.7%**

This establishes that simply predicting the dominant category is not sufficient.

## Baseline 2 — TF-IDF + Logistic Regression

The simple learned classifier uses:

* TF-IDF features
* unigram and bigram features
* Logistic Regression
* AppleSupport customer messages for training

Results on the 200-example evaluation set:

| Metric      |     Score |
| ----------- | --------: |
| Accuracy    | **57.0%** |
| Macro-F1    | **52.8%** |
| Weighted-F1 | **58.5%** |

Per-intent F1:

| Intent                         |   F1 |
| ------------------------------ | ---: |
| `app_problem`                  | 0.56 |
| `apple_id_account_problem`     | 0.70 |
| `apple_watch_problem`          | 0.74 |
| `battery_problem`              | 0.74 |
| `connectivity_problem`         | 0.80 |
| `device_performance_crash`     | 0.49 |
| `hardware_device_problem`      | 0.00 |
| `icloud_media_storage_problem` | 0.36 |
| `ios_update_problem`           | 0.25 |
| `keyboard_input_problem`       | 0.77 |
| `messaging_facetime_problem`   | 0.22 |
| `other_unknown`                | 0.52 |
| `purchase_order_billing`       | 0.71 |

The large variation across intents is important: the aggregate 57% accuracy hides several weak categories.

---

# 7. Historical-response retrieval

The response component uses historical AppleSupport customer/response pairs.

For each incoming message, the system retrieves similar historical customer messages using TF-IDF cosine similarity.

The retrieval corpus contains approximately **104K AppleSupport customer/response pairs** after filtering and excluding evaluation examples.

For the 200-example evaluation set:

* Mean top-1 similarity: **0.344**
* Top-1 similarity ≥ 0.25: **75.0%**
* Top-1 similarity ≥ 0.30: **52.5%**
* Top-1 similarity ≥ 0.40: **19.5%**

These numbers are used as **retrieval diagnostics**, not as reply-quality scores.

A high similarity score does not automatically mean that the retrieved response is correct.

---

# 8. Escalation policy

The agent does not automatically answer every message.

It escalates when one or more of the following conditions hold:

* predicted intent is `other_unknown`,
* classifier confidence is below **0.55**,
* historical retrieval similarity is below **0.25**,
* the customer explicitly requests human/specialist support,
* the message contains high-risk safety cues.

Safety cues include examples such as:

* explosion,
* smoke,
* fire,
* sparking,
* swollen battery,
* injury,
* burn.

This creates a conservative fallback mechanism: **low confidence + weak evidence should result in human review rather than a fabricated answer.**

---

# 9. Golden evaluation set

I created a **200-example evaluation set** from AppleSupport customer messages.

The examples were sampled from the AppleSupport subset and annotated against the frozen 13-intent taxonomy.

The evaluation set was subsequently audited for consistency with the annotation rules.

Important caveat:

> The annotation process was AI-assisted and manually reviewable. The audited labels should not be described as fully independent human ground truth until the final manual review is completed.

The final submission should therefore treat this dataset as a carefully constructed evaluation set, with the labeling methodology documented explicitly.

---

# 10. Reply-quality evaluation

Reply quality is evaluated using six dimensions:

1. **Correctness**
2. **Relevance**
3. **Groundedness**
4. **Helpfulness**
5. **Tone**
6. **Actionability**

Each dimension uses a 1–5 scale.

### Rubric

**5 — Excellent:** correct, relevant, grounded in evidence, useful, appropriate in tone, and gives a clear next step.

**4 — Good:** generally correct and useful, with minor omissions or imperfections.

**3 — Acceptable:** partially useful but has meaningful weaknesses.

**2 — Poor:** substantial problems in correctness, grounding, relevance, or usefulness.

**1 — Unacceptable:** incorrect, misleading, irrelevant, or unsafe.

The evaluation harness contains a 60-example reply-quality sheet.

The first 10 examples were directly rated by the evaluator. The remaining 50 were initially populated with **AI-provisional ratings intended to match the evaluator's demonstrated rating style**.

These 50 ratings are explicitly marked as provisional and should be manually reviewed before being used as human-ground-truth evidence.

---

# 11. What is misleading about my headline number?

The headline **57.0% intent accuracy** is useful, but it is not a complete measure of support-agent quality.

There are several reasons.

### 1. Accuracy hides class imbalance

Some intents are substantially easier than others.

For example, connectivity and battery issues perform much better than messaging, iOS update, and hardware categories.

A single accuracy number therefore hides important weaknesses.

### 2. The evaluation set is relatively small

The golden set contains 200 examples.

That is large enough for useful directional evaluation, but still small enough that individual examples can materially change the headline number.

### 3. Intent accuracy is not the same as successful support

A correctly classified message can still receive a poor response.

Conversely, a message with an imperfect intent prediction may still receive a useful response through retrieval.

### 4. Retrieval similarity is not answer correctness

A retrieved historical response can look similar while being inappropriate for the exact customer situation.

Therefore, similarity thresholds should be treated as evidence quality signals rather than guarantees.

### 5. Historical support responses contain generic handoffs

Some AppleSupport responses are generic requests to continue the conversation through another support channel.

Retrieving such a response can technically be historically grounded while still providing little immediate value to the customer.

### 6. The current evaluation does not establish production safety

The escalation mechanism is intentionally conservative, but it has not been validated on a production traffic distribution.

The system should therefore be viewed as an evaluated prototype rather than a production-ready autonomous support agent.

---

# 12. Top failure modes

## Failure mode 1 — Ambiguous intent boundaries

Some messages contain multiple overlapping symptoms.

For example, a customer may describe an update problem together with battery drain or device freezing.

**Hypothesis:** the taxonomy is useful but the boundaries between symptom categories can still be ambiguous.

**Improvement:** introduce hierarchical classification or multi-label internal reasoning while retaining one final primary intent.

---

## Failure mode 2 — Weak performance on rare/underspecified intents

Hardware, messaging, iOS update, and iCloud-related categories show substantially weaker F1 than connectivity or battery.

**Hypothesis:** these categories have more linguistic variation and fewer distinctive lexical signals.

**Improvement:** add more targeted training examples and semantic embeddings.

---

## Failure mode 3 — Contextless follow-ups

Twitter conversations frequently contain short messages such as a continuation of an earlier conversation.

A message alone may not contain enough information to determine the intent.

**Hypothesis:** classification should operate over a conversation window rather than a single tweet.

**Improvement:** include previous customer/support turns in the classifier input.

---

## Failure mode 4 — Generic historical replies

Some retrieved historical responses are generic support handoffs.

**Hypothesis:** similarity retrieval optimizes textual similarity, not usefulness.

**Improvement:** rank historical responses using both semantic similarity and response usefulness, and explicitly down-rank generic handoffs.

---

## Failure mode 5 — Lexical retrieval limitations

TF-IDF retrieval performs well when customers use similar vocabulary but can miss semantically equivalent messages expressed differently.

**Hypothesis:** lexical similarity is a reasonable baseline but not sufficient for robust semantic retrieval.

**Improvement:** replace or augment TF-IDF with sentence embeddings and compare retrieval quality directly.

---

# 13. Evaluation harness

The evaluation directory contains:

* automated intent metrics,
* per-intent metrics,
* evaluation examples,
* reply-quality rubric,
* judge annotation sheet,
* stored evaluation results.

The intended evaluation progression is:

```text
Trivial baseline
      ↓
TF-IDF classifier
      ↓
Classifier + historical retrieval
      ↓
Reply-quality evaluation
      ↓
Human review of judge agreement
```

The most important future validation is measuring agreement between the LLM judge and human ratings.

That analysis should only be reported after sufficient examples have been independently reviewed by a human.

---

# 14. Decision log

## 1. Selected AppleSupport

AppleSupport has enough interactions and broad technical coverage to support meaningful intent discovery and historical-response retrieval.

## 2. Chose 13 intents

I wanted enough categories to represent meaningful support problems without creating a taxonomy so fine-grained that annotation becomes unreliable.

## 3. Used symptom-first classification

Customers care about the problem they experience, so the primary intent follows the observable support symptom rather than an uncertain underlying cause.

## 4. Kept `other_unknown`

Forcing every ambiguous message into a specific category would artificially inflate classification confidence.

## 5. Used classical ML as the main classifier

TF-IDF + Logistic Regression is fast, interpretable, reproducible, and provides a strong baseline for a small engineering take-home.

## 6. Added historical retrieval

The assignment specifically requires replies grounded in historical support behavior, so retrieval provides an explicit evidence layer.

## 7. Used similarity as a gating signal

A response should not be automatically generated when there is no sufficiently similar historical case.

## 8. Added explicit escalation rules

Low-confidence, ambiguous, human-requested, and safety-sensitive cases should have a human fallback.

## 9. Excluded evaluation examples from training/retrieval

This reduces direct leakage from the golden set into the evaluation process.

## 10. Evaluated per-intent F1

Aggregate accuracy alone hides which support categories are failing.

## 11. Used a six-dimensional reply rubric

Correctness alone is insufficient for customer support; relevance, grounding, helpfulness, tone, and actionability matter independently.

## 12. Separated retrieval quality from reply quality

Similarity is evidence quality, not proof that a final response is good.

## 13. Did not claim human–LLM judge agreement prematurely

The judge agreement requirement requires independent human ratings. Provisional model-generated ratings are clearly marked and are not presented as human evidence.

---

# 15. Reproducing the headline results

The repository is designed to reproduce the headline evaluation using the included evaluation artifacts and a manageable AppleSupport subsample rather than requiring the complete 3M-row dataset.

Reproduction

The repository includes a lightweight AppleSupport customer/support-pair sample and the frozen 200-example audited golden set. The full TWCS dataset is not included.

1. Install dependencies

From the repository root:

pip install pandas scikit-learn pyyaml
2. Run the agent
python -m src.hiver_agent.run \
  --pairs data/apple_support_pairs_sample.csv \
  --input data/golden_set_audit_review.csv \
  --output evaluation/reproduction_predictions.csv

This command runs the agent pipeline end-to-end:

Trains the TF-IDF + Logistic Regression intent classifier on the AppleSupport pair sample.
Predicts one of the 13 frozen intents for each golden-set example.
Retrieves similar historical AppleSupport cases using TF-IDF similarity.
Generates a response grounded in the retrieved historical support response.
Applies the confidence, similarity, human-request, and safety escalation rules.
Writes the resulting predictions to evaluation/reproduction_predictions.csv.
3. Verify the output

The generated file should contain one row for each example in the audited golden set, together with the predicted intent, confidence, retrieved evidence, drafted response, and escalation decision.

The repository also contains the previously generated evaluation artifacts:

evaluation/baseline_predictions.csv — TF-IDF + Logistic Regression baseline predictions.
evaluation/retrieval_baseline_top5.csv — top-5 historical retrieval results.
evaluation/agent_predictions.csv — agent evaluation predictions.
evaluation/evaluation_results.json — aggregate evaluation metrics.
evaluation/intent_metrics.csv — per-intent classification metrics.
Reference results

On the frozen 200-example audited golden set, the reported classifier results are:

Majority baseline: 21.5% accuracy / 2.7% macro-F1
TF-IDF + Logistic Regression: 57.0% accuracy / 52.8% macro-F1
Weighted-F1: 58.5%
Mean top-1 retrieval similarity: 0.344
Top-1 similarity ≥ 0.25: 75.0%
Agent escalation rate: 46.0%

These numbers are evaluation-set results and should not be interpreted as production automation rates.

Reproducibility and leakage

The audited golden-set examples are excluded from classifier training and historical retrieval. The included AppleSupport pair sample is provided to keep the reproduction lightweight and within the assignment's target runtime.

The audited golden set was AI-assisted with manual review/audit and is therefore treated as a curated evaluation set rather than independently annotated human ground truth.

# 16. One more week

With one additional week, I would prioritize:

### 1. Semantic retrieval

Replace TF-IDF retrieval with a sentence-embedding retriever and compare it directly against the lexical baseline.

### 2. Conversation-aware classification

Instead of classifying isolated tweets, include the preceding customer/support turns.

### 3. Better response selection

Rank retrieved responses using:

* semantic similarity,
* historical resolution usefulness,
* intent compatibility,
* generic-handoff penalties.

### 4. Proper LLM-judge validation

Have humans independently rate a sufficiently large sample, compare their ratings with the LLM judge, and report correlation and agreement.

### 5. Threshold calibration

Use a validation set to select confidence and retrieval thresholds based on the desired trade-off between:

* automation rate,
* incorrect auto-handling,
* escalation rate.

The goal would not simply be to maximize automation. It would be to maximize **safe automation**.

---

# 17. Final takeaway

The system demonstrates a complete support-agent loop:

**classify → retrieve evidence → draft → decide whether to handle or escalate**

The most important result is not that the classifier achieves 57% accuracy.

The more important finding is that **support quality depends on much more than intent accuracy**. Ambiguous conversations, weak historical evidence, generic handoffs, and uneven intent performance all affect whether an automated response should actually be trusted.

The architecture therefore treats **confidence, evidence, and escalation as first-class parts of the support system rather than adding them after the response generator.**
