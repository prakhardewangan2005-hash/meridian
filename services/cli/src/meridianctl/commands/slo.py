"""slo command group."""
from __future__ import annotations

import click

from meridianctl.client import ControllerClient
from meridianctl.formatters import render


@click.group()
def slo() -> None:
    """Inspect SLOs and error budgets."""


@slo.command(name="list")
def list_slos() -> None:
    c = ControllerClient()
    try:
        r = c.get("/api/v1/slos")
        r.raise_for_status()
        render(
            r.json(), "table",
            columns=["id", "name", "service", "objective_pct", "window_days"],
            title="slos",
        )
    finally:
        c.close()


@slo.command(name="status")
@click.argument("slo_id", type=int)
def slo_status(slo_id: int) -> None:
    """Show the latest burn-rate snapshot for an SLO."""
    c = ControllerClient()
    try:
        r = c.get(f"/api/v1/slos/{slo_id}/burn-rate")
        if r.status_code == 404:
            click.echo("no snapshots yet; the evaluator may not have run.")
            return
        r.raise_for_status()
        render(r.json(), "yaml")
    finally:
        c.close()
