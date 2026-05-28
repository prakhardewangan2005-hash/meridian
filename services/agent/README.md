# meridian-agent

Per-host telemetry and synthetic probe agent.

## Responsibilities

* Run synthetic probes (DNS, ICMP, TCP, HTTP, traceroute) on a schedule with jitter
* Collect Linux system metrics (`/proc/stat`, `/proc/meminfo`, `/proc/net/*`, cgroup v2)
* Expose Prometheus metrics on `:9101/metrics`
* Ship structured JSON logs to Loki
* Heartbeat to the controller over mTLS
* Buffer results to disk so collector outages don't lose data

## Configuration

Resolved from (later wins):
1. defaults in `config.py`
2. `/etc/meridian/agent.yaml`
3. `MERIDIAN_AGENT_*` env vars
4. CLI flags

See [`config/agent/agent.yaml`](../../config/agent/agent.yaml) for the full schema.

## Metrics

| Metric | Type | Labels |
|---|---|---|
| `meridian_probe_success` | gauge | probe, target, type |
| `meridian_probe_latency_seconds` | histogram | probe, target, type |
| `meridian_probe_last_run_timestamp` | gauge | probe, target, type |
| `meridian_probe_executions_total` | counter | probe, target, type, status |
| `meridian_system{metric}` | gauge | metric |
| `meridian_network{interface,metric}` | gauge | interface, metric |

## Required capabilities

* `CAP_NET_RAW` — ICMP and traceroute probes
* No other privileges. The systemd unit drops all other capabilities and applies syscall filtering.

## Deployment

* **systemd**: see `systemd/meridian-agent.service` and `deploy/ansible/roles/meridian-agent/`
* **Kubernetes**: DaemonSet at `deploy/k8s/base/agent-daemonset.yaml`
* **Docker**: built from `Dockerfile`, distroless final stage, non-root
