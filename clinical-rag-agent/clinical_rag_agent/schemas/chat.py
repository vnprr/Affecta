from typing import Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: Any

    def text_content(self) -> str:
        if isinstance(self.content, str):
            return self.content
        if isinstance(self.content, list):
            parts: list[str] = []
            for item in self.content:
                if isinstance(item, dict):
                    if item.get("type") in {"text", "input_text"} and item.get("text"):
                        parts.append(str(item["text"]))
                    elif item.get("content"):
                        parts.append(str(item["content"]))
                else:
                    parts.append(str(item))
            return "\n".join(parts)
        return str(self.content)


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None
    metadata: dict[str, Any] | None = None


class ChatDraft(BaseModel):
    text: str
    citations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def visible_response(self) -> str:
        return self.text


class ChatCompletionResult(BaseModel):
    text: str
    citations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

