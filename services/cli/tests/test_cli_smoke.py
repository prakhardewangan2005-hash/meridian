"""CLI smoke tests with the Click runner."""
from __future__ import annotations

from click.testing import CliRunner

from meridianctl.main import cli


def test_cli_help() -> None:
    res = CliRunner().invoke(cli, ["--help"])
    assert res.exit_code == 0
    assert "Operator CLI" in res.output


def test_nodes_help() -> None:
    res = CliRunner().invoke(cli, ["nodes", "--help"])
    assert res.exit_code == 0


def test_chaos_help() -> None:
    res = CliRunner().invoke(cli, ["chaos", "--help"])
    assert res.exit_code == 0


def test_all_groups_registered() -> None:
    res = CliRunner().invoke(cli, ["--help"])
    for grp in ("nodes", "probes", "slo", "incident", "chaos", "debug"):
        assert grp in res.output
