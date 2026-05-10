from clinical_rag_agent.nlp.certainty_classifier import CertaintyClassifier
from clinical_rag_agent.nlp.citation_verifier import CitationVerifier
from clinical_rag_agent.nlp.claim_extractor import ClaimExtractor
from clinical_rag_agent.nlp.contradiction_detector import ContradictionDetector
from clinical_rag_agent.nlp.delusion_language_detector import DelusionLanguageDetector
from clinical_rag_agent.nlp.evidence_alignment import EvidenceAlignment
from clinical_rag_agent.nlp.unsupported_inference_detector import UnsupportedInferenceDetector
from clinical_rag_agent.schemas.chat import ChatDraft
from clinical_rag_agent.schemas.clinical import PatientSession
from clinical_rag_agent.schemas.hallucination import HallucinationReport
from clinical_rag_agent.schemas.rag import GraphContext, RetrievalResult


class HallucinationService:
    def __init__(
        self,
        claim_extractor: ClaimExtractor | None = None,
        evidence_alignment: EvidenceAlignment | None = None,
        citation_verifier: CitationVerifier | None = None,
        contradiction_detector: ContradictionDetector | None = None,
        certainty_classifier: CertaintyClassifier | None = None,
        delusion_language_detector: DelusionLanguageDetector | None = None,
        unsupported_inference_detector: UnsupportedInferenceDetector | None = None,
    ):
        self.claim_extractor = claim_extractor or ClaimExtractor()
        self.evidence_alignment = evidence_alignment or EvidenceAlignment()
        self.citation_verifier = citation_verifier or CitationVerifier()
        self.contradiction_detector = contradiction_detector or ContradictionDetector()
        self.certainty_classifier = certainty_classifier or CertaintyClassifier()
        self.delusion_language_detector = delusion_language_detector or DelusionLanguageDetector()
        self.unsupported_inference_detector = unsupported_inference_detector or UnsupportedInferenceDetector()

    async def validate(
        self,
        draft: ChatDraft,
        user_message: str,
        session: PatientSession,
        rag_context: RetrievalResult,
        graph_context: GraphContext,
    ) -> HallucinationReport:
        claims = self.claim_extractor.extract(draft.text)
        evidence_report = self.evidence_alignment.check(
            claims=claims,
            rag_context=rag_context,
            graph_context=graph_context,
            session=session,
            user_message=user_message,
        )
        citation_report = self.citation_verifier.verify(
            claims=claims,
            citations=draft.citations,
            rag_context=rag_context,
        )
        contradiction_report = self.contradiction_detector.check(
            draft=draft,
            session=session,
            rag_context=rag_context,
        )
        certainty_report = self.certainty_classifier.check(draft.text)
        delusion_report = self.delusion_language_detector.check(draft=draft, session=session)
        unsupported_report = self.unsupported_inference_detector.check(draft=draft, session=session)
        return HallucinationReport.aggregate(
            evidence_report,
            citation_report,
            contradiction_report,
            certainty_report,
            delusion_report,
            unsupported_report,
        )

