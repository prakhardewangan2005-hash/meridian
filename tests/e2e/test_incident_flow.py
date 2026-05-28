"""End-to-end incident lifecycle: open -> list -> close."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


def test_incident_lifecycle(controller_url: str) -> None:
    import httpx
    with httpx.Client(base_url=controller_url, verify=False, timeout=10.0) as c:
        r = c.post("/api/v1/incidents", json={
            "code": "INC-E2E", "title": "e2e test incident", "severity": "SEV3",
        })
        assert r.status_code in (200, 201)
        incident_id = r.json()["id"]

        listed = c.get("/api/v1/incidents").json()
        assert any(i["code"] == "INC-E2E" for i in listed)

        r = c.post(f"/api/v1/incidents/{incident_id}/close")
        assert r.status_code == 200
        assert r.json()["status"] == "closed"
