# KnowledgeHub — Railway deployment for Lab 4

This deployment profile is intentionally lightweight so it can fit a
free/trial cloud environment and give repeatable performance results.

## Included in Railway Lite

- Vue 3 production frontend
- FastAPI REST API
- PostgreSQL + Alembic
- registration/login/session auth
- collections
- PDF/DOCX/TXT upload and text extraction
- persistent document files when a Railway Volume is attached
- lexical PostgreSQL search
- admin API/UI
- health endpoint: `/api/v1/health`

## Disabled only in Railway Lite

- sentence-transformers model loading
- semantic search
- hybrid search
- local Qwen LLM
- RAG generation

The normal local KnowledgeHub configuration remains unchanged.

## Railway setup

1. Create a Railway project from the GitHub repository.
2. Add a PostgreSQL service.
3. On the KnowledgeHub service, add:
   `DATABASE_URL=${{Postgres.DATABASE_URL}}`
4. Add a Volume to the KnowledgeHub service and mount it at `/data`.
5. In Settings -> Networking, generate a public domain.
6. Set the healthcheck path to `/api/v1/health`.
7. Deploy.

Railway injects `PORT`; the Dockerfile listens on it automatically.
The container runs `alembic upgrade head` before Uvicorn starts.

Vue and FastAPI are served from one public origin, so auth cookies,
CSRF and API calls work without separate CORS configuration.
