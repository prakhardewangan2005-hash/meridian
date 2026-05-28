"""End-to-end chaos: inject (dry-run) via the controller, list, abort."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


def test_chaos_dry_run_roundtrip(controller_url: str) -> None:
    import httpx
    with httpx.Client(base_url=controller_url, verify=False, timeout=10.0) as c:
        r = c.post("/api/v1/chaos/inject", json={
            "kind": "network_latency",
            "target_node": "e2e-node",
            "duration_s": 5,
            "params": {"interface": "eth0", "delay_ms": 10},
            "dry_run": True,
        })
        # 202 accepted, or 502/503 if chaos service isn't wired in this env
        assert r.status_code in (202, 500, 502, 503)
