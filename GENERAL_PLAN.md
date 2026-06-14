Affecta — General Plan

0. Product Direction

Affecta is a psychological conversation application built around ongoing therapeutic-style sessions.

The core product is not a diagnostic chatbot, not a document Q&A tool, and not a clinical search engine.

The core product is:

A persistent therapeutic session agent that talks with the user over time, remembers what matters, notices emotional and relational patterns, builds a working understanding of the user’s difficulties, and gradually guides future sessions with support from background agents, retrieved knowledge, session summaries, and human review.

The user-facing experience should feel like speaking with one coherent therapeutic companion.

Behind that companion there is a system of agents and services that:

* analyzes conversations,
* stores important therapeutic material,
* builds case formulation,
* creates working hypotheses,
* proposes session direction,
* uses therapeutic knowledge from documents/RAG,
* prepares summaries for human review,
* supports human-in-the-loop supervision,
* validates response quality and consistency.

The main goal is to build a system that can conduct meaningful, goal-directed psychological sessions over time.

⸻

1. Main Architectural Principle

Affecta should be organized around one central path:

User
  ↓
Open WebUI / Frontend
  ↓
FastAPI Backend
  ↓
Therapeutic Session Orchestrator
  ↓
Affecta Therapist Agent
  ↓
Therapy State + Memory + Background Agents
  ↓
Validated response
  ↓
Stored session notes and updated therapeutic direction

The user talks to one main agent.

The system behind the main agent contains multiple specialized agents, but they should not fragment the user experience. Their job is to support the session, not to replace it.

⸻

2. Core Concept: Therapy Over Diagnosis

Affecta may detect clinical patterns and create working hypotheses, but its main purpose is not to immediately diagnose the user.

The system should distinguish between:

User-facing therapeutic work

The main agent:

* explores emotions,
* validates experience,
* asks meaningful questions,
* reflects patterns gently,
* tracks recurring themes,
* helps the user understand conflicts,
* supports emotional regulation,
* helps organize thoughts,
* returns to previous material,
* gives the session direction.

Internal clinical/therapeutic reasoning

Background agents may:

* detect possible patterns,
* create working hypotheses,
* compare the session with therapeutic frameworks,
* search relevant literature or documents,
* suggest session focus,
* recommend human review,
* prepare summaries.

Human-in-the-loop supervision

A human reviewer may:

* see summaries,
* see working hypotheses,
* accept/reject/modify direction,
* add recommendations,
* mark risks or priorities,
* guide the system’s future behavior.

The system should not expose raw internal hypotheses to the user unless the conversation context makes it appropriate.

Example:

Bad visible response:

You probably have borderline personality disorder.

Better internal hypothesis:

{
  "label": "borderline_traits_possible",
  "confidence": "low",
  "evidence": [
    "fear of abandonment",
    "intense relational distress",
    "rapid emotional shifts"
  ],
  "implications_for_session": [
    "use more validation",
    "track attachment triggers",
    "focus on emotion regulation",
    "avoid premature labeling"
  ]
}

Better visible response:

It sounds like the fear of being left becomes very intense very quickly, almost as if your whole body starts searching for certainty. Maybe we can slow down and look at the exact moment when that fear begins.

⸻

3. Current MVP Direction

The current MVP should focus on one working path:

Open WebUI
  ↓
clinical-rag-agent backend
  ↓
Therapeutic Session Agent
  ↓
Therapy State
  ↓
Conversation Memory
  ↓
Therapeutic Process Context
  ↓
RAG-assisted knowledge when needed
  ↓
Response validation
  ↓
Stored session turn + internal session note

The MVP should not focus first on:

* full Neo4j Graph RAG,
* OCR,
* PDF image processing,
* advanced dashboards,
* complex admin UI,
* large-scale vector databases,
* many independent agents talking to the user.

Those are later stages.

The immediate goal is to make the current single chatbot feel like a coherent ongoing therapeutic session agent.

⸻

4. Main User-Facing Agent

Affecta Therapist Agent

This is the main agent the user talks to.

Responsibilities:

* conduct ongoing therapeutic-style sessions,
* maintain continuity between turns and sessions,
* use previous summaries and therapy state,
* ask one meaningful question at a time,
* recognize the current therapeutic focus,
* reflect recurring patterns gently,
* support the user emotionally,
* help the user explore conflicts, needs, fears, relationships and behavior,
* use psychoeducation when useful,
* avoid turning every answer into a diagnostic report,
* avoid exposing internal metadata, agent names, or hidden hypotheses.

The agent should feel:

* warm,
* grounded,
* reflective,
* emotionally precise,
* focused,
* session-like,
* not generic,
* not encyclopedic.

The agent should not behave like:

* a search engine,
* a doctor writing a diagnosis,
* a crisis-only bot,
* a document Q&A bot,
* a purely clinical classifier.

⸻

5. Background Agents

Background agents support the session. They do not usually speak directly to the user.

5.1 Intake Agent

Purpose:

* understand why the user came,
* identify initial presenting problems,
* gather minimal context,
* define early therapeutic focus.

Outputs:

* presenting problems,
* initial emotional state,
* initial goals,
* missing context,
* recommended first-session direction.

5.2 Session Memory Agent

Purpose:

* extract important material from every turn,
* update long-term therapeutic memory,
* summarize key moments,
* detect repeated topics.

Outputs:

* session summary,
* longitudinal summary,
* key emotional moments,
* recurring topics,
* unresolved questions.

5.3 Therapeutic Process Agent

Purpose:

* decide what kind of response is needed now.

Possible modes:

* intake,
* support,
* stabilization,
* exploration,
* pattern reflection,
* psychoeducation,
* summary,
* goal review.

Outputs:

* session mode,
* therapeutic focus,
* response strategy,
* whether to ask a question,
* what the question should achieve,
* whether to use RAG,
* whether to update hypotheses.

5.4 Case Formulation Agent

Purpose:

* build an evolving map of the user’s difficulties.

It should track:

* presenting problems,
* emotional patterns,
* relational patterns,
* cognitive patterns,
* behavioral patterns,
* triggers,
* coping strategies,
* protective factors,
* therapy goals,
* unresolved conflicts.

Output:

* structured case formulation,
* current focus,
* missing information,
* candidate therapeutic directions.

5.5 Hypothesis Agent

Purpose:

* create and update working hypotheses.

Hypotheses may concern:

* depressive patterns,
* anxiety patterns,
* trauma-related patterns,
* attachment patterns,
* borderline-like traits,
* obsessive/compulsive patterns,
* avoidance,
* emotional dysregulation,
* interpersonal sensitivity,
* identity instability,
* grief,
* burnout,
* shame,
* self-criticism.

Important:

* hypotheses are not final diagnoses,
* hypotheses are internal guidance,
* confidence should start low,
* evidence must come from conversation, documents, or human review,
* hypotheses can be strengthened, weakened, confirmed by human, or rejected.

5.6 Therapy Plan Agent

Purpose:

* create direction for future sessions.

This is not a medical treatment plan.

It is a therapeutic work plan:

* what to explore,
* what patterns to track,
* what skills or reflections may help,
* what to return to next session,
* what to ask next,
* what the user may observe between sessions,
* what human reviewer should check.

Outputs:

* active goals,
* next-session focus,
* suggested interventions,
* psychoeducation topics,
* human review questions.

5.7 RAG Reasoning Agent

Purpose:

* retrieve therapeutic knowledge when needed.

RAG should support:

* psychoeducation,
* therapeutic frameworks,
* session direction,
* skill suggestions,
* evidence-informed explanations,
* internal planning.

RAG should not dominate normal emotional conversation.

The system should retrieve knowledge when:

* the user asks for explanation,
* the agent needs therapeutic framework support,
* a hypothesis needs background knowledge,
* Therapy Plan Agent needs direction,
* human summary should reference source material.

5.8 Document Analysis Agent

Purpose:

* analyze user-provided documents when available.

Documents may include:

* personal notes,
* questionnaires,
* mood logs,
* previous therapy notes,
* journal entries,
* clinical documents,
* uploaded PDFs.

The user should not be required to upload documents.

Documents are optional additional evidence.

5.9 Human Review Agent

Purpose:

* prepare material for human-in-the-loop supervision.

Outputs:

* summary for reviewer,
* key patterns,
* working hypotheses,
* therapy goals,
* suggested direction,
* concerns,
* questions for reviewer,
* recommended decisions.

Later this should connect to a human review panel.

5.10 Quality Guard / Judge Agent

Purpose:

* check whether the final response is coherent with the session, therapy state, and system direction.

It should detect:

* contradictions with user history,
* unsupported claims about the user,
* overly strong labels,
* sudden topic jumps,
* responses that ignore active focus,
* excessive psychoeducation,
* generic advice,
* inappropriate diagnostic certainty,
* exposure of internal hypotheses,
* response style mismatch.

This layer exists to improve quality, not to make the whole product revolve around diagnosis.

⸻

6. Services

Agents decide what should happen.

Services perform concrete operations.

Core services

services/
├── llm_service.py
├── session_service.py
├── therapy_state_service.py
├── conversation_memory_service.py
├── therapeutic_process_service.py
├── case_formulation_service.py
├── hypothesis_service.py
├── therapy_plan_service.py
├── rag_service.py
├── document_ingestion_service.py
├── human_review_service.py
├── nlp_service.py
├── safety_service.py
├── hallucination_service.py
├── judge_service.py
├── audit_log_service.py
└── monitoring_service.py

Service responsibilities

SessionService

* stores raw conversation turns,
* stores assistant responses,
* stores metadata per turn.

TherapyStateService

* stores persistent therapeutic state per session/user,
* loads and saves TherapeuticCaseState.

ConversationMemoryService

* builds recent context,
* builds longitudinal summary,
* extracts visible context for the main agent,
* extracts internal therapeutic material.

TherapeuticProcessService

* decides current session mode,
* chooses response strategy,
* decides whether to ask a question,
* decides whether RAG is needed.

CaseFormulationService

* updates formulation over time,
* tracks emotional/relational/cognitive/behavioral patterns.

HypothesisService

* creates working hypotheses,
* updates confidence,
* tracks evidence,
* marks human-confirmed or rejected hypotheses.

TherapyPlanService

* creates session direction,
* updates therapy goals,
* suggests next session focus.

RagService

* stores and retrieves therapeutic knowledge,
* retrieves document chunks,
* returns source material when needed.

HumanReviewService

* creates summaries for human review,
* stores human notes,
* applies human decisions to therapy state.

NlpService

* extracts entities, emotions, intents, risk signals, themes and possible patterns.

Quality/Judge/Hallucination Services

* validate consistency and quality of generated responses.

⸻

7. Data Model: Therapeutic Case State

The key new object is TherapeuticCaseState.

This is what turns the product from a simple chatbot into a session-based therapeutic system.

Example:

{
  "session_id": "session_123",
  "session_count": 4,
  "current_stage": "early_sessions",
  "presenting_problems": [
    "relationship anxiety",
    "fear of abandonment",
    "emotional overwhelm"
  ],
  "current_emotional_state": [
    "fear",
    "anger",
    "sadness"
  ],
  "recurring_patterns": [
    "compulsive checking when feeling abandoned",
    "rapid shift from longing to anger"
  ],
  "relational_patterns": [
    "intense need for reassurance",
    "fear of rejection"
  ],
  "cognitive_patterns": [
    "catastrophic interpretation of silence"
  ],
  "behavioral_patterns": [
    "checking phone repeatedly",
    "seeking reassurance"
  ],
  "working_hypotheses": [
    {
      "label": "attachment_anxiety",
      "confidence": "medium",
      "status": "observed"
    },
    {
      "label": "borderline_traits_possible",
      "confidence": "low",
      "status": "new"
    }
  ],
  "therapy_goals": [
    {
      "title": "Recognize abandonment triggers earlier",
      "status": "active"
    }
  ],
  "active_focus": "fear of abandonment in close relationships",
  "last_session_summary": "User described panic after delayed reply from partner.",
  "longitudinal_summary": "Across sessions user repeatedly describes intense relational fear, checking behavior and difficulty calming down after perceived distance.",
  "open_questions": [
    "What happens in the body before checking starts?",
    "What previous experiences shaped this fear?"
  ],
  "suggested_next_steps": [
    "Explore trigger sequence",
    "Introduce emotion naming",
    "Track reassurance-seeking loop"
  ]
}

⸻

8. Therapeutic Process Context

For each user message, the system should create a short process context.

Example:

{
  "session_mode": "pattern_reflection",
  "therapeutic_focus": "relationship abandonment trigger",
  "response_strategy": "validate emotion, reflect the recurring pattern gently, ask one question about the trigger sequence",
  "should_ask_question": true,
  "question_goal": "identify what appears first: thought, emotion, body sensation, or impulse",
  "should_use_rag": false,
  "should_update_hypotheses": true,
  "human_review_recommended": false
}

This object tells the main agent how to respond.

⸻

9. Main Runtime Workflow

1. User sends message.
2. SessionService loads raw session history.
3. TherapyStateService loads TherapeuticCaseState.
4. ConversationMemoryService builds recent and longitudinal context.
5. NlpService analyzes message:
   - intent,
   - emotions,
   - themes,
   - risk signals,
   - relationship markers,
   - possible patterns.
6. TherapeuticProcessService decides:
   - session mode,
   - active focus,
   - response strategy,
   - whether RAG is needed.
7. If needed, RagService retrieves therapeutic knowledge.
8. Affecta Therapist Agent generates visible response.
9. Quality/Judge layer checks:
   - response fits the session,
   - does not expose internal state,
   - does not over-label the user,
   - does not contradict stored memory,
   - follows the selected therapeutic strategy.
10. PostSessionAnalysis updates:
   - therapy state,
   - session summary,
   - patterns,
   - goals,
   - working hypotheses,
   - next steps.
11. SessionService saves raw turn + metadata.
12. TherapyStateService saves updated therapeutic state.
13. User receives only the visible therapeutic response.

⸻

10. Example Full Flow

User:

I keep checking my phone because I feel like she will leave me if she does not answer.

NLP detects:

{
  "emotions": ["fear", "panic"],
  "themes": ["relationship", "abandonment", "reassurance seeking"],
  "behaviors": ["checking phone"],
  "possible_patterns": ["attachment anxiety", "fear of abandonment"]
}

Therapeutic process context:

{
  "session_mode": "pattern_reflection",
  "therapeutic_focus": "fear of abandonment and checking behavior",
  "response_strategy": "validate emotion, slow down the moment, ask one question about the trigger sequence",
  "should_ask_question": true
}

Internal hypothesis update:

{
  "label": "attachment_anxiety",
  "confidence": "medium",
  "evidence_from_conversation": [
    "User fears being left when partner does not answer",
    "User checks phone repeatedly to reduce uncertainty"
  ],
  "implications_for_session": [
    "track trigger sequence",
    "work on tolerating uncertainty",
    "focus on emotion regulation before interpretation"
  ]
}

Visible response:

That sounds like a moment where fear becomes almost unbearable, and checking the phone gives you a short feeling of control. Let’s slow it down a little: what appears first in that moment — the thought that she will leave, the feeling in your body, or the impulse to check?

⸻

11. Human-in-the-Loop Roadmap

Human review should be introduced gradually.

Stage 1 — Internal summaries only

After each session, generate:

{
  "summary_for_human": "...",
  "key_emotional_patterns": [],
  "working_hypotheses": [],
  "therapy_goals": [],
  "suggested_next_focus": [],
  "needs_review": false,
  "questions_for_human": []
}

Stage 2 — API endpoints

Add:

GET /api/sessions/{session_id}/therapy-state
GET /api/sessions/{session_id}/human-summary
POST /api/sessions/{session_id}/human-review-note
POST /api/sessions/{session_id}/human-decision

Stage 3 — Simple human review panel

Human reviewer can:

* read summaries,
* see working hypotheses,
* accept/reject a hypothesis,
* add notes,
* set next focus,
* mark a session as needing attention.

Stage 4 — Human-guided therapy direction

Human decisions influence future sessions:

* confirmed hypotheses guide response style,
* rejected hypotheses are suppressed,
* human focus overrides automatic focus,
* human notes appear in internal context for the main agent.

⸻

12. RAG Roadmap

RAG should support therapeutic work, not replace it.

Stage 1 — System therapeutic knowledge

Small curated knowledge base:

data/knowledge/
├── emotional_regulation/
├── relationships/
├── anxiety/
├── depression/
├── trauma/
├── attachment/
├── dbt/
├── cbt/
├── psychodynamic/
├── crisis/
└── psychoeducation/

Stage 2 — User documents

Allow optional user documents:

* notes,
* logs,
* questionnaire answers,
* journals,
* previous summaries.

Stage 3 — Human-approved knowledge

Allow human reviewers/admins to add approved knowledge documents.

Stage 4 — Advanced retrieval

Later:

* vector database,
* reranking,
* hybrid search,
* source quality scoring,
* Graph RAG.

⸻

13. Working Hypotheses and Therapy Direction

Working hypotheses should influence session direction, not dominate the visible conversation.

Hypothesis statuses:

* new,
* observed,
* strengthening,
* weakened,
* confirmed_by_human,
* rejected_by_human.

Confidence:

* low,
* medium,
* high.

Sources of evidence:

* conversation,
* repeated patterns,
* user documents,
* human review,
* questionnaires,
* session summaries.

Example use:

If borderline_traits_possible is low confidence:

* do not tell the user,
* track emotional intensity,
* validate more,
* avoid harsh confrontation,
* explore fear of abandonment,
* observe identity instability, impulsivity, relational swings.

If confirmed by human:

* therapy plan may include DBT-informed direction,
* emotion regulation skills,
* distress tolerance,
* interpersonal effectiveness,
* careful pattern reflection.

⸻

14. Evaluation Plan

The system should be evaluated as a therapeutic session system, not only as a clinical fact QA system.

Test categories:

14.1 Session continuity

The agent should remember:

* previous themes,
* active focus,
* stated goals,
* unresolved questions.

14.2 Therapeutic style

The agent should:

* respond warmly,
* ask one meaningful question,
* avoid generic advice,
* avoid over-explaining,
* stay close to the user’s experience.

14.3 Pattern recognition

The system should detect:

* repeated relationship themes,
* avoidance,
* reassurance seeking,
* self-criticism,
* emotional dysregulation,
* rumination,
* shame,
* anger cycles.

14.4 Therapy direction

The system should:

* update focus,
* suggest next steps,
* build goals,
* create useful summaries.

14.5 Human review readiness

The system should produce summaries that are:

* concise,
* useful,
* evidence-linked,
* structured,
* reviewable.

14.6 Quality and consistency

The system should avoid:

* contradicting stored memory,
* exposing hidden hypotheses,
* over-labeling,
* sudden diagnostic conclusions,
* forgetting active focus,
* becoming a generic advice bot.

⸻

15. Implementation Roadmap

Step 1 — Therapeutic Case State

Status: current priority.

Implement:

* schemas/therapy.py,
* TherapyStateService,
* expanded ConversationMemoryService,
* TherapeuticProcessService,
* orchestrator integration,
* therapeutic prompt in LLMService.

Goal:
The current chatbot starts behaving like an ongoing therapeutic session agent.

Step 2 — Internal Session Notes and Post-Session Analysis

Implement:

* SessionNote,
* PostSessionAnalysisService,
* automatic session note after each assistant response,
* internal summary for human review,
* extracted key emotions,
* extracted patterns,
* next-session focus,
* state update improvements.

Goal:
Every conversation turn updates an internal therapeutic record.

Step 3 — Working Hypothesis Engine

Implement:

* HypothesisService,
* rule-based hypothesis suggestions,
* evidence accumulation,
* confidence updates,
* rejected/confirmed states,
* no visible diagnostic labels by default.

Goal:
The system begins forming internal working hypotheses that guide therapy direction.

Step 4 — Therapy Plan Agent

Implement:

* TherapyPlanService,
* therapy goals,
* next-session focus,
* suggested interventions,
* RAG-supported therapy direction.

Goal:
Sessions start having a coherent longer-term path.

Step 5 — Human Review API

Implement:

* read therapy state,
* read summaries,
* add human notes,
* accept/reject hypotheses,
* override active focus.

Goal:
Human-in-the-loop supervision becomes possible without a full UI.

Step 6 — Human Review Panel

Implement:

* simple admin/reviewer interface,
* session list,
* therapy state view,
* summary view,
* hypothesis decisions,
* notes and recommendations.

Goal:
A human can actively supervise or guide the agent.

Step 7 — Curated Therapeutic RAG

Implement:

* curated therapeutic knowledge base,
* metadata by therapeutic domain,
* retrieval for therapy planning,
* RAG use inside TherapyPlanAgent and Psychoeducation mode.

Goal:
The agent uses source-supported therapeutic frameworks when useful.

Step 8 — Optional Document Ingestion

Implement:

* upload notes,
* upload PDFs,
* process journals/questionnaires,
* connect documents to therapy state.

Goal:
User documents enrich the case formulation but are not required.

Step 9 — Advanced Agent System

Implement:

* Graph RAG,
* deeper case formulation,
* advanced NLP models,
* richer evaluation set,
* monitoring,
* advanced observability.

Goal:
The system matures into a multi-agent therapeutic platform.

⸻

16. Suggested Folder Structure

clinical_rag_agent/
├── agents/
│   ├── agent_orchestrator.py
│   ├── therapist_agent.py
│   ├── intake_agent.py
│   ├── session_memory_agent.py
│   ├── therapeutic_process_agent.py
│   ├── case_formulation_agent.py
│   ├── hypothesis_agent.py
│   ├── therapy_plan_agent.py
│   ├── rag_reasoning_agent.py
│   ├── human_review_agent.py
│   ├── quality_guard_agent.py
│   └── crisis_agent.py
│
├── services/
│   ├── llm_service.py
│   ├── session_service.py
│   ├── therapy_state_service.py
│   ├── conversation_memory_service.py
│   ├── therapeutic_process_service.py
│   ├── post_session_analysis_service.py
│   ├── case_formulation_service.py
│   ├── hypothesis_service.py
│   ├── therapy_plan_service.py
│   ├── human_review_service.py
│   ├── rag_service.py
│   ├── document_ingestion_service.py
│   ├── nlp_service.py
│   ├── safety_service.py
│   ├── hallucination_service.py
│   ├── judge_service.py
│   └── audit_log_service.py
│
├── schemas/
│   ├── chat.py
│   ├── session.py
│   ├── therapy.py
│   ├── clinical.py
│   ├── rag.py
│   ├── human_review.py
│   ├── hallucination.py
│   └── judge.py
│
├── data/
│   ├── sessions/
│   ├── therapy_states/
│   ├── session_notes/
│   ├── human_reviews/
│   └── knowledge/
│
└── tests/
    ├── test_therapy_state_service.py
    ├── test_therapeutic_process_service.py
    ├── test_post_session_analysis.py
    ├── test_hypothesis_service.py
    ├── test_therapy_plan_service.py
    └── test_orchestrator_therapy_flow.py

⸻

17. Current Priority

The next development work should follow this order:

1. Make the current chatbot session-based.
2. Add persistent therapy state.
3. Add post-session notes.
4. Add working hypotheses.
5. Add therapy plan direction.
6. Add human review API.
7. Add curated therapeutic RAG.
8. Add optional document ingestion.
9. Add advanced Graph RAG / OCR / dashboards.

Do not build advanced modules before the session loop works well.

The core loop must become:

conversation → memory → formulation → direction → response → note → updated therapy state

That is the heart of Affecta.