# KnowledgeHub RAG v1.6 — performance and responsive UX

## Why v1.6

Practical testing showed that the local RAG request could take several minutes on CPU.
The main reason was not document search: the pipeline could execute up to three full
LLM generations for one answer (draft + mandatory Ukrainian rewrite + strict rewrite),
and claim grounding embedded source excerpts again even though those embeddings were
already stored in PostgreSQL.

## Performance changes

### 1. One-pass by default

The normal Ukrainian path now performs:

```text
retrieval
  -> one short deterministic LLM generation
  -> language check
  -> claim grounding
  -> citations
```

A Ukrainian rewrite is executed only when the language checker finds a critical issue
(or an unusually low score with several suspicious words). There is at most one rewrite.

### 2. Smaller generation budget

The default generation budget was reduced from 320 to 160 new tokens. KnowledgeHub
asks for 2–3 concise grounded sentences, so the previous budget was unnecessary for
normal research answers.

### 3. Source embeddings are reused

Retrieved `document_chunks` already contain normalized embeddings in PostgreSQL.
RAG v1.6 keeps those vectors internally on `ResearchSourceAPI` but excludes them from
API serialization. Claim grounding embeds only the newly generated claims and compares
them with the stored source vectors.

### 4. Vectorized retrieval

Semantic scoring for all chunks is performed as one NumPy matrix multiplication instead
of a Python `np.dot` loop per chunk. This scales much better when a collection contains
thousands of chunks.

### 5. Background model warmup

When the user selects Local LLM, Vue starts a background warmup request. FastAPI remains
available for login and CRUD because the heavy model is still lazy-loaded. The model load
is protected by a lock, so simultaneous warmup/generation requests cannot load the model
twice.

### 6. Real timings

The answer now reports actual server timings:

- retrieval;
- local LLM generation;
- claim grounding;
- total request time;
- whether the request included a cold model start.

This makes performance measurable instead of subjective.

## Large documents

For 100–500 page documents, ingestion still creates embeddings once during upload.
Queries reuse the persisted chunk embeddings and retrieve only a small top-k context.
The next scale step for very large corpora is a PostgreSQL `pgvector` ANN index; that is
not required yet for a few thousand chunks, but it is the planned path when collection
sizes become much larger.

## Responsive UX

The v1.6 frontend adds an adaptive readability layer for medium and narrow windows:

- larger research text on half-screen/small-laptop widths;
- larger form controls and buttons;
- more comfortable panel padding;
- wider use of the available viewport;
- improved mobile result layout;
- performance chips and model warmup state.
