#!/usr/bin/env python3
"""Trigger the update-version-through-pr workflow to create a version bump PR."""
import argparse
import subprocess


def main():
    p = argparse.ArgumentParser(description="Trigger version bump PR workflow")
    p.add_argument("version", help="New version, e.g. 5.0.3")
    p.add_argument("--source-branch", required=True, help="Branch to update, e.g. v5.0.x")
    p.add_argument("--target-branch", required=True, help="PR target branch, e.g. v5.0.x")
    args = p.parse_args()

    cmd = [
        "gh", "workflow", "run", "update-version-through-pr.yml",
        "-f", f"version={args.version}",
        "-f", f"source_branch={args.source_branch}",
        "-f", f"target_branch={args.target_branch}",
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"Workflow triggered for version {args.version}")


if __name__ == "__main__":
    main()
