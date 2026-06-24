# Affecta — Clinical Content Package

This directory is the **authoring workspace for the psychologists** who write
Affecta's clinical knowledge base. It contains everything a clinician needs to
produce content that the system can use safely and consistently — *what* to write,
*how* to write it, *how much*, *in what order*, and *what each finished document
must look like*.

Nothing here is "the AI's" content. These are instructions, templates, and a small
number of fully worked examples. The clinical authors fill the `methods/` folders
using the templates; an engineer then converts the finished documents into the
retrieval knowledge base.

## Who does what

| Role | Responsibility |
| --- | --- |
| **Clinical author** (psychologist) | Writes content into the templates under `methods/`. |
| **Clinical reviewer** (senior psychologist) | Reviews each document against the quality checklist before it is accepted. |
| **Engineer** | Runs the conversion (`tools/build_chunks.py`) and loads content into the RAG store. |

## Read these first, in this order

1. **`AUTHORING_GUIDE.md`** — the rules of writing: tone, length, safety boundaries,
   evidence levels, citation format, what is forbidden. *Read fully before writing.*
2. **`METHODS_ROADMAP.md`** — which therapy methods to write, in what order, and the
   minimum set of documents required for each method's first release (MVP).
3. **`taxonomy.md`** — the controlled vocabularies (pattern labels, hypothesis labels,
   session modes, domains, methods). Every document must use these exact terms so the
   content links to the running system.
4. **`CONTENT_PIPELINE.md`** — the full lifecycle from draft to live, including the
   definition of done and how documents become retrievable.

## Document types and their templates

Every piece of content is one of the following types. Use the matching template in
`templates/`:

| Type | Template | Audience | Purpose |
| --- | --- | --- | --- |
| Knowledge card | `templates/knowledge_card.md` | clinician/internal | One atomic fact/principle used as RAG evidence. |
| Psychoeducation piece | `templates/psychoeducation_piece.md` | user | Short, warm explanation the agent can share. |
| Intervention protocol | `templates/intervention_protocol.md` | clinician | A single technique, step by step. |
| Homework exercise | `templates/homework_exercise.md` | user | A between-session task. |
| Method overview | `templates/method_overview.md` | clinician | The framing document for a whole method. |
| Assessment / questionnaire | `templates/assessment_questionnaire.md` | clinician | A validated scale and how to use/interpret it. |
| Crisis / safety doc | `templates/crisis_safety_doc.md` | mixed | Safety-critical guidance. |

## Fully worked examples

See `examples/` for two complete, accepted documents you can imitate:

- `examples/cbt_cognitive_restructuring.example.md` (intervention protocol)
- `examples/homework_thought_record.example.md` (homework exercise)

## Folder layout

```
clinical-content/
  README.md                ← you are here
  AUTHORING_GUIDE.md
  CONTENT_PIPELINE.md
  METHODS_ROADMAP.md
  taxonomy.md
  templates/               ← copy these to author new documents
  methods/
    cbt/  dbt/  act/  psychodynamic-schema/   ← write content here
  examples/                ← fully worked, accepted documents
  tools/build_chunks.py    ← engineer-run converter to the RAG store
```
