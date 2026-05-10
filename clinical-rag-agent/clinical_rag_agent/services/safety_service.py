from clinical_rag_agent.nlp.risk_signal_extractor import RiskSignalExtractor
from clinical_rag_agent.schemas.clinical import NlpContext, PatientSession, RiskAssessment


class SafetyService:
    def __init__(self):
        self.risk_extractor = RiskSignalExtractor()

    async def assess_risk(self, message: str, nlp_context: NlpContext, session: PatientSession) -> RiskAssessment:
        del session
        level = self.risk_extractor.risk_level(message)
        signals = nlp_context.risk_signals or self.risk_extractor.extract(message)
        rationale = "High-risk crisis language detected." if level == "high" else "No immediate crisis language detected."
        if level == "moderate":
            rationale = "Self-harm related language detected without a direct imminent plan."
        return RiskAssessment(level=level, signals=signals, rationale=rationale)

