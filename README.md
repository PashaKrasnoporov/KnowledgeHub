# KnowledgeHub

KnowledgeHub — україномовно орієнтована вебплатформа для керування дослідницькими документами, повнотекстового, семантичного та гібридного пошуку, а також grounded RAG.

## Основний стек

- FastAPI
- PostgreSQL
- SQLAlchemy + Alembic
- Vue 3 + Vue Router + Vite
- sentence-transformers
- локальна instruction LLM
- wordfreq як м'який корпусний сигнал для української

## RAG v1.5.2

```text
Question
  ↓
Hybrid chunk retrieval
  ↓
Evidence confidence gate
  ↓
Local LLM draft
  ↓
Mandatory Ukrainian editorial pass
  ↓
Soft corpus / language quality scoring
  ↓
Optional strict deterministic rewrite
  ↓
Claim-level grounding
  ↓
Automatic citations
  ↓
Verified answer
```

### Ukrainian-first

Українська — основна мова генерації.

`wordfreq` більше не використовується як абсолютний словник.
Рідкісне або невідоме корпусу слово є лише попередженням і не може саме по собі відхилити відповідь.

Критичними залишаються:

- російські мовні форми;
- очевидні штучні словоформи;
- відомі кальковані конструкції;
- неприродні технічні сполуки.

Український результат має інтегральну оцінку якості `/100`.

### Source-preserving fallback

Якщо LLM-відповідь відхилено, KnowledgeHub не переписує першоджерела.

Система вибирає чисті релевантні речення з retrieved chunks, прибираючи лише display-noise на кшталт службових metadata та тестової нумерації.

Оригінальний текст PDF/DOCX/TXT залишається незмінним.

### Grounding

Після мовного контролю KnowledgeHub:

1. ділить відповідь на твердження;
2. створює embeddings тверджень;
3. порівнює їх із retrieved fragments;
4. додає lexical overlap та retrieval prior;
5. відкидає непідтверджені твердження;
6. сам додає citations `[1]`, `[2]` тощо.

### Startup

`torch`, `transformers` і `sentence-transformers` завантажуються ліниво, щоб звичайний login/health/CRUD не чекав ініціалізації ML-стеку.

## Документація

- `docs/research/rag_v1.md`
- `docs/research/claim_grounding.md`
- `docs/research/ukrainian_rag_v1_2.md`
- `docs/research/ukrainian_quality_layer_v1_3.md`
- `docs/research/ukrainian_quality_v1_4.md`
- `docs/research/rag_v1_5_2.md`
