# KnowledgeHub

KnowledgeHub — україномовно орієнтована вебплатформа для керування дослідницькими документами, повнотекстового, семантичного та гібридного пошуку, а також grounded RAG.

## Основний стек

- FastAPI
- PostgreSQL
- SQLAlchemy + Alembic
- Vue 3 + Vue Router + Vite
- sentence-transformers
- локальна instruction LLM

## RAG v1.3

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
Ukrainian language quality gate
  ↓
Optional strict second editorial pass
  ↓
Claim-level grounding
  ↓
Automatic citations
  ↓
Verified answer + sources
```

### Ukrainian-first

Українська — основна мова генерації.

У режимі `Українська` кожна LLM-відповідь обов'язково проходить окремий редакторський етап. Якщо після нього залишаються явні кальки, російські форми або неприродні словотворення, запускається друге суворіше редагування.

Якщо текст не проходить мовний контроль після двох спроб, KnowledgeHub не показує його як якісну відповідь і використовує безпечний fallback.

### Grounding

Після мовного редагування KnowledgeHub:

1. ділить відповідь на твердження;
2. створює embeddings тверджень;
3. порівнює їх із retrieved fragments;
4. додає lexical overlap та retrieval prior;
5. відкидає непідтверджені твердження;
6. сам додає citations `[1]`, `[2]` тощо.

### Evidence gate

Якщо retrieved evidence слабке, генерація не запускається.

### UX

Research UI містить:

- spinner біля кнопки;
- індикативну смугу активного процесу;
- elapsed time;
- орієнтовний етап обробки;
- Ctrl+Enter;
- лічильник символів;
- копіювання відповіді;
- clickable citations;
- `✓ Відповідь перевірена`;
- підказки для `Покриття` та `Доказовість`;
- `Український контроль ✓`;
- кількість редакторських проходів;
- згортуваний claim audit.

## Документація

- `docs/research/rag_v1.md`
- `docs/research/claim_grounding.md`
- `docs/research/ukrainian_rag_v1_2.md`
- `docs/research/ukrainian_quality_layer_v1_3.md`
