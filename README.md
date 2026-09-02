# ReviewFlow

[![Planning checks](https://github.com/Anoosh-p73/ReviewFlow/actions/workflows/planning-checks.yml/badge.svg)](https://github.com/Anoosh-p73/ReviewFlow/actions/workflows/planning-checks.yml)

ReviewFlow is a planned web application for managing interdisciplinary
engineering document reviews, comments, and revision workflows.

The repository currently contains the first runnable application boundary: a
small FastAPI service with typed environment settings, structured request logs,
request identifiers, and process liveness. Product workflows, persistence, and
the web application are introduced incrementally by the roadmap.

## API quick start

Install the supported `uv` and Python versions described in
[development setup](docs/development.md), then run from the repository root:

```powershell
uv --directory apps/api sync --locked --all-groups
pnpm dev
```

The API listens on `http://127.0.0.1:8000`. Its current HTTP contract is:

```text
GET /health/live
```

The response proves only that the process is alive. It deliberately does not
check a database or another external service.

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

Run `pnpm lint`, `pnpm typecheck`, and `pnpm test` for the API quality checks.
See the development setup for deterministic installation, configuration, and
manual verification commands.
