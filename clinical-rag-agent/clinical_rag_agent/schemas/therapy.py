from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


HypothesisConfidence = Literal["low", "medium", "high"]
HypothesisStatus = Literal[
    "new",
    "observed",
    "strengthening",
    "weakened",
    "confirmed_by_human",
    "rejected_by_human",
]
TherapyGoalStatus = Literal["active", "paused", "completed", "rejected"]
HumanReviewDecision = Literal["comment", "approve", "reject", "needs_attention"]
TherapyStage = Literal["intake", "early_sessions", "ongoing_work", "review"]
SessionMode = Literal[
    "intake",
    "exploration",
    "support",
    "stabilization",
    "pattern_reflection",
    "psychoeducation",
    "summary",
]


class TherapeuticHypothesis(BaseModel):
    id: str
    label: str
    description: str
    confidence: HypothesisConfidence
    evidence_from_conversation: list[str] = Field(default_factory=list)
    evidence_from_documents: list[str] = Field(default_factory=list)
    status: HypothesisStatus = "new"
    implications_for_session: list[str] = Field(default_factory=list)


class TherapyGoal(BaseModel):
    id: str
    title: str
    description: str
    status: TherapyGoalStatus = "active"
    evidence: list[str] = Field(default_factory=list)


class HumanReviewNote(BaseModel):
    id: str
    created_at: datetime
    note: str
    reviewer: str | None = None
    decision: HumanReviewDecision = "comment"


class TherapeuticCaseState(BaseModel):
    session_id: str
    session_count: int = 0
    current_stage: TherapyStage = "intake"
    presenting_problems: list[str] = Field(default_factory=list)
    current_emotional_state: list[str] = Field(default_factory=list)
    recurring_patterns: list[str] = Field(default_factory=list)
    relational_patterns: list[str] = Field(default_factory=list)
    cognitive_patterns: list[str] = Field(default_factory=list)
    behavioral_patterns: list[str] = Field(default_factory=list)
    working_hypotheses: list[TherapeuticHypothesis] = Field(default_factory=list)
    therapy_goals: list[TherapyGoal] = Field(default_factory=list)
    active_focus: str | None = None
    last_session_summary: str | None = None
    longitudinal_summary: str | None = None
    open_questions: list[str] = Field(default_factory=list)
    suggested_next_steps: list[str] = Field(default_factory=list)
    human_review_notes: list[HumanReviewNote] = Field(default_factory=list)


class TherapeuticProcessContext(BaseModel):
    session_mode: SessionMode
    therapeutic_focus: str
    response_strategy: str
    should_ask_question: bool
    question_goal: str | None = None
    should_use_rag: bool = False
    should_update_hypotheses: bool = True
    human_review_recommended: bool = False


class TherapyStateUpdate(BaseModel):
    new_presenting_problems: list[str] = Field(default_factory=list)
    new_emotional_states: list[str] = Field(default_factory=list)
    new_patterns: list[str] = Field(default_factory=list)
    new_relational_patterns: list[str] = Field(default_factory=list)
    new_cognitive_patterns: list[str] = Field(default_factory=list)
    new_behavioral_patterns: list[str] = Field(default_factory=list)
    new_hypotheses: list[TherapeuticHypothesis] = Field(default_factory=list)
    updated_active_focus: str | None = None
    summary_note: str | None = None
    longitudinal_summary_addition: str | None = None
    open_questions: list[str] = Field(default_factory=list)
    suggested_next_steps: list[str] = Field(default_factory=list)


class SessionNote(BaseModel):
    id: str
    session_id: str
    created_at: datetime
    user_message_excerpt: str
    assistant_response_excerpt: str
    summary: str
    therapeutic_significance: str | None = None
    key_emotions: list[str] = Field(default_factory=list)
    key_themes: list[str] = Field(default_factory=list)
    detected_patterns: list[str] = Field(default_factory=list)
    relational_material: list[str] = Field(default_factory=list)
    cognitive_material: list[str] = Field(default_factory=list)
    behavioral_material: list[str] = Field(default_factory=list)
    body_or_somatic_material: list[str] = Field(default_factory=list)
    session_mode: str | None = None
    therapeutic_focus: str | None = None
    response_strategy_used: str | None = None
    user_response_to_strategy: str | None = None
    open_threads: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    suggested_next_focus: str | None = None
    suggested_next_steps: list[str] = Field(default_factory=list)
    possible_hypothesis_updates: list[str] = Field(default_factory=list)
    hypothesis_evidence: list[str] = Field(default_factory=list)
    human_review_recommended: bool = False
    human_review_reason: str | None = None
    questions_for_human_reviewer: list[str] = Field(default_factory=list)
    source: Literal["deterministic", "llm", "mixed"] = "deterministic"
    metadata: dict = Field(default_factory=dict)


class PostSessionAnalysisResult(BaseModel):
    session_note: SessionNote
    therapy_state_update: TherapyStateUpdate
