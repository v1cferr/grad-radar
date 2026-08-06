# GradRadar backend — imagem de DESENVOLVIMENTO.
#
# POR QUE um Dockerfile em vez de `image: python:3.13-slim` + command (como faz o
# frontend com node:22-alpine): o backend precisa do `uv` no PATH e do `curl`
# para o healthcheck. Assar isso na imagem evita baixá-los a cada start.
#
# POR QUE as deps NÃO são instaladas no build: o docker-compose.dev.yml faz
# bind-mount de ./backend sobre /app, o que sombrearia qualquer coisa instalada
# aqui. O `command` do compose roda `uv sync` dentro do volume /app/.venv.
FROM python:3.13-slim

# uv vindo da imagem oficial (mais rápido e reprodutível que pip install uv).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# curl: usado pelo healthcheck do compose (`curl -f .../api/health`).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/app/.venv \
    # A imagem já traz CPython 3.13; nunca baixar outro interpretador.
    UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    # Logs do uvicorn aparecem em `just logs backend` sem esperar o buffer.
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
