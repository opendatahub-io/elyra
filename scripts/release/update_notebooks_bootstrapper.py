#!/usr/bin/env python3
"""Update vendored bootstrapper.py in the notebooks repo after an elyra release."""

import argparse
import subprocess
import sys
import urllib.request
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description="Update vendored elyra bootstrapper in notebooks repo")
    p.add_argument("version", help="New elyra version, e.g. 5.0.3")
    p.add_argument("notebooks_repo", help="Path to notebooks repo checkout")
    args = p.parse_args()

    repo = Path(args.notebooks_repo)
    tag = f"v{args.version}"
    prefetch = repo / "prefetch-input"

    matches = sorted(prefetch.glob("elyra-v*"))
    if len(matches) != 1:
        print(f"Expected 1 elyra-v* dir in {prefetch}, found {len(matches)}: {matches}", file=sys.stderr)
        sys.exit(1)
    old_dir = matches[0]
    old_name = old_dir.name
    new_name = f"elyra-{tag}"

    if old_name == new_name:
        print(f"Already at {new_name}, nothing to do")
        sys.exit(1)

    url = f"https://raw.githubusercontent.com/opendatahub-io/elyra/refs/tags/{tag}/elyra/kfp/bootstrapper.py"
    print(f"Downloading {url}")
    content = urllib.request.urlopen(url).read()
    bp = old_dir / "elyra" / "kfp" / "bootstrapper.py"
    bp.write_bytes(content)
    print(f"  Updated {bp.relative_to(repo)}")

    readme = old_dir / "elyra" / "kfp" / "README.md"
    old_tag = old_name.removeprefix("elyra-")
    readme.write_text(readme.read_text().replace(old_tag, tag))
    print(f"  Updated {readme.relative_to(repo)}")

    new_dir = prefetch / new_name
    subprocess.run(
        ["git", "-C", str(repo), "mv", str(old_dir.relative_to(repo)), str(new_dir.relative_to(repo))],
        check=True,
    )
    print(f"  Renamed {old_name} -> {new_name}")

    count = 0
    for dockerfile in (repo / "runtimes").rglob("Dockerfile.konflux.*"):
        text = dockerfile.read_text()
        if old_name in text:
            dockerfile.write_text(text.replace(old_name, new_name))
            count += 1
            print(f"  Updated {dockerfile.relative_to(repo)}")

    print(f"\nDone. Updated bootstrapper, README, renamed dir, patched {count} Dockerfiles.")
    print(f"Review changes with: git -C {repo} diff --stat")


if __name__ == "__main__":
    main()
