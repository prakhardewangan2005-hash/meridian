# meridianctl

Operator CLI for the Meridian platform.

```bash
meridianctl nodes list
meridianctl probes apply -f probes.yaml
meridianctl slo status checkout-api
meridianctl incident open --code INC-005 --title "Cascading DNS failure" --severity SEV2
meridianctl chaos inject network-latency --target-node edge-01 --delay-ms 50 --duration 60s
meridianctl probes run-once --type http --target https://example.com
```

## Auth

Uses the same mTLS as the controller. Configure paths in `~/.meridian/config.yaml`
or via env vars (`MERIDIAN_CONTROLLER_URL`, `MERIDIAN_CLI_CERT`, `MERIDIAN_CLI_KEY`).
