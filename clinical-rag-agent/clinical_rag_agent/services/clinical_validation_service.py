from clinical_rag_agent.services.hallucination_service import HallucinationService


class ClinicalValidationService:
    def __init__(self, hallucination_service: HallucinationService):
        self.hallucination_service = hallucination_service

