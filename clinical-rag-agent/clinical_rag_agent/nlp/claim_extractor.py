import re
from clinical_rag_agent.schemas.hallucination import Claim


class ClaimExtractor:
    DIAGNOSTIC = re.compile(r"\b(depresj|psychoz|schizofren|borderline|maniakal|mania|diagnos|diagnoz)", re.I)
    TREATMENT = re.compile(r"\b(leczen|terapi|lek|farmakolog|treatment|therapy|medication|plan leczenia)", re.I)
    RISK = re.compile(r"\b(samobój|self[- ]?harm|suicid|skrzywdz|hurt yourself)", re.I)
    SOURCE = re.compile(r"\[(?P<id>[a-zA-Z0-9_.:-]+)\]|źródł|source|citation", re.I)
    PATIENT_SPECIFIC = re.compile(r"\b(masz|cierpisz|doświadczyłeś|doświadczyłaś|you have|you experienced|your symptoms mean)\b", re.I)
    HIGH_CERTAINTY = re.compile(r"\b(na pewno|z pewnością|masz|cierpisz|oznacza|definitely|certainly|you have|you are)\b", re.I)
    MODERATE_CERTAINTY = re.compile(r"\b(może|mogą|sugeruje|wskazuje|may|might|could|suggests)\b", re.I)
    CITATION_ONLY = re.compile(r"^\s*(\[[a-zA-Z0-9_.:-]+\]\s*)+$")
    SAFETY_SCOPE = re.compile(
        r"(nie jest diagnoz|nie zastąpię diagnoz|nie mogę postawić diagnoz|"
        r"nie mam wystarczających|ocena specjalisty|wykwalifikowan\w+ specjalist|"
        r"qualified professional|not a diagnosis|not replace clinical care)",
        re.I,
    )

    def extract(self, text: str) -> list[Claim]:
        sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", text) if item.strip()]
        claims: list[Claim] = []
        for index, sentence in enumerate(sentences, start=1):
            claim_type = self._claim_type(sentence)
            if claim_type is None:
                continue
            certainty = "high" if self.HIGH_CERTAINTY.search(sentence) else "moderate" if self.MODERATE_CERTAINTY.search(sentence) else "low"
            requires_citation = claim_type in {
                "clinical_fact",
                "diagnostic_hypothesis",
                "treatment_recommendation",
                "risk_assessment",
                "source_reference",
            }
            claims.append(
                Claim(
                    id=f"claim_{index}",
                    claim=sentence,
                    type=claim_type,
                    certainty=certainty,
                    requires_citation=requires_citation,
                )
            )
        return claims

    def _claim_type(self, sentence: str) -> str | None:
        lower = sentence.lower()
        if self.CITATION_ONLY.match(sentence):
            return None
        if self.SAFETY_SCOPE.search(sentence):
            return "general_psychoeducation"
        if self.SOURCE.search(sentence):
            return "source_reference"
        if self.RISK.search(sentence):
            return "risk_assessment"
        if self.TREATMENT.search(sentence):
            return "treatment_recommendation"
        if self.DIAGNOSTIC.search(sentence):
            return "diagnostic_hypothesis"
        if self.PATIENT_SPECIFIC.search(sentence):
            return "patient_specific_inference"
        if any(token in lower for token in ("objaw", "symptom", "clinical", "klinicz")):
            return "clinical_fact"
        if any(token in lower for token in ("psychoeduk", "support", "wspar", "specjalist")):
            return "general_psychoeducation"
        return None
