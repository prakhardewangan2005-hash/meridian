"""SLOEvaluator unit tests with a faked Prometheus client."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from meridian_controller.config import PrometheusConfig
from meridian_controller.services.slo_evaluator import PrometheusClient, SLOEvaluator


@pytest.mark.asyncio
async def test_prometheus_client_returns_none_on_no_result(monkeypatch: pytest.MonkeyPatch) -> None:
    c = PrometheusClient(PrometheusConfig(url="http://localhost"))
    # Patch httpx.AsyncClient.get to return empty result
    class _Resp:
        def raise_for_status(self) -> None: ...
        def json(self) -> dict: return {"status": "success", "data": {"result": []}}

    class _C:
        def __init__(self, **_kw): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return None
        async def get(self, *_a, **_kw): return _Resp()

    monkeypatch.setattr("meridian_controller.services.slo_evaluator.httpx.AsyncClient", _C)
    assert await c.instant_query("up") is None


def test_evaluator_constructs() -> None:
    e = SLOEvaluator(PrometheusConfig(url="http://localhost"))
    assert e is not None
