"""FastAPI app factory and lifecycle."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import AsyncIterator

import structlog
from fastapi import FastAPI
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
    multiprocess,
)
from starlette.requests import Request
from starlette.responses import Response

from meridian_controller.api.v1 import chaos, health, incidents, nodes, probes, slos
from meridian_controller.config import ControllerSettings
from meridian_controller.db import init_engine, session_scope
from meridian_controller.services.registry_service import mark_stale_nodes
from meridian_controller.services.slo_evaluator import SLOEvaluator, run_periodic

log = structlog.get_logger(__name__)


@lru_cache(maxsize=1)
def get_settings() -> ControllerSettings:
    return ControllerSettings()  # type: ignore[call-arg]


_registry = CollectorRegistry()
REQUEST_COUNT = Counter(
    "meridian_controller_requests_total",
    "Total HTTP requests received",
    ("method", "path", "status"),
    registry=_registry,
)
REQUEST_LATENCY = Histogram(
    "meridian_controller_request_latency_seconds",
    "Request latency",
    ("method", "path"),
    registry=_registry,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    init_engine(settings)
    shutdown = asyncio.Event()
    evaluator = SLOEvaluator(settings.prometheus)
    eval_task = asyncio.create_task(
        run_periodic(evaluator, settings.slo_eval_interval_s, shutdown),
        name="slo-evaluator",
    )

    async def reaper() -> None:
        while not shutdown.is_set():
            try:
                async with session_scope() as session:
                    await mark_stale_nodes(session, settings.heartbeat_timeout_s)
            except Exception:
                log.exception("reaper.cycle_failed")
            try:
                await asyncio.wait_for(shutdown.wait(), timeout=30.0)
                return
            except asyncio.TimeoutError:
                continue

    reaper_task = asyncio.create_task(reaper(), name="node-reaper")
    log.info("controller.started")
    try:
        yield
    finally:
        shutdown.set()
        for t in (eval_task, reaper_task):
            t.cancel()
            try:
                await t
            except (asyncio.CancelledError, Exception):
                pass
        log.info("controller.stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        title="meridian-controller",
        version="0.1.0",
        description="Meridian central control plane",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def observe(request: Request, call_next):  # type: ignore[no-untyped-def]
        import time as _t

        start = _t.perf_counter()
        response: Response = await call_next(request)
        elapsed = _t.perf_counter() - start
        path = request.url.path
        REQUEST_COUNT.labels(request.method, path, str(response.status_code)).inc()
        REQUEST_LATENCY.labels(request.method, path).observe(elapsed)
        return response

    @app.get("/metrics", include_in_schema=False)
    async def metrics() -> Response:
        data = generate_latest(_registry)
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    # health/readiness at root
    app.include_router(health.router, tags=["health"])
    # versioned API
    app.include_router(nodes.router, prefix="/api/v1/nodes", tags=["nodes"])
    app.include_router(probes.router, prefix="/api/v1/probes", tags=["probes"])
    app.include_router(slos.router, prefix="/api/v1/slos", tags=["slos"])
    app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["incidents"])
    app.include_router(chaos.router, prefix="/api/v1/chaos", tags=["chaos"])
    return app


app = create_app()
