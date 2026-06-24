# Authoring Guide

Read this fully before writing any content. It defines the rules every Affecta
clinical document must follow. A document that violates these rules will be sent
back in review.

## 1. What Affecta is (and is not)

Affecta is a **supportive, psychoeducational, therapy-style conversational system
operating under human supervision**. It is **not** a diagnosing clinician and not a
prescriber. Your content must reflect that everywhere:

- Describe possibilities as **hypotheses**, never diagnoses.
- Never instruct the user to start, stop, or change **medication**.
- Never promise outcomes ("this will cure your anxiety").
- Always preserve the user's autonomy and the role of a human professional.

## 2. Audience: write for one of two readers

Every document declares an `audience` in its front matter:

- **`user`** — content the agent may show or paraphrase to the person in session.
  Write warm, plain, second-person language. No jargon without a plain-language gloss.
  Reading level: roughly age 14–16. Short sentences.
- **`clinician`** / **internal** — content used only to *guide* the agent or the human
  reviewer; the user never sees it verbatim. Here you may use clinical terminology.

If in doubt, assume `user` and write more simply.

## 3. Tone and style

- Warm, validating, non-judgmental, concrete. Avoid lecturing.
- Prefer "many people notice…", "it can help to…" over commands.
- Use inclusive, non-stigmatizing language ("a person experiencing…", not "a borderline").
- One idea per document. If you are explaining two things, write two documents.
- No filler, no motivational clichés.

## 4. Length limits (hard caps)

| Type | Target | Hard cap |
| --- | --- | --- |
| Knowledge card | 80–150 words | 200 words |
| Psychoeducation piece | 120–250 words | 350 words |
| Intervention protocol | 200–500 words | 700 words |
| Homework exercise | 150–350 words | 500 words |
| Method overview | 400–800 words | 1200 words |
| Assessment / questionnaire | 200–500 words | 800 words |
| Crisis / safety doc | 120–300 words | 400 words |

Content is retrieved in small pieces. **Smaller, single-purpose documents retrieve
better than long ones.** When in doubt, split.

## 5. Required structure: front matter + body

Every document is a Markdown file beginning with a YAML-style front-matter block,
then the body. Fields are defined per template, but these are always required:

```
---
id: cbt_cognitive_restructuring          # unique, snake_case, stable forever
title: Cognitive restructuring            # short human title
type: intervention_protocol               # one of the document types
method: CBT                               # see taxonomy.md (or "none")
domain: anxiety                           # see taxonomy.md
audience: clinician                       # user | clinician | internal
evidence_level: strong                    # strong | moderate | emerging | clinical_consensus
language: en                              # en (write source content in English)
links_patterns: [catastrophic interpretation]   # taxonomy pattern labels, optional
links_hypotheses: [anxiety_patterns]             # taxonomy hypothesis labels, optional
sources:
  - "Beck JS. Cognitive Behavior Therapy: Basics and Beyond. 3rd ed. 2020."
tags: [cbt, cognition, restructuring]
---
```

Rules for front matter:

- **`id`** is permanent. Never reuse or rename an `id`; content is referenced by it.
- **`method`, `domain`, `links_patterns`, `links_hypotheses`** must use the exact strings
  in `taxonomy.md`. This is how your content connects to the running system.
- **`audience`** drives how the agent uses the content (see §2).
- List values use `[a, b, c]`; multi-line lists (like `sources`) use `-` bullets.

## 6. Evidence levels

Assign `evidence_level` honestly:

| Level | Meaning |
| --- | --- |
| `strong` | Supported by meta-analyses / multiple RCTs (e.g. CBT for anxiety). |
| `moderate` | Supported by several controlled studies. |
| `emerging` | Promising but limited evidence. |
| `clinical_consensus` | Standard practice / expert consensus, not primarily trial-based. |

## 7. Citing sources

- Every `clinician` document and every clinical claim needs at least one entry in
  `sources`. `user` psychoeducation should still be grounded but may cite the
  underlying clinician document instead of primary literature.
- Cite real, checkable sources: textbooks, manuals, peer-reviewed articles, or
  recognized guidelines (e.g. APA, NICE). Include author, title, year.
- Do **not** fabricate citations. If you cannot source a claim, soften it or remove it.
- Prefer primary treatment manuals (e.g. Linehan for DBT, Hayes for ACT, Young for
  schema therapy, Beck for CBT) and recognized clinical guidelines.

## 8. Hard prohibitions (automatic rejection)

- Diagnostic statements phrased as fact about a person.
- Medication advice or dosing.
- Crisis content that omits "seek immediate local emergency help" routing.
- Techniques contraindicated without supervision presented as self-serve to users
  (e.g. trauma exposure / memory reprocessing must be `clinician` audience and flagged
  `requires_supervision: true`).
- Any claim you cannot cite.

## 9. Quality checklist (a reviewer will run this)

- [ ] Correct template and all required front-matter fields present.
- [ ] `id` is unique, snake_case, and meaningful.
- [ ] `method`/`domain`/links use exact taxonomy terms.
- [ ] Audience-appropriate language and reading level.
- [ ] Within the length cap; single purpose.
- [ ] Hypotheses, not diagnoses; no medication advice.
- [ ] Every clinical claim is cited; sources are real.
- [ ] Safety: crisis routing present where relevant; supervision flag set where needed.
- [ ] No stigmatizing language.
