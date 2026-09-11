
def decide(intent, confidence, evidence, explicit_human=False, risk=False,
           confidence_threshold=0.55, similarity_threshold=0.25):
    if explicit_human:
        return True, "customer requested human support"
    if risk:
        return True, "potentially sensitive/high-risk case"
    if intent=="other_unknown":
        return True, "intent is unknown or insufficiently specified"
    if confidence < confidence_threshold:
        return True, f"low intent confidence ({confidence:.2f})"
    if not evidence or evidence[0]["similarity"] < similarity_threshold:
        return True, "no sufficiently similar historical resolution"
    return False, None
