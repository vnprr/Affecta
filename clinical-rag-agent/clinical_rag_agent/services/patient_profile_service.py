from clinical_rag_agent.schemas.clinical import PatientSession


class PatientProfileService:
    def summarize_known_facts(self, session: PatientSession) -> dict[str, str]:
        return session.profile.facts

