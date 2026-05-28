# Runbook: TCP Retransmit Storm

**Alert:** `HighTCPRetransmitRate` · **Severity:** ticket

## Impact
Elevated TCP retransmits = packet loss being recovered. Manifests as latency and
throughput collapse before any hard failure. Classic causes: MTU mismatch,
congestion, faulty NIC/link.

## Check
1. `meridian:tcp_retransmit_rate:5m` by instance — localized or widespread?
2. Cross-check the ICMP probe loss metric for the same path.
3. On the host: `scripts/tcp-debug.sh` (shows `ss -ti` retrans, `netstat -s`
   retransmit counters, current MTU).
4. **MTU test:** `ping -M do -s 1472 <peer>` — if it fails but smaller sizes
   succeed, you have an MTU/PMTUD problem (a tunnel eating 50+ bytes is typical).

## Mitigate
* MTU mismatch → set the correct MTU on the interface/tunnel, or enable MSS
  clamping on the gateway (`iptables ... TCPMSS --clamp-mss-to-pmtu`).
* Congestion → shed load / rate-limit; check for a traffic spike.
* Bad link/NIC → drain the node, replace hardware/path.

## Verify
Retransmit rate back below threshold; ICMP loss back to ~0.

## Escalate
Physical/transit issues → network engineering.

## Related
[INC-003 TCP retransmit / MTU mismatch](../incident-reports/INC-003-tcp-retransmit-mtu-mismatch.md),
[network-design.md](../docs/network-design.md)
