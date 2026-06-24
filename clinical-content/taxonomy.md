# Controlled Vocabularies (Taxonomy)

Every document must use these exact strings in its front matter so the authored
content links to what the running system actually detects and reasons about. If you
need a term that is not here, **do not invent it** — propose it to the engineering
team so it can be added to both this file and the code.

> Source of truth in code: pattern labels are produced in
> `clinical-rag-agent/.../services/post_session_analysis_service.py`; hypothesis
> labels in `services/hypothesis_service.py`; session modes and goal/visibility in
> `schemas/therapy.py`; goal→method mapping in `services/therapy_plan_service.py`.

## Methods (`method`)

| Value | Name |
| --- | --- |
| `CBT` | Cognitive Behavioral Therapy |
| `DBT` | Dialectical Behavior Therapy |
| `ACT` | Acceptance and Commitment Therapy |
| `schema` | Schema therapy / psychodynamic-informed work |
| `none` | Method-agnostic (e.g. general safety, psychoeducation) |

## Domains (`domain`)

`emotional_regulation`, `relationships`, `anxiety`, `depression`, `trauma`,
`attachment`, `crisis`, `psychoeducation`, `self_criticism`, `rumination`,
`avoidance`.

## Pattern labels (`links_patterns`)

These are the recurring process patterns the system detects from conversation. Link
your content to the patterns it is meant to help with:

- `fear of abandonment`
- `reassurance seeking`
- `catastrophic interpretation`
- `self-criticism`
- `emotional shutdown`
- `avoidance`
- `anger after hurt`
- `relational pursuit/withdrawal`
- `shame spiral`
- `rumination`

## Working-hypothesis labels (`links_hypotheses`)

These are the internal, low-confidence working hypotheses the system maintains
(never shown to the user as diagnoses). Link content that is appropriate when a
hypothesis is active:

| Label | Plain meaning | Typical method direction |
| --- | --- | --- |
| `attachment_anxiety` | Anxious attachment, abandonment fear, reassurance-seeking | CBT + emotion regulation |
| `emotional_dysregulation` | Difficulty regulating intense emotion, rapid shifts | DBT |
| `borderline_traits_possible` | Cautious, low-confidence borderline-like traits | DBT (validation-first) |
| `depressive_patterns` | Low mood, withdrawal, hopelessness, anhedonia | CBT (behavioral activation) |
| `anxiety_patterns` | Catastrophic prediction, worry loops, avoidance | CBT |
| `self_criticism_shame` | Prominent self-criticism and shame | schema / compassion-focused |

## Session modes (`SessionMode`)

Used internally to decide how the agent should respond. You may reference these in
`intervention_protocol` documents to say *when* a technique fits:

`intake`, `exploration`, `support`, `stabilization`, `pattern_reflection`,
`psychoeducation`, `summary`.

## Goal visibility

Therapy goals carry a visibility:

- `visible` — may be shared with the user.
- `internal` — guides the agent's style and is shown to the human reviewer only.

## Audience values (`audience`)

`user`, `clinician`, `internal`. See `AUTHORING_GUIDE.md` §2.

## Evidence levels (`evidence_level`)

`strong`, `moderate`, `emerging`, `clinical_consensus`. See `AUTHORING_GUIDE.md` §6.
