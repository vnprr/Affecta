class Tracer:
    def span(self, name: str):
        del name
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

