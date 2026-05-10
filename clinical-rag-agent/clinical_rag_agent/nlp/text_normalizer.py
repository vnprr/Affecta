import re
import unicodedata


class TextNormalizer:
    def normalize(self, text: str) -> str:
        text = unicodedata.normalize("NFKC", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

