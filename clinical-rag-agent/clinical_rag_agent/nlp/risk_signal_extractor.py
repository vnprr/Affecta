class RiskSignalExtractor:
    HIGH_RISK = (
        "chcę się zabić",
        "zabiję się",
        "popełnić samobójstwo",
        "mam plan samobójczy",
        "nie chcę żyć",
        "skrzywdzę siebie",
        "skrzywdzić siebie",
        "kill myself",
        "suicide plan",
        "want to die",
        "hurt myself",
    )
    MODERATE_RISK = (
        "myśli samobójcze",
        "samobój",
        "self harm",
        "cut myself",
        "bez sensu żyć",
        "nie mam po co żyć",
    )

    def extract(self, text: str) -> list[str]:
        lower = text.lower()
        signals = [token for token in self.HIGH_RISK if token in lower]
        signals.extend(token for token in self.MODERATE_RISK if token in lower and token not in signals)
        return signals

    def risk_level(self, text: str) -> str:
        lower = text.lower()
        if any(token in lower for token in self.HIGH_RISK):
            return "high"
        if any(token in lower for token in self.MODERATE_RISK):
            return "moderate"
        return "low"

