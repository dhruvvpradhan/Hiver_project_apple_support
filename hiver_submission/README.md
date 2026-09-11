# AppleSupport AI Support Agent — Hiver SDE Intern

## What this repo demonstrates

A reproducible baseline-to-agent pipeline for AppleSupport:
1. 13-class intent classification
2. historical-response retrieval
3. grounded response drafting
4. conservative escalation
5. frozen-golden evaluation

## Headline results

- Majority baseline: **21.5% accuracy / 2.7% macro-F1**
- TF-IDF + Logistic Regression: **57.0% accuracy / 52.8% macro-F1**
- Historical top-1 retrieval similarity >= 0.25: **75.0%**
- Conservative agent escalation rate: **46.0%**

These are evaluation-set results, not production automation rates.

## Run

Install dependencies:

```bash
pip install pandas scikit-learn pyyaml
```

Prepare a paired training CSV (`text_customer,text_apple`) from a documented TWCS subsample, then:

```bash
python -m src.hiver_agent.run   --pairs data/apple_support_pairs.csv   --input data/golden_set.csv   --output evaluation/agent_predictions.csv
```

The checked-in evaluation artifacts show the benchmark already run. Raw TWCS data is intentionally not included.

## Evaluation

See:
- `evaluation/README_EVALUATION.md`
- `evaluation/intent_metrics.csv`
- `evaluation/judge_60_annotation_sheet_completed.csv`
- `report/REPORT.md`
- `report/DECISION_LOG.md`

## Important caveat

The current golden set is **AI-assisted and audited**. It should not be called independently hand-labelled ground truth until a human reviewer completes/signs off the remaining review.

The 60-row reply-quality sheet contains 10 user-rated examples and 50 AI-provisional ratings designed for review. Human-vs-LLM agreement is **not claimed yet**; the provisional ratings must be reviewed and independently validated before reporting agreement.

## Data leakage discipline

The golden set must remain out of classifier training and retrieval indexes. The raw TWCS dataset should be supplied separately and only a documented subsample used for the <15 minute reproduction target.
