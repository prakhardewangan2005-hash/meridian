"""Controller test fixtures."""
from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "MERIDIAN_CONTROLLER_DB_DSN",
        "sqlite+aiosqlite:///:memory:",
    )
