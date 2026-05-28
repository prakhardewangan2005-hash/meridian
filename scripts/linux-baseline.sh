#!/usr/bin/env bash
# Snapshot key Linux health signals — the "is this box healthy" one-shot.
set -uo pipefail

echo "=== LOAD / CPU ==="
cat /proc/loadavg
echo "cpu_count=$(nproc)"

echo; echo "=== MEMORY ==="
free -h 2>/dev/null || awk '/MemTotal|MemAvailable|SwapTotal/{print}' /proc/meminfo

echo; echo "=== MEMORY PRESSURE (PSI) ==="
cat /sys/fs/cgroup/memory.pressure 2>/dev/null || echo "  (cgroup v2 PSI not available)"

echo; echo "=== DISK ==="
df -h -x tmpfs -x devtmpfs 2>/dev/null | grep -vE '^Filesystem'

echo; echo "=== TOP MEMORY CONSUMERS ==="
ps -eo pid,comm,rss --sort=-rss 2>/dev/null | head -6

echo; echo "=== D-STATE (uninterruptible) PROCS ==="
ps -eo state,pid,comm 2>/dev/null | awk '$1=="D"{print}' || echo "  none"

echo; echo "=== TCP RETRANSMITS ==="
awk '/Tcp:/{print}' /proc/net/snmp | tail -1
