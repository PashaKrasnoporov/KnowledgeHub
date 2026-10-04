# KnowledgeHub RAG v1.4

## Goals

RAG v1.4 addresses two practical issues:

1. slow login/API readiness immediately after backend restart;
2. malformed Ukrainian words in locally generated answers.

## Faster backend startup

Heavy ML libraries are no longer imported during normal FastAPI startup.

`torch`, `transformers` and `sentence_transformers` are loaded lazily
only when local LLM generation or embedding computation is actually needed.

This allows `/api/v1/health`, authentication and ordinary CRUD routes
to become available earlier.

The Vue login page also waits for the health endpoint and displays a
clear startup message instead of immediately exposing a raw proxy 502.

## Ukrainian lexical quality gate

The project now uses `wordfreq` as a local corpus-based Ukrainian
frequency dictionary.

A generated Cyrillic word is treated as suspicious when:

- it is long enough to be meaningful;
- it is not a known technical term;
- it does not occur in retrieved source text;
- it has no Ukrainian corpus frequency.

This is not used to rewrite source documents.

Source excerpts are preserved exactly as extracted from the files.

The dictionary is used only as a quality signal for generated text.

## Generation pipeline

```text
retrieval
  -> LLM draft
  -> mandatory Ukrainian editorial pass
  -> heuristic + corpus lexical check
  -> strict rewrite with detected issues
  -> second lexical/language check
  -> fallback if still malformed
  -> claim grounding
  -> citations
```

## Why not LanguageTool yet?

LanguageTool supports Ukrainian and can provide grammar/spelling checks,
but a local installation adds a Java runtime/service dependency.

For the current local development stage, `wordfreq` adds a lightweight
offline lexical gate without introducing another long-running service.

LanguageTool remains a candidate for a later optional proofreading layer.
