from pydantic import BaseModel, Field


class JudgeReport(BaseModel):
    approved: bool
    reasons: list[str] = Field(default_factory=list)
    recommended_action: str = "approve"

