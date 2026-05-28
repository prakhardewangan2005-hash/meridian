# INC-002: Agent cgroup Memory Leak

* **Severity:** SEV3
* **Status:** Resolved
* **Date:** 2025-10-03
* **Authors:** on-call, agent-maintainers
* **Duration:** ~6 hours (slow burn, 02:10 → 08:05 UTC)

## Summary
A subset of agents slowly grew memory until the kernel OOM-killed them. Raw
memory-usage graphs looked unremarkable (the box had free RAM), but cgroup PSI
memory pressure was the leading indicator that surfaced it. The leak was a probe
that accumulated resolver objects across executions.

## Impact
* ~4% of agents flapped (OOM → systemd restart) over six hours.
* Buffered results survived restarts (no data loss — the buffer did its job).
* `agent_heartbeat_freshness` dipped slightly but stayed within budget.

## Timeline (UTC)
| Time | Event |
|---|---|
| 02:10 | First agent OOM-kill on a high-probe-count host (auto-restarted) |
| 03:30 | Sporadic `AgentDown` flaps begin appearing (self-resolving) |
| 06:00 | On-call notices a pattern: same hosts, ~hourly restarts |
| 06:25 | cgroup `memory.pressure` (full avg300) clearly trending up pre-OOM |
| 07:10 | Heap inspection shows resolver objects retained across probe runs |
| 07:40 | Fix: reuse a single resolver instance per probe, not per execution |
| 07:55 | Patched agent rolled to affected hosts (25% serial) |
| 08:05 | Memory flat; pressure normal; flapping stops |

## Root cause (5 whys)
1. Why were agents OOM-killed? Resident memory grew past the cgroup limit.
2. Why did it grow? A DNS probe created a new resolver object every execution and
   something retained references.
3. Why wasn't it obvious? Raw memory looked fine — page cache masked the trend on
   the node-level view.
4. Why did we miss it for hours? We were watching node memory, not cgroup PSI;
   the slow-burn rate didn't trip a fast alert.
5. Why no leak test? The agent had no long-running soak test. ← root cause

## Detection
Detection was slow because the only fast signal was the OOM restarts (which
self-healed). PSI was the signal that *should* have been alerting.

## What went well
* The disk buffer made restarts non-destructive — zero data loss.
* PSI, once consulted, pinpointed the issue cleanly.

## What went poorly
* We alerted on the symptom (restart) not the cause (rising pressure).
* No soak/leak test in CI.

## Action items
| Action | Owner | Tracking | Status |
|---|---|---|---|
| Reuse resolver per-probe instead of per-execution | @agent | #131 | done |
| Add `AgentMemoryPressureHigh` alert on PSI full avg300 | @sre | #132 | done |
| Add a 1-hour soak test to CI catching RSS growth | @agent | #133 | done |
| Document PSI-first memory triage in linux-operations | @docs | #134 | done |
