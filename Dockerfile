# Operator ETL — graph-runner image (multi-cloud)
# Build targets:
#   docker build --build-arg CLOUD_EXTRA=gcp -t operator-etl:gcp .
#   docker build --build-arg CLOUD_EXTRA=aws -t operator-etl:aws .
#   docker build --build-arg CLOUD_EXTRA=azure -t operator-etl:azure .
FROM python:3.14-slim AS base

ARG CLOUD_EXTRA=gcp

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    CLOUD_EXTRA=${CLOUD_EXTRA}

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --home-dir /app --shell /usr/sbin/nologin app

# Pin uv release tag (Dependabot docker ecosystem tracks this Dockerfile).
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY sql ./sql
COPY pipelines ./pipelines
COPY samples ./samples

# Sync cloud-specific optional extras (+ llm). Default remains gcp for Cloud Build.
RUN uv sync --frozen --extra ${CLOUD_EXTRA} --extra llm --no-dev \
    && chown -R app:app /app

ENV PATH="/app/.venv/bin:$PATH"

USER app

EXPOSE 8080

# Portable trigger surface: POST /run (Pub/Sub + Event Grid are provider adapters)
# Bind all interfaces for Cloud Run / containers (bandit B104 accepted — see SECURITY-HARDENING.md)
CMD ["uvicorn", "operator_etl_gcp.http.app:app", "--host", "0.0.0.0", "--port", "8080"]
