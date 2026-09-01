# ReviewFlow contributor instructions

## Scope first

- Read `README.md`, `docs/architecture.md`, and the relevant roadmap/domain
  documentation before changing code.
- Treat each requested roadmap task as one pull-request-sized change. Do not
  implement later roadmap items unless they are required for the current task.
- Inspect existing modules and tests before introducing a new pattern or
  dependency. Prefer the established local pattern when it remains sound.
- Avoid unrelated refactors. Recommend them as separate work unless they are
  necessary to make the requested change safe.

## Architecture and security

- Keep ReviewFlow a modular monolith: the Next.js app consumes the FastAPI API,
  and authoritative business rules live in the API.
- Organize backend code by domain capability. Do not create generic repository,
  service, manager, event-bus, or workflow abstractions speculatively.
- Enforce authentication, tenant scoping, and authorization in every protected
  backend operation. Hiding a frontend control is not authorization.
- Validate input at system boundaries and preserve database constraints for
  invariants. Do not expose ORM objects directly as API responses.
- Keep secrets out of source control and logs. Treat filenames, uploads, and
  document content as untrusted confidential data.
- Use explicit transaction boundaries for business operations. Do not swallow
  errors broadly or return sensitive exception details to clients.

## Database changes

- Use Alembic for schema changes. Review both upgrade and downgrade behavior,
  generated constraints/indexes, locking implications, and existing-data
  handling.
- Do not edit a migration that may already have been merged or deployed; add a
  corrective migration instead.
- Use PostgreSQL for persistence integration tests. Do not assume SQLite proves
  PostgreSQL behavior.

## Quality and verification

- Add tests for meaningful success, validation, authorization, tenant-isolation,
  and conflict paths introduced by the change.
- Run the narrowest relevant tests while developing, then the affected lint,
  type-check, test, and build commands before handoff.
- Regenerate and review API client contract changes when the OpenAPI surface
  changes. Never hand-edit generated client files.
- Inspect migrations and generated artifacts directly; a passing test alone is
  not sufficient evidence that they are correct.
- Do not disable lint or type rules merely to obtain a green build.
- Keep CI commands runnable locally, GitHub token permissions minimal, and
  third-party actions pinned to immutable commit SHAs.
- Do not add a deployment workflow until it has a real artifact, environment,
  health check, rollback boundary, and secret-management design.

## Documentation and handoff

- Update architecture, domain, development, or ADR documentation when the
  implemented behavior or decision changes it. Do not make unsupported claims
  in the README.
- End each task with: the change summary, important decisions, significant
  files, migrations, tests run, manual test steps, known limitations, and
  explicitly deferred follow-up work.
- If a requested feature is incomplete, state the boundary clearly. Do not ship
  placeholder or mock behavior as production functionality.
