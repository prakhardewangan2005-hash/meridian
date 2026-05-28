"""DNS resolution probe."""
from __future__ import annotations

import time

import dns.asyncresolver
import dns.exception
import dns.rdatatype
import dns.resolver

from meridian_agent.probes.base import Probe, ProbeResult


class DNSProbe(Probe):
    probe_type = "dns"

    def __init__(
        self,
        *,
        record_type: str = "A",
        resolver: str | None = None,
        expected_substring: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self.record_type = record_type.upper()
        self.resolver_addr = resolver
        self.expected_substring = expected_substring

    async def execute(self) -> ProbeResult:
        try:
            rt = dns.rdatatype.from_text(self.record_type)
        except dns.rdatatype.UnknownRdatatype as e:
            return ProbeResult.errored(self, f"bad record type: {e}")

        resolver = dns.asyncresolver.Resolver(configure=self.resolver_addr is None)
        if self.resolver_addr:
            resolver.nameservers = [self.resolver_addr]
        resolver.lifetime = self.timeout_s

        start = time.perf_counter()
        try:
            answer = await resolver.resolve(self.target, rt)
        except dns.exception.Timeout:
            return ProbeResult.timeout(self)
        except dns.resolver.NXDOMAIN:
            return ProbeResult.fail(self, time.perf_counter() - start, error="NXDOMAIN")
        except dns.resolver.NoAnswer:
            return ProbeResult.fail(self, time.perf_counter() - start, error="NoAnswer")
        except dns.exception.DNSException as e:
            return ProbeResult.fail(
                self, time.perf_counter() - start, error=f"DNSException: {e}"
            )
        latency = time.perf_counter() - start

        records = [r.to_text() for r in answer]
        if self.expected_substring and not any(
            self.expected_substring in r for r in records
        ):
            return ProbeResult.fail(
                self,
                latency,
                error=f"expected {self.expected_substring!r} not in answer",
                records=records,
            )
        ttl = int(answer.rrset.ttl) if answer.rrset else 0
        return ProbeResult.ok(
            self,
            latency,
            record_type=self.record_type,
            records=records,
            ttl=ttl,
            resolver=self.resolver_addr or "system",
        )
