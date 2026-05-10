from typing import Literal
from pydantic import BaseModel, Field


RiskLevel = Literal["low", "moderate", "high"]


class Entity(BaseModel):
    text: str
    label: str


class NlpContext(BaseModel):
    language: str = "unknown"
    intent: str = "general_support"
    retrieval_query: str
    suggested_filters: dict[str, str] = Field(default_factory=dict)
    entities: list[Entity] = Field(default_factory=list)
    risk_signals: list[str] = Field(default_factory=list)
    sentiment: str = "neutral"


class RiskAssessment(BaseModel):
    level: RiskLevel = "low"
    signals: list[str] = Field(default_factory=list)
    rationale: str = ""


class ConversationTurn(BaseModel):
    user_message: str
    assistant_message: str
    metadata: dict = Field(default_factory=dict)


class PatientProfile(BaseModel):
    facts: dict[str, str] = Field(default_factory=dict)


class PatientSession(BaseModel):
    session_id: str
    turns: list[ConversationTurn] = Field(default_factory=list)
    profile: PatientProfile = Field(default_factory=PatientProfile)

    def conversation_text(self) -> str:
        parts: list[str] = []
        for turn in self.turns:
            parts.append(f"User: {turn.user_message}")
            parts.append(f"Assistant: {turn.assistant_message}")
        return "\n".join(parts)

