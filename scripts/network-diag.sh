#!/usr/bin/env bash
# Full network diagnostic bundle. Usage: network-diag.sh [target]
set -uo pipefail
TGT="${1:-1.1.1.1}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "########## INTERFACES ##########"
ip -br addr 2>/dev/null || ifconfig -a

echo; echo "########## ROUTES ##########"
ip route 2>/dev/null || netstat -rn

echo; echo "########## INTERFACE DROPS (/proc/net/dev) ##########"
awk 'NR>2{printf "%-12s rx_drop=%s tx_drop=%s\n",$1,$5,$13}' /proc/net/dev

echo; echo "########## TCP ##########"
bash "$HERE/tcp-debug.sh" "$TGT"

echo; echo "########## DNS ##########"
bash "$HERE/dns-debug.sh" "$(echo "$TGT" | grep -qE '^[0-9.]+$' && echo example.com || echo "$TGT")"

echo; echo "########## CONNECTIVITY ##########"
ping -c3 -W1 "$TGT" 2>/dev/null | tail -3 || echo "  ping: FAIL"

if command -v traceroute >/dev/null; then
  echo; echo "########## PATH ##########"
  traceroute -n -w1 -q1 -m15 "$TGT" 2>/dev/null
fi
