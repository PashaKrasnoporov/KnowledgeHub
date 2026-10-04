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

## RAG v1.6

```text
Question
  ↓
Vectorized hybrid chunk retrieval
  ↓
Evidence confidence gate
  ↓
Short local LLM generation (1 pass by default)
  ↓
Ukrainian quality check
  ↓
Optional single rewrite only for real language problems
  ↓
Claim-level grounding with persisted source embeddings
  ↓
Automatic citations
  ↓
Verified answer + real performance timings
```

### Ukrainian-first

Українська — основна мова генерації.

`wordfreq` не використовується як абсолютний словник. Рідкісне або невідоме корпусу слово є попередженням і не може саме по собі відхилити відповідь.

Критичними залишаються:

- російські мовні форми;
- очевидні штучні словоформи;
- відомі кальковані конструкції;
- неприродні технічні сполуки.

Український rewrite більше не є обов'язковим для кожної відповіді. Він запускається лише тоді, коли система справді виявляє мовну проблему.

### Performance

RAG v1.6 прибирає два основні зайві витрати:

1. нормальна відповідь генерується одним LLM-проходом замість 2–3;
2. embeddings retrieved chunks повторно не обчислюються під час grounding — використовуються вектори, вже збережені в PostgreSQL.

Semantic retrieval виконується векторизовано через NumPy matrix multiplication. За замовчуванням LLM генерує до 160 нових токенів замість 320.

Vue у режимі Local LLM запускає фоновий warmup моделі, а відповідь показує реальні timings: retrieval, LLM, grounding і total.

### Source-preserving fallback

Якщо LLM-відповідь відхилено, KnowledgeHub не переписує першоджерела.

Система вибирає чисті релевантні речення з retrieved chunks, прибираючи лише display-noise на кшталт службових metadata та тестової нумерації.

Оригінальний текст PDF/DOCX/TXT залишається незмінним.

### Grounding

Після мовного контролю KnowledgeHub:

1. ділить відповідь на твердження;
2. створює embeddings лише нових тверджень;
3. порівнює їх із persisted embeddings retrieved chunks;
4. додає lexical overlap та retrieval prior;
5. відкидає непідтверджені твердження;
6. сам додає citations `[1]`, `[2]` тощо.

### Responsive UI

Для medium-width і mobile viewport додано окремий adaptive-readability layer: основний текст, поля, кнопки, метрики та картки стають читабельнішими, а контент краще використовує доступну ширину.

### Startup

`torch`, `transformers` і `sentence-transformers` завантажуються ліниво, щоб звичайний login/health/CRUD не чекав ініціалізації ML-стеку. Модель Local LLM може прогріватися у фоні вже після відкриття research UI.

## Документація

- `docs/research/rag_v1.md`
- `docs/research/claim_grounding.md`
- `docs/research/ukrainian_rag_v1_2.md`
- `docs/research/ukrainian_quality_layer_v1_3.md`
- `docs/research/ukrainian_quality_v1_4.md`
- `docs/research/rag_v1_5_2.md`
- `docs/research/rag_v1_6_performance.md`
