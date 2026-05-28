"""meridian-chaos FastAPI server."""
from __future__ import annotations

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from meridian_chaos.experiments import ExperimentSpec
from meridian_chaos.runner import ChaosRunner


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MERIDIAN_CHAOS_", extra="ignore")
    bind_host: str = "0.0.0.0"
    bind_port: int = 8080
    dry_run: bool = True
    max_concurrent_experiments: int = 5
    log_level: str = "INFO"


_runner: ChaosRunner | None = None


def _get_runner() -> ChaosRunner:
    assert _runner is not None
    return _runner


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    global _runner
    s = _Settings()
    _runner = ChaosRunner(max_concurrent=s.max_concurrent_experiments)
    try:
        yield
    finally:
        await _runner.shutdown()


class InjectRequest(BaseModel):
    kind: str
    target_node: str
    duration_s: float = Field(ge=1.0, le=3600.0)
    params: dict[str, Any] = Field(default_factory=dict)
    dry_run: bool | None = None


def create_app() -> FastAPI:
    app = FastAPI(title="meridian-chaos", version="0.1.0", lifespan=lifespan)
    settings = _Settings()

    @app.post("/inject", status_code=status.HTTP_202_ACCEPTED)
    async def inject(req: InjectRequest) -> dict:
        spec = ExperimentSpec(
            kind=req.kind,
            target_node=req.target_node,
            duration_s=req.duration_s,
            params=req.params,
            dry_run=req.dry_run if req.dry_run is not None else settings.dry_run,
        )
        try:
            exp = await _get_runner().inject(spec)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return {
            "id": exp.spec.id,
            "kind": exp.spec.kind,
            "dry_run": exp.spec.dry_run,
            "duration_s": exp.spec.duration_s,
        }

    @app.get("/experiments")
    async def list_experiments() -> list[dict]:
        return _get_runner().list_active()

    @app.delete("/experiments/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def abort(experiment_id: str) -> None:
        ok = await _get_runner().abort(experiment_id)
        if not ok:
            raise HTTPException(status_code=404, detail="experiment not found")

    @app.get("/healthz", include_in_schema=False)
    async def healthz() -> dict:
        return {"status": "ok"}

    return app


def _configure_logging(level: str) -> None:
    logging.basicConfig(stream=sys.stderr, level=level, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level)),
    )


def main() -> None:
    s = _Settings()
    _configure_logging(s.log_level)
    uvicorn.run(create_app(), host=s.bind_host, port=s.bind_port, log_config=None)


if __name__ == "__main__":
    main()
