# Chaos Tests

Assert that fault injection produces the expected detection + recovery, without
touching real kernel state (experiments run in dry-run).

```bash
make chaos-test
# or
PYTHONPATH=services/chaos/src pytest tests/chaos -v
```

`partition_test.py` drives a network-partition experiment through the runner and
asserts the inject → watchdog-revert lifecycle holds.
