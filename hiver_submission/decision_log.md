# Decision Log

## 1. Brand selection: AppleSupport
Selected AppleSupport because it has a large volume of customer-support interactions and covers diverse technical support issues, making it suitable for intent discovery, retrieval, and escalation experiments.

## 2. Frozen 13-intent taxonomy
I fixed the intent taxonomy before evaluating the model rather than continuously adding categories to improve results. This keeps the evaluation comparable and prevents taxonomy drift.

## 3. Symptom-first intent assignment
When a message contains multiple concepts, the primary intent is based on the main customer-facing symptom rather than incidental context.

## 4. Specific app vs. generic performance
A problem clearly tied to a specific app is classified as `app_problem`. Generic/system-wide slowness, crashing, freezing, or performance issues are classified as `device_performance_crash`.

## 5. Apple Watch gets a dedicated intent
Apple Watch issues are classified as `apple_watch_problem` when the watch is the primary subject, even when the underlying symptom could otherwise fit connectivity or hardware.

## 6. Physical hardware evidence required
`hardware_device_problem` is reserved for physical device damage or hardware-specific failure. Generic black screens, freezing, or crashes are not automatically treated as hardware failures.

## 7. Ambiguous cases use `other_unknown`
I prefer an explicit unknown category over forcing ambiguous customer messages into an incorrect specific intent.

## 8. Golden-set IDs excluded from baseline training
Examples used in the golden evaluation set are excluded from heuristic training data to reduce direct leakage between training and evaluation.

## 9. Two baselines
I compare against both a trivial majority-class baseline and a simple TF-IDF + Logistic Regression classifier. This distinguishes improvement over a naive strategy from improvement over a lightweight practical ML baseline.

## 10. TF-IDF retrieval for historical grounding
Historical support interactions are retrieved using TF-IDF similarity. This provides a simple, interpretable retrieval baseline without requiring a large embedding model or external API.

## 11. Retrieval is evidence, not a quality score
Similarity to a historical case is treated as evidence quality rather than proof that the generated answer is correct. A high lexical similarity score can still retrieve an inappropriate resolution.

## 12. Conservative escalation gate
The agent escalates when intent confidence is low, historical evidence is weak, the customer explicitly requests a human, the message is unknown, or safety-sensitive cues are present. The goal is to avoid confidently automating risky cases.

## 13. Human evaluation separated from automatic metrics
Intent accuracy/F1 and operational escalation metrics are reported separately from reply-quality evaluation. The reply-quality sheet uses a six-dimension rubric covering correctness, relevance, groundedness, helpfulness, tone, and actionability.

## 14. Provisional judge ratings are not claimed as independent human ground truth
The completed 60-row judge sheet contains the user's first 10 ratings plus AI-provisional ratings for the remaining examples. These ratings are clearly marked for later review and are not presented as independent human/LLM agreement evidence.

## 15. Headline-number caveat
The headline classification score is based on a 200-example golden set with AI-assisted annotation and manual-review intent. It should therefore be interpreted as an evaluation snapshot rather than a definitive estimate of production performance.
