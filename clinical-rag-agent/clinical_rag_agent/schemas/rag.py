from pydantic import BaseModel, Field


class DocumentInput(BaseModel):
    source: str = "manual"
    title: str = "Untitled"
    text: str
    metadata: dict[str, str] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    id: str
    source: str
    title: str
    text: str
    metadata: dict[str, str] = Field(default_factory=dict)
    score: float = 0.0


class RetrievalResult(BaseModel):
    query: str
    chunks: list[DocumentChunk] = Field(default_factory=list)
    evidence_coverage: float = 0.0
    source_agreement: float = 0.0
    clinical_source_quality: str = "unknown"
    missing_evidence: list[str] = Field(default_factory=list)
    conflicting_evidence: list[str] = Field(default_factory=list)


class GraphContext(BaseModel):
    enabled: bool = False
    degraded: bool = True
    entities: list[str] = Field(default_factory=list)
    relations: list[dict[str, str]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

