# Scripts

Operational and development helpers. Network/debug scripts back the
`meridianctl debug` subcommands.

| Script | Purpose |
|---|---|
| `bootstrap-dev.sh` | one-shot local dev setup (certs + compose up) |
| `generate-certs.sh` | generate a dev CA + server/agent/operator certs |
| `seed-inventory.py` | seed the controller with sample nodes/probes |
| `simulate-fleet.sh` | run N agents locally to simulate a fleet |
| `check-slo-compliance.py` | query current SLO compliance from Prometheus |
| `export-incident-timeline.py` | export an incident's timeline to markdown |
| `healthcheck.sh` | quick end-to-end health probe of the stack |
| `tcp-debug.sh` | TCP retransmit / MTU diagnostics |
| `dns-debug.sh` | DNS resolution diagnostics |
| `network-diag.sh` | full network diagnostic bundle |
| `linux-baseline.sh` | snapshot key Linux health signals |
| `packet-capture.sh` | targeted tcpdump capture wrapper |
