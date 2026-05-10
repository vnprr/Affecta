class GraphBuilder:
    def build_relations(self, entities: list[str]) -> list[dict[str, str]]:
        return [{"subject": entity, "relation": "observed_in_message", "object": "current_session"} for entity in entities]

