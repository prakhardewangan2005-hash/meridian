# Runbook: Network Partition

**Severity:** operational

## Impact
A segment of the fleet can't reach the controller, a dependency, or each other.
Probes will correctly report failures for the partitioned paths — that's the
system working. The job is to localize and route around it.

## Check
1. Pattern of failures: which probes, from which hosts, to which targets? A
   partition shows as a *coherent* block (one region, one AZ, one peer).
2. ICMP + traceroute probes: where does the path break? The traceroute hop list
   shows the last reachable hop.
3. Correlate with cloud provider status / recent network changes.

## Mitigate
* Provider/AZ issue → fail traffic away from the affected zone.
* Misconfigured firewall/NetworkPolicy/route → revert the change.
* Confirm inhibition is preventing a storm of downstream alerts.

## Verify
Paths recover; probe success ratios return to baseline.

## Escalate
Provider-level partition → open a provider ticket; communicate scope.

## Related
[alert-storm](alert-storm.md), [tcp-retransmit-storm](tcp-retransmit-storm.md)
