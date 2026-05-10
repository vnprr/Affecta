class Neo4jClient:
    def __init__(self, uri: str | None = None):
        self.uri = uri

    @property
    def enabled(self) -> bool:
        return bool(self.uri)

