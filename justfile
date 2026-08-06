# GradRadar — atalhos de desenvolvimento.
# Requer: docker + just (o just vem do devShell; entre no diretório com direnv).
# Rode `just` sem args para ver as receitas.

set shell := ["bash", "-uc"]

compose := "docker compose -f docker-compose.dev.yml"

# lista as receitas (default ao rodar `just` sem args)
default:
    @just --list

# sobe o stack de dev com HOT RELOAD em foreground → https://grad-radar.localhost
dev: _require-env
    {{compose}} up --build

# igual ao `dev`, mas em background (detached)
up: _require-env
    {{compose}} up --build -d

# logs ao vivo — todos os serviços, ou um só: `just logs caddy`
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
rebuild-frontend:
    {{compose}} up -d --force-recreate frontend

# reset PRISTINE: apaga volumes (banco, node_modules, .next, CA do Caddy) e recria
# ATENÇÃO: isto DESTRÓI os dados do Postgres e invalida a CA já confiada.
fresh: _require-env
    {{compose}} down -v --remove-orphans
    {{compose}} up --build

# psql no banco do projeto (usa as credenciais do .env)
psql:
    {{compose}} exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'

# extrai a CA raiz interna do Caddy e mostra como confiá-la no NixOS
trust-ca:
    #!/usr/bin/env bash
    set -euo pipefail
    dest=deploy/caddy-root.crt
    {{compose}} exec -T caddy cat /data/caddy/pki/authorities/local/root.crt > "$dest"
    echo "✓ CA raiz extraída para $dest"
    echo
    echo "O Caddy só gera essa CA no primeiro start com TLS — se o arquivo saiu"
    echo "vazio, abra https://grad-radar.localhost uma vez e rode de novo."
    echo
    echo "Para confiar system-wide (o NixOS não aceita jogar cert em /etc/ssl/certs):"
    echo
    echo "  1. copie o cert para os dotfiles:"
    echo "       cp $dest ~/Projects/GitHub/v1cferr/dotfiles/system/core/caddy-grad-radar-root.crt"
    echo "  2. no módulo correspondente dos dotfiles, adicione:"
    echo "       security.pki.certificateFiles = [ ./caddy-grad-radar-root.crt ];"
    echo "  3. rebuild do sistema."
    echo
    echo "Sem esse passo o browser mostra aviso de certificado — em dev é"
    echo "inofensivo e clicável, e no CLI basta 'curl -k'."

# valida o Caddyfile sem subir o stack
validate:
    caddy validate --adapter caddyfile --config deploy/Caddyfile

# formata os arquivos Nix (nixfmt-tree, igual aos dotfiles)
fmt:
    nix fmt

# guarda: o compose lê o .env por env_file, e a falta dele dá erro obscuro
_require-env:
    @test -f .env || { echo "ERRO: .env ausente. Rode: cp .env.example .env  (e troque a senha)"; exit 1; }
