FROM node:22-alpine AS frontend-build

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
COPY VERSION /VERSION
RUN npm ci

COPY frontend/ ./

ENV VITE_DEPLOYMENT_PROFILE=railway-ml

RUN npm run build


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

ENV DEPLOYMENT_PROFILE=railway-ml
ENV ML_ENABLED=true
ENV LLM_ENABLED=false
ENV COOKIE_SECURE=true
ENV FASTEMBED_CACHE_PATH=/opt/fastembed_cache

WORKDIR /app/backend

COPY VERSION /app/VERSION
COPY backend/requirements.railway.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', cache_dir='/opt/fastembed_cache', threads=2, providers=['CPUExecutionProvider'])"

COPY backend/ /app/backend/
COPY --from=frontend-build /frontend/dist /app/frontend_dist

RUN mkdir -p /data/uploads

CMD ["/bin/sh", "-c", "alembic upgrade head && python -m app.scripts.backfill_embeddings && exec uvicorn app.production:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips=*"]
