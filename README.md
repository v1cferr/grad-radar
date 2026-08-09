# GradRadar

> Discover, compare, and track graduate opportunities.

GradRadar is a self-hosted system for discovering, organizing, comparing, and tracking graduate programs
and academic opportunities.

The project is initially focused on tuition-free, in-person graduate programs in Computer Science, Artificial
Intelligence, Machine Learning, Natural Language Processing, Large Language Models, Software Engineering, and
related fields in São Carlos, Brazil — especially programs connected to the UFSCar Department of Computing and
the USP Institute of Mathematics and Computer Sciences (ICMC).

**Status:** F1 — domain model, verified PPGCC/UFSCar data and a read API. See [Roadmap](#roadmap).

---

## Getting started

Requirements: [Nix](https://nixos.org) with flakes, [direnv](https://direnv.net), and Docker. Everything else
comes from the dev shell — nothing is installed on the host.

```bash
direnv allow                 # once per clone: loads the devShell from flake.nix
cp .env.example .env         # then change POSTGRES_PASSWORD
just dev                     # builds and starts the whole stack
```

Open <https://pos.v1cferr.dev>.

Run `just` with no arguments to list every recipe. The most useful ones:

| Recipe | What it does |
| --- | --- |
| `just dev` | Start the stack with hot reload, in the foreground |
| `just up` | Same, detached |
| `just logs [service]` | Follow logs — all services, or one (`just logs backend`) |
| `just down` | Tear down, preserving volumes |
| `just fresh` | **Destructive** — drop volumes (database included) and rebuild |
| `just psql` | Open `psql` against the project database |
| `just migrate` | Apply pending Alembic migrations |
| `just seed` | Load the verified PPGCC data (idempotent) |
| `just test` | Backend tests + lint |
| `just ingress` | Show where the reverse proxy lives and its current status |

### Things worth knowing

- **The reverse proxy is not part of this repo.** `pos.v1cferr.dev` is served by the central Caddy declared in
  the dotfiles (`system/services/caddy.nix`), which owns the TLS certificate and the loopback port map for
  every self-hosted project on the machine. See [`deploy/README.md`](deploy/README.md). Its logs are in
  `journalctl -u caddy`, not in `just logs`.
- **From outside the home network you get an HTTP basic auth prompt.** GradRadar has no login of its own yet,
  so Caddy gates external access; on the LAN it opens directly. Repeated failures are banned by fail2ban.
- **PostgreSQL is published on `127.0.0.1:5433`, not 5432.** Port 5432 on this host already belongs to another
  project's container. Inside the compose network the database still listens on 5432, which is the port that
  goes in `DATABASE_URL`.
- **The published ports are `3006` (frontend) and `8006` (API), loopback only.** They are the interface with
  Caddy, not with the network. Changing them requires changing the port map in the dotfiles module too.
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
| Reverse proxy | Caddy 2 (central, in the dotfiles), wildcard Let's Encrypt cert |
| Dev environment | Nix flake dev shell + direnv; `uv` for Python, `pnpm` for Node |
| Task runner | `just` |

`flake.nix` provides the **host** toolchain only — editor/LSP tooling and the CLIs `just` invokes. Application
dependencies live in `backend/uv.lock` and `frontend/web/pnpm-lock.yaml`, and the runtime always runs in
containers. This keeps the host machine clean and the environment reproducible per clone.

### Layout

```
backend/app/models/ Domain models — academic, curriculum, admission, provenance
backend/app/api.py  Read-only endpoints over the seeded domain
backend/app/seed.py Verified PPGCC data, idempotent
backend/alembic/    Migrations (the app never calls create_all)
frontend/web/       Next.js dashboard — cycles, cronograma, weekly grid
deploy/README.md    Points at the central Caddy in the dotfiles
docs/research/      Domain discovery, with a source URL per fact
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
| F0 | Infrastructure foundation — dev shell, compose stack, Caddy, PostgreSQL |
| **F1** | Data model, Alembic, verified PPGCC seed, read API ← **current** |
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
