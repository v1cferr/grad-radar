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
rebuild-frontend:
    {{compose}} up -d --force-recreate frontend

# reset PRISTINE: apaga volumes (banco, node_modules, .next) e recria
# ATENÇÃO: isto DESTRÓI os dados do Postgres.
fresh: _require-env
    {{compose}} down -v --remove-orphans
    {{compose}} up --build

# psql no banco do projeto (usa as credenciais do .env)
psql:
    {{compose}} exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'

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
