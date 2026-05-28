# Network Design

Meridian's network telemetry is built on five probe types that share one result
schema. This document explains each, the kernel mechanisms they use, and the
interpretation gotchas.

## Probe types

| Probe | Layer | Mechanism | Required cap |
|---|---|---|---|
| DNS | L7 | `dnspython` async resolver | none |
| TCP | L4 | `asyncio.open_connection` + optional banner read | none |
| HTTP | L7 | `aiohttp` with TLS validation + body regex | none |
| ICMP | L3 | raw socket echo request/reply | `CAP_NET_RAW` |
| Traceroute | L3 | UDP datagrams with incrementing TTL + raw ICMP listen | `CAP_NET_RAW` |

## Uniform result schema

Every probe returns a `ProbeResult` with `status` ∈ {ok, fail, timeout, error},
a latency, a timestamp, and a free-form `metadata` dict. This is what lets a
single Prometheus exporter and a single set of alert rules work across all probe
types. See [ADR-0007](adr/0007-uniform-probe-schema.md).

## ICMP details

The ICMP probe builds echo-request packets by hand: an 8-byte ICMP header
(type 8, code 0, checksum, identifier, sequence) followed by a payload. The
checksum is the standard one's-complement sum. We match replies by `(identifier,
sequence)` to avoid cross-talk between concurrent probes. Loss, jitter (stdev of
RTTs), and min/max RTT are all derived from the per-packet sample.

## Traceroute details

UDP datagrams are sent to a high destination port with TTL incrementing from 1.
Each router that decrements TTL to zero emits an ICMP TIME_EXCEEDED (type 11)
which we catch on a raw ICMP socket; the destination emits DEST_UNREACHABLE
(type 3) when the high port is closed, signaling we've arrived. The hop list is
returned in metadata for path-change detection.

## MTU and retransmits

The agent reads TCP retransmit counters from `/proc/net/netstat` and
`/proc/net/snmp` (`TcpExt_TCPLostRetransmit`, `Tcp_RetransSegs`,
`TcpExt_TCPSynRetrans`). A sustained rise in retransmits without a corresponding
rise in traffic is the classic signature of an MTU mismatch (e.g. a tunnel that
doesn't honor PMTUD) or congestion. The
[tcp-retransmit-storm runbook](../runbooks/tcp-retransmit-storm.md) walks through
the diagnosis, and [INC-003](../incident-reports/INC-003-tcp-retransmit-mtu-mismatch.md)
is a real-world example.

## Listen drops

`TcpExt_ListenDrops` and `TcpExt_ListenOverflows` indicate the accept queue is
overflowing — the application isn't `accept()`-ing fast enough or the backlog is
too small. We surface these as fleet metrics because they're an early warning of
saturation that precedes user-visible latency.

## ASN / topology annotation (future)

The traceroute hop list is structured so that hops can be annotated with ASN and
geo data in a later iteration, enabling path-change alerts ("traffic to upstream
now transits a different AS").
