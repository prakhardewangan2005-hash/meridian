"""meridian-agent entry point: `python -m meridian_agent` or `meridian-agent` script."""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

import structlog
import yaml

try:
    import uvloop
except ImportError:  # pragma: no cover
    uvloop = None  # type: ignore[assignment]

from meridian_agent.config import load_config
from meridian_agent.probes.base import Probe
from meridian_agent.probes.registry import discover
from meridian_agent.runner import AgentRunner


def _configure_logging(level: str) -> None:
    logging.basicConfig(stream=sys.stderr, level=level, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(level)
        ),
        cache_logger_on_first_use=True,
    )


def _load_probes(path: Path) -> list[Probe]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8") as f:
        spec = yaml.safe_load(f) or {}
    registry = discover()
    out: list[Probe] = []
    for item in spec.get("probes", []):
        ptype = item.pop("type")
        cls = registry.get(ptype)
        if cls is None:
            raise ValueError(
                f"unknown probe type: {ptype!r} (known: {sorted(registry)})"
            )
        out.append(cls(**item))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(prog="meridian-agent")
    parser.add_argument(
        "--config", type=Path, default=None, help="agent config YAML"
    )
    parser.add_argument(
        "--probes",
        type=Path,
        default=Path("/etc/meridian/probes.yaml"),
        help="probe definitions YAML",
    )
    args = parser.parse_args()

    settings = load_config(args.config)
    _configure_logging(settings.log_level)
    probes = _load_probes(args.probes)

    if uvloop is not None:
        uvloop.install()
    asyncio.run(AgentRunner(settings, probes).run())


if __name__ == "__main__":
    main()
