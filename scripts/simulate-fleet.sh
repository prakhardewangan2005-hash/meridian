#!/usr/bin/env bash
# Run N local agents (different node ids + metrics ports) to simulate a fleet.
# Usage: simulate-fleet.sh [count]
set -euo pipefail
COUNT="${1:-3}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/services/agent/src:$ROOT/libs/meridian_common/src:$ROOT/libs/meridian_proto/src"

pids=()
cleanup() { echo "stopping $COUNT agents"; for p in "${pids[@]}"; do kill "$p" 2>/dev/null || true; done; }
trap cleanup EXIT INT TERM

for i in $(seq 1 "$COUNT"); do
  port=$((9100 + i))
  MERIDIAN_AGENT_NODE_ID="sim-$i" \
  MERIDIAN_AGENT_EXPORTER__BIND_PORT="$port" \
  python3 -m meridian_agent --probes "$ROOT/config/agent/probes.example.yaml" &
  pids+=("$!")
  echo "started sim-$i on :$port (pid $!)"
done
echo "fleet of $COUNT running; Ctrl-C to stop"
wait
