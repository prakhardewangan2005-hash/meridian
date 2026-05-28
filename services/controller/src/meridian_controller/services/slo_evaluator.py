"""SLO evaluator.

Periodically queries Prometheus for each SLO's SLI, computes:
  * current SLI value
  * 1h and 6h burn rate (Google SRE multi-window method)
  * error budget remaining

Persists snapshots to slo_budget_snapshots. Exposes a query API
for the controller's /api/v1/slos/{id}/burn-rate endpoint.

Multi-window burn-rate alert thresholds (per Google SRE workbook):
  * fast burn:  1h > 14.4    AND 5m > 14.4
  * slow burn:  6h > 6       AND 30m > 6
We compute the long windows here; the short windows are evaluated in
Prometheus recording rules (config/prometheus/recording-rules/slo-burn-rate.yml).
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meridian_controller.config import PrometheusConfig
from meridian_controller.db import session_scope
from meridian_controller.models.slo import SLOBudgetSnapshot, SLODefinition

log = structlog.get_logger(__name__)


@dataclass(slots=True)
class BurnRateResult:
    slo_id: int
    sli_value: float
    burn_rate_1h: float
    burn_rate_6h: float
    error_budget_remaining_pct: float


class PrometheusClient:
    def __init__(self, cfg: PrometheusConfig) -> None:
        self._cfg = cfg

    async def instant_query(self, expr: str) -> float | None:
        async with httpx.AsyncClient(timeout=self._cfg.query_timeout_s) as c:
            r = await c.get(
                f"{self._cfg.url}/api/v1/query", params={"query": expr}
            )
            r.raise_for_status()
            data = r.json()
        if data.get("status") != "success":
            return None
        result = data.get("data", {}).get("result", [])
        if not result:
            return None
        try:
            return float(result[0]["value"][1])
        except (KeyError, IndexError, ValueError):
            return None


def _burn_rate_expr(sli_query: str, window: str) -> str:
    """Wrap an SLI query so it returns the burn-rate over a window.

    burn_rate = error_rate_window / (1 - SLO_objective)
    For simplicity the SLI query should return "current SLI value" directly;
    the caller provides the objective for the budget computation step.
    """
    return f"(1 - ({sli_query})) [{window}]"


class SLOEvaluator:
    def __init__(self, prom_cfg: PrometheusConfig) -> None:
        self._prom = PrometheusClient(prom_cfg)

    async def evaluate_all(self) -> list[BurnRateResult]:
        out: list[BurnRateResult] = []
        async with session_scope() as session:
            slos = (await session.execute(select(SLODefinition))).scalars().all()
            for slo in slos:
                try:
                    result = await self._evaluate_one(slo)
                    out.append(result)
                    await self._persist(session, result)
                except Exception:
                    log.exception("slo.eval_failed", slo_id=slo.id, name=slo.name)
        return out

    async def _evaluate_one(self, slo: SLODefinition) -> BurnRateResult:
        # current SLI value
        sli_value = await self._prom.instant_query(slo.sli_query) or 0.0
        objective = slo.objective_pct / 100.0

        # burn rate: how fast we're consuming the budget vs the rate that
        # would burn 100% in one window. We approximate with two queries.
        # In production this is done in Prometheus recording rules and we
        # just query the pre-computed values.
        burn_1h = await self._prom.instant_query(
            f"meridian:slo_burn_rate_1h{{slo=\"{slo.name}\"}}"
        ) or 0.0
        burn_6h = await self._prom.instant_query(
            f"meridian:slo_burn_rate_6h{{slo=\"{slo.name}\"}}"
        ) or 0.0

        # error budget remaining as a percent of allowed errors:
        # remaining = 1 - (observed_error / allowed_error)
        if objective < 1.0:
            allowed_error = 1.0 - objective
            observed_error = max(0.0, 1.0 - sli_value)
            remaining = max(0.0, 1.0 - observed_error / allowed_error)
        else:
            remaining = 1.0 if sli_value >= 1.0 else 0.0

        return BurnRateResult(
            slo_id=slo.id,
            sli_value=sli_value,
            burn_rate_1h=burn_1h,
            burn_rate_6h=burn_6h,
            error_budget_remaining_pct=remaining * 100.0,
        )

    async def _persist(self, session: AsyncSession, r: BurnRateResult) -> None:
        snap = SLOBudgetSnapshot(
            slo_id=r.slo_id,
            sli_value=r.sli_value,
            burn_rate_1h=r.burn_rate_1h,
            burn_rate_6h=r.burn_rate_6h,
            error_budget_remaining_pct=r.error_budget_remaining_pct,
        )
        session.add(snap)


async def run_periodic(
    evaluator: SLOEvaluator,
    interval_s: float,
    shutdown: asyncio.Event,
) -> None:
    log.info("slo_evaluator.starting", interval_s=interval_s)
    while not shutdown.is_set():
        try:
            results = await evaluator.evaluate_all()
            log.info("slo_evaluator.cycle_complete", evaluated=len(results))
        except Exception:
            log.exception("slo_evaluator.cycle_failed")
        try:
            await asyncio.wait_for(shutdown.wait(), timeout=interval_s)
            return
        except asyncio.TimeoutError:
            continue
