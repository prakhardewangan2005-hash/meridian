#!/usr/bin/env python3
"""Export an incident's metadata + a timeline skeleton to markdown.

Pulls the incident from the controller and emits a postmortem stub pre-filled
with what we know, ready to flesh out.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys

try:
    import httpx
except ImportError:
    print("httpx required", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("code", help="incident code, e.g. INC-005")
    ap.add_argument("--url", default=os.environ.get("MERIDIAN_CONTROLLER_URL", "https://localhost:8443"))
    args = ap.parse_args()

    with httpx.Client(base_url=args.url, verify=False, timeout=10.0) as c:
        r = c.get("/api/v1/incidents")
        r.raise_for_status()
        match = [i for i in r.json() if i["code"] == args.code]
    if not match:
        print(f"incident {args.code} not found", file=sys.stderr)
        sys.exit(1)
    inc = match[0]

    now = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d")
    print(f"""# {inc['code']}: {inc['title']}

* **Severity:** {inc['severity']}
* **Status:** {inc['status']}
* **Date:** {now}
* **Opened:** {inc['opened_at']}
* **Closed:** {inc.get('closed_at') or 'n/a'}

## Summary
{inc.get('description') or '<fill in>'}

## Timeline (UTC)
| Time | Event |
|---|---|
| {inc['opened_at']} | incident opened |
| ... | ... |

## Root cause (5 whys)
1. <fill in>

## Action items
| Action | Owner | Tracking | Status |
|---|---|---|---|
| <fill in> | @owner | #NNN | open |
""")


if __name__ == "__main__":
    main()
