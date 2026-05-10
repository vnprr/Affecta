from clinical_rag_agent.nlp.evidence_alignment import EvidenceAlignment
from clinical_rag_agent.schemas.clinical import PatientSession
from clinical_rag_agent.schemas.hallucination import Claim
from clinical_rag_agent.schemas.rag import DocumentChunk, GraphContext, RetrievalResult


def test_evidence_alignment_supports_claim_from_retrieved_chunk():
    claim = Claim(
        id="claim_1",
        claim="Insomnia and racing thoughts can be associated with manic symptoms.",
        type="diagnostic_hypothesis",
        certainty="moderate",
        requires_citation=True,
    )
    rag = RetrievalResult(
        query="insomnia racing thoughts",
        chunks=[
            DocumentChunk(
                id="chunk_1",
                source="test",
                title="Mood symptoms",
                text="Insomnia and racing thoughts can be associated with manic or hypomanic symptoms.",
            )
        ],
    )

    report = EvidenceAlignment().check([claim], rag, GraphContext(), PatientSession(session_id="s1"))

    assert report.findings[0].supported is True
    assert report.findings[0].support_score > 0.5

