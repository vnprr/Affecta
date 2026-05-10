from pydantic import BaseModel, Field


class StoredSession(BaseModel):
    session_id: str
    turns: list[dict] = Field(default_factory=list)

