from clinical_rag_agent.schemas.clinical import RiskAssessment


def should_use_crisis_protocol(risk: RiskAssessment) -> bool:
    return risk.level == "high"

