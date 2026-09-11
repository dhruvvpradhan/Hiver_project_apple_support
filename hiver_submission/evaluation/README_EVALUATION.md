# Evaluation Harness

Evaluates the AppleSupport agent on the frozen 200-example golden set.

## Intent metrics
- Accuracy: 0.570
- Macro-F1: 0.528
- Weighted-F1: 0.585

See `intent_metrics.csv` for per-intent precision/recall/F1.

## Reply-quality rubric
Human/LLM ratings use 1–5 on:
1. Correctness
2. Relevance
3. Groundedness
4. Helpfulness
5. Tone
6. Actionability

`judge_60_annotation_sheet_completed.csv` contains 60 examples: 10 user-rated examples plus 50 AI-provisional ratings prepared for later human review. The provisional ratings are not human ground truth.

The `*_proxy` columns are automatic diagnostics only and must not be reported as human or LLM judge results.

## Judge agreement
After independent human annotation and LLM judging, compare the LLM judge with humans using:
- Spearman correlation for ordinal scores
- weighted Cohen's kappa for categorical agreement
- mean absolute error

## Evaluation discipline
The golden set stays frozen and is not used for model fitting or retrieval tuning.
