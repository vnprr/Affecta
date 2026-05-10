class SentimentAnalyzer:
    NEGATIVE = ("boję", "lęk", "przeraż", "smut", "panic", "afraid", "scared", "depressed")
    POSITIVE = ("dobrze", "spokoj", "ok", "better", "calm")

    def analyze(self, text: str) -> str:
        lower = text.lower()
        if any(token in lower for token in self.NEGATIVE):
            return "distressed"
        if any(token in lower for token in self.POSITIVE):
            return "positive"
        return "neutral"

