#!/usr/bin/env bash
# TCP retransmit / MTU diagnostics. Usage: tcp-debug.sh [peer]
set -uo pipefail
PEER="${1:-}"

echo "=== TCP retransmit counters (/proc/net/snmp + netstat) ==="
netstat -s 2>/dev/null | grep -iE "retrans|segments" || \
  awk '/Tcp:/{print}' /proc/net/snmp

echo; echo "=== Per-socket retransmits (ss -ti) ==="
ss -ti 2>/dev/null | grep -iB1 retrans | head -40

echo; echo "=== Listen queue overflows ==="
grep -iE "ListenDrops|ListenOverflows" /proc/net/netstat 2>/dev/null || true

if [[ -n "$PEER" ]]; then
  echo; echo "=== MTU probe to $PEER (DF set) ==="
  for sz in 1472 1422 1372; do
    if ping -c1 -W1 -M do -s "$sz" "$PEER" >/dev/null 2>&1; then
      echo "  size $sz (+28 = $((sz+28)) bytes): OK"
    else
      echo "  size $sz (+28 = $((sz+28)) bytes): FAIL  <-- path MTU likely below this"
    fi
  done
fi
