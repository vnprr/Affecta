from clinical_rag_agent.nlp.evidence_alignment import EvidenceAlignment
from clinical_rag_agent.schemas.hallucination import Claim, CitationError, CitationVerificationReport
from clinical_rag_agent.schemas.rag import RetrievalResult


class CitationVerifier:
    def __init__(self):
        self.alignment = EvidenceAlignment()

    def verify(
        self,
        claims: list[Claim],
        citations: list[str],
        rag_context: RetrievalResult,
    ) -> CitationVerificationReport:
        chunk_by_id = {chunk.id: chunk for chunk in rag_context.chunks}
        errors: list[CitationError] = []
        required_claims = [claim for claim in claims if claim.requires_citation]
        if required_claims and not citations:
            errors.extend(
                CitationError(claim_id=claim.id, reason="Claim requires citation but draft has no citations.")
                for claim in required_claims
            )
            return CitationVerificationReport(checked_citations=1, errors=errors)

        for citation_id in citations:
            if citation_id not in chunk_by_id:
                errors.append(CitationError(citation_id=citation_id, reason="Citation id is not present in retrieved evidence."))

        for claim in required_claims:
            if not any(
                citation_id in chunk_by_id and self.alignment._overlap(claim.claim, chunk_by_id[citation_id].text) >= 0.10
                for citation_id in citations
            ):
                errors.append(
                    CitationError(
                        claim_id=claim.id,
                        reason="No cited chunk directly supports this claim.",
                    )
                )
        return CitationVerificationReport(checked_citations=max(len(citations), len(required_claims), 1), errors=errors)

