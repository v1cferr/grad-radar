{
  # ═══════════════════════════════════════════════════════════════════════════
  # GradRadar — toolchain de HOST.
  #
  # Este flake NÃO empacota as dependências da aplicação: essas vivem em
  # backend/uv.lock e frontend/web/pnpm-lock.yaml, e o runtime sobe pelo
  # docker-compose.dev.yml (`just dev`). O papel deste devShell é o que precisa
  # existir FORA do container: LSP/editor, lint, os CLIs que o justfile chama e
  # o cliente psql.
  #
  # POR QUÊ assim: mantém a máquina host limpa (nada de node/pnpm/caddy
  # instalados globalmente) e deixa o ambiente reprodutível por clone via
  # direnv, que já está habilitado em dotfiles/home/shell/cli.nix.
  #
  # Pegadinha: `nixos-unstable` aqui é deliberadamente independente do canal do
  # host (dotfiles pina nixos-26.05). Um projeto não deve arrastar o sistema.
  # ═══════════════════════════════════════════════════════════════════════════
  description = "GradRadar — host dev toolchain (deps da app ficam em backend/uv.lock e frontend/web/pnpm-lock.yaml)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f (import nixpkgs { inherit system; }));
    in
    {
      formatter = forAllSystems (pkgs: pkgs.nixfmt-tree);

      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            # ── Backend ──────────────────────────────────────────────────────
            python313 # interpretador nativo p/ o uv usar (ver env abaixo); casa com o python:3.13-slim do Dockerfile
            uv # gerencia backend/.venv a partir do uv.lock

            # ── Frontend ─────────────────────────────────────────────────────
            nodejs_22 # casa com o node:22-alpine do compose
            pnpm # instala a partir do pnpm-lock.yaml (dispensa corepack no host)

            # ── Infra ────────────────────────────────────────────────────────
            just # task runner: `just dev` sobe o compose (ver justfile)
            caddy # ausente no host — usado p/ `caddy fmt`/`caddy validate` no deploy/Caddyfile
            postgresql_17 # só o cliente psql; casa com o postgres:17-alpine do compose

            git

            # ── E2E ──────────────────────────────────────────────────────────
            # Browsers do Playwright já buildados p/ Nix. Sem isso o
            # `playwright install` baixaria binários não-FHS que não rodam aqui.
            playwright-driver.browsers
          ];

          env = {
            # No NixOS o CPython standalone que o uv baixa não roda (sem FHS).
            # Força o uv a usar o python313 do Nix, nunca baixar um.
            UV_PYTHON_DOWNLOADS = "never";
            UV_PYTHON_PREFERENCE = "only-system";

            # Usa os browsers do Nix em vez de baixar. A versão do pacote npm
            # @playwright/test PRECISA casar com a do driver — o banner do
            # shellHook imprime a do driver justamente p/ conferir na hora.
            PLAYWRIGHT_BROWSERS_PATH = "${pkgs.playwright-driver.browsers}";
            PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS = "true";
          };

          # NOTA p/ a fase de scraping/PDF (F5): quando entrarem lxml e wheels
          # binários do PyPI, este shellHook vai precisar de LD_LIBRARY_PATH com
          # stdenv.cc.cc.lib + zlib (eles linkam libstdc++, que no NixOS não está
          # no path padrão). Hoje nada aqui compila C, então fica de fora.
          shellHook = ''
            echo "grad-radar devShell → python $(python3 --version 2>&1 | cut -d' ' -f2) · node $(node --version) · uv $(uv --version | cut -d' ' -f2) · pnpm $(pnpm --version) · caddy $(caddy version | head -1 | cut -d' ' -f1)"
            echo "playwright-driver: ${pkgs.playwright-driver.version} — o @playwright/test do pnpm precisa casar com essa versão."
          '';
        };
      });
    };
}
