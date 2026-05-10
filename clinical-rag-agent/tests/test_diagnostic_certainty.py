from clinical_rag_agent.nlp.certainty_classifier import CertaintyClassifier


def test_certainty_classifier_blocks_overconfident_diagnosis():
    report = CertaintyClassifier().check("Masz depresję i to na pewno wyjaśnia wszystkie objawy.")

    assert report.overconfident_diagnoses

