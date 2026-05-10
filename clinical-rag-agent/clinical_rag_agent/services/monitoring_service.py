from collections import Counter


class MonitoringService:
    def __init__(self):
        self.counters: Counter[str] = Counter()

    def increment(self, name: str) -> None:
        self.counters[name] += 1

    def render_prometheus(self) -> str:
        lines = []
        for name, value in sorted(self.counters.items()):
            metric = name.replace(".", "_").replace("-", "_")
            lines.append(f"clinical_rag_{metric} {value}")
        return "\n".join(lines) + ("\n" if lines else "")

