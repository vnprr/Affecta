class IntentClassifier:
    DIAGNOSTIC = ("diagno", "depres", "mania", "psycho", "schizofren", "borderline")
    TREATMENT = ("leczenie", "terapia", "lek", "treatment", "therapy", "medication", "plan")
    RAG = ("źród", "source", "citation", "badani", "evidence", "literature")

    def classify(self, text: str) -> str:
        lower = text.lower()
        if any(token in lower for token in self.TREATMENT):
            return "treatment_support"
        if any(token in lower for token in self.DIAGNOSTIC):
            return "diagnostic_hypothesis"
        if any(token in lower for token in self.RAG):
            return "evidence_question"
        return "general_support"

