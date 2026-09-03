# ReviewFlow

[![Planning checks](https://github.com/Anoosh-p73/ReviewFlow/actions/workflows/planning-checks.yml/badge.svg)](https://github.com/Anoosh-p73/ReviewFlow/actions/workflows/planning-checks.yml)

ReviewFlow is a planned web application for managing interdisciplinary
engineering document reviews, comments, and revision workflows.

The repository currently contains two runnable application boundaries: a
restrained Next.js web shell and a small FastAPI service with typed environment
settings, structured request logs, request identifiers, process health, and a
PostgreSQL persistence foundation. Product workflows are introduced
incrementally by the roadmap; no domain tables exist yet.

## Web quick start

Install the supported Node.js and pnpm versions described in
[development setup](docs/development.md), then run from the repository root:

```powershell
pnpm install --frozen-lockfile
pnpm dev
```

The planning-stage web shell listens on `http://localhost:3000`. It contains no
product data, API integration, authentication, or inactive workflow controls.

## API quick start

Install the supported `uv` and Python versions described in
[development setup](docs/development.md), start PostgreSQL, apply migrations,
and run the API from the repository root:

```powershell
uv --directory apps/api sync --locked --all-groups
pnpm db:up
pnpm db:migrate
pnpm dev:api
```

The API listens on `http://127.0.0.1:8000`. Its current HTTP contract is:

```text
GET /health/live
GET /health/ready
```

Liveness proves only that the process is alive. Readiness separately probes
PostgreSQL and returns HTTP 503 without sensitive diagnostics when unavailable.

## Planning documents

- [Initial architecture proposal](docs/architecture.md)
- [Incremental development roadmap](docs/roadmap.md)
- [CI/CD strategy](docs/ci-cd.md)
- [Development setup](docs/development.md)
- [Contributor instructions](AGENTS.md)

## Current automation

GitHub Actions currently validates the planning documents and repository
hygiene on pull requests and pushes to `main`. Application CI, PostgreSQL
integration tests, and deployment are added at the roadmap stages where those
boundaries become real. Run the current repository check locally with:

```powershell
./scripts/validate-planning.ps1
```

Run `pnpm lint`, `pnpm format:check`, `pnpm typecheck`, `pnpm test`, and
`pnpm build` for the current application quality checks. See the development
setup for deterministic installation, configuration, and manual verification
commands.
