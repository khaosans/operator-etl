# Operator ETL — graph-runner image (multi-cloud)
# Build targets:
#   docker build --build-arg CLOUD_EXTRA=gcp -t operator-etl:gcp .
#   docker build --build-arg CLOUD_EXTRA=aws -t operator-etl:aws .
#   docker build --build-arg CLOUD_EXTRA=azure -t operator-etl:azure .
FROM python:3.12-slim AS base

ARG CLOUD_EXTRA=gcp

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    CLOUD_EXTRA=${CLOUD_EXTRA}

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY sql ./sql
COPY pipelines ./pipelines
COPY samples ./samples

# Sync cloud-specific optional extras (+ llm). Default remains gcp for Cloud Build.
RUN uv sync --frozen --extra ${CLOUD_EXTRA} --extra llm --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080

# Portable trigger surface: POST /run (Pub/Sub + Event Grid are provider adapters)
CMD ["uvicorn", "operator_etl_gcp.http.app:app", "--host", "0.0.0.0", "--port", "8080"]
