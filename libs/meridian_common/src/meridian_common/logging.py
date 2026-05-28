"""Centralized structlog configuration shared by all services."""
from __future__ import annotations

import logging
import sys


def configure_logging(level: str = "INFO", *, json: bool = True) -> None:
    import structlog

    logging.basicConfig(stream=sys.stderr, level=level, format="%(message)s")
    renderer = (
        structlog.processors.JSONRenderer()
        if json
        else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(level)
        ),
        cache_logger_on_first_use=True,
    )
