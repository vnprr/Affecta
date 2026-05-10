import pytest
from clinical_rag_agent.schemas.rag import DocumentInput
from clinical_rag_agent.services.rag_service import RagService


@pytest.mark.asyncio
async def test_rag_pipeline_retrieves_ingested_document(tmp_path):
    service = RagService(tmp_path / "rag")
    await service.ingest(
        [
            DocumentInput(
                source="unit_test",
                title="Manic symptoms",
                text="Insomnia and racing thoughts can be associated with manic symptoms.",
                metadata={"quality": "high"},
            )
        ]
    )

    result = await service.retrieve("racing thoughts insomnia")

    assert result.chunks
    assert any("racing thoughts" in chunk.text for chunk in result.chunks)

