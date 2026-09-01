# ReviewFlow development setup

## Current repository boundary

ReviewFlow currently contains planning documents and root workspace tooling.
There is no runnable API, web application, database, or application dependency
set yet. Those artifacts are introduced by later roadmap tasks.

## Supported tools

Install these versions before working in the repository:

| Tool | Supported version | Policy location |
| --- | --- | --- |
| Node.js | 24.20.0 | `.node-version` |
| pnpm | 11.19.0 | `package.json` |
| Python | 3.14.7 | `.python-version` |
| uv | 0.12.1 | This document |
| PowerShell | 7 or later | Required by repository checks |

Node.js 24 is constrained to its LTS major line in `package.json`; the exact
version in `.node-version` is the development and CI baseline. pnpm is pinned
exactly because different pnpm releases can produce different lockfile output.
Python and uv are defined now so the API bootstrap uses one agreed toolchain,
but Task 1 intentionally has no Python package or dependencies to install.

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

uv manages Python for the API work that begins in Task 2. Install uv 0.12.1
using the official installer, then install the pinned Python version:

PowerShell:

```powershell
$env:UV_VERSION = '0.12.1'
irm https://astral.sh/uv/install.ps1 | iex
Remove-Item Env:UV_VERSION
uv python install 3.14.7
```

Unix shells:

```sh
curl -LsSf https://astral.sh/uv/install.sh | env UV_VERSION=0.12.1 sh
uv python install 3.14.7
```

No `uv sync` command is available yet because the API package and its lockfile
are explicitly deferred to Task 2.

## Install the workspace

From the repository root, install exactly what is recorded in the lockfile:

```text
pnpm install --frozen-lockfile
```

The root workspace currently has no JavaScript dependencies, so this validates
the manifest, workspace configuration, package-manager pin, and lockfile
without creating application packages.

## Repository commands

Run the checks that exist in the current repository:

```text
pnpm check
```

`pnpm check` validates required planning files, roadmap structure, local
Markdown links, and trailing whitespace. It is the same check used by the
current GitHub Actions workflow.

The root command names `dev`, `build`, `lint`, `typecheck`, and `test` are
reserved for consistent use as applications are added. Today each exits with a
clear error explaining that the corresponding application does not exist; a
successful no-op would incorrectly imply that work was checked.

## Line endings and local files

`.editorconfig` defines UTF-8, LF line endings, a final newline, spaces, and
trailing-whitespace removal. `.gitattributes` normalizes committed text to LF.
On Windows, configure the editor to honor EditorConfig; Git may use CRLF in the
working tree depending on local `core.autocrlf`, but committed text remains LF.

Create a local `.env` only when a later task documents real variables. The
current `.env.example` is deliberately empty except for an explanatory comment.
Do not commit secrets, machine-specific paths, virtual environments,
`node_modules`, pnpm stores, editor state, or generated build/test output.

## Clean-clone verification

To verify Task 1 from a clean clone:

1. Confirm `node --version` and `pnpm --version` match the supported versions.
2. Run `pnpm install --frozen-lockfile`.
3. Run `pnpm check`.
4. Run one unavailable command such as `pnpm dev` and confirm it exits nonzero
   with the bootstrap message.
5. Run `git status --short` and confirm the commands created no tracked changes.
