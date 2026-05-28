# System Design

How Meridian reads Linux internals and turns them into metrics.

## /proc and /sys reading

All system metrics come from kernel pseudo-filesystems, read synchronously
(they're memory-backed, so there's no blocking I/O concern):

| Source | Metrics |
|---|---|
| `/proc/stat` | CPU time deltas (user/system/idle/iowait/steal) |
| `/proc/loadavg` | 1/5/15-minute load |
| `/proc/meminfo` | memory + swap |
| `/proc/net/dev` | per-interface bytes/packets/errors/drops |
| `/proc/net/netstat`, `/proc/net/snmp` | TCP retransmits, listen drops |
| `/proc/net/sockstat` | socket allocation |
| `/proc/diskstats` | per-device IO counters |
| `statvfs` | filesystem usage + inodes |
| `/sys/fs/cgroup` | cgroup v2 memory/cpu/pids/pressure |

## CPU delta computation

`/proc/stat` exposes cumulative jiffies since boot. A single read is meaningless;
the busy percentage is `Δbusy / Δtotal` between two reads. The agent keeps the
previous snapshot and computes the delta each collection cycle. The first cycle
after start reports no percentages (no baseline yet).

## cgroup v2 only

We deliberately support only the cgroup v2 unified hierarchy. v1 is deprecated
and its multi-controller path layout adds significant branching for little value
on modern kernels. We read `memory.current`, `memory.max`, `cpu.stat`
(usage/throttling), `pids.current`, and crucially `memory.pressure` (PSI), which
is the best single signal for "this cgroup is about to OOM." See
[ADR](adr/0001-record-architecture-decisions.md) and
[INC-002](../incident-reports/INC-002-cgroup-memory-leak.md).

## Pressure Stall Information (PSI)

`memory.pressure` reports the fraction of time tasks were stalled waiting for
memory (`some` and `full` at avg10/avg60/avg300). Rising `full` pressure means
real work is being blocked — a far better leading indicator than raw memory
usage, which can sit near 100% perfectly healthily thanks to page cache.

## Why synchronous reads in an async agent

The probe path is fully async (network I/O dominates). System metric collection
is synchronous because `/proc` reads are memory copies that complete in
microseconds; wrapping them in async machinery would add overhead without
removing any blocking. They run on the same loop in a short periodic task.
