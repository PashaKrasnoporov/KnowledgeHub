# KnowledgeHub

KnowledgeHub — україномовно орієнтована вебплатформа для керування дослідницькими документами, повнотекстового, семантичного та гібридного пошуку, а також grounded RAG.

## Основний стек

- FastAPI
- PostgreSQL
- SQLAlchemy + Alembic
- Vue 3 + Vue Router + Vite
- sentence-transformers
- локальна instruction LLM

## Пошук

KnowledgeHub підтримує:

- **Lexical** — PostgreSQL Full Text Search;
- **Semantic** — multilingual sentence embeddings;
- **Hybrid** — lexical + semantic retrieval;
- **Research retrieval** — ранжування на рівні `document_chunks`.

## RAG v1.2

Основний RAG-процес:

```text
Question
  ↓
Query embedding
  ↓
Chunk retrieval
  ↓
Semantic + lexical ranking
  ↓
Evidence confidence gate
  ↓
Local LLM
  ↓
Ukrainian language quality check
  ↓
Optional Ukrainian rewrite
  ↓
Claim-level grounding
  ↓
Automatic citations
  ↓
Grounded answer + sources
```

### Ukrainian-first

За замовчуванням генерація виконується українською мовою, навіть якщо частина доказових джерел іншомовна.

Англійські технічні терміни можуть зберігатися в природній професійній формі, але пояснення формулюються українською.

### Local LLM

Поточна модель:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

API-ключ не потрібний.

### Claim-level grounding

LLM не створює citations самостійно.

KnowledgeHub:

1. ділить generated answer на твердження;
2. створює embeddings тверджень;
3. порівнює їх із retrieved sources;
4. додає lexical overlap та retrieval prior;
5. відкидає непідтверджені твердження;
6. сам додає `[1]`, `[2]` тощо.

### Evidence gate

Якщо retrieved evidence надто слабке, KnowledgeHub не запускає LLM і прямо повідомляє, що доказів недостатньо. Це знижує ризик hallucinations.

## Vue UX

Research UI містить:

- режим швидкої чернетки;
- режим локальної LLM;
- українську мову як default;
- індикатор активної генерації;
- elapsed time;
- Ctrl+Enter;
- character counter;
- copy answer;
- clickable citations;
- grounding coverage;
- evidence confidence;
- claim audit.

## Документація

- `docs/research/rag_v1.md`
- `docs/research/claim_grounding.md`
- `docs/research/ukrainian_rag_v1_2.md`
