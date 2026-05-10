from clinical_rag_agent.schemas.clinical import Entity


class EntityExtractor:
    KEYWORDS = {
        "sleep": ("bezsen", "sen", "insomnia", "sleep"),
        "mood": ("nastrój", "depres", "smutek", "mood", "sad"),
        "mania": ("gonitwa myśli", "mania", "grandio", "specjalna misja", "racing thoughts"),
        "delusional_belief": ("śledzą", "kontrolują", "sterują", "podsłuch", "control my thoughts", "watching me"),
        "risk": ("samobój", "zabić", "kill myself", "suicide"),
        "treatment": ("lek", "terapia", "leczenie", "therapy", "medication"),
    }

    def extract(self, text: str) -> list[Entity]:
        lower = text.lower()
        entities: list[Entity] = []
        for label, markers in self.KEYWORDS.items():
            for marker in markers:
                if marker in lower:
                    entities.append(Entity(text=marker, label=label))
                    break
        return entities

