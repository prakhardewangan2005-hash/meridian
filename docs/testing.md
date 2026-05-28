# Testing

## Test pyramid

| Layer | Location | What |
|---|---|---|
| Unit | `services/*/tests/unit` | probes, buffer, config, SLO math, chaos runner |
| Integration | `services/*/tests/integration` | agent lifecycle, controller + DB |
| E2E | `tests/e2e` | full stack: register → probe → alert → incident |
| Load | `tests/load` | Locust against the controller API |
| Chaos | `tests/chaos` | fault injection asserts SLO/alert behavior |

## Running

```bash
make test              # unit + integration
make test-e2e          # full stack (needs docker compose up)
make chaos-test        # chaos scenarios
make perf-test         # benchmarks
```

## Conventions

* `pytest-asyncio` in `auto` mode — async tests need no decorator.
* Ephemeral servers (aiohttp, asyncio) for probe tests — no external deps.
* Controller tests use an in-memory SQLite override so unit tests need no
  Postgres.
* Chaos tests run experiments in **dry-run** so they never touch real `tc`/
  `iptables` in CI.

## Coverage

Coverage is collected per service (`--cov`) and reported in CI. The buffer,
probe base, and SLO math are the highest-value targets and are covered directly.
