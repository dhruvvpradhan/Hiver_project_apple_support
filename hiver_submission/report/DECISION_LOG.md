# Decision Log

1. **Chose AppleSupport.** It has enough volume and clear recurring support themes for a focused single-brand study.
2. **Frozen 13-intent taxonomy.** We avoided endlessly expanding labels after exploratory inspection.
3. **One primary intent.** This makes the routing problem operationally simple and exposes multi-intent cases as a measurable failure mode.
4. **Symptom-first rule.** When cause and symptom coexist, route by the actionable customer problem.
5. **Specific app beats generic performance.** This prevents broad system labels from swallowing app-specific issues.
6. **Apple Watch is a dedicated intent.** Watch cases have distinct troubleshooting behavior.
7. **Unknown is explicit.** We prefer `other_unknown` over forcing weak evidence into an unrelated class.
8. **Golden set is frozen.** It must not become a tuning set.
9. **AI-assisted annotation with review.** Automated labels accelerate construction but are not treated as independent ground truth.
10. **TF-IDF + Logistic Regression baseline.** It is fast, transparent and strong enough to establish whether the taxonomy is learnable.
11. **Retrieval uses historical customer/response pairs.** Similar customer language is the most direct available evidence of historical resolution behavior.
12. **Conservative escalation.** Low confidence or weak evidence should go to a human rather than produce a fabricated confident answer.
13. **Reply quality is separate from intent accuracy.** A correct classifier can still produce an unsafe or unhelpful response.
14. **LLM judge requires validation.** Judge scores are not reported as authoritative until checked against human ratings.
15. **Headline metric is qualified.** The golden set is stratified and relatively small; accuracy must not be presented as production automation quality.
