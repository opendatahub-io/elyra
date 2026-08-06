# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the **ODH (Open Data Hub) fork** of [elyra-ai/elyra](https://github.com/elyra-ai/elyra) — a set of AI-centric JupyterLab extensions focused on Data Science Pipelines v2 and OpenShift AI Workbench. It is published as `odh-elyra` on PyPI (not `elyra`). Only KFP (Kubeflow Pipelines) and local pipeline processors are active.

> **IMPORTANT — Airflow is permanently out of scope for this team.**
> Airflow support is fully disabled and will never be contributed to or maintained by this team. Do **not** analyze, suggest changes to, write tests for, or include `elyra/airflow/` in any work. Treat that directory as dead code.

## Prerequisites

- Node.js 22
- Python 3.11+
- Yarn 3.5.0 (via `packageManager` in `package.json`)

## Common Commands

### Building

```bash
# Full production build and install
make install-prod

# Full development build and install
make install-dev

# Build backend only (Python wheel)
make install-server

# Build frontend only
make build-ui-dev     # development build
make build-ui-prod    # production build

# Build wheel for release (no install)
make release

# Watch frontend during development (run alongside `jupyter lab --watch`)
make watch
```

### Linting

```bash
# Run all linters
make lint

# Backend only (flake8 + black check)
make lint-server

# Apply black formatting
make black-format

# Frontend only (prettier + eslint)
make lint-ui

# Check only (no auto-fix)
make prettier-check-ui
make eslint-check-ui
```

### Testing

```bash
# Run all tests
make test

# Backend Python tests only
make test-server

# Run pytest directly (faster, skips copy steps)
python -m pytest -v elyra/tests/

# Run a single test file
python -m pytest -v elyra/tests/pipeline/test_pipeline_definition.py

# Run a single test
python -m pytest -v elyra/tests/pipeline/test_pipeline_definition.py::TestClass::test_method

# Frontend unit tests
make test-ui-unit
# or: yarn test:unit

# Cypress integration tests
make test-integration

# Open Cypress debugger
make test-integration-debug
```

### Cleanup

```bash
make purge    # Remove build artifacts
make clean    # Full clean: artifacts + uninstall extensions
```

## Architecture

The project has three co-located layers:

### 1. Python backend (`elyra/`)

Jupyter server extension exposing REST APIs. Key modules:

- `pipeline/` — Core pipeline engine. `processor.py` defines the abstract `PipelineProcessor`; `kfp/processor_kfp.py` implements KFP submission. `pipeline_definition.py` and `properties.py` are central to how pipelines are modeled. `validation.py` is very large (~57k) and handles pipeline validation logic.
- `metadata/` — Schema-based metadata system for storing/retrieving runtime configs, runtime images, code snippets, and component catalogs via `schemaspaces` and `schemasproviders` entry points.
- `api/` — Jupyter server HTTP handlers wired up via `elyra_app.py`.
- `cli/` — `elyra-pipeline` and `elyra-metadata` CLI commands.
- `contents/` — Notebook/file content utilities.
- `util/` — Shared utilities.

### 2. TypeScript frontend packages (`packages/`)

Yarn workspaces built with lerna. Each package maps to a JupyterLab extension:

| Package | Purpose |
|---|---|
| `pipeline-editor` | Visual drag-and-drop pipeline editor |
| `metadata` / `metadata-common` | Metadata UI (forms, lists) |
| `code-snippet` | Code snippet manager |
| `python-editor` | Python script editor with run support |
| `script-editor` | Base script editor |
| `script-debugger` | Debugger integration |
| `services` | Shared frontend services (API client) |
| `ui-components` | Shared React components |
| `theme` | Elyra JupyterLab theme |

### 3. JupyterLab extensions (`labextensions/`)

Pre-built labextension bundles (named `elyra_*`) that get installed into Jupyter's share directory. These are the build outputs of the `packages/` TypeScript sources. The Python wheel ships these bundles via `pyproject.toml` `[tool.hatch.build.targets.wheel.shared-data]`.

### Entry Points

The Python package declares entry points that Jupyter discovers at runtime:
- `metadata.schemaspaces` — registers metadata namespaces (runtimes, runtime-images, code-snippets, component-catalogs)
- `elyra.pipeline.processors` — registers `local` and `kfp` pipeline runtime processors
- `elyra.component.catalog_types` — registers component catalog connector types
- `papermill.engine` — registers `ElyraEngine` for notebook execution

### Pipeline Execution Flow

1. User builds a pipeline visually in the frontend (`packages/pipeline-editor`)
2. Frontend sends pipeline JSON to backend via REST (`elyra/pipeline/handlers.py`)
3. `processor.py` dispatches to the appropriate `PipelineProcessor` subclass based on runtime type
4. KFP processor (`elyra/pipeline/kfp/processor_kfp.py`) compiles notebooks/scripts to KFP components and submits to a Kubeflow Pipelines server
5. Component definitions come from catalogs registered via the `elyra.component.catalog_types` entry point

## ODH-Specific Notes

- The PyPI package name is `odh-elyra`, not `elyra`
- R editor, Scala editor, and code viewer extensions are excluded from the ODH distribution (commented out in `pyproject.toml`)
- Airflow pipeline processor is permanently disabled and out of scope — ignore `elyra/airflow/` entirely
- Tests are copied to the installed package before running and cleaned up after (`copy-tests-to-package` / `clean-tests-from-package` make targets) because pytest needs them in the installed location
- Python target versions: 3.11, 3.12, 3.13
- JupyterLab version pinned to `~4.5.0`
