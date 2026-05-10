class LanguageDetector:
    POLISH_MARKERS = {"że", "nie", "jestem", "mam", "czuję", "myśli", "są", "może", "który"}

    def detect(self, text: str) -> str:
        lower = text.lower()
        if any(char in lower for char in "ąćęłńóśźż"):
            return "pl"
        words = set(lower.split())
        if words & self.POLISH_MARKERS:
            return "pl"
        return "en"

