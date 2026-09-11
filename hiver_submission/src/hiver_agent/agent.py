
from .escalation import decide
from .generator import draft_reply

class SupportAgent:
    def __init__(self, classifier, retriever):
        self.classifier=classifier
        self.retriever=retriever

    def run(self, text, explicit_human=False, risk=False):
        intent, confidence=self.classifier.predict_one(text)
        evidence=self.retriever.retrieve(text, k=5)
        escalate, reason=decide(intent, confidence, evidence, explicit_human, risk)
        reply=draft_reply(text,intent,evidence,escalate)
        return {"reply":reply,"intent":intent,"confidence":confidence,
                "escalate":escalate,"escalation_reason":reason,
                "evidence":evidence}
