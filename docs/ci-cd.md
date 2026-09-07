# CI/CD strategy

## Current state

ReviewFlow contains runnable Next.js and FastAPI development processes, plus a
production build for the static planning-stage web shell and a local PostgreSQL
persistence foundation. It has no supported deployment artifact or domain
tables. The current GitHub Actions workflow has four independent jobs:

- repository planning and hygiene validation;
- API Ruff, formatting, strict mypy, and database-independent pytest checks;
- web ESLint, Prettier, TypeScript, Vitest, and Next.js production build checks;
  and
- Alembic application and integration tests against an ephemeral PostgreSQL
  service.

The planning and hygiene check runs locally with:

```powershell
./scripts/validate-planning.ps1
```

The workflow runs for pull requests and pushes to `main`, uses read-only
repository permissions, pins third-party actions to full commit SHAs, applies
bounded job timeouts, and cancels superseded runs. Python and pnpm download
caches are keyed from their dependency lockfiles, but every cached job still
executes locked or frozen dependency installation. The PostgreSQL job uses
committed CI-only credentials and no production material. The workflow does not
receive repository secrets, publish artifacts, or deploy anything.

## CI evolution

The current continuous integration sequence is:

```text
Pull request
  -> repository/planning checks
  -> Python lint + types + unit tests
  -> TypeScript lint + format + types + unit tests + production build
  -> PostgreSQL integration tests + Alembic verification
  -> required checks before merge
```

Later tasks add API-contract drift checks, browser smoke tests, container builds,
dependency review, and security scanning only when the corresponding artifacts
exist. Those later checks and all delivery behavior remain explicitly outside
the current workflow.

## Delivery evolution

Continuous delivery should begin only when Task 50 establishes a supported
deployment target, immutable application images, migrations, health checks, and
recovery procedures. The intended pipeline is:

```text
Merge to main
  -> repeat required CI gates
  -> build and scan immutable images once
  -> publish images by commit SHA/digest
  -> deploy exact digests to staging
  -> run migrations as an explicit job
  -> run smoke tests
  -> require protected-environment approval for production
  -> deploy the already-tested digests
  -> verify health and retain rollback evidence
```

Pull requests must never deploy to shared environments. Production must not
rebuild source or select a floating image tag. Database rollback is not assumed
to be safe: migrations need compatibility review, backups and restore drills,
and release-specific rollback guidance.

## Decisions deliberately deferred

- Hosting provider and deployment mechanism.
- Container registry and environment topology.
- Whether staging deployment is automatic or scheduled.
- Secret-management provider and workload identity mechanism.
- Preview environments, because confidential engineering data and cleanup costs
  require a concrete design.
- Kubernetes, unless the selected hosting platform genuinely requires it.

These choices should be made from an actual deployment target rather than added
to the repository as nonfunctional YAML.
