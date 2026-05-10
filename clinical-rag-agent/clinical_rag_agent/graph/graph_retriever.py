from clinical_rag_agent.schemas.rag import GraphContext


class GraphRetriever:
    async def retrieve(self, entities: list[str]) -> GraphContext:
        return GraphContext(enabled=False, degraded=True, entities=entities)

