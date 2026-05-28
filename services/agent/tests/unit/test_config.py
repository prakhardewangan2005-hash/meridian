"""AgentSettings config resolution tests."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from meridian_agent.config import AgentSettings, load_config


def test_reserved_label_rejected() -> None:
    with pytest.raises(Exception):
        AgentSettings(node_id="x", labels={"job": "no"})


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MERIDIAN_AGENT_NODE_ID", "from-env")
    monkeypatch.setenv("MERIDIAN_AGENT_LOG_LEVEL", "DEBUG")
    s = AgentSettings()
    assert s.node_id == "from-env"
    assert s.log_level == "DEBUG"


def test_yaml_file_load(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Clean env to avoid cross-test contamination
    for k in list(os.environ):
        if k.startswith("MERIDIAN_AGENT_"):
            monkeypatch.delenv(k, raising=False)

    cfg = tmp_path / "agent.yaml"
    cfg.write_text(yaml.safe_dump({"node_id": "from-file", "log_level": "WARNING"}))
    s = load_config(cfg)
    assert s.node_id == "from-file"
    assert s.log_level == "WARNING"
