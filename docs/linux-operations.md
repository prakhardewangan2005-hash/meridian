# Linux Operations

Practical interpretation of the Linux signals Meridian collects.

## Reading CPU correctly

* `cpu_iowait_pct` high + low `cpu_busy_pct` → the box is blocked on disk, not
  compute. Look at `/proc/diskstats` (`ms_doing_io`).
* `cpu_steal_pct` > a few percent on a VM → the hypervisor is descheduling you;
  a noisy-neighbor or oversubscription problem, not your workload.
* `load_1m` >> `cpu_count` with low busy% → processes blocked in
  uninterruptible sleep (D state), usually I/O.

## Reading memory correctly

* High `mem_used_pct` is **not** a problem by itself — Linux uses free RAM for
  page cache. Use `mem_available_bytes`, which accounts for reclaimable cache.
* The real OOM predictor is `cgroup_memory_pressure_full_avg60`. Rising `full`
  pressure means tasks are actually stalling on memory reclaim.
* Swap activity (`swap_used_pct` climbing) on a server is usually bad — it means
  reclaim has spilled past cache eviction.

## Reading the network correctly

* `Tcp_RetransSegs` rate rising with flat traffic → loss or MTU problem. Cross-
  check with the ICMP probe's loss metric.
* `TcpExt_ListenDrops` / `ListenOverflows` rising → accept backlog overflow;
  raise `somaxconn`/app backlog or speed up `accept()`.
* `rx_dropped`/`tx_dropped` on an interface → ring buffer exhaustion; check
  `ethtool -g` and IRQ affinity.

## cgroup v2 quick reference

```
memory.current      bytes currently charged
memory.max          hard limit (OOM above this)
memory.high         soft limit (throttle, reclaim pressure)
memory.pressure     PSI: time stalled on memory
cpu.stat            usage_usec, throttled_usec, nr_throttled
pids.current        live pids (catch fork bombs / leaks)
```

## Useful one-liners (also in scripts/)

```bash
# Top retransmitting connections
ss -ti | grep -i retrans

# Per-interface drops at a glance
awk 'NR>2{print $1, $5, $13}' /proc/net/dev

# Current PSI memory pressure
cat /sys/fs/cgroup/memory.pressure

# What's in D state (uninterruptible)
ps -eo state,pid,comm | awk '$1=="D"'
```

See [`scripts/`](../scripts/) for the packaged versions: `linux-baseline.sh`,
`network-diag.sh`, `tcp-debug.sh`, `dns-debug.sh`, `packet-capture.sh`.
