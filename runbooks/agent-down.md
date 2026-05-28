# Runbook: Agent Down

**Alert:** `AgentDown` (`up{job="meridian-agent"} == 0`) · **Severity:** page

## Impact
The node is not being scraped. Probes from that host are not running; we are
blind to that host's network path and system health.

## Check
1. Is it one node or many? Many → suspect controller/scrape config/network, not
   the agent. One → host-local.
2. `meridianctl nodes describe <node>` — last heartbeat?
3. On the host: `systemctl status meridian-agent`, `journalctl -u meridian-agent -n 100`.
4. `curl -s localhost:9101/metrics | head` — is the exporter up?

## Mitigate
* Crashed service → `systemctl restart meridian-agent` (systemd should already
  be retrying via `Restart=on-failure`).
* Cert problem (logs show TLS/handshake) → see [cert-rotation](cert-rotation.md).
* Disk full preventing buffer writes → see [disk-full](disk-full.md).
* If the node is genuinely gone, drain it: `meridianctl nodes drain <node>`.

## Verify
`up{job="meridian-agent",instance="<node>"} == 1` and the node returns to
`healthy` in `meridianctl nodes list`.

## Escalate
Fleet-wide AgentDown → page the platform team; check Prometheus SD and network
policy before assuming agent fault.

## Related
[controller-degraded](controller-degraded.md), [cert-rotation](cert-rotation.md),
[INC-002](../incident-reports/INC-002-cgroup-memory-leak.md)
