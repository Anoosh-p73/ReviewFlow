# ReviewFlow incremental development roadmap

## How to use this roadmap

Each task is intended to be one reviewable pull request. A task may be split if
implementation reveals more risk than expected; adjacent tasks should not be
silently combined. Acceptance criteria describe the observable boundary of the
task, not permission to implement later capabilities.

Tasks 1-5 are the first milestone and are intentionally more detailed. They
establish reproducible development and a very small amount of running software:
an API liveness endpoint, a web shell, and PostgreSQL connectivity. They do not
create ReviewFlow domain records.

## Milestone 1: repository and runtime foundation

### Task 1 - Bootstrap repository tooling

**Goal:** Establish reproducible, documented monorepo conventions without
creating application behavior.

**Main implementation work:**

- Add pnpm workspace metadata, root scripts, a pinned Node version policy, and a
  committed lockfile.
- Define the Python version and uv-based dependency workflow that Task 2 will
  use; do not install backend runtime dependencies before the API package exists.
- Review and extend the project-specific `.gitignore`; add `.editorconfig` and a
  non-secret `.env.example` containing only variables that are already
  meaningful.
- Add `docs/development.md` with prerequisites, install commands, command naming,
  and Windows/Unix notes. Keep commands executable rather than aspirational.
- Preserve the existing architecture and roadmap documents as the statement of
  intent; do not create empty `apps`, `packages`, or `infra` subtrees.

**Acceptance criteria:** A clean clone can install the root JavaScript workspace
deterministically with the documented supported tool versions. Formatting and
line-ending rules are explicit. No secret or machine-specific path is committed,
and no application is claimed to run yet.

**Tests expected:** Run the workspace install with a frozen lockfile; validate
root manifest syntax; run any root formatting/config checks introduced by this
task; inspect ignored files with `git status`.

**Manual verification:** Follow `docs/development.md` from a clean worktree and
confirm every Task 1 command behaves as documented.

**Failure and design notes:** Root scripts should fail clearly when an app has
not yet been bootstrapped. Tool versions should be constrained tightly enough
for repeatability without depending on globally installed project libraries.

**Explicitly deferred:** FastAPI and Next.js source, database configuration,
Docker Compose, application CI beyond the existing planning check, shared lint
packages, and production infrastructure.

### Task 2 - Add the FastAPI application shell

**Goal:** Create the smallest runnable API with typed configuration and useful
request diagnostics.

**Main implementation work:**

- Create `apps/api` with `pyproject.toml`, a uv lockfile, and packages for the
  composition root, core settings/logging, and cross-module API routes.
- Configure FastAPI without domain modules. Add `GET /health/live` returning a
  small versioned Pydantic response that proves only that the process is alive.
- Parse environment settings once with safe local defaults where appropriate;
  fail startup for malformed required settings.
- Emit structured logs to stdout and accept or create a request identifier that
  is returned in a response header. Do not log request bodies or secrets.
- Configure Ruff, mypy, and pytest for this package and document API commands.

**Acceptance criteria:** The documented command starts the API, `/health/live`
returns HTTP 200 with the declared response shape and request identifier, and an
unknown route uses FastAPI's normal 404 behavior. Importing the application does
not connect to external services. The API package passes lint and strict type
checking under the documented configuration.

**Tests expected:** Unit/API tests for liveness response shape, request-ID
generation, propagation of a valid caller request ID, and invalid settings.
Run Ruff, mypy, and pytest.

**Manual verification:** Start the API, call liveness twice (once with and once
without a request ID), inspect response headers and stdout logs, then terminate
it cleanly.

**Failure and design notes:** Liveness must remain independent of PostgreSQL so
orchestrators can distinguish a running process from dependency readiness.
Unexpected exceptions must not expose stack traces in production responses.

**Explicitly deferred:** Database readiness, ORM/Alembic, domain entities,
authentication, generalized error envelopes, CORS policy, and container images.

### Task 3 - Add the Next.js application shell

**Goal:** Create a restrained, accessible web shell that can grow into the
professional ReviewFlow interface.

**Main implementation work:**

- Create `apps/web` with Next.js, React, strict TypeScript, Tailwind CSS, ESLint,
  Prettier, Vitest, and React Testing Library using mutually compatible pinned
  versions.
- Implement root metadata, a skip link, semantic page structure, visible focus
  styles, and a simple page explaining that product workflows are not yet
  available.
- Establish only proven global styling tokens such as color, spacing, and text
  defaults. Avoid a component library, dashboard placeholders, and fake metrics.
- Add documented development, type-check, lint, unit-test, and production-build
  commands, wired through the root workspace.

**Acceptance criteria:** The root page renders at narrow and wide widths, can be
navigated by keyboard, contains no fabricated product data or nonfunctional
controls, and completes a production build with strict TypeScript enabled.

**Tests expected:** A focused rendering/accessibility-oriented unit test for the
shell, plus lint, formatting check, TypeScript check, unit tests, and production
build. Do not add snapshot tests for the entire page.

**Manual verification:** Run the development server, inspect the page at mobile
and desktop widths, traverse it by keyboard, and confirm the browser console and
server output contain no errors.

**Failure and design notes:** The page should clearly represent planning-stage
software. Server/client component boundaries must be intentional; no global
client state is needed.

**Explicitly deferred:** API calls, authentication screens, application
navigation, design-system extraction, dashboards, end-to-end tests, and
deployment hosting.

### Task 4 - Add PostgreSQL persistence foundations

**Goal:** Establish one reliable PostgreSQL development dependency, SQLAlchemy
session lifecycle, and Alembic workflow without inventing domain tables.

**Main implementation work:**

- Add a narrowly scoped Compose service for a pinned PostgreSQL version, with a
  named development volume and a health check. Do not containerize the apps yet.
- Add validated database settings, SQLAlchemy 2.x engine/session construction,
  declarative metadata, and request-scoped session cleanup.
- Configure Alembic to use the application's metadata and settings. Do not add
  an empty "baseline" revision merely to create history.
- Add `GET /health/ready` that performs a bounded database probe and reports only
  readiness, with non-sensitive failure behavior.
- Provide PostgreSQL integration-test fixtures with isolated database state and
  clear cleanup; tests must not target a developer's normal database.

**Acceptance criteria:** A developer can start PostgreSQL, run Alembic to the
current head, start the API, and receive ready status. With PostgreSQL stopped,
liveness remains 200 while readiness returns a documented unavailable response
within a bounded time. Sessions are closed on both success and failure.

**Tests expected:** PostgreSQL integration tests for session execution,
commit/rollback behavior, readiness success, and readiness failure. Run Alembic
upgrade/current checks, Ruff, mypy, and the complete API test suite.

**Manual verification:** Start and stop the Compose dependency while exercising
both health endpoints. Inspect the database to confirm no product tables or
sample data were created.

**Failure and design notes:** Database credentials come from environment
configuration. Pool and connection errors should be logged with request context
without echoing credentials. Readiness must not hang indefinitely.

**Explicitly deferred:** Organization/user tables, seed data, SQLite support,
connection proxies, replicas, backup automation, and app containers.

### Task 5 - Add continuous integration quality gates

**Goal:** Make the foundation reproducibly verifiable on every proposed change.

**Main implementation work:**

- Expand the planning-stage workflow with path-aware or cached jobs for Python
  quality, web quality/build, and PostgreSQL-backed integration tests.
- Install dependencies from frozen lockfiles and use pinned action versions.
- Run Ruff, mypy, pytest, ESLint, Prettier check, TypeScript check, Vitest, and
  the Next.js production build using the same scripts documented locally.
- Run PostgreSQL as an ephemeral CI service and apply Alembic before integration
  tests. Use CI secrets/environment values that contain no production material.
- Add a concise status section to development documentation, without claiming
  deployment or production readiness.

**Acceptance criteria:** CI retains the planning check and runs application gates
on pull requests and the default branch; a clean revision passes; deliberate
lint, type, unit-test, build, and migration failures each fail the owning job;
dependency caches do not bypass frozen-lock checks.

**Tests expected:** The CI workflow is the verification. Also validate workflow
syntax where practical and run every underlying command locally before merge.

**Manual verification:** Inspect a complete CI run, its PostgreSQL service and
Alembic output, useful failure annotations, cache behavior, and absence of
secrets in logs.

**Failure and design notes:** Keep one understandable workflow until timing or
ownership justifies splitting it. Do not permit failures or reduce strictness to
make the initial run green.

**Explicitly deferred:** Deployment, release publishing, browser E2E tests,
code-coverage thresholds, dependency-update bots, security scanning, and preview
environments.

## Milestone 2: identity, authentication, and organization administration

### Task 6 - Model organizations, users, and organization membership

**Goal:** Add the first domain persistence model while keeping login out of scope.

**Main implementation work:** Add UUID-based `Organization`, `User`, and
`OrganizationMembership` tables, normalized email rules, active flags, UTC
timestamps, constraints/indexes, Pydantic read models, and the first real
Alembic migration. Document identity versus membership semantics.

**Acceptance criteria:** The schema represents a user belonging to one or more
organizations without duplicate membership; no public CRUD endpoint exists.

**Tests expected:** Migration upgrade/downgrade on PostgreSQL, constraint and
normalization tests, ORM mapping tests, and model serialization tests.

**Explicitly deferred:** Passwords, sessions, invitations, organization CRUD,
roles beyond the minimum membership marker, and project access.

### Task 7 - Add a local administrator bootstrap command

**Goal:** Provide a deterministic, non-HTTP way to create the first organization
and administrator for development and controlled deployment bootstrap.

**Main implementation work:** Add a typed CLI command using the same settings and
transaction boundaries as the API, with explicit inputs, idempotent conflict
handling, and no default password or sample data.

**Acceptance criteria:** The command atomically creates the requested records,
refuses ambiguous duplicates, reports safe results, and is documented.

**Tests expected:** CLI success, rerun/conflict, invalid input, transaction
rollback, and secret-redaction tests against PostgreSQL.

**Explicitly deferred:** Credentials, interactive prompts, fixtures, user
invitations, and organization settings.

### Task 8 - Add password credentials and server-side sessions

**Goal:** Implement secure credential verification and revocable session
persistence behind non-HTTP functions.

**Main implementation work:** Accept an authentication ADR, add a maintained
password hasher, credential/session tables with hashed opaque tokens and expiry,
session creation/revocation use cases, and bootstrap credential input.

**Acceptance criteria:** Plaintext passwords and session tokens are never stored
or logged; verification is timing-safe through the selected library; expired,
revoked, inactive-user, and inactive-membership sessions are rejected.

**Tests expected:** Hash/verify, wrong password, token hashing, expiry,
revocation, inactive principals, transaction rollback, and migration tests.

**Explicitly deferred:** HTTP cookies, login UI, password reset, MFA, SSO,
lockout/rate limiting, and email delivery.

### Task 9 - Expose login, current-session, and logout endpoints

**Goal:** Establish the browser authentication boundary safely.

**Main implementation work:** Add login, current-principal, and logout routes;
set opaque session cookies with environment-appropriate security attributes;
implement the accepted same-origin/CORS and CSRF model; add a consistent
machine-readable API error envelope.

**Acceptance criteria:** Successful login rotates/sets a session and returns a
safe principal; logout revokes it; protected calls reject missing, expired, or
forged sessions; state-changing cookie requests enforce the chosen CSRF control.

**Tests expected:** Success and generic failure, cookie attributes, CSRF,
logout/replay, expiry, inactive access, error envelope, and no credential leaks.

**Explicitly deferred:** Frontend UI, password recovery/change, MFA, SSO,
remember-me behavior, and broad rate limiting.

### Task 10 - Generate the TypeScript API client

**Goal:** Make OpenAPI the checked, typed contract between the two applications.

**Main implementation work:** Select and pin a focused generator, create
`packages/api-client`, generate from the API OpenAPI document, add deterministic
scripts and a CI drift check, and document compatibility expectations.

**Acceptance criteria:** The web workspace can import generated auth/health
types and client calls; regeneration is deterministic; generated code is never
hand-edited; stale output fails CI.

**Tests expected:** Clean regeneration check, TypeScript compile, a client test
against representative responses, and API OpenAPI schema regression checks.

**Explicitly deferred:** A generic shared package, runtime domain sharing,
public SDK guarantees, and versioned external APIs.

### Task 11 - Add the web sign-in and session boundary

**Goal:** Let a bootstrapped user sign in and reach a protected application shell.

**Main implementation work:** Build an accessible sign-in form, server-side
session lookup, protected route group, logout action, safe return-path handling,
and generic authentication errors through the generated client.

**Acceptance criteria:** Anonymous users are redirected to sign-in; valid users
reach the shell; invalid credentials do not reveal account existence; logout
returns to sign-in; return URLs cannot redirect off-site.

**Tests expected:** Form validation, success/failure, protected routing, safe
redirects, logout, keyboard/error accessibility, and a focused Playwright smoke
test if the harness is introduced here.

**Explicitly deferred:** Self-registration, password reset, MFA, profile editing,
organization switching, and polished application navigation.

### Task 12 - Add organization user administration API

**Goal:** Let organization administrators list, create, activate, and deactivate
members with a minimal explicit permission model.

**Main implementation work:** Add permission checks, paginated member queries,
create/deactivate/reactivate use cases, temporary credential handling appropriate
for the no-email stage, and protected REST endpoints.

**Acceptance criteria:** Only organization administrators can administer their
organization; cross-organization IDs cannot leak records; the last active
administrator cannot accidentally deactivate themselves if that would orphan
the organization.

**Tests expected:** Allowed and denied roles, cross-tenant cases, pagination,
duplicates, last-admin invariant, inactive sessions, and concurrent conflicts.

**Explicitly deferred:** Email invitations, custom roles, bulk import, profile
fields, deletion, and project membership.

### Task 13 - Add organization user administration UI

**Goal:** Provide a usable interface for the Task 12 operations.

**Main implementation work:** Add a paginated member table, create form,
activate/deactivate confirmation, permission-aware navigation, and accessible
loading/empty/error states.

**Acceptance criteria:** Administrators can complete every supported operation;
non-administrators cannot navigate to the screen and remain protected by API
checks; secrets are not redisplayed after their one intended presentation.

**Tests expected:** Table/forms, pagination, validation/conflict errors,
confirmations, permission rendering, and an admin flow integration test.

**Explicitly deferred:** Invitations, bulk actions, role editor, profile page,
and user deletion.

## Milestone 3: projects, departments, and project access

### Task 14 - Add projects API

**Goal:** Create and retrieve organization-scoped projects.

**Main implementation work:** Add project table/migration, code/name validation,
active state, organization-scoped uniqueness, use cases, paginated list/create/
detail/update endpoints, and initial organization-admin authorization.

**Acceptance criteria:** Administrators manage only their organization's
projects; project codes are unique within an organization; responses never
expose another tenant.

**Tests expected:** CRUD behavior, validation, constraints, pagination,
authorization, cross-tenant IDs, and migration tests.

**Explicitly deferred:** Project membership, project deletion, dashboards,
documents, templates, and custom metadata.

### Task 15 - Add project list, creation, and detail UI

**Goal:** Make the first core domain entity usable from the web application.

**Main implementation work:** Add project navigation, paginated list, create/edit
forms, detail shell, and honest empty/loading/error states.

**Acceptance criteria:** Authorized administrators can create and edit a project;
users receive clear forbidden/not-found handling; no fake dashboard statistics
are shown.

**Tests expected:** Form validation, list/detail states, pagination, conflicts,
permission rendering, and a project-create integration flow.

**Explicitly deferred:** Project members, departments, documents, metrics,
archiving, and deletion.

### Task 16 - Add organization departments API

**Goal:** Represent stable organization departments used in review workflows.

**Main implementation work:** Add department schema/migration, organization-
scoped code/name uniqueness, activate/deactivate use cases, and admin endpoints.

**Acceptance criteria:** Administrators manage departments within their tenant;
deactivation preserves references; duplicate normalized codes are rejected.

**Tests expected:** Constraints, lifecycle, authorization, cross-tenant access,
pagination, and migration tests.

**Explicitly deferred:** Department hierarchy, leads, deletion, project-specific
departments, and review assignments.

### Task 17 - Add department administration UI

**Goal:** Expose the minimal department lifecycle to organization administrators.

**Main implementation work:** Add list/create/edit/deactivate UI with concise
validation and inactive-state treatment.

**Acceptance criteria:** All Task 16 operations are usable and accessible; the UI
does not imply hierarchy or department-lead functionality.

**Tests expected:** Forms, list states, conflicts, activation controls,
permissions, and keyboard interaction.

**Explicitly deferred:** Department leads, hierarchy, bulk import, project
mapping, and reviewer assignment.

### Task 18 - Add project membership and authorization policies

**Goal:** Make project context, not organization membership alone, control
project access.

**Main implementation work:** Accept the tenant/authorization ADR; add project
membership with the minimum roles needed now; centralize named permission checks;
add list/add/change/remove endpoints; update project reads/writes to use them.

**Acceptance criteria:** Project administrators manage membership; members see
only authorized projects; organization administrators retain documented access;
removing access takes effect on the next request; cross-tenant membership is
impossible.

**Tests expected:** Role/permission matrix, cross-tenant and guessed-ID cases,
last-project-admin invariant, removal, duplicates, stale sessions, and migration.

**Explicitly deferred:** Custom roles, department-derived access, group sync,
resource-level ACLs, invitations, and public projects.

### Task 19 - Add project membership UI

**Goal:** Let project administrators manage the access model introduced in
Task 18.

**Main implementation work:** Add member list, organization-user selection,
role changes/removal, confirmations, and project navigation based on effective
permissions.

**Acceptance criteria:** Supported membership changes work without exposing
other organizations' users; the final-admin safeguard is clear; API remains the
authority.

**Tests expected:** Member management, permission states, conflicts, empty/error
states, and an access-removal integration flow.

**Explicitly deferred:** Teams, bulk assignment, invitation, department mapping,
custom permissions, and access reports.

## Milestone 4: documents, revisions, and files

### Task 20 - Add logical documents API

**Goal:** Represent a project document independently from any revision or file.

**Main implementation work:** Add document schema/migration, document-number
normalization and project uniqueness, title/type fields with deliberately small
semantics, paginated endpoints, and project permissions.

**Acceptance criteria:** Authorized members create/read/update documents in their
projects; logical documents contain no file bytes or current-revision shortcut;
cross-project IDs are scoped.

**Tests expected:** Validation/constraints, permissions, tenant isolation,
pagination/filter basics, concurrency conflicts, and migration.

**Explicitly deferred:** Revisions, uploads, document type administration,
custom fields, soft deletion, and search service.

### Task 21 - Add document list, creation, and detail UI

**Goal:** Make logical document management usable.

**Main implementation work:** Add project document table, create/edit forms,
detail shell, bounded filters, permission states, and navigation.

**Acceptance criteria:** Users can manage documents allowed by Task 20; the UI
does not fabricate revision, review, or comment data.

**Tests expected:** Forms, filters/pagination, duplicate number errors,
permissions, responsive table behavior, and create flow.

**Explicitly deferred:** Revision timeline, upload, bulk import, previews,
reviews, and dashboards.

### Task 22 - Add document revision metadata API

**Goal:** Represent immutable revision identity separately from the logical
document and uploaded object.

**Main implementation work:** Document initial revision-label semantics; add
revision schema/migration, create/list/detail endpoints, issue date and notes,
uniqueness constraints, and rules for what metadata may change.

**Acceptance criteria:** A document has ordered, distinct revision records under
the documented limited convention; creating a revision does not require a file;
issued identity fields cannot be silently rewritten.

**Tests expected:** Label/ordering edge cases, constraints, immutability,
authorization, concurrent creation, serialization, and migration.

**Explicitly deferred:** File objects, revision comparison, automatic next label,
discipline-specific schemes, replacement, and review cycles.

### Task 23 - Add revision timeline and metadata UI

**Goal:** Show and create revision metadata from a document detail page.

**Main implementation work:** Add chronological timeline/table, creation form,
revision detail route, immutable-field presentation, and permission/error states.

**Acceptance criteria:** Users can distinguish the logical document from each
revision and see clearly that no file is attached when absent.

**Tests expected:** Timeline ordering, create validation/conflict, missing file
state, permissions, and a revision-create integration flow.

**Explicitly deferred:** Upload/download, inline viewing, compare, review cycles,
and revision deletion.

### Task 24 - Introduce file metadata and local storage contract

**Goal:** Define a narrow, testable storage boundary before accepting uploads.

**Main implementation work:** Accept the storage ADR; add file-object metadata
and state migration; define store/open/delete behavior using opaque keys; add a
development local-filesystem adapter with root containment and atomic writes.

**Acceptance criteria:** Storage behavior is testable without HTTP; user
filenames never determine paths; metadata can represent pending/available/failed
state; cleanup failures are explicit.

**Tests expected:** Path traversal, duplicate names, streaming, partial-write
cleanup, integrity metadata, missing object, adapter contract, and migration.

**Explicitly deferred:** Upload routes/UI, object storage, antivirus scanning,
previews, public URLs, and large-file multipart uploads.

### Task 25 - Add revision PDF upload API

**Goal:** Attach one validated PDF object to a revision through a failure-aware
workflow.

**Main implementation work:** Add streaming multipart endpoint, size limit,
filename sanitization, declared and detected PDF validation, checksum, staged
metadata transition, compensating cleanup, and project authorization.

**Acceptance criteria:** Valid bounded PDFs become available exactly once;
invalid/oversized/non-PDF or interrupted uploads leave no usable orphan; file
bytes stay outside PostgreSQL; conflicts have stable errors.

**Tests expected:** Valid PDF, magic/type mismatch, malformed/oversized input,
zero bytes, traversal names, duplicate/concurrent upload, storage/DB failures,
cleanup, authorization, and tenant isolation.

**Explicitly deferred:** Upload UI, replacement/versioning, malware service,
object storage, annotations, thumbnails, and OCR.

### Task 26 - Add revision upload UI

**Goal:** Provide a clear, accessible upload interaction with realistic failure
states.

**Main implementation work:** Add permission-gated file selection, client-side
advisory checks, upload progress where supported, conflict/failure recovery, and
revision metadata refresh.

**Acceptance criteria:** Users can upload a supported PDF and see authoritative
server results; client validation is not treated as security; retries do not
silently create duplicates.

**Tests expected:** File selection, advisory validation, progress/success,
server rejection, retry/conflict, permissions, and an upload integration flow.

**Explicitly deferred:** Drag-drop polish, batch upload, replacement, preview,
annotations, and resumable multipart upload.

### Task 27 - Add authorized file download

**Goal:** Allow permitted project members to retrieve revision files without
exposing storage paths.

**Main implementation work:** Add a streaming download endpoint, safe content
headers, authorization before object access, checksum/length handling, and UI
download action.

**Acceptance criteria:** Authorized users download the expected bytes and safe
filename; unauthorized or cross-tenant callers learn no storage details;
missing/corrupt objects produce actionable diagnostics without data leakage.

**Tests expected:** Byte integrity, headers/non-ASCII filename, permission and
cross-tenant denial, missing/corrupt storage, interrupted stream, and UI states.

**Explicitly deferred:** Inline PDF viewer, public/signed links, caching/CDN,
range requests, object storage, and file replacement.

## Milestone 5: review cycles and assignments

### Task 28 - Add review cycle creation and query API

**Goal:** Bind an explicitly named review cycle to one document revision.

**Main implementation work:** Add review-cycle schema/migration, draft state,
name/deadline fields, create/list/detail endpoints, and document-control
permissions.

**Acceptance criteria:** A draft cycle references exactly one revision and its
project; deadline is stored as a UTC instant under documented input semantics;
no assignments or comments exist yet.

**Tests expected:** Constraints, deadline validation/time zones, permissions,
tenant isolation, pagination, concurrent duplicates if prohibited, and migration.

**Explicitly deferred:** Starting/completing cycles, requested departments,
assignments, comments, notifications, and recurring reviews.

### Task 29 - Add review cycle lifecycle commands

**Goal:** Support explicit draft, active, completed, and cancelled transitions
without building a generic workflow engine.

**Main implementation work:** Document state semantics; add named start,
complete, and cancel use cases/endpoints; add optimistic concurrency and stable
conflict responses; freeze relevant configuration after start.

**Acceptance criteria:** Only valid authorized transitions succeed; stale writes
return conflict; timestamps and actor context are recorded as domain data where
needed; invalid transitions do not partially mutate state.

**Tests expected:** Complete transition matrix, permissions, stale versions,
double submission, rollback, deadline behavior, and serialization.

**Explicitly deferred:** Assignments/comments as completion prerequisites,
reopening, audit-event subsystem, notifications, and configurable workflows.

### Task 30 - Add review cycle UI

**Goal:** Let authorized users create, inspect, and transition review cycles.

**Main implementation work:** Add revision review list/detail, draft form,
deadline display, state actions with confirmations, optimistic version handling,
and empty/error states.

**Acceptance criteria:** The UI exposes exactly the Task 28-29 transitions,
handles stale conflicts by refreshing context, and never implies reviewer work
that is not implemented.

**Tests expected:** Forms, time-zone display, transition permissions,
confirmations, conflict recovery, and lifecycle integration flow.

**Explicitly deferred:** Assignments, comments, calendar views, notifications,
review templates, and dashboards.

### Task 31 - Add review assignments API

**Goal:** Assign active organization users and departments to a review cycle
with an explicit responsibility record.

**Main implementation work:** Add assignment schema/migration, reviewer and
department references, due date/status minimum, bulk-safe add/remove/list
operations, project access checks, and uniqueness rules.

**Acceptance criteria:** Only eligible project/organization members can be
assigned; department and reviewer context is preserved; duplicates and cross-
tenant references fail atomically; cycle-state restrictions are explicit.

**Tests expected:** Eligibility, constraints, bulk rollback, permissions,
cross-tenant IDs, inactive users/departments, cycle states, and migration.

**Explicitly deferred:** Assignment completion, delegation, reminders,
department leads, workload balancing, and comments.

### Task 32 - Add assignment management and reviewer inbox UI

**Goal:** Let controllers assign reviewers and let reviewers find their current
work.

**Main implementation work:** Add cycle assignment management, eligible reviewer
selection, a paginated "My reviews" page, deadline/state filters, and access-
aware navigation.

**Acceptance criteria:** Controllers manage supported assignments; reviewers see
only their own eligible work; empty/overdue states are factual; cross-tenant
data never appears.

**Tests expected:** Assignment forms, eligibility, bulk/conflict errors, inbox
filters/pagination, permissions, and assignment integration flow.

**Explicitly deferred:** Completion attestations, email reminders, delegation,
calendar integration, workload analytics, and comments.

## Milestone 6: comments and resolution

### Task 33 - Add review comments API

**Goal:** Let an assigned reviewer create and list textual comments tied to the
exact review cycle/revision.

**Main implementation work:** Add comment schema/migration with author,
department snapshot/reference, page reference, text, creation time, and initial
minimal state; add paginated create/list/detail endpoints and assignment checks.

**Acceptance criteria:** Eligible reviewers create comments only on active
assigned reviews; comments retain revision/cycle provenance; page/text rules are
validated; authorship cannot be supplied by the client.

**Tests expected:** Eligibility/permissions, lifecycle states, validation,
department provenance, pagination, tenant isolation, concurrent creation, and
migration.

**Explicitly deferred:** Coordinates, editing, replies, dispositions, attachments,
carry-forward, deletion, and audit events.

### Task 34 - Add comment creation and register UI

**Goal:** Provide a dense, usable first comment register for a review cycle.

**Main implementation work:** Add comment form, paginated/filterable register,
detail route, page/department/author presentation, permission states, and robust
long-text display.

**Acceptance criteria:** Assigned reviewers create valid comments and permitted
members browse them; the UI clearly identifies revision and cycle; no PDF
annotation behavior is implied.

**Tests expected:** Form validation, register filters/pagination, long text,
permissions, empty/errors, and a comment-create integration flow.

**Explicitly deferred:** Inline PDF context, editing, replies, status actions,
bulk import, and exports.

### Task 35 - Add controlled comment editing

**Goal:** Permit narrowly defined correction of a comment without erasing
authorship or concurrent changes.

**Main implementation work:** Define edit eligibility and frozen states; add
versioned update endpoint, updated timestamp, conflict response, and edit UI.

**Acceptance criteria:** Only the author under documented cycle/state conditions
can edit text/page; immutable provenance remains unchanged; stale updates never
overwrite newer content.

**Tests expected:** Author/non-author, cycle states, validation, optimistic
conflict, immutable fields, tenant isolation, and UI recovery.

**Explicitly deferred:** Full edit history/audit, deletion, moderator editing,
replies, dispositions, and rich text.

### Task 36 - Add comment replies API

**Goal:** Support an ordered discussion on each comment without a generic nested
conversation model.

**Main implementation work:** Add reply table/migration, create/list endpoints,
author and timestamps, bounded plain text, and review/project participation
permissions.

**Acceptance criteria:** Permitted participants reply to a comment; replies are
ordered deterministically and cannot nest; closed/cancelled behavior is explicit;
client-supplied authorship is ignored/rejected.

**Tests expected:** Permissions, ordering ties, validation, lifecycle states,
pagination if used, tenant isolation, concurrency, and migration.

**Explicitly deferred:** Reply editing/deletion, mentions, attachments, reactions,
notifications, and audit history.

### Task 37 - Add comment discussion UI

**Goal:** Make comment conversations readable and reply creation accessible.

**Main implementation work:** Add discussion timeline, reply form, incremental
refresh, author/time presentation, long-content handling, and lifecycle errors.

**Acceptance criteria:** Permitted participants read and reply without losing
context; ordering matches the API; duplicate submission is prevented or clearly
handled; no real-time collaboration is implied.

**Tests expected:** Timeline ordering, reply validation/submission, duplicate
handling, permissions, closed state, accessibility, and discussion flow.

**Explicitly deferred:** WebSockets, presence, mentions, notifications, rich
text, reply editing/deletion, and attachments.

### Task 38 - Model comment disposition and workflow transitions

**Goal:** Add the smallest validated comment resolution lifecycle while keeping
disposition semantics distinct in the design.

**Main implementation work:** Document the lifecycle from observed product
requirements; add necessary fields/migration, named transition use cases,
resolution text rules, role permissions, timestamps, and optimistic concurrency.

**Acceptance criteria:** Every allowed transition and actor is explicit; invalid
or stale transitions fail atomically; resolution data requirements are enforced;
the model does not overload a value with contradictory meanings.

**Tests expected:** Full transition/permission matrix, required resolution,
reopen behavior if included, stale/double actions, lifecycle interactions,
constraints, and migration.

**Explicitly deferred:** Configurable workflows, customer-defined statuses,
automation, audit subsystem integration, bulk transitions, and cross-revision
relationships.

### Task 39 - Add comment resolution UI

**Goal:** Let authorized participants disposition and close comments with clear
history-independent current state.

**Main implementation work:** Add status badges with text, permitted actions,
resolution forms, confirmations, version/conflict recovery, and register filters.

**Acceptance criteria:** UI actions exactly match server permissions/transitions;
required explanations are accessible; stale actions preserve user input while
refreshing context.

**Tests expected:** Transition forms/matrix, required text, permissions, stale
conflict, filters, keyboard use, and resolution integration flow.

**Explicitly deferred:** Bulk actions, configurable colors/statuses, formal audit
timeline, notifications, analytics, and revision carry-forward.

### Task 40 - Add explicit cross-revision comment relationships

**Goal:** Preserve provenance when a prior comment is carried or superseded in a
new revision review.

**Main implementation work:** Define supported relationship semantics; add
relation table/migration and guarded link/create operations; expose predecessor/
successor context in API and UI without copying historical records.

**Acceptance criteria:** Links join compatible documents/revisions under one
project, cannot form prohibited duplicates/cycles, preserve both comments, and
require explicit authorized action.

**Tests expected:** Compatibility and tenant checks, duplicate/cycle constraints,
permissions, concurrent linking, provenance serialization, UI context, migration.

**Explicitly deferred:** Automatic text/page matching, PDF diff, mass carry-
forward, semantic AI matching, and configurable relationship types.

### Task 41 - Add document review status aggregation

**Goal:** Derive a documented review outcome from cycle, assignment, and comment
state without conflating those concepts.

**Main implementation work:** Define aggregation rules; add assignment completion
operation if required; implement efficient query/read model and display on review
and document pages.

**Acceptance criteria:** Status is deterministic for edge cases such as no
assignments, overdue work, open comments, and cancelled cycles; authoritative
source states remain inspectable; queries are bounded.

**Tests expected:** Rule table/edge cases, permissions, concurrent completion,
query counts/performance fixture, serialization, and UI states.

**Explicitly deferred:** Custom formulas, SLA policy, scheduled reminders,
portfolio rollups, materialized views, and external reporting.

## Milestone 7: finding, reporting, and auditability

### Task 42 - Add project review dashboard

**Goal:** Show a small set of trustworthy project review metrics backed by
implemented workflows.

**Main implementation work:** Define each metric precisely; add purpose-built,
permission-scoped aggregate queries and a restrained project dashboard with
drill-down links and an "as of" time.

**Acceptance criteria:** Counts reconcile to filtered source lists, exclude
unauthorized data, handle empty projects, and avoid unbounded ORM loading.

**Tests expected:** Metric fixtures and boundary cases, tenant/permission scope,
query budget, time/deadline cases, and dashboard rendering.

**Explicitly deferred:** Custom widgets, charts without decisions to support,
cross-organization analytics, caching, scheduled snapshots, and forecasting.

### Task 43 - Add cross-project search and advanced filters

**Goal:** Let a user find authorized documents, reviews, and comments with
PostgreSQL-backed bounded search.

**Main implementation work:** Define search semantics; add indexed queries,
cursor or stable offset pagination as appropriate, entity/filter facets, a
search endpoint, and accessible result UI.

**Acceptance criteria:** Results are deterministic, tenant/project scoped, safe
from wildcard abuse, and responsive for an agreed representative dataset;
ranking behavior is documented.

**Tests expected:** Scope/permissions, query semantics, escaping, pagination
stability, index/query-plan check on representative data, and UI filters.

**Explicitly deferred:** Elasticsearch, fuzzy/semantic search, OCR content,
saved searches, highlighting sophistication, and global admin search.

### Task 44 - Export a consolidated comment register

**Goal:** Produce a deterministic Excel register from authorized filtered review
data.

**Main implementation work:** Define columns and value semantics; add a bounded
export endpoint/service using a maintained workbook library; prevent spreadsheet
formula injection; stream a styled but simple workbook with traceable filters.

**Acceptance criteria:** Exported rows reconcile to API filters and include the
document/revision/reviewer/comment/resolution/status timestamps defined by the
domain; hostile cell values remain data; large allowed exports stay bounded.

**Tests expected:** Workbook structure and cell types, formula injection,
Unicode/long text, time zones, permissions, filter reconciliation, row limit,
and deterministic fixture inspection.

**Explicitly deferred:** PDF/CSV reports, templates, background exports, email
delivery, pivot dashboards, and organization-specific column customization.

### Task 45 - Add transactional audit event foundation

**Goal:** Record structured, immutable business events atomically with selected
state changes.

**Main implementation work:** Accept the audit ADR; add audit schema/migration,
actor/resource/action fields, safe structured metadata policy, writer interface
using the caller transaction, and coverage for one representative command.

**Acceptance criteria:** The domain mutation and audit record commit or roll back
together; records cannot be changed through application APIs; sensitive content
is excluded by policy; system versus user actors are distinguishable.

**Tests expected:** Atomic success/rollback, actor/resource integrity, metadata
validation/redaction, immutability boundary, permissions, and migration.

**Explicitly deferred:** Retrofitting all actions, hash chaining, external SIEM,
retention/archive jobs, audit UI, and compliance claims.

### Task 46 - Expand audit coverage and add an audit timeline

**Goal:** Cover the agreed high-value workflow commands and make their history
available to authorized users.

**Main implementation work:** Add events to authentication administration,
project/document/revision, review assignment/lifecycle, comment transition, and
file actions; add permission-scoped paginated queries and a human-readable UI
mapper separate from stored event data.

**Acceptance criteria:** The documented auditable-command matrix has coverage;
events retain stable identifiers and before/after data only where safe; viewers
cannot access unrelated tenant history; unknown event versions remain displayable.

**Tests expected:** Per-command event and rollback assertions, tenant/permission
scope, pagination/order, metadata redaction, event-version fallback, and UI.

**Explicitly deferred:** Tamper-evident external ledger, SIEM export, long-term
archive, legal retention policies, full-text audit search, and compliance
certification.

## Milestone 8: production hardening

### Task 47 - Add an S3-compatible object storage adapter

**Goal:** Support production-style private object storage without changing file
domain semantics.

**Main implementation work:** Implement the Task 24 adapter contract for a
selected S3-compatible service, typed settings, private bucket/key policy,
streaming integrity checks, timeouts, cleanup/retry behavior, and adapter
contract tests against an ephemeral real service.

**Acceptance criteria:** Local and object adapters pass the same behavioral
contract; no bucket is public; storage credentials/keys are not exposed; failed
operations preserve accurate metadata and diagnostics.

**Tests expected:** Shared adapter suite, service integration, large streaming
fixture, checksum mismatch, timeout/partial failure, cleanup, permissions, and
configuration validation.

**Explicitly deferred:** CDN/public links, multi-region replication, automatic
tiering, provider-specific lock-in, and migration of existing production data.

### Task 48 - Harden HTTP and dependency security controls

**Goal:** Establish measured production HTTP protections and repeatable
dependency review.

**Main implementation work:** Configure trusted proxies/hosts, explicit origins,
security headers, request/body/time limits, targeted login/upload throttling,
safe production error settings, dependency vulnerability scanning, and a
documented threat checklist.

**Acceptance criteria:** Production fails closed on unsafe/missing configuration;
spoofed forwarding headers and disallowed origins/hosts are rejected; targeted
limits return stable errors; scan findings have an ownership process rather than
being silently ignored.

**Tests expected:** Host/origin/proxy matrix, headers, limits/throttling,
production error leakage, configuration failure, and scanner execution.

**Explicitly deferred:** WAF vendor integration, DDoS guarantees, penetration
test claims, universal rate limiting, DLP, and formal security certification.

### Task 49 - Add operational observability and graceful runtime behavior

**Goal:** Make deployed failures diagnosable without exposing confidential
document data.

**Main implementation work:** Define structured log fields and redaction;
instrument request latency/error and database/storage dependency metrics; add
graceful shutdown/readiness behavior, trace-context compatibility, runbooks, and
tested log/metric cardinality boundaries.

**Acceptance criteria:** Operators can correlate a failed request across web/API
and identify dependency class; shutdown stops new ready traffic and drains
bounded in-flight work; logs/metrics contain no document bodies, passwords, or
session tokens.

**Tests expected:** Redaction, request correlation, metric labels, readiness
during shutdown, bounded drain, dependency failure, and configuration tests.

**Explicitly deferred:** A mandated observability vendor, full distributed
tracing backend, automatic incident response, SLO claims, and business analytics.

### Task 50 - Add a production deployment and recovery baseline

**Goal:** Define one reproducible supported deployment shape and prove recovery
procedures without claiming broad scalability.

**Main implementation work:** Add hardened multi-stage app images, non-root
runtime users, migration job/process, environment contract, one concrete
deployment configuration, TLS/reverse-proxy assumptions, PostgreSQL backup/
restore runbook, release checklist, rollback guidance, and a protected delivery
workflow that promotes immutable tested image digests through staging and
production.

**Acceptance criteria:** Pinned source builds immutable images; pull requests do
not deploy; staging and approved production releases use the same image digests;
deployment starts only with valid configuration and compatible schema; a staging
restore drill recovers database records and reconciles file objects; rollback
limitations are documented and tested where safe.

**Tests expected:** Image builds and health checks, container security inspection,
migration-from-prior-release test, configuration failures, delivery-workflow and
deployment manifest validation, staging smoke flow, protected-environment checks,
and a backup/restore drill.

**Explicitly deferred:** Kubernetes unless the selected hosting requires it,
multi-region/high-availability claims, zero-downtime guarantees, autoscaling
policy, disaster-recovery certification, and additional deployment targets.

## Milestone 1 completion boundary

After Tasks 1-5, ReviewFlow should have a reliable development skeleton and no
product workflow. A developer can run a web shell, a liveness/readiness-aware API,
and local PostgreSQL; CI proves lint, types, tests, migration configuration, and
the web production build. The first database entity deliberately arrives in
Task 6.
