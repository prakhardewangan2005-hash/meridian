"""Controller configuration."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TLSConfig(BaseModel):
    ca_cert: Path = Path("/etc/meridian/pki/ca.pem")
    server_cert: Path = Path("/etc/meridian/pki/controller.pem")
    server_key: Path = Path("/etc/meridian/pki/controller-key.pem")
    require_client_cert: bool = True


class PrometheusConfig(BaseModel):
    url: str = "http://prometheus:9090"
    query_timeout_s: float = 10.0


class ChaosConfig(BaseModel):
    service_url: str = "http://chaos:8080"
    default_dry_run: bool = True
    max_concurrent_experiments: int = 5


class ControllerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MERIDIAN_CONTROLLER_",
        env_nested_delimiter="__",
        extra="forbid",
    )

    bind_host: str = "0.0.0.0"
    bind_port: int = Field(default=8443, ge=1, le=65535)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    db_dsn: str = "postgresql+asyncpg://meridian:meridian-dev@postgres:5432/meridian"
    db_pool_size: int = 10
    db_max_overflow: int = 5

    tls: TLSConfig = TLSConfig()
    prometheus: PrometheusConfig = PrometheusConfig()
    chaos: ChaosConfig = ChaosConfig()

    # SLO evaluator runs as a background task
    slo_eval_interval_s: float = Field(default=60.0, ge=10.0)

    # mark node unhealthy if no heartbeat in this many seconds
    heartbeat_timeout_s: float = Field(default=90.0, ge=10.0)
