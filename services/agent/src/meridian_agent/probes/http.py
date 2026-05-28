"""HTTP/HTTPS probe — status, body regex, TLS validation."""
from __future__ import annotations

import re
import ssl
import time

import aiohttp

from meridian_agent.probes.base import Probe, ProbeResult


class HTTPProbe(Probe):
    probe_type = "http"

    def __init__(
        self,
        *,
        method: str = "GET",
        expected_status: list[int] | None = None,
        body_regex: str | None = None,
        verify_tls: bool = True,
        follow_redirects: bool = True,
        headers: dict[str, str] | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self.method = method.upper()
        self.expected_status = expected_status or [200]
        self.body_regex = re.compile(body_regex) if body_regex else None
        self.verify_tls = verify_tls
        self.follow_redirects = follow_redirects
        self.headers = headers or {}

    async def execute(self) -> ProbeResult:
        ssl_param: ssl.SSLContext | bool = True if self.verify_tls else False
        timeout = aiohttp.ClientTimeout(total=self.timeout_s)
        start = time.perf_counter()
        try:
            connector = aiohttp.TCPConnector(ssl=ssl_param)
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.request(
                    self.method,
                    self.target,
                    headers=self.headers,
                    allow_redirects=self.follow_redirects,
                ) as resp:
                    body = await resp.text()
                    latency = time.perf_counter() - start
                    meta = {
                        "status_code": resp.status,
                        "url_final": str(resp.url),
                        "content_length": len(body),
                    }
                    if resp.status not in self.expected_status:
                        return ProbeResult.fail(
                            self, latency, error=f"unexpected status {resp.status}", **meta,
                        )
                    if self.body_regex and not self.body_regex.search(body):
                        return ProbeResult.fail(
                            self, latency, error="body regex did not match", **meta,
                        )
                    return ProbeResult.ok(self, latency, **meta)
        except aiohttp.ClientConnectorCertificateError as e:
            return ProbeResult.fail(self, time.perf_counter() - start, error=f"tls: {e}")
        except aiohttp.ClientConnectorError as e:
            return ProbeResult.fail(self, time.perf_counter() - start, error=f"connect: {e}")
        except TimeoutError:
            return ProbeResult.timeout(self)
        except aiohttp.ClientError as e:
            return ProbeResult.fail(self, time.perf_counter() - start, error=f"http: {e}")
