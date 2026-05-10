from clinical_rag_agent.nlp.citation_verifier import CitationVerifier
from clinical_rag_agent.schemas.hallucination import Claim
from clinical_rag_agent.schemas.rag import DocumentChunk, RetrievalResult


def test_citation_verification_accepts_supporting_chunk():
    claim = Claim(
        id="claim_1",
        claim="Treatment planning requires qualified clinical evaluation.",
        type="treatment_recommendation",
        certainty="low",
        requires_citation=True,
    )
    rag = RetrievalResult(
        query="treatment planning",
        chunks=[
            DocumentChunk(
                id="chunk_1",
                source="test",
                title="Treatment scope",
                text="Treatment planning requires qualified clinical evaluation and should not be replaced by automated advice.",
            )
        ],
    )

    report = CitationVerifier().verify([claim], ["chunk_1"], rag)

    assert report.errors == []


def test_citation_verification_rejects_missing_chunk():
    claim = Claim(id="claim_1", claim="Depression has many symptoms.", type="clinical_fact", requires_citation=True)
    report = CitationVerifier().verify([claim], ["missing"], RetrievalResult(query=""))

    assert report.errors

