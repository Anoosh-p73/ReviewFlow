# CI/CD strategy

## Current state

ReviewFlow contains a runnable FastAPI development process, but no packaged
deployment artifact or persistence boundary. Until Task 5 adds application
quality gates, the current GitHub Actions workflow validates the repository
planning and hygiene contract:

- required planning documents are present;
- the roadmap has 35-50 sequential, consistently structured tasks;
- Tasks 1-5 retain their additional implementation detail;
- local Markdown links resolve; and
- repository text files contain no trailing whitespace.

The same check runs locally with:

```powershell
./scripts/validate-planning.ps1
```

The workflow runs for pull requests and pushes to `main`, uses read-only
repository permissions, pins third-party actions to a full commit SHA, has a
short timeout, and cancels superseded runs. It does not receive secrets or
deploy anything. API lint, strict type checking, and tests are available locally
through the commands documented in [development.md](development.md); adding them
to GitHub Actions remains the explicit Task 5 boundary.

## CI evolution

Task 5 will expand continuous integration when both applications and PostgreSQL
support exist. CI will then run the same commands developers run locally:

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
exist. Lockfiles remain mandatory, action references remain immutable, and CI
credentials use least privilege.

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
