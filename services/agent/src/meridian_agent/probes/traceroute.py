"""UDP-based traceroute probe.

Sends UDP datagrams with incrementing TTL. Listens on a raw ICMP socket for
TIME_EXCEEDED (type 11) and DEST_UNREACHABLE (type 3) replies. Requires CAP_NET_RAW.
"""
from __future__ import annotations

import asyncio
import socket
import time
from dataclasses import asdict, dataclass

from meridian_agent.probes.base import Probe, ProbeResult


@dataclass(slots=True)
class Hop:
    ttl: int
    ip: str | None
    rtt_s: float | None
    timeout: bool


class TracerouteProbe(Probe):
    probe_type = "traceroute"

    def __init__(
        self,
        *,
        max_hops: int = 30,
        start_port: int = 33434,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self.max_hops = max_hops
        self.start_port = start_port

    async def execute(self) -> ProbeResult:
        loop = asyncio.get_running_loop()
        try:
            dest_ip = (await loop.getaddrinfo(self.target, None))[0][4][0]
        except socket.gaierror as e:
            return ProbeResult.fail(self, 0.0, error=f"resolve: {e}")
        try:
            return await self._run(loop, dest_ip)
        except PermissionError:
            return ProbeResult.errored(self, "traceroute requires CAP_NET_RAW")
        except OSError as e:
            return ProbeResult.errored(self, f"socket: {e}")

    async def _run(self, loop: asyncio.AbstractEventLoop, dest_ip: str) -> ProbeResult:
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        recv_sock.setblocking(False)
        recv_sock.bind(("", 0))

        hops: list[Hop] = []
        reached = False
        budget_per_hop = self.timeout_s / self.max_hops
        start = time.perf_counter()
        try:
            for ttl in range(1, self.max_hops + 1):
                send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
                port = self.start_port + ttl
                send_at = time.perf_counter()
                try:
                    send_sock.sendto(b"meridian-trace", (dest_ip, port))
                except OSError:
                    hops.append(Hop(ttl, None, None, timeout=True))
                    continue

                deadline = send_at + budget_per_hop
                hop_ip: str | None = None
                hop_rtt: float | None = None
                while True:
                    remaining = deadline - time.perf_counter()
                    if remaining <= 0:
                        break
                    try:
                        data, addr = await asyncio.wait_for(
                            loop.sock_recvfrom(recv_sock, 1500), timeout=remaining
                        )
                    except asyncio.TimeoutError:
                        break
                    if len(data) < 21:
                        continue
                    icmp_type = data[20]
                    if icmp_type in (11, 3):  # TIME_EXCEEDED, DEST_UNREACHABLE
                        hop_ip = addr[0]
                        hop_rtt = time.perf_counter() - send_at
                        break

                hops.append(Hop(ttl, hop_ip, hop_rtt, timeout=(hop_ip is None)))
                if hop_ip == dest_ip:
                    reached = True
                    break
        finally:
            send_sock.close()
            recv_sock.close()

        latency = time.perf_counter() - start
        meta = {
            "destination_ip": dest_ip,
            "hops": [asdict(h) for h in hops],
            "hop_count": len(hops),
            "reached": reached,
        }
        if not reached:
            return ProbeResult.fail(
                self, latency, error="destination not reached", **meta
            )
        return ProbeResult.ok(self, latency, **meta)
