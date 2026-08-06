#!/usr/bin/env python3
"""Poll PyPI until the odh-elyra package at a given version is published."""

import argparse
import sys
import time
import urllib.error
import urllib.request

PACKAGE = "odh-elyra"
POLL_INTERVAL = 30


def main():
    p = argparse.ArgumentParser(description="Verify PyPI publish of odh-elyra")
    p.add_argument("version", help="Version to check, e.g. 5.0.3")
    p.add_argument("--timeout", type=int, default=300, help="Timeout in seconds (default: 300)")
    args = p.parse_args()

    url = f"https://pypi.org/pypi/{PACKAGE}/{args.version}/json"
    deadline = time.time() + args.timeout
    print(f"Polling {url} (timeout {args.timeout}s)")

    while time.time() < deadline:
        try:
            urllib.request.urlopen(url)
            print(f"{PACKAGE} {args.version} is on PyPI")
            return
        except urllib.error.HTTPError:
            remaining = int(deadline - time.time())
            print(f"  Not yet available, {remaining}s remaining...")
            time.sleep(POLL_INTERVAL)

    print(f"TIMEOUT: {PACKAGE} {args.version} not found after {args.timeout}s", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
