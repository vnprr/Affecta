import re
from clinical_rag_agent.schemas.hallucination import CertaintyReport


class CertaintyClassifier:
    OVERCONFIDENT = (
        re.compile(r"\bmasz\s+(depresj\w*|psychoz\w*|schizofreni\w*|borderline)\b", re.I),
        re.compile(r"\bcierpisz\s+na\s+(depresj\w*|psychoz\w*|schizofreni\w*|borderline)\b", re.I),
        re.compile(r"\b(to\s+na\s+pewno|twoje\s+objawy\s+oznaczają)\b", re.I),
        re.compile(r"\byou\s+have\s+(depression|psychosis|schizophrenia|borderline)\b", re.I),
    )

    def check(self, text: str) -> CertaintyReport:
        matches: list[str] = []
        for pattern in self.OVERCONFIDENT:
            matches.extend(match.group(0) for match in pattern.finditer(text))
        return CertaintyReport(overconfident_diagnoses=matches)

