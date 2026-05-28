"""End-to-end: register a node, create a probe, see it listed."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


def test_health_and_ready(controller_url: str) -> None:
    import httpx
    assert httpx.get(f"{controller_url}/healthz", verify=False).status_code == 200
    assert httpx.get(f"{controller_url}/readyz", verify=False).status_code in (200, 503)


def test_register_then_list_node(controller_url: str) -> None:
    import httpx
    with httpx.Client(base_url=controller_url, verify=False, timeout=10.0) as c:
        r = c.post("/api/v1/nodes/register", json={
            "node_id": "e2e-node", "hostname": "e2e", "kernel": "test",
        })
        assert r.status_code in (200, 201)
        nodes = c.get("/api/v1/nodes").json()
        assert any(n["id"] == "e2e-node" for n in nodes)


def test_create_and_list_probe(controller_url: str) -> None:
    import httpx
    with httpx.Client(base_url=controller_url, verify=False, timeout=10.0) as c:
        r = c.post("/api/v1/probes", json={
            "name": "e2e-probe", "probe_type": "dns", "target": "example.com",
        })
        assert r.status_code in (200, 201)
        probes = c.get("/api/v1/probes").json()
        assert any(p["name"] == "e2e-probe" for p in probes)
