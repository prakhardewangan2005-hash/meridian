# Benchmarks

Reproducible performance benchmarks with a committed baseline and a CI regression
gate (>10% regression fails the PR — see
[.github/workflows/perf-regression.yml](../.github/workflows/perf-regression.yml)).

## Run

```bash
python benchmarks/agent_throughput.py --out results/latest.json
python benchmarks/probe_scheduling.py --out results/latest-sched.json
python benchmarks/controller_api_load.py --url https://localhost:8443
```

Compare against the baseline:
```bash
python benchmarks/compare.py results/baseline-v0.1.0.json results/latest.json
```

## Files

| File | Measures |
|---|---|
| `agent_throughput.py` | probe executions/sec the runner sustains |
| `probe_scheduling.py` | scheduler jitter/drift under load |
| `controller_api_load.py` | controller API latency under concurrency |
| `results/baseline-v0.1.0.json` | committed reference numbers |
