class EntityLinker:
    def link(self, entity_label: str) -> str:
        return entity_label.lower().replace(" ", "_")

