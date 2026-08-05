#!/usr/bin/env python3
"""Create a GitHub release, which creates the v* tag and triggers PyPI publish."""
import argparse
import subprocess


def main():
    p = argparse.ArgumentParser(description="Create a GitHub release")
    p.add_argument("version", help="Version to release, e.g. 5.0.3")
    p.add_argument("--target-branch", required=True, help="Release branch, e.g. v5.0.x")
    args = p.parse_args()

    tag = f"v{args.version}"
    cmd = [
        "gh", "release", "create", tag,
        "--target", args.target_branch,
        "--generate-notes",
        "--title", tag,
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print(f"Release created: {result.stdout.strip()}")


if __name__ == "__main__":
    main()
