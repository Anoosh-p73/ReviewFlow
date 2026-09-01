# ReviewFlow initial architecture proposal

## Status and scope

This document proposes the starting architecture for ReviewFlow. It is a plan,
not a claim about currently implemented behavior. The repository should be
bootstrapped incrementally through the tasks in [roadmap.md](roadmap.md).

The initial system is a modular monolith with two deployable applications and
one relational database:

```text
Browser -> Next.js web application -> FastAPI REST API -> PostgreSQL
                                      |
                                      `-> file storage (introduced later)
```

This separation earns its cost because the browser UI and engineering workflow
API have different runtimes, testing needs, and deployment concerns. It also
keeps authorization and business rules in one backend instead of splitting
them between Next.js server actions and FastAPI. It does not imply independent
domain services or databases.

## Technology choices

### Web application

Use Next.js with React, strict TypeScript, and Tailwind CSS. Prefer server
components for page composition and initial data loading where they reduce
client JavaScript, and client components for interactive forms and tables.
All domain writes go through the FastAPI API. The web application may act as a
same-origin proxy in production, but it must not become a second business-logic
backend.

The first UI should use semantic HTML and small local components. A large
component library, global state framework, and elaborate design system are not
justified yet. Add a dependency when a concrete interaction demonstrates the
need.

### API application

Use FastAPI, Pydantic, SQLAlchemy 2.x, and Alembic. Organize code by domain
capability rather than by a repository-wide collection of routes, schemas,
services, and models. Each mature module can contain its own HTTP schemas,
routes, persistence models, queries, and use cases.

Route handlers adapt HTTP input and output. Business decisions belong in
plain, typed use-case functions. Those functions may use SQLAlchemy sessions
directly at first. A repository abstraction should appear only where it hides
a real persistence boundary, enables materially different implementations, or
removes demonstrated duplication. Transactions wrap complete use cases and
are committed at an explicit application boundary.

The API returns Pydantic response models, never raw ORM instances as its public
contract. Collection endpoints use bounded pagination before they are exposed
to potentially large datasets.

### PostgreSQL

PostgreSQL is the system of record. Use UUID primary keys, timezone-aware UTC
timestamps, foreign keys, uniqueness/check constraints, and indexes based on
real access paths. Alembic migrations are append-only once merged and are
reviewed as code. Application validation improves error messages; database
constraints preserve invariants under concurrency.

SQLite is not a supported substitute for integration tests because its type,
constraint, locking, and migration behavior differs from PostgreSQL. Fast unit
tests may avoid a database, while persistence and API integration tests run
against PostgreSQL.

### API contracts

FastAPI's OpenAPI document is the source of truth for the HTTP contract. When
the first product API is consumed by the frontend, generate a small typed
TypeScript client into `packages/api-client`. CI should reject an out-of-date
generated client.

Do not attempt to share Python domain classes with TypeScript. Do not manually
maintain matching request and response interfaces in two languages. A general
`packages/shared` directory is intentionally omitted until there is real
runtime-neutral code to share.

### Configuration and dependency management

Use environment variables parsed once into typed settings. Fail at startup for
missing or invalid required configuration, and keep secrets out of committed
files. Proposed bootstrap tooling is:

- pnpm workspaces for JavaScript packages and a committed lockfile;
- a Python `pyproject.toml` and lockfile managed by uv;
- Ruff, mypy, and pytest for Python;
- ESLint, Prettier, strict TypeScript, and Vitest/Testing Library for the web;
- Docker Compose only for local PostgreSQL at first.

These tools provide reproducible installs and focused quality gates without
adding runtime architecture.

## Module boundaries

### Backend boundaries

`app/core` owns cross-cutting process concerns: typed settings, logging setup,
request identifiers, and the application error contract. It must not become a
miscellaneous utility folder.

`app/db` owns the SQLAlchemy engine/session lifecycle, declarative metadata,
and migration integration. Domain modules define their own tables but import a
single metadata base.

`app/modules/<capability>` owns a cohesive business capability. Early examples
will be `identity`, `organizations`, and `projects`; later examples include
`documents`, `reviews`, and `comments`. Modules may call narrow public functions
from another module. They must not reach through another module to mutate its
tables casually.

`app/api` owns HTTP assembly and genuinely cross-module endpoints such as
health checks. Domain routes live with the domain module and are registered by
the API router.

Dependency direction is:

```text
HTTP routes -> use cases/domain rules -> SQLAlchemy/session boundary
     |                 |
 Pydantic          domain-owned persistence models
```

Not every operation needs four physical layers. A simple read query can remain
a typed query function until complexity proves otherwise.

### Frontend boundaries

Next.js route groups represent user workflows. Reusable application-wide UI
primitives live in `components`; feature-specific components stay near their
route or in `features/<capability>` after reuse warrants that directory.
`lib/api` configures the generated client and maps transport failures into UI
states. Authentication/session helpers stay separate from presentation.

The frontend may decide presentation and navigation. It must not decide whether
an operation is authorized; every protected API endpoint enforces that itself.

### Transaction and error boundaries

One API request normally opens one database session. A write use case performs
all invariant checks and mutations within a transaction. Expected domain
failures become a stable, machine-readable error envelope. Unexpected failures
are logged with a request identifier and return a non-sensitive response.
Retries are not applied blindly to non-idempotent writes.

## Proposed repository structure

The following is the target shape as the first roadmap tasks are completed. Do
not create empty directories merely to resemble this tree.

```text
ReviewFlow/
|-- AGENTS.md
|-- README.md
|-- .gitignore
|-- .editorconfig
|-- .env.example
|-- compose.yaml                  # PostgreSQL only when persistence is added
|-- package.json                  # pnpm workspace commands
|-- pnpm-lock.yaml
|-- pnpm-workspace.yaml
|-- .github/
|   `-- workflows/                # CI now; delivery after a target exists
|-- scripts/                      # local/CI automation entry points
|-- apps/
|   |-- web/
|   |   |-- app/                  # Next.js routes and layouts
|   |   |-- components/           # proven reusable UI components
|   |   |-- lib/                  # API/session adapters
|   |   |-- public/
|   |   `-- package.json
|   `-- api/
|       |-- pyproject.toml
|       |-- alembic.ini
|       |-- migrations/
|       |-- app/
|       |   |-- api/              # API assembly and cross-module routes
|       |   |-- core/             # settings, logging, errors
|       |   |-- db/               # engine, sessions, metadata
|       |   |-- modules/          # domain-oriented modules
|       |   `-- main.py           # FastAPI composition root
|       `-- tests/
|           |-- unit/
|           `-- integration/
|-- packages/
|   `-- api-client/               # generated only when a real API is consumed
|-- docs/
|   |-- architecture.md
|   |-- ci-cd.md
|   |-- roadmap.md
|   |-- development.md            # added with executable setup instructions
|   |-- domain.md                 # added as domain rules become implemented
|   `-- adr/                      # added with the first accepted ADR
`-- infra/                        # added only for real deployment artifacts
```

Responsibilities are deliberately narrow:

- `apps/web` is the browser-facing application and contains no authoritative
  domain rules.
- `apps/api` is the sole application API and transaction boundary.
- `packages/api-client` is generated transport code, not a shared domain model.
- `docs` records current decisions, setup, domain semantics, and the roadmap.
- `infra` is reserved for deployment configuration that is actually exercised;
  it is not part of the initial bootstrap.

There is no initial `packages/config`: sharing a few lint settings is cheaper
than maintaining a package until two JavaScript packages demonstrably need it.

## CI/CD boundary

CI should grow with executable repository behavior. The planning-stage workflow
checks document structure, links, and hygiene. Task 5 adds application lint,
types, tests, builds, PostgreSQL integration, and migration verification. Later
feature tasks add contract, browser, container, and security checks when their
artifacts exist.

CD starts only after a real deployment target and immutable application images
exist. Task 50 adds a protected delivery workflow that promotes the same tested
image digests through staging and production, runs migrations explicitly, and
verifies health and recovery boundaries. The staged design and current commands
are maintained in [ci-cd.md](ci-cd.md).

## Abstractions intentionally not introduced

- No microservices, message broker, background-job platform, cache, search
  cluster, CQRS, event sourcing, or GraphQL.
- No generic repository/service/manager class per database table.
- No plugin framework or universal domain-event bus.
- No generalized workflow engine. Review and comment transitions should first
  be modeled as explicit domain operations.
- No full RBAC policy language. Start with named permissions evaluated against
  organization and project context, then expand from observed needs.
- No storage abstraction before file metadata exists. Introduce a narrow file
  object interface with the upload feature, then add an object-storage adapter.
- No audit implementation disguised as ordinary application logs.
- No hand-written cross-language shared types.
- No speculative soft deletion, localization, notification framework, or
  multi-region support.

## Architectural risks and evolutionary guardrails

### Authorization and tenant isolation

Risk: organization roles and project membership are easy to scatter across
route handlers, causing inconsistent access or cross-tenant data exposure.

Guardrail: establish an authenticated principal and explicit permission checks
that receive both organization and project context. Scope queries by tenant,
test denied and cross-tenant cases, and keep authorization in the API. Do not
design a general policy language until the permission matrix is understood.

### Document identity and revision identity

Risk: treating a file upload, logical document, revision label, and reviewable
revision as one record makes replacement, history, and uniqueness ambiguous.

Guardrail: introduce `Document` and `DocumentRevision` separately, with
organization/project-scoped document-number uniqueness and an explicit policy
for revision labels. Add file metadata as a child concern. Defer complex
revision ordering until real naming schemes are known.

### Comment disposition versus workflow state

Risk: one status enum may conflate an author's response, the review team's
decision, and whether work is operationally closed.

Guardrail: begin with the smallest verified lifecycle and named transition
operations. Document semantics before adding values. Preserve room for separate
disposition and workflow fields, but do not add both without use cases.

### File storage and untrusted content

Risk: HTTP request handling, database transactions, storage writes, and malware
scanning cannot be made atomic as one transaction. Files also expose path,
content-type, size, and authorization hazards.

Guardrail: store object keys and verified metadata, never user-provided paths.
Use staged upload states and compensating cleanup. Keep download authorization
in the API. Start with a narrow local adapter for development and preserve the
same behavioral contract for object storage.

### Auditability

Risk: application logs or mutable display strings will not form a reliable
engineering audit trail; adding events after the fact can miss state changes.

Guardrail: first identify auditable commands and stable actor/resource data.
Later write structured audit records in the same database transaction as the
domain change. Keep operational logs separate. Avoid pretending that a generic
ORM hook understands business meaning.

### Concurrent review activity

Risk: two reviewers or controllers can overwrite status, resolution, or
assignment changes.

Guardrail: rely on uniqueness and foreign-key constraints for structural
invariants. Add version columns or conditional updates to mutable collaborative
records once those writes exist, return conflict responses, and test stale
updates. Do not put versioning on every table preemptively.

### Cross-revision comment relationships

Risk: copying comments between revisions destroys provenance, while binding a
comment only to the logical document loses the reviewed artifact context.

Guardrail: comments belong to a specific review cycle/revision. Introduce an
explicit relation for carried, superseded, or related comments only when the
carry-forward workflow is implemented. Never infer equivalence from matching
text or page numbers.

### Generated contract drift

Risk: the frontend can compile against stale API types or depend on accidental
OpenAPI details.

Guardrail: generate deterministically from a pinned API environment, review the
contract diff, and make CI verify regeneration is clean. Keep domain-friendly
frontend adapters around awkward transport details rather than editing generated
files.

### Reporting load and query sprawl

Risk: dashboards and Excel exports can grow into unbounded ORM graphs or lock
the transactional path.

Guardrail: add bounded filters and purpose-built read queries based on measured
needs. Introduce asynchronous export or a reporting store only when request
duration or volume demonstrates the need.

## Initial ADR candidates

These decisions are broad or costly enough to deserve ADRs when they become
active. Trivial tool configuration and individual table definitions do not.

1. **Modular monolith with separate web and API deployables.** Record why
   business logic is centralized in FastAPI and why independent domain services
   are rejected initially.
2. **OpenAPI as the cross-language contract source.** Record the generator,
   ownership of generated code, compatibility policy, and CI drift check when
   client generation is introduced.
3. **Authentication session and browser security model.** Before authentication
   is implemented, decide between opaque server-side sessions and another
   concrete model, including cookie, CSRF, revocation, and same-origin behavior.
4. **Tenant and authorization context.** When organization/project permissions
   are implemented, record identity membership assumptions, scoping rules, and
   the backend enforcement pattern.
5. **File storage consistency model.** When uploads are introduced, record local
   versus object storage behavior, staging, cleanup, integrity, and download
   authorization.
6. **Transactional audit records.** Before audit coverage expands, record event
   schema, atomicity, retention, sensitive-data handling, and the distinction
   from logs.

The precise comment lifecycle and revision-label rules should initially live in
domain documentation. They warrant ADRs only if a decision constrains multiple
subsystems or is unusually costly to reverse.
