"""probes command group."""
from __future__ import annotations

from pathlib import Path

import click
import yaml

from meridianctl.client import ControllerClient
from meridianctl.formatters import render


@click.group()
def probes() -> None:
    """Manage probe definitions."""


@probes.command(name="list")
@click.option("--format", "format_", type=click.Choice(["table", "json", "yaml"]), default="table")
def list_probes(format_: str) -> None:
    c = ControllerClient()
    try:
        r = c.get("/api/v1/probes")
        r.raise_for_status()
        render(
            r.json(), format_,
            columns=["id", "name", "probe_type", "target", "enabled"],
            title="probes",
        )
    finally:
        c.close()


@probes.command(name="apply")
@click.option("-f", "--file", "filepath", type=click.Path(exists=True, path_type=Path), required=True)
def apply_probes(filepath: Path) -> None:
    """Apply probe definitions from a YAML file."""
    with filepath.open() as f:
        spec = yaml.safe_load(f)
    c = ControllerClient()
    created = 0
    try:
        for probe in spec.get("probes", []):
            r = c.post("/api/v1/probes", json=probe)
            if r.status_code in (200, 201):
                created += 1
            else:
                click.echo(f"  fail: {probe.get('name')}: HTTP {r.status_code} {r.text}", err=True)
        click.echo(f"applied {created} probe(s)")
    finally:
        c.close()


@probes.command(name="delete")
@click.argument("probe_id", type=int)
def delete_probe(probe_id: int) -> None:
    c = ControllerClient()
    try:
        r = c.delete(f"/api/v1/probes/{probe_id}")
        if r.status_code == 204:
            click.echo(f"deleted probe {probe_id}")
        else:
            raise click.ClickException(f"HTTP {r.status_code} {r.text}")
    finally:
        c.close()


@probes.command(name="run-once")
@click.option("--type", "probe_type", required=True, type=click.Choice(["dns", "tcp", "http", "icmp", "traceroute"]))
@click.option("--target", required=True)
@click.option("--timeout-s", type=float, default=5.0)
def run_once(probe_type: str, target: str, timeout_s: float) -> None:
    """Execute a one-shot probe locally and print the result."""
    import asyncio
    import json as _json

    from meridian_agent.probes.registry import discover  # type: ignore[import-not-found]

    registry = discover()
    cls = registry[probe_type]
    probe = cls(name="adhoc", target=target, timeout_s=timeout_s)
    result = asyncio.run(probe.execute())
    print(_json.dumps(result.to_dict(), indent=2, default=str))
