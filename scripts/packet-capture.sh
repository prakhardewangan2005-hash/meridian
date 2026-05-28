#!/usr/bin/env bash
# Targeted tcpdump capture wrapper. Usage: packet-capture.sh <iface> <filter> [seconds]
set -euo pipefail
IFACE="${1:?usage: packet-capture.sh <iface> <filter> [seconds]}"
FILTER="${2:-}"
SECS="${3:-10}"
OUT="/tmp/meridian-capture-$(date +%s).pcap"

echo "==> capturing on $IFACE filter='$FILTER' for ${SECS}s -> $OUT"
timeout "$SECS" tcpdump -i "$IFACE" -w "$OUT" -s 96 $FILTER || true
echo "==> wrote $OUT ($(du -h "$OUT" 2>/dev/null | cut -f1))"
echo "    open with: tcpdump -r $OUT  (or Wireshark)"
