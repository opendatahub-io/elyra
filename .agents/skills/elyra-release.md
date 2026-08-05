---
name: elyra-release
description: Guide the user through the odh-elyra release process
---

# ODH-Elyra Release Process

## Prerequisites

- Write access to the `opendatahub-io/elyra` repo
- Permissions to trigger GitHub Actions workflows
- PyPI trusted publishing is configured (no manual credentials needed)
- `gh` CLI authenticated

## Steps

### 1. Decide the new version number

Determine the new version (e.g. `5.0.3`). Follow semver conventions — patch for bug fixes, minor for new features, major for breaking changes.

### 2. Create the release branch (major/minor only)

If this is a **patch release** (e.g. `5.0.2` → `5.0.3`), skip this step — the existing release branch (e.g. `v5.0.x`) is reused.

If this is a **minor version increase** (e.g. `5.0.x` → `5.1.x`), create the new release branch from the previous release branch:

```bash
git checkout v5.0.x && git pull upstream v5.0.x
git checkout -b v5.1.x
git push upstream v5.1.x
```

If this is a **major version increase** (e.g. `5.0.x` → `6.0.x`), create the new release branch from `main`:

```bash
git checkout main && git pull upstream main
git checkout -b v6.0.x
git push upstream v6.0.x
```

### 3. Cherry-pick fixes onto the release branch

Go to the release branch (e.g. `v5.0.x`) and cherry-pick all the features and fixes intended for this release. This is a human judgment step — decide which commits from `main` belong in the release.

### 4. Trigger the version bump workflow

From the elyra repo, run:

```bash
python scripts/release/trigger_version_bump.py <VERSION> --source-branch <RELEASE_BRANCH> --target-branch <RELEASE_BRANCH>
```

This triggers the `update-version-through-pr.yml` workflow, which updates the version across all 15 files (`elyra/_version.py`, root `package.json`, `lerna.json`, and 12 sub-package `package.json` files) and opens a PR automatically.

The version bump commit must be the last commit before the release tag.

### 5. Review and merge the version bump PR

Review the automated PR to confirm the version was updated correctly across all files, then merge it.

### 6. Create the GitHub release

From the elyra repo, run:

```bash
python scripts/release/create_release.py <VERSION> --target-branch <RELEASE_BRANCH>
```

This creates a GitHub release with auto-generated release notes and a `v<VERSION>` tag pointing at the release branch. The `v*` tag push automatically triggers the `release.yml` workflow, which builds the wheel and publishes to PyPI via trusted publishing.

### 7. Verify PyPI publish

```bash
python scripts/release/verify_pypi_publish.py <VERSION>
```

This polls PyPI until `odh-elyra` at the given version appears (default timeout: 300s).

### 8. Update the vendored bootstrapper in the notebooks repo

The `opendatahub-io/notebooks` repo vendors a copy of `elyra/kfp/bootstrapper.py` for use in **pipeline runtime images** — the containers that execute inside Kubeflow Pipeline steps. This copy is checked into the notebooks repo at `prefetch-input/elyra-v<VERSION>/elyra/kfp/bootstrapper.py` and is NOT updated automatically by the elyra release workflow. All seven runtime Dockerfiles (`runtimes/*/ubi9-python-3.12/Dockerfile.konflux.*`) COPY from this vendored path.

This script automates the file changes in a local clone of the notebooks repo. It downloads the new bootstrapper from the release tag, updates the README, renames the `prefetch-input/elyra-v*` directory, and patches all runtime Dockerfiles:

```bash
python scripts/release/update_notebooks_bootstrapper.py <VERSION> /path/to/local/notebooks/repo
```

After running it, review the changes in the notebooks repo, commit them, and open a PR there.

If this step is skipped, pipeline runtime images will continue running the old bootstrapper even after the workbench images pick up the new elyra wheel via PyPI.

### 9. (Optional) Bump to next dev version

```bash
python scripts/release/trigger_version_bump.py <NEXT_DEV_VERSION> --source-branch <RELEASE_BRANCH> --target-branch main
```

For example, after releasing `5.0.3`, bump to `5.1.0.dev0`. This opens a PR against `main`. Review and merge it.

## Daily CI dry run

The release workflow also runs daily at 4am UTC as a dry run (`release.yml` cron schedule). This catches build issues early without publishing anything. No action needed — just be aware it runs.

## Container images

Container images are not part of the elyra release process. The `notebooks` repo builds workbench and pipeline runtime images separately. The elyra release only publishes to PyPI.
