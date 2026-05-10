from clinical_rag_agent.nlp.claim_extractor import ClaimExtractor


def test_claim_extraction_detects_diagnostic_hypothesis():
    claims = ClaimExtractor().extract(
        "Bezsenność, gonitwa myśli i poczucie specjalnej misji mogą wskazywać na epizod maniakalny."
    )

    assert len(claims) == 1
    assert claims[0].type == "diagnostic_hypothesis"
    assert claims[0].certainty == "moderate"
    assert claims[0].requires_citation is True

