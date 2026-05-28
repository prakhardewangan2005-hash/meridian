"""Layered configuration for meridian-agent.

Resolution order (later wins):
  1. defaults defined here
  2. /etc/meridian/agent.yaml (or path passed via --config)
  3. MERIDIAN_AGENT_* environment variables (12-factor override)
  4. CLI flags (handled by __main__.py)
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ControllerConfig(BaseModel):
    url: str = Field(default="https://controller.meridian.local:8443")
    ca_cert: Path = Path("/etc/meridian/pki/ca.pem")
    client_cert: Path = Path("/etc/meridian/pki/agent.pem")
    client_key: Path = Path("/etc/meridian/pki/agent-key.pem")
    heartbeat_interval_s: float = Field(default=30.0, ge=1.0, le=300.0)
    register_retry_initial_s: float = 1.0
    register_retry_max_s: float = 60.0


class ExporterConfig(BaseModel):
    bind_host: str = "0.0.0.0"
    bind_port: int = Field(default=9101, ge=1, le=65535)


class BufferConfig(BaseModel):
    path: Path = Path("/var/lib/meridian/buffer")
    max_bytes: int = Field(default=1024 * 1024 * 1024, ge=1024 * 1024)  # 1 GiB
    flush_batch_size: int = 256


class SystemMetricsConfig(BaseModel):
    enabled: bool = True
    interval_s: float = Field(default=15.0, ge=1.0)
    include_cgroups: bool = True


class ProbeDefaults(BaseModel):
    timeout_s: float = Field(default=5.0, gt=0.0)
    interval_s: float = Field(default=30.0, gt=0.0)
    jitter_s: float = Field(default=2.0, ge=0.0)
    max_concurrent: int = Field(default=64, ge=1)


class LogShipperConfig(BaseModel):
    enabled: bool = True
    endpoint: str = "https://logs.meridian.local:3100/loki/api/v1/push"
    batch_size: int = 100
    batch_interval_s: float = 5.0


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MERIDIAN_AGENT_",
        env_nested_delimiter="__",
        extra="forbid",
    )

    node_id: str = Field(min_length=1)
    labels: dict[str, str] = Field(default_factory=dict)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    controller: ControllerConfig = ControllerConfig()
    exporter: ExporterConfig = ExporterConfig()
    buffer: BufferConfig = BufferConfig()
    system_metrics: SystemMetricsConfig = SystemMetricsConfig()
    probes: ProbeDefaults = ProbeDefaults()
    logs: LogShipperConfig = LogShipperConfig()

    @field_validator("labels")
    @classmethod
    def _no_reserved_labels(cls, v: dict[str, str]) -> dict[str, str]:
        reserved = {"__name__", "instance", "job"}
        bad = reserved & v.keys()
        if bad:
            raise ValueError(f"reserved label(s): {sorted(bad)}")
        return v


def _load_yaml(path: Path) -> dict:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level must be a mapping")
    return data


def load_config(file_path: Path | None = None) -> AgentSettings:
    """Resolve file + env into AgentSettings."""
    file_data: dict = {}
    if file_path is not None:
        file_data = _load_yaml(file_path)
    elif Path("/etc/meridian/agent.yaml").is_file():
        file_data = _load_yaml(Path("/etc/meridian/agent.yaml"))
    return AgentSettings(**file_data)
