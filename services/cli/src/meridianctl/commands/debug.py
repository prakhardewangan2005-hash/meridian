"""debug command group — invokes the local debug shell scripts."""
from __future__ import annotations

import subprocess

import click


@click.group()
def debug() -> None:
    """Run ad-hoc diagnostics."""


@debug.command(name="network-diag")
@click.argument("target")
def network_diag(target: str) -> None:
    """Run the full network diagnostic bundle against a target."""
    subprocess.run(["bash", "scripts/network-diag.sh", target], check=False)


@debug.command(name="tcp")
@click.argument("target")
def tcp_debug(target: str) -> None:
    subprocess.run(["bash", "scripts/tcp-debug.sh", target], check=False)


@debug.command(name="dns")
@click.argument("target")
def dns_debug(target: str) -> None:
    subprocess.run(["bash", "scripts/dns-debug.sh", target], check=False)
