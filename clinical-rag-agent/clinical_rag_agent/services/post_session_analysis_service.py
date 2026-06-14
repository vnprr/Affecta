from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from clinical_rag_agent.schemas.therapy import (
    PostSessionAnalysisResult,
    SessionNote,
    TherapeuticCaseState,
    TherapeuticProcessContext,
    TherapyStateUpdate,
)


class PostSessionAnalysisService:
    EMOTION_RULES = {
        "fear": ("fear", "scared", "afraid", "anxious", "lęk", "lek", "boję", "boje", "strach", "przeraż"),
        "panic": ("panic", "panika", "panicz"),
        "anger": ("anger", "angry", "rage", "złość", "zlosc", "wściek", "wsciek"),
        "sadness": ("sad", "sadness", "smutek", "smutno", "płacz", "placz"),
        "emptiness": ("empty", "emptiness", "pustka", "pusto"),
        "numbness": ("numb", "nothing", "odrętw", "odretw", "nic nie czuję", "nic nie czuje"),
        "shame": ("shame", "guilt", "wstyd", "winny", "wina"),
        "loneliness": ("lonely", "alone", "samotn"),
        "hopelessness": ("hopeless", "beznadziej"),
    }
    RELATIONAL_RULES = {
        "partner availability or distance": (
            "partner",
            "partnerka",
            "girlfriend",
            "boyfriend",
            "wife",
            "husband",
            "dziewczyna",
            "chłopak",
            "chlopak",
        ),
        "family relationship material": ("mother", "father", "matka", "ojciec", "mama", "tata"),
        "fear of being left or rejected": (
            "left",
            "abandoned",
            "rejected",
            "ignored",
            "zostawi",
            "porzuci",
            "odrzuci",
            "ignoruje",
        ),
        "betrayal or broken trust": ("betrayed", "betrayal", "zdradziła", "zdradzila", "zdradził", "zdradzil"),
    }
    BEHAVIORAL_RULES = {
        "checking behavior": ("checking", "check", "sprawdzam", "sprawdzałem", "sprawdzalem"),
        "calling or texting for contact": ("calling", "texting", "dzwonię", "dzwonie", "piszę", "pisze", "sms"),
        "avoidance": ("avoiding", "avoid", "unikam", "uciekam", "running away"),
        "isolation": ("isolating", "isolate", "izoluję", "izoluje", "zamykam się", "zamykam sie"),
        "drinking as coping": ("drinking", "drink", "piję", "pije", "alkohol"),
        "arguing": ("arguing", "argument", "kłócę", "kloce", "kłótn", "klotn"),
    }
    COGNITIVE_RULES = {
        "absolute framing": ("always", "never", "everyone", "no one", "zawsze", "nigdy", "wszyscy", "nikt"),
        "certainty about the other person": ("i know she will", "i know he will", "wiem że", "wiem, że"),
        "catastrophic ending expectation": ("it always ends", "na pewno", "koniec", "wszystko się skończy", "wszystko sie skonczy"),
        "self-critical thought": ("i hate myself", "my fault", "jestem beznadziej", "moja wina", "nienawidzę siebie"),
        "ruminative thought loop": ("can't stop thinking", "overthinking", "ciągle myślę", "ciagle mysle", "analizuję", "analizuje"),
    }
    SOMATIC_RULES = {
        "chest tension or pressure": ("chest", "klatka", "serce"),
        "stomach sensation": ("stomach", "brzuch", "żołądek", "zoladek"),
        "shaking": ("shaking", "trzęsę", "trzese", "drżę", "drze"),
        "tension": ("tension", "napięcie", "napiecie", "spięcie", "spiecie"),
        "tiredness or exhaustion": ("tired", "exhausted", "zmęczenie", "zmeczenie", "wyczerpan"),
        "sleep disturbance": ("sleep", "insomnia", "sen", "bezsenność", "bezsennosc"),
    }

    async def analyze_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        therapy_state: TherapeuticCaseState,
        therapy_context: TherapeuticProcessContext,
        nlp_context: Any | None = None,
        rag_context: Any | None = None,
    ) -> PostSessionAnalysisResult:
        lower = user_message.lower()
        emotions = self._labels_for(lower, self.EMOTION_RULES)
        relational_material = self._labels_for(lower, self.RELATIONAL_RULES)
        behavioral_material = self._labels_for(lower, self.BEHAVIORAL_RULES)
        cognitive_material = self._labels_for(lower, self.COGNITIVE_RULES)
        somatic_material = self._labels_for(lower, self.SOMATIC_RULES)
        patterns = self._detect_patterns(
            lower=lower,
            emotions=emotions,
            relational_material=relational_material,
            behavioral_material=behavioral_material,
            cognitive_material=cognitive_material,
        )
        key_themes = self._key_themes(patterns, relational_material, behavioral_material, cognitive_material, somatic_material)
        open_threads = self._open_threads(patterns, therapy_context)
        suggested_next_focus = self._suggested_next_focus(patterns, therapy_context)
        suggested_next_steps = self._suggested_next_steps(patterns, therapy_context)
        summary = self._summary(user_message, emotions, key_themes, patterns)
        significance = self._therapeutic_significance(patterns, key_themes, therapy_context)
        hypothesis_updates = self._possible_hypothesis_updates(patterns)
        hypothesis_evidence = self._hypothesis_evidence(user_message, patterns)
        human_review = therapy_context.human_review_recommended or "hopelessness" in emotions

        note = SessionNote(
            id=f"note_{uuid4().hex}",
            session_id=session_id,
            created_at=datetime.now(timezone.utc),
            user_message_excerpt=self._excerpt(user_message, 320),
            assistant_response_excerpt=self._excerpt(assistant_response, 320),
            summary=summary,
            therapeutic_significance=significance,
            key_emotions=emotions,
            key_themes=key_themes,
            detected_patterns=patterns,
            relational_material=relational_material,
            cognitive_material=cognitive_material,
            behavioral_material=behavioral_material,
            body_or_somatic_material=somatic_material,
            session_mode=therapy_context.session_mode,
            therapeutic_focus=therapy_context.therapeutic_focus,
            response_strategy_used=therapy_context.response_strategy,
            open_threads=open_threads,
            unresolved_questions=open_threads,
            suggested_next_focus=suggested_next_focus,
            suggested_next_steps=suggested_next_steps,
            possible_hypothesis_updates=hypothesis_updates,
            hypothesis_evidence=hypothesis_evidence,
            human_review_recommended=human_review,
            human_review_reason="Hopelessness or review-sensitive process material appeared." if human_review else None,
            questions_for_human_reviewer=self._review_questions(human_review, emotions),
            metadata={
                "therapy_session_count_before_update": therapy_state.session_count,
                "rag_chunks": len(getattr(rag_context, "chunks", []) or []),
                "nlp_intent": getattr(nlp_context, "intent", None),
            },
        )
        update = TherapyStateUpdate(
            new_emotional_states=emotions,
            new_patterns=patterns,
            new_relational_patterns=self._relational_patterns(patterns),
            new_cognitive_patterns=self._cognitive_patterns(patterns, cognitive_material),
            new_behavioral_patterns=self._behavioral_patterns(patterns, behavioral_material),
            updated_active_focus=suggested_next_focus or therapy_context.therapeutic_focus,
            summary_note=summary,
            longitudinal_summary_addition=significance,
            open_questions=open_threads,
            suggested_next_steps=suggested_next_steps,
        )
        return PostSessionAnalysisResult(session_note=note, therapy_state_update=update)

    def _detect_patterns(
        self,
        lower: str,
        emotions: list[str],
        relational_material: list[str],
        behavioral_material: list[str],
        cognitive_material: list[str],
    ) -> list[str]:
        patterns: list[str] = []
        relationship_present = bool(relational_material)
        abandonment_present = "fear of being left or rejected" in relational_material
        checking_present = any(item in behavioral_material for item in {"checking behavior", "calling or texting for contact"})
        anger_present = "anger" in emotions
        shame_present = "shame" in emotions
        numb_present = "numbness" in emotions or "emptiness" in emotions

        if abandonment_present or (relationship_present and "fear" in emotions):
            patterns.append("fear of abandonment")
        if checking_present:
            patterns.append("reassurance seeking")
        if any(item in cognitive_material for item in {"absolute framing", "certainty about the other person", "catastrophic ending expectation"}):
            patterns.append("catastrophic interpretation")
        if "self-critical thought" in cognitive_material:
            patterns.append("self-criticism")
        if numb_present:
            patterns.append("emotional shutdown")
        if any(item in behavioral_material for item in {"avoidance", "isolation"}):
            patterns.append("avoidance")
        if anger_present and (relationship_present or abandonment_present or "betrayal or broken trust" in relational_material):
            patterns.append("anger after hurt")
        if checking_present and relationship_present:
            patterns.append("relational pursuit/withdrawal")
        if shame_present and ("self-critical thought" in cognitive_material or "hopelessness" in emotions):
            patterns.append("shame spiral")
        if "ruminative thought loop" in cognitive_material:
            patterns.append("rumination")
        if "czy ona" in lower and "odpis" in lower:
            self._append_unique(patterns, "reassurance seeking")
        return patterns

    def _key_themes(
        self,
        patterns: list[str],
        relational_material: list[str],
        behavioral_material: list[str],
        cognitive_material: list[str],
        somatic_material: list[str],
    ) -> list[str]:
        themes: list[str] = []
        if relational_material:
            themes.append("relationship insecurity")
        if "fear of abandonment" in patterns:
            themes.append("abandonment fear")
        if behavioral_material:
            themes.append("coping behavior")
        if cognitive_material:
            themes.append("thought pattern under stress")
        if somatic_material:
            themes.append("body cues of emotion")
        return themes

    def _open_threads(self, patterns: list[str], therapy_context: TherapeuticProcessContext) -> list[str]:
        threads: list[str] = []
        if "reassurance seeking" in patterns:
            threads.append("what appears first before checking: thought, body sensation, emotion, or impulse")
        if "fear of abandonment" in patterns:
            threads.append("what the unavailable or distant relationship moment means emotionally")
        if "catastrophic interpretation" in patterns:
            threads.append("which facts support the feared conclusion and which remain uncertain")
        if therapy_context.question_goal:
            self._append_unique(threads, therapy_context.question_goal)
        return threads

    def _suggested_next_focus(self, patterns: list[str], therapy_context: TherapeuticProcessContext) -> str:
        if "reassurance seeking" in patterns:
            return "trigger sequence before reassurance seeking"
        if "fear of abandonment" in patterns:
            return "fear of abandonment in close relationships"
        if "catastrophic interpretation" in patterns:
            return "how certainty rises during distress"
        return therapy_context.therapeutic_focus

    def _suggested_next_steps(self, patterns: list[str], therapy_context: TherapeuticProcessContext) -> list[str]:
        steps: list[str] = []
        if "reassurance seeking" in patterns:
            steps.append("Ask what appears first: thought, body sensation, emotion, or impulse.")
            steps.append("Track how reassurance changes emotion short-term and long-term.")
        if "fear of abandonment" in patterns:
            steps.append("Explore what silence or distance starts to mean in the user's inner story.")
        if "catastrophic interpretation" in patterns:
            steps.append("Separate the feared interpretation from what is currently known.")
        if therapy_context.question_goal:
            self._append_unique(steps, therapy_context.question_goal)
        if not steps:
            steps.append(f"Continue with {therapy_context.therapeutic_focus}.")
        return steps

    def _summary(self, user_message: str, emotions: list[str], themes: list[str], patterns: list[str]) -> str:
        pieces = ["User described"]
        if emotions:
            pieces.append(f"emotions: {', '.join(emotions[:4])}")
        if themes:
            pieces.append(f"themes: {', '.join(themes[:3])}")
        if patterns:
            pieces.append(f"patterns: {', '.join(patterns[:3])}")
        if len(pieces) == 1:
            pieces.append("the current concern without a clearly detected recurring pattern")
        return "; ".join(pieces) + f". Excerpt: {self._excerpt(user_message, 180)}"

    def _therapeutic_significance(
        self,
        patterns: list[str],
        themes: list[str],
        therapy_context: TherapeuticProcessContext,
    ) -> str:
        if patterns:
            return f"This exchange adds material to the recurring process pattern: {', '.join(patterns[:3])}."
        if themes:
            return f"This exchange clarifies therapeutic themes around {', '.join(themes[:3])}."
        return f"This exchange supports continuity in {therapy_context.therapeutic_focus}."

    def _possible_hypothesis_updates(self, patterns: list[str]) -> list[str]:
        updates: list[str] = []
        if "fear of abandonment" in patterns:
            updates.append("relationship anxiety / abandonment fear may be a recurring process theme")
        if "reassurance seeking" in patterns:
            updates.append("reassurance seeking may reduce distress short-term while maintaining the loop")
        if "catastrophic interpretation" in patterns:
            updates.append("distress may increase certainty in feared interpretations")
        return updates

    def _hypothesis_evidence(self, user_message: str, patterns: list[str]) -> list[str]:
        if not patterns:
            return []
        return [self._excerpt(user_message, 220)]

    def _review_questions(self, human_review: bool, emotions: list[str]) -> list[str]:
        if not human_review:
            return []
        questions = ["Should this material change the next-session focus?"]
        if "hopelessness" in emotions:
            questions.append("Does the level of hopelessness require additional safety review?")
        return questions

    @staticmethod
    def _relational_patterns(patterns: list[str]) -> list[str]:
        relational = {"fear of abandonment", "anger after hurt", "relational pursuit/withdrawal"}
        return [pattern for pattern in patterns if pattern in relational]

    @staticmethod
    def _cognitive_patterns(patterns: list[str], cognitive_material: list[str]) -> list[str]:
        cognitive = {"catastrophic interpretation", "self-criticism", "shame spiral", "rumination"}
        values = [pattern for pattern in patterns if pattern in cognitive]
        values.extend(cognitive_material)
        return PostSessionAnalysisService._unique(values)

    @staticmethod
    def _behavioral_patterns(patterns: list[str], behavioral_material: list[str]) -> list[str]:
        behavioral = {"reassurance seeking", "avoidance", "relational pursuit/withdrawal"}
        values = [pattern for pattern in patterns if pattern in behavioral]
        values.extend(behavioral_material)
        return PostSessionAnalysisService._unique(values)

    @staticmethod
    def _labels_for(lower: str, rules: dict[str, tuple[str, ...]]) -> list[str]:
        return [label for label, markers in rules.items() if any(marker in lower for marker in markers)]

    @staticmethod
    def _excerpt(text: str, limit: int) -> str:
        normalized = " ".join(text.split())
        return normalized[:limit]

    @staticmethod
    def _append_unique(target: list[str], value: str) -> None:
        if value and value.lower() not in {item.lower() for item in target}:
            target.append(value)

    @staticmethod
    def _unique(values: list[str]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for value in values:
            normalized = value.strip()
            key = normalized.lower()
            if normalized and key not in seen:
                result.append(normalized)
                seen.add(key)
        return result
