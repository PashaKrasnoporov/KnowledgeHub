FROM node:22-alpine AS frontend-build

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

ENV VITE_DEPLOYMENT_PROFILE=railway-lite

RUN npm run build


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

ENV DEPLOYMENT_PROFILE=railway-lite
ENV ML_ENABLED=false
ENV COOKIE_SECURE=true

WORKDIR /app/backend

COPY backend/requirements.railway.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend/ /app/backend/
COPY --from=frontend-build /frontend/dist /app/frontend_dist

RUN mkdir -p /data/uploads

CMD ["/bin/sh", "-c", "alembic upgrade head && exec uvicorn app.production:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips=*"]
