# INC-003: TCP Retransmit Storm from MTU Mismatch

* **Severity:** SEV2
* **Status:** Resolved
* **Date:** 2025-10-21
* **Authors:** on-call, network-eng
* **Duration:** 1h 12m (14:03 → 15:15 UTC)

## Summary
A new overlay network was rolled out with a 1450-byte MTU, but the agents kept
the default 1500. Large packets that couldn't fragment were silently dropped;
TCP recovered via retransmission, collapsing throughput on affected paths. The
ICMP probe's loss signal and the retransmit counter together localized it; an
MSS clamp on the gateway mitigated it immediately while MTU was corrected.

## Impact
* `icmp_loss_slo` and `http_probe_latency_slo` both burned budget for ~72 min.
* Affected paths saw p99 latency rise ~6× and effective throughput drop sharply.
* ~22% of the 30-day icmp_loss budget consumed.

## Timeline (UTC)
| Time | Event |
|---|---|
| 13:55 | Overlay network with MTU 1450 rolled out to a subnet |
| 14:03 | `HighTCPRetransmitRate` fires for hosts in that subnet |
| 14:05 | ICMP probe loss for the same paths rises in parallel |
| 14:12 | On-call runs `scripts/tcp-debug.sh`: high retrans, MTU 1500 on host |
| 14:25 | `ping -M do -s 1472` fails; `-s 1422` succeeds → MTU ~1450 path |
| 14:34 | Root cause confirmed: overlay MTU < host MTU, PMTUD not working |
| 14:41 | Mitigation: MSS clamp to PMTU on the gateway (immediate relief) |
| 14:48 | Retransmits dropping; latency recovering |
| 15:02 | Host interface MTU corrected to 1450 fleet-wide in that subnet |
| 15:15 | All SLIs recovered |

## Root cause (5 whys)
1. Why the retransmit storm? Large TCP segments were being dropped.
2. Why dropped? They exceeded the overlay path MTU and couldn't fragment (DF set).
3. Why wasn't PMTUD saving us? ICMP "fragmentation needed" was being filtered, so
   senders never learned to lower MSS.
4. Why the MTU mismatch? The overlay rollout changed path MTU but host/agent MTU
   config wasn't updated in the same change.
5. Why no guard? Nothing validated that path MTU ≥ configured interface MTU after
   network changes. ← root cause

## Detection
Excellent: two independent signals (TCP retransmit counter + ICMP loss) agreed,
which is exactly the corroboration the uniform-probe design is meant to provide.

## What went well
* Retransmit + ICMP signals localized the problem fast.
* MSS clamp gave immediate relief without waiting for the full MTU fix.

## What went poorly
* Network change and host MTU config weren't coupled.
* ICMP filtering broke PMTUD — a latent misconfiguration.

## Action items
| Action | Owner | Tracking | Status |
|---|---|---|---|
| Couple MTU config to overlay rollout in one change | @network | #151 | done |
| Stop filtering ICMP "fragmentation needed" | @network | #152 | done |
| Add an MTU probe (`ping -M do`) to the probe catalog | @agent | #153 | planned |
| Expand tcp-retransmit-storm runbook with the MTU test | @docs | #154 | done |
