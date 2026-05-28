"""meridianctl root command."""
from __future__ import annotations

import click

from meridianctl.commands import chaos, debug, incident, nodes, probes, slo


@click.group()
@click.version_option()
def cli() -> None:
    """Operator CLI for the Meridian platform."""


cli.add_command(nodes.nodes)
cli.add_command(probes.probes)
cli.add_command(slo.slo)
cli.add_command(incident.incident)
cli.add_command(chaos.chaos)
cli.add_command(debug.debug)
