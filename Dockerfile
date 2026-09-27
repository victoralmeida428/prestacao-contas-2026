# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.9.13 /uv /uvx /bin/

WORKDIR /app

# 1) Dependencias de runtime (camada cacheavel, sem o projeto)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 2) Codigo e dados do dashboard (parquet enxuto, ~16 MB)
COPY src ./src
COPY data/dashboard ./data/dashboard
RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["sh", "-c", "gunicorn -w 1 --threads 4 -b 0.0.0.0:${PORT:-8000} --timeout 120 candidatos.app:server"]
