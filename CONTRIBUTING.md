# Contributing

Thanks for your interest. This is a reference project, but contributions that
improve clarity, correctness, or coverage are welcome.

## Development setup

```bash
git clone https://github.com/your-org/meridian
cd meridian
python -m venv .venv && source .venv/bin/activate
pip install -e libs/meridian_common -e libs/meridian_proto
pip install -e "services/agent[dev]" -e "services/controller[dev]" \
            -e "services/cli[dev]" -e "services/chaos[dev]"
pre-commit install
```

Bring up the stack locally:
```bash
make dev
```

## Before you open a PR

```bash
make lint      # ruff, mypy, yamllint, shellcheck
make test      # unit + integration
tools/ci-local.sh   # full gate incl. the alert/runbook invariant
```

## Conventions

* **Code**: ruff-formatted, mypy-clean, fully type-hinted, async where I/O-bound.
* **Commits**: imperative mood ("add X", not "added X"); reference issues.
* **Alerts**: every new alert MUST carry a `runbook_url` and ship the runbook.
* **Metrics**: keep label cardinality bounded (ADR-0007).
* **Decisions**: significant ones get an ADR in `docs/adr/`.
* **Tests**: new behavior comes with tests; chaos tests run in dry-run.

## Project layout

See the [README](README.md#layout) and [docs/](docs/README.md).
