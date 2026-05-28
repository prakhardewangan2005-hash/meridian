"""E2E fixtures. Skips the whole suite if the stack isn't reachable."""
from __future__ import annotations

import os

import pytest

CONTROLLER_URL = os.environ.get("MERIDIAN_CONTROLLER_URL", "https://localhost:8443")


def _stack_up() -> bool:
    try:
        import httpx
        r = httpx.get(f"{CONTROLLER_URL}/healthz", verify=False, timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="session", autouse=True)
def require_stack() -> None:
    if not _stack_up():
        pytest.skip("Meridian stack not reachable; start it with `make dev`")


@pytest.fixture
def controller_url() -> str:
    return CONTROLLER_URL
