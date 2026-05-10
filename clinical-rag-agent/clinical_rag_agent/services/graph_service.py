from clinical_rag_agent.schemas.clinical import Entity
from clinical_rag_agent.schemas.rag import GraphContext


class GraphService:
    async def retrieve_clinical_context(self, entities: list[Entity]) -> GraphContext:
        names = [entity.label for entity in entities]
        relations: list[dict[str, str]] = []
        if "delusional_belief" in names:
            relations.append(
                {
                    "subject": "distressing unverified belief",
                    "relation": "requires_response_style",
                    "object": "acknowledge distress without validating the belief",
                }
            )
        if "risk" in names:
            relations.append(
                {
                    "subject": "self-harm signal",
                    "relation": "requires",
                    "object": "crisis safety protocol",
                }
            )
        return GraphContext(
            enabled=False,
            degraded=True,
            entities=names,
            relations=relations,
            notes=["Neo4j adapter is not configured; using MVP degraded graph context."],
        )

