# Running a Chaos Experiment

Experiments default to **dry-run**. Always start there.

## Dry-run (prints the commands, changes nothing)
```bash
meridianctl chaos inject network_latency \
  --target-node edge-01 --duration 60 \
  --params '{"interface":"eth0","delay_ms":50,"jitter_ms":10}'
```

## Actually run it (note --apply)
```bash
meridianctl chaos inject network_latency \
  --target-node edge-01 --duration 60 \
  --params '{"interface":"eth0","delay_ms":50}' --apply
```

## Safety guarantees
* Mandatory `--duration`; a watchdog auto-reverts even if the service crashes.
* On shutdown the chaos service reverts everything in flight.
* `meridianctl chaos list` shows active experiments; `chaos abort <id>` reverts.

See [experiment.yaml](experiment.yaml) for a batch spec and
[config/chaos/experiments.example.yaml](../../config/chaos/experiments.example.yaml).
