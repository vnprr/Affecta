# Methods Roadmap

This is the order in which therapy methods should be authored, and the **minimum set
of documents** each method needs for its first release. Write methods top to bottom.
Do not start a later method before the earlier one's MVP set is complete and
reviewed — the system, the goals it generates, and the panel all assume CBT content
exists first.

## Why this order

1. **CBT** — broadest evidence base, most modular, and the system already maps most
   detected patterns and several hypotheses (`anxiety_patterns`, `depressive_patterns`,
   `attachment_anxiety`) to CBT goals. It also gives us the homework backbone.
2. **DBT** — required as soon as `emotional_dysregulation` or `borderline_traits_possible`
   become relevant; the plan engine already routes these toward DBT skills.
3. **ACT** — complements CBT for `rumination` and `avoidance`; values-based work.
4. **Psychodynamic / schema** — depth work on relational patterns, `self-criticism`,
   and `shame spiral`; richest for case formulation but least scripted, so last.

## Definition of "MVP complete" for a method

A method is releasable when it has: **1 method overview**, the listed
**intervention protocols**, the listed **psychoeducation pieces**, the listed
**homework exercises**, and every document has passed clinical review.

---

## 1. CBT — write first

- **Method overview** ×1 (`method_overview.md`): the cognitive model, structure of
  CBT work, indications, contraindications.
- **Psychoeducation pieces** ×3–4 (`audience: user`):
  - the thought–feeling–behavior link (cognitive model)
  - cognitive distortions / "thinking traps" (cover 8–10 common ones)
  - how avoidance maintains anxiety
  - the reassurance-seeking loop
- **Intervention protocols** ×4–6 (`audience: clinician`):
  - cognitive restructuring (see worked example)
  - evidence-for-and-against
  - behavioral activation
  - graded exposure (flag `requires_supervision` where relevant)
  - behavioral experiment
  - worry postponement
- **Homework exercises** ×4–6 (`audience: user`):
  - thought record (see worked example)
  - activity scheduling / activation log
  - exposure ladder step
  - delay-the-reassurance experiment
  - worry time
  - values-light "one small approach action"
- **Domains touched:** `anxiety`, `depression`, `avoidance`, `relationships`.

## 2. DBT — write second

- **Method overview** ×1: dialectics, the four skills modules, when DBT-informed
  work fits, the validation-first stance for `borderline_traits_possible`.
- **Psychoeducation pieces** ×3:
  - the window of tolerance
  - emotions as information (primary vs secondary emotions)
  - what "dialectical" means (acceptance *and* change)
- **Intervention protocols** ×4 (one per skills module, `audience: clinician`):
  - mindfulness ("what" and "how" skills)
  - distress tolerance (TIP, self-soothe, radical acceptance)
  - emotion regulation (check the facts, opposite action)
  - interpersonal effectiveness (DEAR MAN)
- **Homework exercises** ×3:
  - diary card (emotion + urge tracking)
  - opposite-action practice
  - paced breathing / TIP skill
- **Domains touched:** `emotional_regulation`, `relationships`, `crisis`.

## 3. ACT — write third

- **Method overview** ×1: psychological flexibility, the six core processes (hexaflex).
- **Psychoeducation pieces** ×3: values, cognitive defusion, acceptance vs avoidance.
- **Intervention protocols** ×3 (`audience: clinician`): values clarification,
  cognitive defusion, willingness/acceptance exercise.
- **Homework exercises** ×3: values card-sort reflection, a defusion practice,
  one committed action toward a value.
- **Domains touched:** `rumination`, `avoidance`, `emotional_regulation`.

## 4. Psychodynamic / schema — write last

- **Method overview** ×1: early maladaptive schemas, modes, the relational/attachment
  lens; emphasize this is depth, formulation-supporting work.
- **Psychoeducation pieces** ×2–3: the inner critic, where schemas come from,
  attachment styles (plain-language).
- **Intervention protocols** ×2–3 (`audience: clinician`): schema identification,
  chair-work (flag `requires_supervision: true`), compassionate reframe of the inner critic.
- **Homework exercises** ×2: self-compassion practice, schema-trigger diary.
- **Domains touched:** `attachment`, `self_criticism`, `relationships`, `trauma`.

---

## Cross-cutting: write alongside CBT

These are method-agnostic (`method: none`) and needed early because the safety layer
already runs:

- **Crisis / safety docs** ×2–3 (`crisis_safety_doc.md`): general safety routing,
  responding to suicidal ideation (clinician-facing), grounding for acute distress.
- **Assessments** ×2 (`assessment_questionnaire.md`): PHQ-9 (depression) and GAD-7
  (anxiety) — how to administer, score, and interpret cautiously, with the explicit
  note that scores are screening signals, not diagnoses.

## Suggested volume for first full release

~10–14 CBT documents, ~11 DBT, ~10 ACT, ~8 schema, ~5 cross-cutting ≈ **45–50
documents total**. Start with the CBT MVP set; that alone makes the system usefully
grounded.
