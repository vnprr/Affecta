from clinical_rag_agent.nlp.entity_extractor import EntityExtractor
from clinical_rag_agent.nlp.intent_classifier import IntentClassifier
from clinical_rag_agent.nlp.language_detector import LanguageDetector
from clinical_rag_agent.nlp.risk_signal_extractor import RiskSignalExtractor
from clinical_rag_agent.nlp.sentiment_analyzer import SentimentAnalyzer
from clinical_rag_agent.nlp.text_normalizer import TextNormalizer
from clinical_rag_agent.schemas.clinical import NlpContext, PatientSession


class NlpService:
    def __init__(self):
        self.normalizer = TextNormalizer()
        self.language_detector = LanguageDetector()
        self.intent_classifier = IntentClassifier()
        self.risk_extractor = RiskSignalExtractor()
        self.entity_extractor = EntityExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()

    async def analyze_user_message(self, message: str, session: PatientSession) -> NlpContext:
        normalized = self.normalizer.normalize(message)
        entities = self.entity_extractor.extract(normalized)
        entity_terms = " ".join(entity.text for entity in entities)
        session_hint = session.turns[-1].user_message if session.turns else ""
        retrieval_query = " ".join(part for part in [normalized, entity_terms, session_hint] if part).strip()
        return NlpContext(
            language=self.language_detector.detect(normalized),
            intent=self.intent_classifier.classify(normalized),
            retrieval_query=retrieval_query or normalized,
            suggested_filters={},
            entities=entities,
            risk_signals=self.risk_extractor.extract(normalized),
            sentiment=self.sentiment_analyzer.analyze(normalized),
        )

