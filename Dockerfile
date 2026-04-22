FROM python:3.12-slim-trixie AS builder

ENV UV_NO_CACHE=1 \
  UV_LINK_MODE=copy \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:0.11.3 /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock README.md mirsi-automation.json ./

RUN uv sync --locked --no-dev --no-install-project

COPY . .

RUN uv sync --locked --no-dev

FROM python:3.12-slim-trixie AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PATH="/app/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
  libpango-1.0-0 \
  libpangoft2-1.0-0 \
  && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app
COPY --from=builder --chown=appuser:appuser /app/ /app/

RUN mkdir -p /app/logs && chown appuser:appuser /app/logs

USER appuser

ENTRYPOINT ["python", "main.py"]
