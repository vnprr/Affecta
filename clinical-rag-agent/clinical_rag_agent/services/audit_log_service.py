import json
from pathlib import Path


class AuditLogService:
    def __init__(self, data_dir: Path):
        self.path = data_dir / "audit" / "events.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def record(self, event: str, metadata: dict) -> None:
        sanitized = {key: value for key, value in metadata.items() if key not in {"user_message", "assistant_message"}}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"event": event, "metadata": sanitized}, ensure_ascii=False, default=str) + "\n")

