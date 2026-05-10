import pytest
from clinical_rag_agent.agents.crisis_agent import CrisisAgent
from clinical_rag_agent.schemas.clinical import PatientSession, RiskAssessment


@pytest.mark.asyncio
async def test_crisis_agent_prioritizes_immediate_safety():
    draft = await CrisisAgent().respond(
        "Chcę się zabić.",
        PatientSession(session_id="s1"),
        RiskAssessment(level="high", signals=["chcę się zabić"]),
    )

    assert "bezpieczeństwo" in draft.text.lower()
    assert "diagno" not in draft.text.lower()

