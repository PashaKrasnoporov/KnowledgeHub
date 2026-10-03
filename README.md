# KnowledgeHub

Основний проєкт KnowledgeHub.

## Структура

### backend/
FastAPI backend:

- REST API
- PostgreSQL
- SQLAlchemy
- Alembic
- authentication / sessions
- security
- collections
- documents
- lexical search
- semantic search
- hybrid search
- embeddings
- administration
- Jinja2 legacy frontend

Jinja2-версія зберігається як стабільна реалізація лабораторної роботи №1.

### frontend/
Основний frontend на Vue 3 + Vite.

Усі подальші функціональні можливості KnowledgeHub розвиваються тут.

### docs/
Документація:

- architecture
- api
- labs
- deployment
- research

## Архітектура

Vue
    ↓ REST API
FastAPI
    ↓
Services
    ↓
Repositories
    ↓
PostgreSQL

Jinja2 залишається всередині backend як стабільний legacy frontend.
