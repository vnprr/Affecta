from clinical_rag_agent.safety.forbidden_outputs import FORBIDDEN_DELUSION_VALIDATION, FORBIDDEN_DIAGNOSTIC_PHRASES


def contains_forbidden_output(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in FORBIDDEN_DIAGNOSTIC_PHRASES + FORBIDDEN_DELUSION_VALIDATION)

