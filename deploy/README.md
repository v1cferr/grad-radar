# deploy/

**There is no Caddyfile here on purpose.**

GradRadar is served by the **central Caddy**, a systemd service declared in the dotfiles repository:

```
~/Projects/GitHub/v1cferr/dotfiles/system/services/caddy.nix
```

That module owns the vhost, the TLS certificate and the port map for every self-hosted project on this
machine. GradRadar's entry is:

| | |
| --- | --- |
| Hostname | `pos.v1cferr.dev` |
| Frontend | `127.0.0.1:3006` |
| API | `127.0.0.1:8006` (path `/api/*`, prefix preserved) |
| TLS | wildcard `*.v1cferr.dev`, Let's Encrypt via Cloudflare DNS-01 |
| Auth | HTTP basic auth for requests from outside the home network |

## Why it is not here

Only one process can bind port 443. A per-project reverse proxy cannot coexist with another project's, and
the loopback port map needs a single owner — otherwise the next collision is silent. Centralising it also
means one wildcard certificate instead of one ACME order per project.

`docker-compose.dev.yml` therefore publishes both services on **loopback only**; the port is the interface
with Caddy, not with the network.

## Changing the routing

Edit the module in the dotfiles repo and rebuild the system — not this directory:

```bash
cd ~/Projects/GitHub/v1cferr/dotfiles
$EDITOR system/services/caddy.nix
nixos-rebuild build --flake .#nixos-kingston   # validate first
sudo nixos-rebuild switch --flake .#nixos-kingston
```

Changing the ports in `docker-compose.dev.yml` requires changing them in that module too. The port map lives
in its header comment.
