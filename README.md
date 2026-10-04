# KnowledgeHub

KnowledgeHub — вебплатформа для керування дослідницькими документами, повнотекстового, семантичного та гібридного пошуку, а також побудови доказової бази для RAG.

## Структура

```text
KnowledgeHub/
├── backend/
│   ├── app/
│   │   ├── api/              # REST API
│   │   ├── baza_danykh/      # підключення до PostgreSQL
│   │   ├── bezpeka/          # сесії, CSRF, паролі, файли
│   │   ├── modeli/           # SQLAlchemy models
│   │   ├── parsers/          # PDF / DOCX / TXT parsing
│   │   ├── repositories/     # доступ до даних
│   │   ├── schemas/          # API / service schemas
│   │   ├── services/         # бізнес-логіка, retrieval, RAG
│   │   ├── routes/           # стабільний Jinja frontend ЛР1
│   │   ├── templates/        # Jinja templates
│   │   └── static/           # Jinja static files
│   ├── migrations/
│   └── scripts/
├── frontend/
│   └── src/
│       ├── api/              # модульний API client
│       ├── components/       # reusable Vue components
│       ├── composables/
│       ├── router/
│       ├── styles/
│       └── views/
└── docs/
```

## Backend

FastAPI + PostgreSQL + SQLAlchemy + Alembic.

Реалізовано:

- registration / login / logout;
- server-side sessions;
- Argon2 password hashing;
- CSRF protection;
- user ownership checks;
- administrator role;
- collections CRUD;
- PDF / DOCX / TXT upload and parsing;
- persistent document chunks and embeddings;
- lexical search;
- semantic search;
- hybrid search;
- document preview / download;
- chunk-level research retrieval;
- grounded RAG generation through a local LLM;
- citation validation and extractive fallback.

Jinja2-версія зберігається як стабільна реалізація лабораторної роботи №1 і надалі не є основним frontend.

## Frontend

Основний frontend — Vue 3 + Vue Router + Vite.

Frontend розділений на:

- `api/` — окремі модулі auth, collections, documents, search, research, admin;
- `components/collections/` — компоненти колекцій;
- `components/documents/` — список і завантаження документів;
- `components/search/` — пошуковий інтерфейс;
- `components/research/` — RAG, відповідь і джерела;
- `components/common/` — спільні UI-компоненти;
- `views/` — сторінки маршрутизатора.

## Пошук

KnowledgeHub підтримує три режими:

- **Lexical** — PostgreSQL Full Text Search;
- **Semantic** — multilingual sentence embeddings;
- **Hybrid** — 30% lexical + 70% semantic.

## RAG

Research retrieval працює на рівні `document_chunks`.

Для запитання користувача система:

1. створює embedding запиту;
2. обчислює semantic similarity для фрагментів;
3. обчислює lexical overlap;
4. формує hybrid chunk score;
5. вибирає релевантні фрагменти з обмеженням на дублювання одного документа;
6. будує evidence-only prompt;
7. за вибором користувача формує extractive draft або локальну LLM-відповідь;
8. перевіряє citations `[n]`;
9. у разі некоректної генерації автоматично повертається до extractive fallback;
10. повертає відповідь разом із конкретними джерелами.

Локальний режим за замовчуванням використовує:

```text
Qwen/Qwen2.5-0.5B-Instruct
```

API-ключ не потрібний. Модель завантажується ліниво при першому використанні та кешується Hugging Face.

Детальніше: `docs/research/rag_v1.md`.

## Архітектура

```text
Vue
  ↓ REST API
FastAPI
  ↓
Services
  ↓
Repositories
  ↓
PostgreSQL
```

RAG pipeline:

```text
Question
  ↓
Query embedding
  ↓
Chunk retrieval
  ↓
Semantic + lexical ranking
  ↓
Evidence context
  ↓
Local LLM
  ↓
Citation validation
  ↓
Grounded answer + sources
```
