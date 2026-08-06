# GradRadar

> Discover, compare, and track graduate opportunities.

GradRadar is a self-hosted system for discovering, organizing, comparing, and tracking graduate programs
and academic opportunities.

The project is initially focused on tuition-free, in-person graduate programs in Computer Science, Artificial
Intelligence, Machine Learning, Natural Language Processing, Large Language Models, Software Engineering, and
related fields in São Carlos, Brazil — especially programs connected to the UFSCar Department of Computing and
the USP Institute of Mathematics and Computer Sciences (ICMC).

**Status:** F0 — infrastructure foundation. No domain model yet; see [Roadmap](#roadmap).

---

## Getting started

Requirements: [Nix](https://nixos.org) with flakes, [direnv](https://direnv.net), and Docker. Everything else
comes from the dev shell — nothing is installed on the host.

```bash
direnv allow                 # once per clone: loads the devShell from flake.nix
cp .env.example .env         # then change POSTGRES_PASSWORD
just dev                     # builds and starts the whole stack
```

Open <https://grad-radar.localhost>.

Run `just` with no arguments to list every recipe. The most useful ones:

| Recipe | What it does |
| --- | --- |
| `just dev` | Start the stack with hot reload, in the foreground |
| `just up` | Same, detached |
| `just logs [service]` | Follow logs — all services, or one (`just logs caddy`) |
| `just down` | Tear down, preserving volumes |
| `just fresh` | **Destructive** — drop volumes (database included) and rebuild |
| `just psql` | Open `psql` against the project database |
| `just validate` | Validate `deploy/Caddyfile` without starting anything |
| `just trust-ca` | Extract Caddy's internal root CA and print how to trust it |

### Things worth knowing

- **Certificate warning on first load.** Caddy terminates TLS with its own internal CA, because `.localhost`
  cannot be validated by ACME. The warning is harmless in development and click-through; run `just trust-ca`
  to get rid of it (it prints the `security.pki.certificateFiles` snippet to add to your NixOS config), or use
  `curl -k` from the CLI.
- **PostgreSQL is published on `127.0.0.1:5433`, not 5432.** Port 5432 on this host already belongs to another
  project's container. Inside the compose network the database still listens on 5432, which is the port that
  goes in `DATABASE_URL`.
- **`grad-radar.localhost` needs no `/etc/hosts` entry.** `nss-myhostname` resolves any `*.localhost` name to
  `127.0.0.1`/`::1` automatically. To reach the app from other devices on the LAN or over Tailscale, change the
  site address in `deploy/Caddyfile` to a real hostname and publish a matching DNS record.
- **`.env` is not optional.** The compose file loads it via `env_file`, and `just` refuses to start without it.

---

## Architecture

A single Caddy host is the only entry point; neither the backend nor the frontend publishes a port. Frontend
and API therefore share an origin, which removes CORS entirely and keeps the backend port out of the JS bundle.

```
browser ──► caddy :443 ──┬── /api/*  ──► backend  (FastAPI, :8000) ──► db (PostgreSQL, :5432)
                         └── /*      ──► frontend (Next.js, :3000) ──┘
```

| Layer | Choice |
| --- | --- |
| Frontend | Next.js 15 (App Router), TypeScript, Tailwind v4 |
| Backend | FastAPI, SQLAlchemy 2.0 (async), Python 3.13 |
| Database | PostgreSQL 17, self-hosted in a container |
| Reverse proxy | Caddy 2, `tls internal` |
| Dev environment | Nix flake dev shell + direnv; `uv` for Python, `pnpm` for Node |
| Task runner | `just` |

`flake.nix` provides the **host** toolchain only — editor/LSP tooling and the CLIs `just` invokes. Application
dependencies live in `backend/uv.lock` and `frontend/web/pnpm-lock.yaml`, and the runtime always runs in
containers. This keeps the host machine clean and the environment reproducible per clone.

### Layout

```
backend/            FastAPI service (F0: a single /api/health endpoint)
frontend/web/       Next.js app (F0: a smoke-test page)
deploy/Caddyfile    Reverse proxy and local TLS
docs/               Design notes
flake.nix           Host dev shell
justfile            Development shortcuts
```

---

## Motivation

Information about graduate programs is fragmented across institutional websites, admissions notices, PDF
documents, faculty pages, research group websites, academic calendars, and application systems. That makes
practical questions hard to answer:

- Which programs are currently accepting applications, and when is the next notice published?
- Which ones are in person and tuition-free?
- Which research lines involve AI, NLP, or LLMs, and which faculty members are accepting students?
- Are the class schedules compatible with a full-time job?
- Which documents are required, and is special-student enrollment available first?
- Which scholarships exist, and do they forbid formal employment?
- Which opportunities actually match each candidate's academic and professional goals?

GradRadar centralizes this into a structured decision-making system, tracked per candidate.

## Scope

The first tracked programs are the UFSCar Computer Science graduate program (PPGCC) and the ICMC-USP Computer
Science and Computational Mathematics program (PPG-CCMC), covering both regular and special-student admissions.

Planned modules: program catalog, research lines, faculty and laboratories, admissions notices with version
diffing, courses and schedules, costs and scholarships, document checklists, a per-candidate application
pipeline, and opportunity scoring. The analysis structure is:

```
institution → program → research area → faculty member → laboratory → project → course
```

The system supports multiple candidates, each with independent interests, schedule constraints, document
checklist, application history and scores.

## Roadmap

| Phase | Contents |
| --- | --- |
| **F0** | Infrastructure foundation — dev shell, compose stack, Caddy, PostgreSQL ← **current** |
| F1 | Data model, Alembic migrations, seed data for PPGCC and PPG-CCMC, candidate profiles |
| F2 | REST API — CRUD, filters, opportunity scoring |
| F3 | UI — program list and filters, program detail, deadline calendar, pipeline board, checklists |
| F4 | Notifications — deadline and change alerts |
| F5 | Automated monitoring — registered official sources, page and PDF change detection, extraction |

Automated scraping is deliberately last: the manual workflow and the data model have to be validated first.

## Development principles

- Official sources first, and always preferred over third-party aggregators.
- Traceable, verifiable information — preserve the original source and record when it was last checked.
- Manual-first MVP; automation only after the domain is validated.
- Self-hosted whenever practical, with reproducible development environments.
- Multiple candidate support from the start.
- English-first codebase and documentation.

## License

To be defined.
