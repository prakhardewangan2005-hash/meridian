"""HTTP client wrapping the controller API with mTLS."""
from __future__ import annotations

import os
import ssl
from pathlib import Path

import httpx


def _build_ssl() -> ssl.SSLContext | bool:
    ca = Path(os.environ.get("MERIDIAN_CLI_CA", "/etc/meridian/pki/ca.pem"))
    cert = Path(os.environ.get("MERIDIAN_CLI_CERT", "/etc/meridian/pki/operator.pem"))
    key = Path(os.environ.get("MERIDIAN_CLI_KEY", "/etc/meridian/pki/operator-key.pem"))
    if not (ca.exists() and cert.exists() and key.exists()):
        return False  # development: skip TLS verification
    ctx = ssl.create_default_context(cafile=str(ca))
    ctx.load_cert_chain(certfile=str(cert), keyfile=str(key))
    return ctx


class ControllerClient:
    def __init__(self, base_url: str | None = None) -> None:
        self._base = (
            base_url
            or os.environ.get("MERIDIAN_CONTROLLER_URL", "https://localhost:8443")
        ).rstrip("/")
        verify = _build_ssl()
        self._client = httpx.Client(
            base_url=self._base, verify=verify, timeout=10.0
        )

    def close(self) -> None:
        self._client.close()

    def get(self, path: str, **kwargs: object) -> httpx.Response:
        return self._client.get(path, **kwargs)  # type: ignore[arg-type]

    def post(self, path: str, **kwargs: object) -> httpx.Response:
        return self._client.post(path, **kwargs)  # type: ignore[arg-type]

    def put(self, path: str, **kwargs: object) -> httpx.Response:
        return self._client.put(path, **kwargs)  # type: ignore[arg-type]

    def delete(self, path: str, **kwargs: object) -> httpx.Response:
        return self._client.delete(path, **kwargs)  # type: ignore[arg-type]
