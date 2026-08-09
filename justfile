# GradRadar — atalhos de desenvolvimento.
# Requer: docker + just (o just vem do devShell; entre no diretório com direnv).
# Rode `just` sem args para ver as receitas.

set shell := ["bash", "-uc"]

compose := "docker compose -f docker-compose.dev.yml"

# lista as receitas (default ao rodar `just` sem args)
default:
    @just --list

# sobe o stack de dev com HOT RELOAD em foreground → https://pos.v1cferr.dev
dev: _require-env
    {{compose}} up --build

# igual ao `dev`, mas em background (detached)
up: _require-env
    {{compose}} up --build -d

# logs ao vivo — todos os serviços, ou um só: `just logs backend`
# (o Caddy não está aqui: `journalctl -u caddy -f`)
logs service="":
    {{compose}} logs -f {{service}}

# derruba o stack (remove órfãos, preserva os volumes)
down:
    {{compose}} down --remove-orphans

# estado atual dos containers do projeto
ps:
    {{compose}} ps

# recria só o BACKEND — use após mudar deps (backend/uv.lock)
rebuild-backend:
    {{compose}} up -d --build --force-recreate backend

# recria só o FRONTEND — use após mudar package.json/pnpm-lock.yaml
#
# APAGA o volume de node_modules de propósito. O container é alpine (musl) e o
# host é glibc; quando o grafo de dependências muda, o `--frozen-lockfile` sobre
# um volume já populado deixa uma árvore MISTA — o sintoma real foi
# `Cannot find module '../lightningcss.linux-x64-musl.node'` e HTTP 500 no Next.
# Reinstalar do zero custa ~15s e evita uma hora de investigação.
rebuild-frontend:
    {{compose}} rm -sf frontend
    -docker volume rm grad-radar_frontend_node_modules grad-radar_frontend_next
    {{compose}} up -d frontend

# reset PRISTINE: apaga volumes (banco, node_modules, .next) e recria
# ATENÇÃO: isto DESTRÓI os dados do Postgres.
fresh: _require-env
    {{compose}} down -v --remove-orphans
    {{compose}} up --build

# psql no banco do projeto (usa as credenciais do .env)
psql:
    {{compose}} exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'

# aplica as migrations pendentes
migrate:
    {{compose}} exec backend sh -c 'cd /app && alembic upgrade head'

# cria uma migration a partir do diff entre os modelos e o banco
# ATENÇÃO: revise o arquivo gerado. O autogenerate NÃO dropa ENUM no downgrade —
# sem acrescentar os DROP TYPE à mão, o próximo `upgrade` morre com DuplicateObject.
migration name:
    {{compose}} exec backend sh -c 'cd /app && alembic revision --autogenerate -m "{{name}}"'

# popula o banco com os dados verificados do PPGCC (idempotente)
seed:
    {{compose}} exec backend sh -c 'cd /app && python -m app.seed'

# e2e no navegador contra o stack NO AR (requer `just up` antes)
# Browsers vêm do devShell; @playwright/test tem que casar com a versão que o
# shellHook imprime.
e2e:
    cd frontend/web && pnpm exec playwright test

# verifica as fontes oficiais uma vez e grava o que mudou
# Uma PASSADA só, de propósito: o agendamento mora fora (systemd timer/cron),
# onde dá para declarar, inspecionar e desligar sem mexer no código — e um
# scheduler dentro do processo morreria junto com o container.
monitor:
    {{compose}} exec backend sh -c 'cd /app && python -m app.monitor'

# testes + lint do backend
test:
    {{compose}} exec backend sh -c 'cd /app && python -m pytest -q && python -m ruff check app tests'

# status do ingress: o proxy NÃO é deste projeto, vive nos dotfiles
ingress:
    @echo "O ingress é do Caddy central (systemd), não deste compose:"
    @echo "  módulo:  ~/Projects/GitHub/v1cferr/dotfiles/system/services/caddy.nix"
    @echo "  vhost:   pos.v1cferr.dev  →  127.0.0.1:3006 (front) · 127.0.0.1:8006 (/api/*)"
    @echo
    systemctl status caddy --no-pager | head -5 || true

# formata os arquivos Nix deste repo (nixfmt-tree, igual aos dotfiles)
fmt:
    nix fmt

# guarda: o compose lê o .env por env_file, e a falta dele dá erro obscuro
_require-env:
    @test -f .env || { echo "ERRO: .env ausente. Rode: cp .env.example .env  (e troque a senha)"; exit 1; }
