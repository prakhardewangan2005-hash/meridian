"""OpenTelemetry tracing setup for FastAPI."""
from __future__ import annotations

from fastapi import FastAPI


def instrument(app: FastAPI) -> None:
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(app)
    except Exception:
        # OTel is optional in dev; the app continues without traces
        pass
