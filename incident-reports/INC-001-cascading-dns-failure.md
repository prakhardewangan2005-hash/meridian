# INC-001: Cascading DNS Failure

* **Severity:** SEV2
* **Status:** Resolved
* **Date:** 2025-09-12
* **Authors:** on-call (primary), platform-team
* **Duration:** 41 minutes (09:14 → 09:55 UTC)

## Summary
A resolver configuration push removed a forwarding zone, causing internal name
resolution to fail fleet-wide. DNS probes correctly detected it, but the failure
cascaded: HTTP and TCP probes that resolve by name also failed, producing an
alert storm that initially obscured the root cause. Reverting the resolver
config restored service.

## Impact
* `dns_probe_success_ratio` dropped to ~12% for 41 minutes.
* ~38% of the 7-day error budget for that SLO consumed.
* Downstream: HTTP/TCP probe success dipped because targets were name-based.
* No external customer impact (this is internal telemetry), but the platform was
  effectively blind to real failures during the window.

## Timeline (UTC)
| Time | Event |
|---|---|
| 09:12 | Resolver config change merged and auto-deployed |
| 09:14 | DNS probe success begins dropping |
| 09:16 | `DNSResolutionFailing` pages; within 60s, 20+ downstream alerts fire |
| 09:19 | On-call engaged; overwhelmed by alert volume |
| 09:27 | On-call sorts alerts by first-seen, identifies DNS as earliest |
| 09:31 | `scripts/dns-debug.sh` shows internal zone NXDOMAIN, public resolvers fine |
| 09:38 | Resolver config diff reviewed; missing forwarding zone identified |
| 09:46 | Previous resolver config redeployed |
| 09:52 | DNS probe success climbing through 90% |
| 09:55 | All SLIs recovered; downstream alerts auto-resolved |

## Root cause (5 whys)
1. Why did resolution fail? The resolver lost a forwarding zone for the internal
   domain.
2. Why? A config refactor dropped the zone block while reformatting.
3. Why wasn't it caught? The resolver config had no schema/contents validation in
   CI — only YAML syntax was checked.
4. Why did it cascade into a storm? Many probes are name-based, and there was no
   inhibition treating DNS as an upstream dependency of other probe types.
5. Why was triage slow? Alerts weren't ordered by causality; on-call had to
   manually reconstruct first-seen order. ← root causes (validation gap +
   missing inhibition + triage ergonomics)

## Detection
The correct alert (`DNSResolutionFailing`) fired first and fast — detection
worked. The problem was *signal-to-noise* during triage.

## What went well
* DNS probe caught it immediately; the burn-rate alert was accurate.
* Mitigation was a clean config revert; no data loss.

## What went poorly
* Alert storm buried the root cause for ~13 minutes.
* No content validation on resolver config in CI.

## Action items
| Action | Owner | Tracking | Status |
|---|---|---|---|
| Add resolver-config content validation to CI | @platform | #112 | done |
| Add inhibition: DNS failure suppresses name-based probe alerts | @sre | #113 | done |
| Add "first-seen" ordering to the incident dashboard | @sre | #114 | done |
| Document DNS-first triage in alert-storm runbook | @oncall | #115 | done |
