# Performance

## Benchmark methodology

[benchmarks/](../benchmarks/) contains reproducible benchmarks:

* `agent_throughput.py` — probe executions per second the runner sustains
* `probe_scheduling.py` — scheduler jitter and drift under load
* `controller_api_load.py` — controller API latency under concurrent clients

Each writes a JSON result to `benchmarks/results/`. A committed baseline
(`baseline-v0.1.0.json`) is the reference.

## CI regression gate

[.github/workflows/perf-regression.yml](../.github/workflows/perf-regression.yml)
runs the benchmarks on every PR and **fails the build if throughput regresses by
more than 10%** vs the committed baseline. This makes performance a reviewable,
enforced property rather than something that silently rots.

## Key performance properties

* **Async probe execution**: network I/O dominates probe cost, so the runner is
  fully async with bounded concurrency. CPU stays low even with many probes.
* **uvloop**: installed when available for a faster event loop.
* **fsync batching**: the buffer fsyncs every 64 writes, not every write —
  durability vs throughput tradeoff documented in
  [ADR-0006](adr/0006-local-buffer-on-agent.md).
* **Synchronous /proc reads**: microsecond memory copies, not worth async
  overhead (see [system-design.md](system-design.md)).

## Profiling

The benchmarks support `--profile` to emit a `cProfile` dump for flame-graphing.
