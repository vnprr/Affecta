from typing import Literal
from pydantic import BaseModel, Field


ClaimType = Literal[
    "clinical_fact",
    "diagnostic_hypothesis",
    "treatment_recommendation",
    "patient_specific_inference",
    "risk_assessment",
    "source_reference",
    "general_psychoeducation",
]

Certainty = Literal["low", "moderate", "high"]


class Claim(BaseModel):
    id: str
    claim: str
    type: ClaimType
    certainty: Certainty = "low"
    requires_citation: bool = False


class EvidenceFinding(BaseModel):
    claim_id: str
    claim: str
    supported: bool
    support_score: float = 0.0
    reason: str = ""
    action: Literal["approve", "downgrade_or_remove", "remove", "ask_clarifying_question"] = "approve"


class EvidenceAlignmentReport(BaseModel):
    findings: list[EvidenceFinding] = Field(default_factory=list)

    @property
    def total_claims(self) -> int:
        return len(self.findings)


class CitationError(BaseModel):
    citation_id: str | None = None
    claim_id: str | None = None
    reason: str


class CitationVerificationReport(BaseModel):
    checked_citations: int = 0
    errors: list[CitationError] = Field(default_factory=list)


class Contradiction(BaseModel):
    contradiction: bool = True
    contradiction_type: str
    severity: Literal["low", "medium", "high"] = "medium"
    reason: str = ""


class ContradictionReport(BaseModel):
    contradictions: list[Contradiction] = Field(default_factory=list)


class CertaintyReport(BaseModel):
    overconfident_diagnoses: list[str] = Field(default_factory=list)


class DelusionReport(BaseModel):
    detected: bool = False
    problems: list[str] = Field(default_factory=list)


class UnsupportedInferenceReport(BaseModel):
    inferences: list[str] = Field(default_factory=list)


class HallucinationReport(BaseModel):
    approved: bool
    hallucination_score: float
    unsupported_claims: list[EvidenceFinding] = Field(default_factory=list)
    weakly_supported_claims: list[EvidenceFinding] = Field(default_factory=list)
    citation_errors: list[CitationError] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)
    overconfident_diagnoses: list[str] = Field(default_factory=list)
    delusion_validation_detected: bool = False
    unsupported_patient_inferences: list[str] = Field(default_factory=list)
    recommended_action: Literal[
        "approve",
        "rewrite",
        "remove_claims",
        "ask_clarifying_question",
        "force_human_review",
        "crisis_protocol",
    ]

    @classmethod
    def aggregate(
        cls,
        evidence_report: EvidenceAlignmentReport,
        citation_report: CitationVerificationReport,
        contradiction_report: ContradictionReport,
        certainty_report: CertaintyReport,
        delusion_report: DelusionReport,
        unsupported_report: UnsupportedInferenceReport,
    ) -> "HallucinationReport":
        total_claims = max(evidence_report.total_claims, 1)
        unsupported = [finding for finding in evidence_report.findings if not finding.supported]
        weak = [
            finding
            for finding in evidence_report.findings
            if finding.supported and 0 < finding.support_score < 0.45
        ]
        unsupported_claim_ratio = len(unsupported) / total_claims
        citation_error_ratio = len(citation_report.errors) / max(citation_report.checked_citations, 1)
        contradiction_score = 0.0
        if contradiction_report.contradictions:
            contradiction_score = max(
                1.0 if item.severity == "high" else 0.65 if item.severity == "medium" else 0.35
                for item in contradiction_report.contradictions
            )
        diagnostic_overconfidence_score = 1.0 if certainty_report.overconfident_diagnoses else 0.0
        unsupported_patient_inference_score = 1.0 if unsupported_report.inferences else 0.0
        weak_source_score = min(len(weak) / total_claims, 1.0)

        score = (
            0.30 * unsupported_claim_ratio
            + 0.20 * citation_error_ratio
            + 0.20 * contradiction_score
            + 0.15 * diagnostic_overconfidence_score
            + 0.10 * unsupported_patient_inference_score
            + 0.05 * weak_source_score
        )
        if delusion_report.detected:
            score = max(score, 0.41)

        if score <= 0.20:
            recommended_action = "approve"
        elif score <= 0.40:
            recommended_action = "rewrite"
        elif score <= 0.70:
            recommended_action = "ask_clarifying_question"
        else:
            recommended_action = "force_human_review"

        blocking_flags = (
            delusion_report.detected
            or bool(certainty_report.overconfident_diagnoses)
            or bool(unsupported_report.inferences)
            or any(item.severity == "high" for item in contradiction_report.contradictions)
        )
        approved = recommended_action == "approve" and not blocking_flags
        if blocking_flags and recommended_action == "approve":
            recommended_action = "rewrite"

        return cls(
            approved=approved,
            hallucination_score=round(min(score, 1.0), 4),
            unsupported_claims=unsupported,
            weakly_supported_claims=weak,
            citation_errors=citation_report.errors,
            contradictions=contradiction_report.contradictions,
            overconfident_diagnoses=certainty_report.overconfident_diagnoses,
            delusion_validation_detected=delusion_report.detected,
            unsupported_patient_inferences=unsupported_report.inferences,
            recommended_action=recommended_action,
        )

