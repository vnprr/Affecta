from dataclasses import dataclass
from clinical_rag_agent.agents.agent_orchestrator import AgentOrchestrator
from clinical_rag_agent.agents.crisis_agent import CrisisAgent
from clinical_rag_agent.agents.hallucination_guard_agent import HallucinationGuardAgent
from clinical_rag_agent.agents.judge_agent import JudgeAgent
from clinical_rag_agent.config import Settings
from clinical_rag_agent.services.audit_log_service import AuditLogService
from clinical_rag_agent.services.conversation_memory_service import ConversationMemoryService
from clinical_rag_agent.services.document_ingestion_service import DocumentIngestionService
from clinical_rag_agent.services.graph_service import GraphService
from clinical_rag_agent.services.hallucination_service import HallucinationService
from clinical_rag_agent.services.llm_service import LLMService
from clinical_rag_agent.services.monitoring_service import MonitoringService
from clinical_rag_agent.services.nlp_service import NlpService
from clinical_rag_agent.services.post_session_analysis_service import PostSessionAnalysisService
from clinical_rag_agent.services.rag_service import RagService
from clinical_rag_agent.services.safety_service import SafetyService
from clinical_rag_agent.services.session_note_service import SessionNoteService
from clinical_rag_agent.services.session_service import SessionService
from clinical_rag_agent.services.therapeutic_process_service import TherapeuticProcessService
from clinical_rag_agent.services.therapy_state_service import TherapyStateService


@dataclass
class AppContainer:
    settings: Settings
    session_service: SessionService
    nlp_service: NlpService
    safety_service: SafetyService
    rag_service: RagService
    graph_service: GraphService
    llm_service: LLMService
    hallucination_service: HallucinationService
    crisis_agent: CrisisAgent
    hallucination_guard_agent: HallucinationGuardAgent
    judge_agent: JudgeAgent
    monitoring_service: MonitoringService
    audit_log_service: AuditLogService
    document_ingestion_service: DocumentIngestionService
    conversation_memory_service: ConversationMemoryService
    therapy_state_service: TherapyStateService
    therapeutic_process_service: TherapeuticProcessService
    session_note_service: SessionNoteService
    post_session_analysis_service: PostSessionAnalysisService
    orchestrator: AgentOrchestrator


def create_container(settings: Settings) -> AppContainer:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    session_service = SessionService(settings.sessions_dir)
    nlp_service = NlpService()
    safety_service = SafetyService()
    rag_service = RagService(settings.rag_dir, max_chunks=settings.max_retrieval_chunks)
    graph_service = GraphService()
    llm_service = LLMService(settings)
    hallucination_service = HallucinationService()
    crisis_agent = CrisisAgent()
    hallucination_guard_agent = HallucinationGuardAgent()
    judge_agent = JudgeAgent()
    monitoring_service = MonitoringService()
    audit_log_service = AuditLogService(settings.data_dir)
    document_ingestion_service = DocumentIngestionService(rag_service)
    conversation_memory_service = ConversationMemoryService()
    therapy_state_service = TherapyStateService(settings.therapy_states_dir)
    therapeutic_process_service = TherapeuticProcessService()
    session_note_service = SessionNoteService(settings.session_notes_dir)
    post_session_analysis_service = PostSessionAnalysisService()
    orchestrator = AgentOrchestrator(
        session_service=session_service,
        therapy_state_service=therapy_state_service,
        therapeutic_process_service=therapeutic_process_service,
        conversation_memory_service=conversation_memory_service,
        session_note_service=session_note_service,
        post_session_analysis_service=post_session_analysis_service,
        nlp_service=nlp_service,
        safety_service=safety_service,
        rag_service=rag_service,
        graph_service=graph_service,
        llm_service=llm_service,
        hallucination_service=hallucination_service,
        crisis_agent=crisis_agent,
        hallucination_guard_agent=hallucination_guard_agent,
        judge_agent=judge_agent,
        monitoring_service=monitoring_service,
        audit_log_service=audit_log_service,
    )
    return AppContainer(
        settings=settings,
        session_service=session_service,
        nlp_service=nlp_service,
        safety_service=safety_service,
        rag_service=rag_service,
        graph_service=graph_service,
        llm_service=llm_service,
        hallucination_service=hallucination_service,
        crisis_agent=crisis_agent,
        hallucination_guard_agent=hallucination_guard_agent,
        judge_agent=judge_agent,
        monitoring_service=monitoring_service,
        audit_log_service=audit_log_service,
        document_ingestion_service=document_ingestion_service,
        conversation_memory_service=conversation_memory_service,
        therapy_state_service=therapy_state_service,
        therapeutic_process_service=therapeutic_process_service,
        session_note_service=session_note_service,
        post_session_analysis_service=post_session_analysis_service,
        orchestrator=orchestrator,
    )
