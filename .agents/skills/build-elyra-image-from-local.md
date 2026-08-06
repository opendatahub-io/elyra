---
name: build-elyra-image-from-local
description: Build and push a notebook image with local elyra changes for testing on RHOAI
---

# Build Elyra Image from Local Changes for RHOAI Testing

Build a datascience notebook image that includes local elyra changes, push it to quay.io, and import it into RHOAI for testing.

## Background

The `odh-elyra` JupyterLab extension is developed in a separate repo (https://github.com/opendatahub-io/elyra) and packaged as a Python wheel. The notebooks repo (https://github.com/opendatahub-io/notebooks) builds the workbench container images that include `odh-elyra` as a dependency.

The notebooks build system is hermetic — it uses prefetched wheels from a `cachi2/output/deps/pip/` directory with no network access during the container build. To test local elyra changes on RHOAI, we build a custom wheel, swap it into the prefetch cache, build the notebook image, and push it to quay.io for import into RHOAI. This workflow injects an unreleased wheel into the container build.

## Scope

This skill builds a custom **workbench image** (`jupyter/datascience/`). It covers changes to the JupyterLab extension UI and the backend Python code that compiles and submits pipelines — everything that runs inside the user's browser/notebook session.

It does **not** cover changes to `elyra/kfp/bootstrapper.py`. The bootstrapper runs inside **pipeline runtime images** (`runtimes/datascience/`), which are separate container images. The notebooks repo vendors a copy of the bootstrapper at `prefetch-input/elyra-v<VERSION>/elyra/kfp/bootstrapper.py` — that copy is baked into the runtime images independently of the workbench wheel. To test bootstrapper changes, you would need to also build a custom runtime image with the updated file.

## When to use

- You have local elyra changes (your own branch, a coworker's PR branch, etc.) that you want to test on a deployed RHOAI or ODH instance

## Repos involved

- **Elyra repo:** https://github.com/opendatahub-io/elyra (upstream), plus your fork
- **Notebooks repo:** https://github.com/opendatahub-io/notebooks (upstream), plus your fork
- **Quay namespace for test images:** your quay.io namespace (e.g. `quay.io/<YOUR_USERNAME>/workbench-images`)

## Steps

### 1. In the elyra repo — build the wheel

```bash
# activate the venv first
source .venv/bin/activate

# checkout the branch with the local changes you want to test
# build the wheel (includes frontend JS + backend)
pip install -r build_requirements.txt
make release
# output: dist/odh_elyra-<VERSION>-py3-none-any.whl
```

Note the version in the wheel filename (e.g. `5.0.0.dev0`) — you'll need it in step 2 to update `requirements.cpu.txt`.

`make release` requires Node.js and Yarn for the frontend build. If only backend changes are being tested and the frontend assets are already built, `python -m build` alone may suffice, but `make release` is the safe default.

### 2. In the notebooks repo — prefetch dependencies and swap the wheel

```bash
# check out a new branch based on the latest main to make these changes
# activate the venv
uv sync
source .venv/bin/activate

# run the prefetch script to populate cachi2/output/deps/ with all build dependencies
RELEASE_PYTHON_VERSION=3.12 BUILD_ARCH=linux/amd64 \
    ./scripts/lockfile-generators/prefetch-all.sh \
    --component-dir jupyter/datascience/ubi9-python-3.12
```

After the prefetch completes:

1. **Copy your custom wheel** from `elyra/dist/odh_elyra-<VERSION>-py3-none-any.whl` into `notebooks/cachi2/output/deps/pip/`
2. **Delete the old wheel** — remove the existing `odh_elyra-*-py3-none-any.whl` that the prefetch downloaded, so there's no ambiguity about which version gets installed
3. **Update `requirements.cpu.txt`** — change the `odh-elyra==<OLD_VERSION>` line to match your wheel's version in `jupyter/datascience/ubi9-python-3.12/requirements.cpu.txt`. No hash updates are needed — the Dockerfile uses `--no-verify-hashes`

**Note:** These instructions default to the datascience image (`jupyter/datascience/ubi9-python-3.12`). Tell the user you are updating the datascience image's requirements file. If they need to test on a different image (pytorch, tensorflow, trustyai, rocm), the corresponding `requirements.*.txt` file for that image must be updated instead. To find all files that pin elyra:

```bash
grep -rl "odh-elyra==" --include="requirements*.txt" .
```

### 3. Build the notebook image

```bash
make jupyter-datascience-ubi9-python-3.12 \
    BUILD_ARCH=linux/amd64 \
    PUSH_IMAGES=no
```

The Makefile auto-detects `cachi2/output/` and mounts it into the build. The output image will be tagged as `quay.io/opendatahub/workbench-images:jupyter-datascience-ubi9-python-3.12-<RELEASE>_<DATE>` — note the exact tag from the build output for the next step.

### 4. Tag and push to quay.io

```bash
# retag with a descriptive name for your test
podman tag <IMAGE_TAG_FROM_BUILD_OUTPUT> quay.io/<YOUR_NAMESPACE>/<YOUR_TEST_TAG>
# e.g. quay.io/myuser/workbench-images:datascience-elyra-test

podman login quay.io
podman push quay.io/<YOUR_NAMESPACE>/<YOUR_TEST_TAG>
```

### 5. Import and test on RHOAI
# This part should be done manually by the user to mimic customer usage, it should not be done by the model

1. Go to **Settings > Notebook images > Import new image**
2. Add `quay.io/<YOUR_NAMESPACE>/<YOUR_TEST_TAG>`
3. Create a workbench using that image
4. Test the elyra changes in the workbench

## Troubleshooting

- **Build fails with "No solution found" for a missing package:** The prefetch cache is incomplete. Run `prefetch-all.sh` again (step 2). After it completes, re-copy your custom elyra wheel and re-delete the old one before rebuilding.
- **Wheel version mismatch:** Make sure the version in `requirements.cpu.txt` exactly matches the version string in your wheel filename (e.g. `odh_elyra-5.0.0.dev0-py3-none-any.whl` → `odh-elyra==5.0.0.dev0`).
