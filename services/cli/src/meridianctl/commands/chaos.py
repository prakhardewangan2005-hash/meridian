"""chaos command group."""
from __future__ import annotations

import click

from meridianctl.client import ControllerClient
from meridianctl.formatters import render


@click.group()
def chaos() -> None:
    """Inject and manage chaos experiments."""


@chaos.command(name="inject")
@click.argument("kind", type=click.Choice([
    "network_latency", "network_loss", "network_partition",
    "cpu_pressure", "memory_pressure", "disk_fill",
]))
@click.option("--target-node", required=True)
@click.option("--duration", "duration_s", required=True, type=float)
@click.option("--params", default="{}", help="JSON params, e.g. '{\"delay_ms\": 50}'")
@click.option("--apply", is_flag=True, help="Actually run (without this flag, dry-run)")
def inject(kind: str, target_node: str, duration_s: float, params: str, apply: bool) -> None:
    import json as _json
    parsed = _json.loads(params)
    c = ControllerClient()
    try:
        r = c.post(
            "/api/v1/chaos/inject",
            json={
                "kind": kind,
                "target_node": target_node,
                "duration_s": duration_s,
                "params": parsed,
                "dry_run": not apply,
            },
        )
        r.raise_for_status()
        render(r.json(), "yaml")
    finally:
        c.close()


@chaos.command(name="list")
def list_experiments() -> None:
    c = ControllerClient()
    try:
        r = c.get("/api/v1/chaos")
        r.raise_for_status()
        render(r.json(), "yaml")
    finally:
        c.close()


@chaos.command(name="abort")
@click.argument("experiment_id")
def abort_experiment(experiment_id: str) -> None:
    c = ControllerClient()
    try:
        r = c.delete(f"/api/v1/chaos/{experiment_id}")
        r.raise_for_status()
        click.echo(f"aborted {experiment_id}")
    finally:
        c.close()
