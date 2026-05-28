"""incident command group."""
from __future__ import annotations

import click

from meridianctl.client import ControllerClient
from meridianctl.formatters import render


@click.group()
def incident() -> None:
    """Manage incident lifecycle."""


@incident.command(name="list")
def list_incidents() -> None:
    c = ControllerClient()
    try:
        r = c.get("/api/v1/incidents")
        r.raise_for_status()
        render(
            r.json(), "table",
            columns=["code", "title", "severity", "status", "opened_at"],
            title="incidents",
        )
    finally:
        c.close()


@incident.command(name="open")
@click.option("--code", required=True)
@click.option("--title", required=True)
@click.option("--severity", default="SEV3", type=click.Choice(["SEV1", "SEV2", "SEV3", "SEV4"]))
@click.option("--description", default="")
def open_incident(code: str, title: str, severity: str, description: str) -> None:
    c = ControllerClient()
    try:
        r = c.post(
            "/api/v1/incidents",
            json={
                "code": code,
                "title": title,
                "severity": severity,
                "description": description,
            },
        )
        r.raise_for_status()
        render(r.json(), "yaml")
    finally:
        c.close()


@incident.command(name="close")
@click.argument("incident_id", type=int)
def close_incident(incident_id: int) -> None:
    c = ControllerClient()
    try:
        r = c.post(f"/api/v1/incidents/{incident_id}/close")
        r.raise_for_status()
        render(r.json(), "yaml")
    finally:
        c.close()
