---
name: elyra-release
description: "DRAFT: Guide the user through the odh-elyra release process (some steps may be incomplete)"
---

# ODH-Elyra Release Process (DRAFT)

**This skill is a draft.** It documents what is known about the release process from the repo's CI workflows and scripts. Steps marked with "UNKNOWN" need to be filled in by someone who has done a release before.

## Prerequisites

- Write access to the `opendatahub-io/elyra` repo
- Permissions to trigger GitHub Actions workflows
- PyPI trusted publishing is configured (no manual credentials needed)

## Steps

### 1. Decide the new version number

Determine the new version (e.g. `5.0.3`). Follow semver conventions — patch for bug fixes, minor for new features, major for breaking changes.

### 2. Update the version via GitHub Actions

Trigger the **"Update version through Pull Request"** workflow (`update-version-through-pr.yml`) in the GitHub Actions UI:

- **version**: the new version (e.g. `5.0.3`)
- **source_branch**: the branch to update (usually `main`)
- **target_branch**: the branch to merge into (usually a release branch)

This runs `.github/workflows/scripts/update_version.sh`, which updates the version in:
- `elyra/_version.py`
- Root `package.json`
- All lerna sub-package `package.json` files

It then opens a PR automatically.

### 3. Review and merge the version bump PR

Review the automated PR to confirm the version was updated correctly across all files, then merge it.

### 4. Tag the release

**UNKNOWN**: It is not clear from the repo whether the tag is created manually or automatically after the version PR merges. Someone needs to create a git tag matching the version:

```bash
git tag v5.0.3
git push origin v5.0.3
```

### 5. Publish to PyPI (automatic)

Pushing the `v*` tag triggers the **"Elyra Release"** workflow (`release.yml`), which:
1. Checks out the tagged commit
2. Verifies `_version.py` matches the tag
3. Builds the wheel (`make install-prod`)
4. Publishes to PyPI via trusted publishing

You can also trigger this manually via `workflow_dispatch` with:
- **tag**: the tag name (e.g. `v5.0.3`)
- **dry_run**: set to `true` to test without publishing

### 6. Create a GitHub Release

**UNKNOWN**: It is not clear whether a GitHub Release is created manually or by another workflow. Check the repo's release history for conventions on release notes format.

### 7. Container image

**UNKNOWN**: The release workflow only publishes to PyPI. It is not clear how or where container images are built and published for releases. This may happen in a separate CI system or be a manual step.

### 8. Post-release: bump main to dev version

**UNKNOWN**: After a release, main should be bumped to the next dev version (e.g. `5.1.0.dev0`). It is not clear if this is done automatically or manually. Currently, main shows `5.0.0.dev0` even after multiple 5.x releases, which may be an oversight.

## Daily CI dry run

The release workflow also runs daily at 4am UTC as a dry run (`release.yml` cron schedule). This catches build issues early without publishing anything. No action needed — just be aware it runs.

## Post-release: update the vendored bootstrapper in the notebooks repo

The `opendatahub-io/notebooks` repo vendors a copy of `elyra/kfp/bootstrapper.py` for use in **pipeline runtime images** — the containers that execute inside Kubeflow Pipeline steps. This copy is checked into the notebooks repo at `prefetch-input/elyra-v<VERSION>/elyra/kfp/bootstrapper.py` and is NOT updated automatically by the elyra release workflow. All seven runtime Dockerfiles (`runtimes/*/ubi9-python-3.12/Dockerfile.konflux.*`) COPY from this vendored path.

After publishing a new elyra release, open a PR in the notebooks repo to update the bootstrapper:

1. Replace `prefetch-input/elyra-v<OLD>/elyra/kfp/bootstrapper.py` with the file from the new tag:
   ```bash
   curl -o prefetch-input/elyra-v<OLD>/elyra/kfp/bootstrapper.py \
     https://raw.githubusercontent.com/opendatahub-io/elyra/refs/tags/v<NEW>/elyra/kfp/bootstrapper.py
   ```
2. Rename the directory to match the new version:
   ```bash
   git mv prefetch-input/elyra-v<OLD> prefetch-input/elyra-v<NEW>
   ```
3. Update the README inside that directory to reflect the new version and upstream source URL.
4. Update all runtime Dockerfiles that reference the old path. Find them with:
   ```bash
   grep -rl "elyra-v<OLD>" runtimes/
   ```
   Change `prefetch-input/elyra-v<OLD>/elyra/kfp/bootstrapper.py` to `prefetch-input/elyra-v<NEW>/elyra/kfp/bootstrapper.py` in each.

If this step is skipped, pipeline runtime images will continue running the old bootstrapper even after the workbench images pick up the new elyra wheel via PyPI.

## Known gaps

- How the git tag is created (manual vs automated)
- How GitHub Releases are created and what format the release notes follow
- How container images are built and published for releases
- Whether main's dev version is supposed to be bumped after each release
