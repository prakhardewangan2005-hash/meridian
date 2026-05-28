"""ICMP echo probe — raw socket, requires CAP_NET_RAW."""
from __future__ import annotations

import asyncio
import os
import socket
import statistics
import struct
import time

from meridian_agent.probes.base import Probe, ProbeResult

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0


def _checksum(data: bytes) -> int:
    s = 0
    for i in range(0, len(data) - 1, 2):
        s += (data[i + 1] << 8) | data[i]
    if len(data) % 2:
        s += data[-1]
    s = (s >> 16) + (s & 0xFFFF)
    s += s >> 16
    return ~s & 0xFFFF


def _build_packet(ident: int, seq: int, payload_size: int) -> bytes:
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, 0, ident, seq)
    payload = b"meridian-icmp\x00" + os.urandom(max(0, payload_size - 14))
    cksum = _checksum(header + payload)
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, cksum, ident, seq)
    return header + payload


class ICMPProbe(Probe):
    probe_type = "icmp"

    def __init__(
        self,
        *,
        packet_count: int = 4,
        packet_size: int = 56,
        interval_between_packets_s: float = 0.2,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self.packet_count = packet_count
        self.packet_size = packet_size
        self.interval_between_packets_s = interval_between_packets_s

    async def execute(self) -> ProbeResult:
        try:
            return await self._execute()
        except PermissionError:
            return ProbeResult.errored(self, "icmp requires CAP_NET_RAW")
        except socket.gaierror as e:
            return ProbeResult.fail(self, 0.0, error=f"resolve: {e}")
        except OSError as e:
            return ProbeResult.errored(self, f"socket: {e}")

    async def _execute(self) -> ProbeResult:
        loop = asyncio.get_running_loop()
        addr = (await loop.getaddrinfo(self.target, None, type=socket.SOCK_RAW))[0][4][0]
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.setblocking(False)
        ident = os.getpid() & 0xFFFF
        rtts: list[float] = []
        per_packet_budget = self.timeout_s / self.packet_count
        try:
            for seq in range(self.packet_count):
                pkt = _build_packet(ident, seq, self.packet_size)
                sent_at = time.perf_counter()
                await loop.sock_sendto(sock, pkt, (addr, 0))
                deadline = sent_at + per_packet_budget
                while True:
                    remaining = deadline - time.perf_counter()
                    if remaining <= 0:
                        break
                    try:
                        data, _ = await asyncio.wait_for(
                            loop.sock_recvfrom(sock, 1024), timeout=remaining
                        )
                    except asyncio.TimeoutError:
                        break
                    if len(data) < 28:
                        continue
                    icmp_type = data[20]
                    _, recv_id, recv_seq = struct.unpack("!HHH", data[22:28])
                    if (
                        icmp_type == ICMP_ECHO_REPLY
                        and recv_id == ident
                        and recv_seq == seq
                    ):
                        rtts.append(time.perf_counter() - sent_at)
                        break
                await asyncio.sleep(self.interval_between_packets_s)
        finally:
            sock.close()

        sent = self.packet_count
        received = len(rtts)
        if received == 0:
            return ProbeResult.fail(
                self, 0.0, error="100% loss", sent=sent, received=0
            )
        return ProbeResult.ok(
            self,
            latency_s=statistics.fmean(rtts),
            sent=sent,
            received=received,
            loss=1.0 - received / sent,
            jitter_s=statistics.pstdev(rtts) if len(rtts) > 1 else 0.0,
            min_rtt_s=min(rtts),
            max_rtt_s=max(rtts),
            resolved_ip=addr,
        )
