# AppleSupport AI Support Agent — Hiver SDE Intern Take-Home

## 1. Problem framing

We build an AI support agent for AppleSupport using the Customer Support on Twitter (TWCS) dataset.

For each incoming customer message the system:
1. assigns one primary support intent from a frozen 13-class taxonomy;
2. retrieves historically similar AppleSupport conversations;
3. drafts a grounded response using historical support behavior;
4. decides whether to auto-handle or escalate to a human.

The design deliberately favors **groundedness and conservative escalation** over maximizing the apparent automation rate.

### Frozen taxonomy

- ios_update_problem
- battery_problem
- device_performance_crash
- app_problem
- keyboard_input_problem
- connectivity_problem
- messaging_facetime_problem
- apple_id_account_problem
- hardware_device_problem
- apple_watch_problem
- icloud_media_storage_problem
- purchase_order_billing
- other_unknown

The golden set contains 200 examples. It was AI-assisted and then audited; it should therefore be described as **AI-assisted annotation with manual review**, not independently hand-labelled ground truth unless a human completes the remaining review.

## 2. Headline results

| System | Accuracy | Macro-F1 |
|---|---:|---:|
| Majority baseline | 21.5% | 2.7% |
| TF-IDF + Logistic Regression | 57.0% | 52.8% |
| Retrieval baseline | — | — |
| Full conservative agent | 57.0% intent accuracy | 52.8% intent macro-F1 |

Historical retrieval produced a top-1 similarity >= 0.25 for 75.0% of golden examples. The agent escalated 46.0% of examples.

The retrieval baseline is evaluated primarily as a **grounding/evidence component**, rather than pretending that lexical similarity alone is a reply-quality metric.

## 3. Architecture

```text
customer message
      |
      v
TF-IDF + Logistic Regression
      |
      +---- intent + confidence
      |
      v
risk / confidence gate
      |
      v
TF-IDF historical retrieval
      |
      v
historical AppleSupport response evidence
      |
      v
grounded response draft
      |
      v
auto-handle / escalate
```

### Escalation policy

Escalate when:
- the predicted intent is `other_unknown`;
- classifier confidence is insufficient;
- no sufficiently similar historical evidence is available;
- the request is sensitive/high-risk;
- the customer explicitly asks for a human;
- the case appears to require an exception or account-specific action.

Auto-handle only when intent confidence, retrieval evidence and risk are acceptable.

## 4. Evaluation methodology

The golden set is frozen and excluded from model fitting and retrieval tuning.

Intent evaluation:
- accuracy
- macro-F1
- weighted-F1
- per-intent precision/recall/F1
- confusion matrix

Reply-quality rubric (1–5 each):
1. Correctness
2. Relevance
3. Groundedness
4. Helpfulness
5. Tone
6. Actionability

A 60-example reply-quality annotation sheet is included: 10 examples were rated by the user and 50 have AI-provisional ratings prepared for review. LLM-judge agreement should only be reported after independent human ratings are completed and compared. Recommended agreement statistics are Spearman correlation, weighted Cohen's kappa, and MAE.

## 5. Top failure modes and hypotheses

### 1. Ambiguous / context-only tweets
Very short messages such as version numbers, acknowledgements or follow-ups contain too little information for a reliable intent.

**Hypothesis:** conversation reconstruction should precede classification.

### 2. Multi-intent messages
A tweet can mention an update, battery, crash and connectivity in one message.

**Hypothesis:** a single-label taxonomy forces information loss. A future version should predict primary intent plus secondary tags.

### 3. System UI vs hardware ambiguity
Black screens, freezing, display behavior and button problems can be software or physical hardware.

**Hypothesis:** conversation context and troubleshooting history are needed before assigning hardware.

### 4. Specific app vs system-level symptoms
A named app can look like a general performance problem, while multiple apps suggest device-wide failure.

**Hypothesis:** explicit app/entity detection plus conversation-level context would improve routing.

### 5. Weak or generic historical evidence
Some AppleSupport responses are generic DM handoffs rather than substantive troubleshooting.

**Hypothesis:** retrieval needs response-quality filtering/reranking, not just customer-message similarity.

## 6. What is misleading about my headline number?

The 57.0% intent accuracy is useful but **not a measure of end-to-end support quality**.

It is measured on a small, stratified golden set whose class distribution was intentionally constructed, not sampled to represent production prevalence. It also evaluates a classifier trained using heuristic labels on the historical corpus, so the training labels are noisier than independently hand-labelled data.

Most importantly, a correct intent does not guarantee a good support response. Conversely, a conservative escalation can be operationally preferable to an incorrect auto-reply.

Therefore the honest headline is:

> **The simple classifier reaches 57% accuracy / 52.8 macro-F1 on the current audited golden set, while the system's real value depends on grounded response quality and safe escalation.**

## 7. Baseline interpretation

The majority classifier establishes the floor. TF-IDF + logistic regression substantially improves on that floor, showing that the taxonomy contains learnable lexical structure.

The remaining errors are concentrated in classes with overlapping vocabulary or insufficient context. This motivates conversation reconstruction, retrieval and confidence-aware escalation rather than simply making the classifier larger.

## 8. One-more-week plan

**Day 1–2:** reconstruct full conversation threads and train/evaluate on conversation windows rather than isolated tweets.

**Day 3:** replace TF-IDF with a sentence-embedding classifier and compare macro-F1.

**Day 4:** add hybrid retrieval: dense similarity + lexical similarity + intent match; filter generic DM-only responses.

**Day 5:** implement an LLM response generator constrained to retrieved evidence and explicit uncertainty.

**Day 6:** complete human-vs-LLM judge validation and optimize the escalation threshold for a target false-auto-handle rate.

**Day 7:** enlarge the golden set, audit disagreements, package reproducible scripts and run a clean end-to-end benchmark.

## 9. Reproducibility

The repository should expose one command that:
1. loads a documented AppleSupport subset;
2. builds training labels;
3. trains the simple classifier;
4. builds the retrieval index;
5. runs the agent;
6. evaluates on the frozen golden set;
7. writes metrics and predictions.

The full TWCS file is large; the submission should use a documented subsample so headline results can be reproduced within the assignment's 15-minute constraint.
