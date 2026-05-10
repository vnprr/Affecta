from clinical_rag_agent.rag.embeddings import tokenize
from clinical_rag_agent.schemas.clinical import PatientSession
from clinical_rag_agent.schemas.hallucination import Claim, EvidenceAlignmentReport, EvidenceFinding
from clinical_rag_agent.schemas.rag import GraphContext, RetrievalResult


class EvidenceAlignment:
    def check(
        self,
        claims: list[Claim],
        rag_context: RetrievalResult,
        graph_context: GraphContext,
        session: PatientSession,
        user_message: str = "",
    ) -> EvidenceAlignmentReport:
        evidence_texts = [chunk.text for chunk in rag_context.chunks]
        evidence_texts.append(session.conversation_text())
        evidence_texts.append(user_message)
        evidence_texts.extend(" ".join(item.values()) for item in graph_context.relations)
        findings: list[EvidenceFinding] = []
        for claim in claims:
            score = max((self._overlap(claim.claim, evidence) for evidence in evidence_texts if evidence), default=0.0)
            if claim.type == "general_psychoeducation":
                supported = True
                score = max(score, 0.65)
            else:
                supported = score >= 0.12
            findings.append(
                EvidenceFinding(
                    claim_id=claim.id,
                    claim=claim.claim,
                    supported=supported,
                    support_score=round(score, 4),
                    reason="Claim has lexical grounding in evidence." if supported else "No retrieved, graph, or patient context support found.",
                    action="approve" if supported else "downgrade_or_remove",
                )
            )
        return EvidenceAlignmentReport(findings=findings)

    def _overlap(self, claim: str, evidence: str) -> float:
        claim_tokens = {token for token in tokenize(claim) if len(token) > 2}
        evidence_tokens = {token for token in tokenize(evidence) if len(token) > 2}
        if not claim_tokens or not evidence_tokens:
            return 0.0
        return len(claim_tokens & evidence_tokens) / len(claim_tokens)

