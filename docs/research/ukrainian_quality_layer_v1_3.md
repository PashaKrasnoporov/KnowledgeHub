# KnowledgeHub RAG v1.3 — Ukrainian Quality Layer

## Purpose

Ukrainian is the primary language of generated answers.

RAG v1.3 separates factual grounding from linguistic quality.

## Pipeline

```text
retrieval
  -> evidence gate
  -> local LLM draft
  -> mandatory Ukrainian editorial pass
  -> Ukrainian quality check
  -> optional strict second editorial pass
  -> repetition guard
  -> claim-level grounding
  -> automatic citations
  -> verified answer
```

## Mandatory editorial pass

In Ukrainian mode every generated draft is rewritten once.

The editor must:

- preserve all factual content;
- add no new facts;
- avoid Russian words and calques;
- avoid invented terms and malformed words;
- prefer established terminology;
- keep English technical terms where natural.

## Strict second pass

A second pass is triggered when the first edited text still contains
known Russian markers or suspicious artificial forms.

Examples of rejected forms include:

- `пошукування`;
- `семана-...`;
- `семантос...`;
- malformed noun/adjective agreement.

If the second pass still fails the language gate, the generated answer
is not shown. KnowledgeHub falls back to the safe extractive answer.

## UI

The result now exposes:

- `✓ Відповідь перевірена`;
- grounding coverage;
- evidence confidence;
- `Український контроль ✓`;
- number of editorial passes;
- tooltips for technical metrics;
- collapsible claim audit.

The loading state displays an indeterminate progress bar and an
approximate current stage without pretending to know an exact percent.
