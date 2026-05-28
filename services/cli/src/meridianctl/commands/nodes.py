"""nodes command group."""
from __future__ import annotations

import click

from meridianctl.client import ControllerClient
from meridianctl.formatters import render


@click.group()
def nodes() -> None:
    """Manage registered nodes."""


@nodes.command(name="list")
@click.option("--format", "format_", type=click.Choice(["table", "json", "yaml"]), default="table")
def list_nodes(format_: str) -> None:
    """List all nodes the controller knows about."""
    c = ControllerClient()
    try:
        r = c.get("/api/v1/nodes")
        r.raise_for_status()
        render(
            r.json(), format_,
            columns=["id", "hostname", "state", "last_heartbeat"],
            title="nodes",
        )
    finally:
        c.close()


@nodes.command(name="describe")
@click.argument("node_id")
def describe_node(node_id: str) -> None:
    """Show details for a single node."""
    c = ControllerClient()
    try:
        r = c.get("/api/v1/nodes")
        r.raise_for_status()
        match = [n for n in r.json() if n["id"] == node_id]
        if not match:
            raise click.ClickException(f"node {node_id!r} not found")
        render(match[0], "yaml")
    finally:
        c.close()


@nodes.command(name="drain")
@click.argument("node_id")
def drain_node(node_id: str) -> None:
    """Mark a node as draining (no new probe assignments)."""
    click.echo(f"[stub] draining {node_id}")
