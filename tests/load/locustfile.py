"""Locust load test for the controller API.

Run: locust -f tests/load/locustfile.py --host https://localhost:8443
"""
from __future__ import annotations

import random

from locust import HttpUser, between, task


class FleetUser(HttpUser):
    wait_time = between(0.5, 2.0)

    def on_start(self) -> None:
        # disable TLS verification for the self-signed dev cert
        self.client.verify = False

    @task(5)
    def list_nodes(self) -> None:
        self.client.get("/api/v1/nodes", name="GET /nodes")

    @task(3)
    def list_probes(self) -> None:
        self.client.get("/api/v1/probes", name="GET /probes")

    @task(2)
    def list_slos(self) -> None:
        self.client.get("/api/v1/slos", name="GET /slos")

    @task(4)
    def heartbeat(self) -> None:
        node = f"load-node-{random.randint(1, 50)}"
        # register first (idempotent upsert), then heartbeat
        self.client.post(
            "/api/v1/nodes/register",
            json={"node_id": node, "hostname": node},
            name="POST /nodes/register",
        )
        self.client.post(
            f"/api/v1/nodes/{node}/heartbeat",
            json={"alive": True},
            name="POST /nodes/{id}/heartbeat",
        )

    @task(1)
    def health(self) -> None:
        self.client.get("/healthz", name="GET /healthz")
