#!/usr/bin/env bash
# DNS resolution diagnostics. Usage: dns-debug.sh <name>
set -uo pipefail
NAME="${1:?usage: dns-debug.sh <name>}"

echo "=== System resolver ==="
getent hosts "$NAME" || echo "  system resolver: FAIL"

for r in 1.1.1.1 8.8.8.8; do
  echo; echo "=== via $r ==="
  if command -v dig >/dev/null; then
    dig +short +time=2 +tries=1 "@$r" "$NAME" || echo "  $r: FAIL"
  else
    nslookup "$NAME" "$r" 2>/dev/null | tail -n +4 || echo "  $r: FAIL"
  fi
done

echo; echo "=== /etc/resolv.conf ==="
grep -vE '^\s*#' /etc/resolv.conf 2>/dev/null | grep -E 'nameserver|search' || true

if command -v dig >/dev/null; then
  echo; echo "=== trace (authoritative path) ==="
  dig +trace +time=2 "$NAME" 2>/dev/null | grep -E "NS|A|CNAME" | head -20
fi
