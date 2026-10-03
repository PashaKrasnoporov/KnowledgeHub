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
│   │   ├── services/         # бізнес-логіка та пошук
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
- RAG research context endpoint.

Jinja2-версія зберігається як стабільна реалізація лабораторної роботи №1 і надалі не є основним frontend.

## Frontend

Основний frontend — Vue 3 + Vue Router + Vite.

Frontend розділений на:

- `api/` — окремі модулі auth, collections, documents, search, research, admin;
- `components/collections/` — компоненти колекцій;
- `components/documents/` — список і завантаження документів;
- `components/search/` — пошуковий інтерфейс;
- `components/research/` — дослідницький режим;
- `components/common/` — спільні UI-компоненти;
- `views/` — сторінки маршрутизатора.

## Пошук

KnowledgeHub підтримує три режими:

- **Lexical** — PostgreSQL Full Text Search;
- **Semantic** — multilingual sentence embeddings;
- **Hybrid** — 30% lexical + 70% semantic.

## Дослідницький режим / RAG foundation

Нова функція працює на рівні `document_chunks`.

Для запитання користувача система:

1. створює embedding запиту;
2. обчислює semantic similarity для фрагментів;
3. обчислює lexical overlap;
4. формує hybrid chunk score;
5. вибирає релевантні фрагменти з обмеженням на дублювання одного документа;
6. формує витягувальну чернетку відповіді;
7. повертає джерела, номери фрагментів і окремі оцінки semantic / lexical.

Цей етап є фундаментом для наступного підключення генеративної LLM: retrieval і source attribution уже відокремлені від майбутнього answer generation.

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

Для semantic / research retrieval:

```text
Question
  ↓
Embedding
  ↓
Document chunks
  ↓
Semantic + lexical scoring
  ↓
Ranked evidence
  ↓
Extractive draft + sources
```
