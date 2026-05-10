from clinical_rag_agent.agents.crisis_agent import CrisisAgent
from clinical_rag_agent.agents.hallucination_guard_agent import HallucinationGuardAgent
from clinical_rag_agent.agents.judge_agent import JudgeAgent
from clinical_rag_agent.schemas.chat import ChatCompletionResult
from clinical_rag_agent.services.audit_log_service import AuditLogService
from clinical_rag_agent.services.graph_service import GraphService
from clinical_rag_agent.services.hallucination_service import HallucinationService
from clinical_rag_agent.services.llm_service import LLMService
from clinical_rag_agent.services.monitoring_service import MonitoringService
from clinical_rag_agent.services.nlp_service import NlpService
from clinical_rag_agent.services.rag_service import RagService
from clinical_rag_agent.services.safety_service import SafetyService
from clinical_rag_agent.services.session_service import SessionService


class AgentOrchestrator:
    def __init__(
        self,
        session_service: SessionService,
        nlp_service: NlpService,
        safety_service: SafetyService,
        rag_service: RagService,
        graph_service: GraphService,
        llm_service: LLMService,
        hallucination_service: HallucinationService,
        crisis_agent: CrisisAgent,
        hallucination_guard_agent: HallucinationGuardAgent,
        judge_agent: JudgeAgent,
        monitoring_service: MonitoringService,
        audit_log_service: AuditLogService,
    ):
        self.session_service = session_service
        self.nlp_service = nlp_service
        self.safety_service = safety_service
        self.rag_service = rag_service
        self.graph_service = graph_service
        self.llm_service = llm_service
        self.hallucination_service = hallucination_service
        self.crisis_agent = crisis_agent
        self.hallucination_guard_agent = hallucination_guard_agent
        self.judge_agent = judge_agent
        self.monitoring_service = monitoring_service
        self.audit_log_service = audit_log_service

    async def handle_clinical_chat(self, user_message: str, session_id: str) -> ChatCompletionResult:
        self.monitoring_service.increment("chat.requests")
        session = await self.session_service.get_session(session_id)
        nlp_context = await self.nlp_service.analyze_user_message(message=user_message, session=session)
        risk = await self.safety_service.assess_risk(message=user_message, nlp_context=nlp_context, session=session)

        if risk.level == "high":
            self.monitoring_service.increment("chat.crisis")
            draft = await self.crisis_agent.respond(user_message, session, risk)
            await self.session_service.save_turn(
                session_id=session_id,
                user_message=user_message,
                assistant_message=draft.visible_response,
                metadata={"risk": risk.model_dump(), "nlp": nlp_context.model_dump(), "agent": "crisis_agent"},
            )
            await self.audit_log_service.record("clinical_chat_crisis", {"session_id": session_id, "risk": risk.model_dump()})
            return ChatCompletionResult(text=draft.visible_response, citations=draft.citations, metadata=draft.metadata)

        retrieval_result = await self.rag_service.retrieve(
            query=nlp_context.retrieval_query,
            filters=nlp_context.suggested_filters,
        )
        graph_context = await self.graph_service.retrieve_clinical_context(entities=nlp_context.entities)
        draft = await self.llm_service.generate_clinical_response(
            user_message=user_message,
            session=session,
            nlp_context=nlp_context,
            rag_context=retrieval_result,
            graph_context=graph_context,
        )

        hallucination_report = await self.hallucination_service.validate(
            draft=draft,
            user_message=user_message,
            session=session,
            rag_context=retrieval_result,
            graph_context=graph_context,
        )
        if not hallucination_report.approved:
            self.monitoring_service.increment("chat.rewrites")
            draft = await self.hallucination_guard_agent.rewrite(
                draft=draft,
                report=hallucination_report,
                session=session,
                rag_context=retrieval_result,
            )
            hallucination_report = await self.hallucination_service.validate(
                draft=draft,
                user_message=user_message,
                session=session,
                rag_context=retrieval_result,
                graph_context=graph_context,
            )

        judge_report = await self.judge_agent.evaluate(
            draft=draft,
            session=session,
            risk=risk,
            hallucination_report=hallucination_report,
        )
        if not judge_report.approved:
            self.monitoring_service.increment("chat.fallbacks")
            draft = await self.hallucination_guard_agent.safe_fallback_response(
                user_message=user_message,
                judge_report=judge_report,
            )

        metadata = {
            "risk": risk.model_dump(),
            "nlp": nlp_context.model_dump(),
            "rag": retrieval_result.model_dump(),
            "graph": graph_context.model_dump(),
            "hallucination": hallucination_report.model_dump(),
            "judge": judge_report.model_dump(),
        }
        await self.session_service.save_turn(
            session_id=session_id,
            user_message=user_message,
            assistant_message=draft.visible_response,
            metadata=metadata,
        )
        await self.audit_log_service.record(
            "clinical_chat_completed",
            {
                "session_id": session_id,
                "risk_level": risk.level,
                "hallucination_score": hallucination_report.hallucination_score,
                "judge": judge_report.model_dump(),
            },
        )
        return ChatCompletionResult(text=draft.visible_response, citations=draft.citations, metadata=metadata)

