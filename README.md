# ReviewFlow

[![Planning checks](https://github.com/Anoosh-p73/ReviewFlow/actions/workflows/planning-checks.yml/badge.svg)](https://github.com/Anoosh-p73/ReviewFlow/actions/workflows/planning-checks.yml)

ReviewFlow is a planned web application for managing interdisciplinary
engineering document reviews, comments, and revision workflows.

The repository is currently in its architecture and bootstrap-planning stage;
the application has not been implemented yet.

## Planning documents

- [Initial architecture proposal](docs/architecture.md)
- [Incremental development roadmap](docs/roadmap.md)
- [CI/CD strategy](docs/ci-cd.md)
- [Development setup](docs/development.md)
- [Contributor instructions](AGENTS.md)

## Current automation

GitHub Actions validates the planning documents and repository hygiene on pull
requests and pushes to `main`. Application builds, PostgreSQL integration tests,
and deployment are added at the roadmap stages where those artifacts become
real. Run the current check locally with:

```powershell
./scripts/validate-planning.ps1
```

The root workspace and supported tool versions are defined, but no application
exists yet. See the development setup for the deterministic install and current
commands.
