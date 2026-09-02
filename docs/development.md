# ReviewFlow development setup

## Current repository boundary

ReviewFlow currently contains planning documents, root workspace tooling, a
runnable Next.js web shell in `apps/web`, and a FastAPI process in `apps/api`.
The web application presents only the planning-stage boundary; the API exposes
process liveness and request diagnostics only. The database and all product
domain behavior remain deferred to later roadmap tasks.

## Supported tools

Install these versions before working in the repository:

| Tool | Supported version | Policy location |
| --- | --- | --- |
| Node.js | 24.20.0 | `.node-version` |
| pnpm | 11.19.0 | `package.json` |
| Python | 3.14.7 | `.python-version` |
| uv | 0.12.9 | This document |
| PowerShell | 7 or later | Required by repository checks |

Node.js 24 is constrained to its LTS major line in `package.json`; the exact
version in `.node-version` is the development and CI baseline. pnpm is pinned
exactly because different pnpm releases can produce different lockfile output.
Python and uv are pinned because they produce the API environment and lockfile.

After installing Node.js, install the pinned pnpm release:

```powershell
npm install --global pnpm@11.19.0
```

The same command works in PowerShell, Command Prompt, and Unix shells. Confirm
the active tools from the repository root:

```text
node --version
pnpm --version
```

The expected output is `v24.20.0` and `11.19.0`.

uv manages Python for the API work that begins in Task 2. Install uv 0.12.9
using the official installer, then install the pinned Python version:

PowerShell:

```powershell
$env:UV_VERSION = '0.12.9'
irm https://astral.sh/uv/install.ps1 | iex
Remove-Item Env:UV_VERSION
uv python install 3.14.7
```

Unix shells:

```sh
curl -LsSf https://astral.sh/uv/install.sh | env UV_VERSION=0.12.9 sh
uv python install 3.14.7
```

Confirm the active Python project tool with `uv --version`; the expected output
starts with `uv 0.12.9`.

## Install the workspace

From the repository root, install exactly what is recorded in both lockfiles:

```text
pnpm install --frozen-lockfile
uv --directory apps/api sync --locked --all-groups
```

The first command installs the exact web runtime and development dependency
graph from the root `pnpm-lock.yaml`. The second creates `apps/api/.venv` with
the exact API runtime and development dependencies from `apps/api/uv.lock`.

## Repository commands

Run the repository hygiene check:

```text
pnpm check
```

`pnpm check` validates required planning files, roadmap structure, local
Markdown links, and trailing whitespace. It is the same check used by the
current GitHub Actions workflow. Run the application checks locally with:

```text
pnpm lint
pnpm format:check
pnpm typecheck
pnpm test
pnpm build
```

The aggregate commands run Ruff/ESLint, Prettier, strict mypy/TypeScript, and
pytest/Vitest across the applications. `pnpm build` creates the optimized
Next.js production output.

## Run and inspect the web application

Start the web development server from the repository root:

```text
pnpm dev
```

Open `http://localhost:3000`. Inspect the page at narrow and wide viewport
sizes, then press Tab from the top of the page. The first keyboard-focusable
element is the visible `Skip to main content` link; activating it moves focus to
the main content. Confirm that the page has no inactive product controls and
that neither the browser console nor the development server reports errors.
Stop the server with Ctrl+C.

## Run and inspect the API

Start the development server from the repository root:

```text
pnpm dev:api
```

The command listens on `http://127.0.0.1:8000`, reloads after source changes,
and leaves access logging to ReviewFlow's structured request middleware. Check
liveness from another terminal, first with a generated request ID and then with
a valid caller ID:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health/live
Invoke-WebRequest http://127.0.0.1:8000/health/live `
    -Headers @{ 'X-Request-ID' = 'manual-check-001' }
```

Both calls return HTTP 200 and JSON
`{"status":"ok","schema_version":"1"}`. Each response includes an
`X-Request-ID` header; the second response preserves `manual-check-001`.
Application lifecycle and request completion records are emitted as one JSON
object per line on stdout. Stop the server with Ctrl+C.

The API still has no packaged deployment artifact; the root build command
currently builds only the web application.

## API configuration

Settings are read once from environment variables when the application is
created. Supported variables are:

| Variable | Allowed values | Default |
| --- | --- | --- |
| `REVIEWFLOW_ENVIRONMENT` | `local`, `test`, `production` | `local` |
| `REVIEWFLOW_LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `INFO` |

Malformed values stop application startup with a validation error. The local
environment enables FastAPI debug diagnostics; use `production` outside local
development so unexpected responses never expose stack traces. No secrets or
external-service settings exist yet.

## Line endings and local files

`.editorconfig` defines UTF-8, LF line endings, a final newline, spaces, and
trailing-whitespace removal. `.gitattributes` normalizes committed text to LF.
On Windows, configure the editor to honor EditorConfig; Git may use CRLF in the
working tree depending on local `core.autocrlf`, but committed text remains LF.

The root `.env.example` documents safe local values. Use it as a reference and
export only the overrides you need into the process environment before starting
the API. The service does not implicitly search parent directories for dotenv
files. Do not commit secrets, machine-specific paths, virtual environments,
`node_modules`, pnpm stores, editor state, or generated build/test output.

## Clean-clone verification

To verify Task 3 from a clean clone:

1. Confirm Node.js, pnpm, Python, and uv match the supported versions.
2. Run `pnpm install --frozen-lockfile`.
3. Run `uv --directory apps/api sync --locked --all-groups`.
4. Run `pnpm check`, `pnpm lint`, `pnpm format:check`, `pnpm typecheck`,
   `pnpm test`, and `pnpm build`.
5. Start `pnpm dev` and complete the responsive and keyboard inspection above.
6. Stop the web server, start `pnpm dev:api`, and complete both liveness
   requests above.
7. Stop the API server cleanly and confirm `git status --short` has no tracked
   changes.
