"""meridian-controller entry point."""
from __future__ import annotations

import logging
import sys

import structlog
import uvicorn

from meridian_controller.app import app, get_settings


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
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level)),
        cache_logger_on_first_use=True,
    )


def main() -> None:
    settings = get_settings()
    _configure_logging(settings.log_level)
    uvicorn.run(
        "meridian_controller.app:app",
        host=settings.bind_host,
        port=settings.bind_port,
        ssl_certfile=str(settings.tls.server_cert) if settings.tls.server_cert.exists() else None,
        ssl_keyfile=str(settings.tls.server_key) if settings.tls.server_key.exists() else None,
        ssl_ca_certs=str(settings.tls.ca_cert) if settings.tls.require_client_cert and settings.tls.ca_cert.exists() else None,
        ssl_cert_reqs=2 if settings.tls.require_client_cert else 0,  # CERT_REQUIRED=2
        log_config=None,
    )


if __name__ == "__main__":
    main()
